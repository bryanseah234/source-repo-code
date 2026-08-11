#!/usr/bin/env python
"""Report and optionally push clean, ahead-only workspace repos.

This tool deliberately does not auto-commit. It also does not use --no-verify,
so the global SHELL pre-commit/push hooks remain in force.
"""

from __future__ import annotations

import argparse
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


def parse_full_name(remote_url: str) -> str | None:
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", remote_url.strip())
    if not match:
        return None
    owner, repo = match.groups()
    return f"{owner}/{repo.removesuffix('.git')}"


def normalize_path(path: Path) -> Path:
    return Path(str(path).strip().strip('"')).resolve()


def authenticated_user() -> str:
    proc = run(["gh", "api", "user", "--jq", ".login"], timeout=30)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError("gh authentication is required to determine the personal owner")
    return proc.stdout.strip()


def iter_git_repos(workspace: Path) -> list[Path]:
    repos: list[Path] = []
    for first in workspace.iterdir():
        if not first.is_dir() or first.name in EXCLUDED_DIRS:
            continue
        if (first / ".git").exists():
            repos.append(first)
            continue
        repos.extend(p for p in first.iterdir() if p.is_dir() and (p / ".git").exists())
    return sorted(repos, key=lambda p: str(p).lower())


def status(repo_dir: Path, personal_owner: str, command_timeout: int) -> tuple[str, str | None]:
    remote = run(["git", "remote", "get-url", "origin"], cwd=repo_dir, timeout=command_timeout)
    full_name = parse_full_name(remote.stdout) if remote.returncode == 0 else None
    if not full_name:
        return "skip non-github", None
    owner = full_name.split("/", 1)[0]
    if owner not in {"hongyime", personal_owner}:
        return "skip external", full_name

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, timeout=command_timeout)
    if branch.returncode != 0 or branch.stdout.strip() == "HEAD":
        return "skip detached", full_name

    dirty = run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo_dir, timeout=command_timeout)
    if dirty.returncode != 0:
        if dirty.returncode == 124:
            return f"skip status timeout {command_timeout}s", full_name
        return "skip status failed", full_name
    if dirty.stdout.strip():
        return "dirty - commit manually", full_name

    upstream = run(["git", "rev-parse", "--abbrev-ref", "@{u}"], cwd=repo_dir, timeout=command_timeout)
    if upstream.returncode != 0:
        return "skip no upstream", full_name

    ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"], cwd=repo_dir, timeout=command_timeout)
    behind = run(["git", "rev-list", "--count", "HEAD..@{u}"], cwd=repo_dir, timeout=command_timeout)
    if ahead.returncode != 0 or behind.returncode != 0:
        return "skip rev-list failed", full_name
    ahead_n = int((ahead.stdout or "0").strip() or "0")
    behind_n = int((behind.stdout or "0").strip() or "0")
    if behind_n:
        return f"skip behind {behind_n}", full_name
    if ahead_n:
        return f"push {ahead_n}", full_name
    return "clean", full_name


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="Report/push clean ahead-only owned repos.")
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--push", action="store_true", help="push clean ahead-only repos")
    parser.add_argument("--command-timeout", type=int, default=8, help="per-repo git command timeout in seconds")
    args = parser.parse_args()

    workspace = normalize_path(args.workspace)
    personal_owner = authenticated_user()
    pushed = 0
    print(f"Workspace: {workspace}")
    print("No commits are created by this tool.")
    print("-" * 72)
    for repo_dir in iter_git_repos(workspace):
        state, full_name = status(repo_dir, personal_owner, args.command_timeout)
        label = full_name or repo_dir.name
        print(f"[{state.upper():22}] {label} -> {repo_dir}")
        if args.push and state.startswith("push "):
            proc = run(["git", "push"], cwd=repo_dir, timeout=300)
            if proc.returncode == 0:
                pushed += 1
                print(f"  pushed {label}")
            else:
                print(f"  push failed: {(proc.stderr or proc.stdout).strip()[:160]}")
    print("-" * 72)
    print(f"Pushed: {pushed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
