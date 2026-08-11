#!/usr/bin/env python
"""Synchronise the local repo workspace without deleting anything.

Scope:
- hongyime org repos
- repos owned by the authenticated GitHub user
- repos where the authenticated user is an explicit collaborator

This replaces the old root sync script's dangerous pruning behavior. Missing
repos are cloned. Existing repos are fetched and fast-forwarded only when their
working tree is clean and the current branch has a matching remote branch.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


EXCLUDED_DIRS = {
    ".codeflicker",
    ".git",
    ".kiro",
    ".molt",
    ".omo",
    ".pytest_cache",
    ".shell",
    ".vscode",
    "_molt",
    "_shell",
    "Git",
    "Python",
    "Readme",
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "Never"
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            errors="replace",
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(cmd, 124, exc.stdout or "", f"timeout after {timeout}s")


def gh_json(args: list[str]) -> object:
    proc = run(["gh", *args], timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout or "null")


def normalize_path(path: Path) -> Path:
    return Path(str(path).strip().strip('"')).resolve()


def authenticated_user() -> str:
    data = gh_json(["api", "user"])
    return str(data["login"])


def paginated(endpoint: str) -> list[dict]:
    proc = run(["gh", "api", "--paginate", endpoint], timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    items: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, list):
            items.extend(payload)
        else:
            items.append(payload)
    return items


def remote_repos() -> list[dict]:
    user = authenticated_user()
    repos: dict[str, dict] = {}

    for repo in paginated("orgs/hongyime/repos?per_page=100&type=all"):
        if not repo.get("fork") and not repo.get("disabled"):
            repos[repo["full_name"]] = repo

    for repo in paginated("user/repos?per_page=100&affiliation=owner,collaborator"):
        owner = repo.get("owner", {})
        owner_login = owner.get("login")
        owner_type = owner.get("type")
        if repo.get("fork") or repo.get("disabled"):
            continue
        if owner_login in {"hongyime", user}:
            repos[repo["full_name"]] = repo
            continue
        if owner_type == "User":
            repos[repo["full_name"]] = repo

    return sorted(repos.values(), key=lambda item: item["full_name"].lower())


def parse_full_name(remote_url: str) -> str | None:
    match = re.search(r"github\.com[:/]([^/]+)/(.+?)(?:\.git)?$", remote_url.strip())
    if not match:
        return None
    owner, repo = match.groups()
    return f"{owner}/{repo.removesuffix('.git')}"


def local_repos(workspace: Path, command_timeout: int) -> dict[str, Path]:
    found: dict[str, Path] = {}
    candidates = [p for p in workspace.iterdir() if p.is_dir() and p.name not in EXCLUDED_DIRS]
    for first in candidates:
        repo_dirs = [first] if (first / ".git").exists() else []
        if not repo_dirs:
            repo_dirs.extend(p for p in first.iterdir() if p.is_dir() and (p / ".git").exists())
        for repo_dir in repo_dirs:
            proc = run(["git", "remote", "get-url", "origin"], cwd=repo_dir, timeout=command_timeout)
            if proc.returncode != 0:
                continue
            full_name = parse_full_name(proc.stdout)
            if full_name and full_name not in found:
                found[full_name] = repo_dir
    return found


def clone_path(workspace: Path, full_name: str) -> Path:
    owner, repo = full_name.split("/", 1)
    if owner in {"hongyime", authenticated_user()}:
        return workspace / repo
    return workspace / owner / repo


def selected(full_name: str, filters: set[str]) -> bool:
    if not filters:
        return True
    lowered = full_name.lower()
    repo = lowered.rsplit("/", 1)[-1]
    return lowered in filters or repo in filters


def is_clean(repo_dir: Path, command_timeout: int) -> bool:
    proc = run(["git", "status", "--porcelain"], cwd=repo_dir, timeout=command_timeout)
    return proc.returncode == 0 and not proc.stdout.strip()


def has_tracked_changes(repo_dir: Path, command_timeout: int) -> bool:
    proc = run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo_dir, timeout=command_timeout)
    return proc.returncode != 0 or bool(proc.stdout.strip())


def current_branch(repo_dir: Path, command_timeout: int) -> str | None:
    proc = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, timeout=command_timeout)
    if proc.returncode != 0:
        return None
    branch = proc.stdout.strip()
    return None if branch == "HEAD" else branch


def count_revs(repo_dir: Path, revspec: str, command_timeout: int) -> int | None:
    proc = run(["git", "rev-list", "--count", revspec], cwd=repo_dir, timeout=command_timeout)
    if proc.returncode != 0:
        return None
    try:
        return int((proc.stdout or "0").strip() or "0")
    except ValueError:
        return None


def ask_choice(prompt: str, choices: set[str], default: str) -> str:
    suffix = "/".join(sorted(choices))
    response = input(f"{prompt} [{suffix}] default={default}: ").strip().lower()
    return response if response in choices else default


def merge_origin(repo_dir: Path, branch: str) -> str:
    merge = run(["git", "merge", "--no-edit", f"origin/{branch}"], cwd=repo_dir, timeout=300)
    if merge.returncode == 0:
        return "merged"

    print((merge.stderr or merge.stdout).strip()[:400])
    choice = ask_choice("Merge conflicted. Choose: abort, local, github", {"abort", "local", "github"}, "abort")
    if choice == "local":
        run(["git", "checkout", "--ours", "."], cwd=repo_dir, timeout=120)
        run(["git", "add", "-A"], cwd=repo_dir, timeout=120)
        commit = run(["git", "commit", "--no-edit"], cwd=repo_dir, timeout=120)
        return "merged keep-local" if commit.returncode == 0 else "merge keep-local failed"
    if choice == "github":
        run(["git", "checkout", "--theirs", "."], cwd=repo_dir, timeout=120)
        run(["git", "add", "-A"], cwd=repo_dir, timeout=120)
        commit = run(["git", "commit", "--no-edit"], cwd=repo_dir, timeout=120)
        return "merged keep-github" if commit.returncode == 0 else "merge keep-github failed"

    run(["git", "merge", "--abort"], cwd=repo_dir, timeout=120)
    return "skip merge conflict"


def interactive_dirty_sync(repo_dir: Path, branch: str, command_timeout: int) -> str:
    choice = ask_choice("Dirty repo. Choose: skip, stash, local, github", {"skip", "stash", "local", "github"}, "skip")
    if choice == "skip":
        return "skip dirty"
    if choice == "github":
        confirm = ask_choice("This discards local tracked changes and untracked files. Type github to confirm", {"github", "skip"}, "skip")
        if confirm != "github":
            return "skip dirty"
        reset = run(["git", "reset", "--hard", f"origin/{branch}"], cwd=repo_dir, timeout=180)
        clean = run(["git", "clean", "-fd"], cwd=repo_dir, timeout=180)
        return "kept github" if reset.returncode == 0 and clean.returncode == 0 else "keep github failed"
    if choice == "local":
        if not has_tracked_changes(repo_dir, command_timeout):
            return "skip dirty untracked only"
        commit = run(["git", "add", "-A"], cwd=repo_dir, timeout=120)
        if commit.returncode != 0:
            return "stage failed"
        commit = run(["git", "commit", "-m", "chore: save local workspace changes"], cwd=repo_dir, timeout=180)
        if commit.returncode != 0:
            return "commit failed"
        return merge_origin(repo_dir, branch)

    stash = run(["git", "stash", "push", "-u", "-m", "workspace sync"], cwd=repo_dir, timeout=180)
    if stash.returncode != 0:
        return "stash failed"
    ff = run(["git", "merge", "--ff-only", f"origin/{branch}"], cwd=repo_dir, timeout=180)
    if ff.returncode != 0:
        run(["git", "stash", "pop"], cwd=repo_dir, timeout=180)
        return "stash restored; ff failed"
    pop = run(["git", "stash", "pop"], cwd=repo_dir, timeout=180)
    return "updated with stash" if pop.returncode == 0 else "updated; stash pop conflict"


def sync_existing(repo_dir: Path, full_name: str, dry_run: bool, command_timeout: int, interactive: bool) -> str:
    branch = current_branch(repo_dir, command_timeout)
    if not branch:
        return "skip detached"
    if dry_run:
        return "would fetch/ff"

    fetch = run(["git", "fetch", "origin"], cwd=repo_dir, timeout=180)
    if fetch.returncode != 0:
        return "fetch failed"
    remote_branch = run(["git", "rev-parse", "--verify", f"origin/{branch}"], cwd=repo_dir, timeout=command_timeout)
    if remote_branch.returncode != 0:
        return f"skip no origin/{branch}"

    if not is_clean(repo_dir, command_timeout):
        return interactive_dirty_sync(repo_dir, branch, command_timeout) if interactive else "skip dirty"

    ahead = count_revs(repo_dir, f"origin/{branch}..HEAD", command_timeout)
    behind = count_revs(repo_dir, f"HEAD..origin/{branch}", command_timeout)
    if ahead is None or behind is None:
        return "skip rev-list failed"
    if ahead == 0 and behind == 0:
        return "current"
    if ahead > 0 and behind == 0:
        return "local ahead"

    ff = run(["git", "merge", "--ff-only", f"origin/{branch}"], cwd=repo_dir, timeout=180)
    if ff.returncode == 0:
        return "updated"

    if not interactive:
        return "skip not fast-forward"
    choice = ask_choice("Branch diverged. Choose: skip, merge, local, github", {"skip", "merge", "local", "github"}, "skip")
    if choice == "merge":
        return merge_origin(repo_dir, branch)
    if choice == "github":
        confirm = ask_choice("This resets the branch to GitHub. Type github to confirm", {"github", "skip"}, "skip")
        if confirm != "github":
            return "skip not fast-forward"
        reset = run(["git", "reset", "--hard", f"origin/{branch}"], cwd=repo_dir, timeout=180)
        return "kept github" if reset.returncode == 0 else "keep github failed"
    if choice == "local":
        return "kept local"
    return "skip not fast-forward"


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="Safely clone/fetch/fast-forward workspace repos.")
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--interactive", action="store_true", help="prompt for dirty/diverged repo decisions")
    parser.add_argument("--command-timeout", type=int, default=8, help="per-repo git command timeout in seconds")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="limit to a repo name or full repo name; may be repeated",
    )
    args = parser.parse_args()

    workspace = normalize_path(args.workspace)
    filters = {item.strip().lower() for raw in args.only for item in raw.split(",") if item.strip()}
    remotes = remote_repos()
    if filters:
        remotes = [repo for repo in remotes if selected(repo["full_name"], filters)]
    local = local_repos(workspace, args.command_timeout)

    print(f"Workspace: {workspace}")
    print(f"Remote repos in scope: {len(remotes)}")
    if filters:
        print(f"Filter: {', '.join(sorted(filters))}")
    print("No local repos are deleted by this tool.")
    print("-" * 72)

    cloned = updated = skipped = 0
    for repo in remotes:
        full_name = repo["full_name"]
        repo_dir = local.get(full_name)
        if repo_dir:
            result = sync_existing(repo_dir, full_name, args.dry_run, args.command_timeout, args.interactive)
            if result == "updated":
                updated += 1
            else:
                skipped += 1
            print(f"[{result.upper():18}] {full_name} -> {repo_dir}")
            continue

        target = clone_path(workspace, full_name)
        if args.dry_run:
            print(f"[WOULD CLONE        ] {full_name} -> {target}")
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        clone = run(["gh", "repo", "clone", full_name, str(target), "--", "--filter=blob:none"], timeout=600)
        if clone.returncode == 0:
            cloned += 1
            print(f"[CLONED            ] {full_name} -> {target}")
        else:
            skipped += 1
            print(f"[CLONE FAILED      ] {full_name}: {(clone.stderr or clone.stdout).strip()[:160]}")

    print("-" * 72)
    print(f"Updated: {updated} | Cloned: {cloned} | Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
