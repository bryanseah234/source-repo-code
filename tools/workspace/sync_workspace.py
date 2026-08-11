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
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        errors="replace",
        env=env,
        timeout=timeout,
    )


def gh_json(args: list[str]) -> object:
    proc = run(["gh", *args], timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout or "null")


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
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", remote_url.strip())
    if not match:
        return None
    owner, repo = match.groups()
    return f"{owner}/{repo.removesuffix('.git')}"


def local_repos(workspace: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    candidates = [p for p in workspace.iterdir() if p.is_dir() and p.name not in EXCLUDED_DIRS]
    for first in candidates:
        repo_dirs = [first] if (first / ".git").exists() else []
        if not repo_dirs:
            repo_dirs.extend(p for p in first.iterdir() if p.is_dir() and (p / ".git").exists())
        for repo_dir in repo_dirs:
            proc = run(["git", "remote", "get-url", "origin"], cwd=repo_dir, timeout=20)
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


def is_clean(repo_dir: Path) -> bool:
    proc = run(["git", "status", "--porcelain"], cwd=repo_dir, timeout=30)
    return proc.returncode == 0 and not proc.stdout.strip()


def current_branch(repo_dir: Path) -> str | None:
    proc = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, timeout=20)
    if proc.returncode != 0:
        return None
    branch = proc.stdout.strip()
    return None if branch == "HEAD" else branch


def sync_existing(repo_dir: Path, full_name: str, dry_run: bool) -> str:
    branch = current_branch(repo_dir)
    if not branch:
        return "skip detached"
    if not is_clean(repo_dir):
        return "skip dirty"
    if dry_run:
        return "would fetch/ff"

    fetch = run(["git", "fetch", "origin"], cwd=repo_dir, timeout=180)
    if fetch.returncode != 0:
        return "fetch failed"
    remote_branch = run(["git", "rev-parse", "--verify", f"origin/{branch}"], cwd=repo_dir, timeout=20)
    if remote_branch.returncode != 0:
        return f"skip no origin/{branch}"
    ff = run(["git", "merge", "--ff-only", f"origin/{branch}"], cwd=repo_dir, timeout=180)
    if ff.returncode != 0:
        return "skip not fast-forward"
    return "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely clone/fetch/fast-forward workspace repos.")
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    remotes = remote_repos()
    local = local_repos(workspace)

    print(f"Workspace: {workspace}")
    print(f"Remote repos in scope: {len(remotes)}")
    print("No local repos are deleted by this tool.")
    print("-" * 72)

    cloned = updated = skipped = 0
    for repo in remotes:
        full_name = repo["full_name"]
        repo_dir = local.get(full_name)
        if repo_dir:
            result = sync_existing(repo_dir, full_name, args.dry_run)
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
