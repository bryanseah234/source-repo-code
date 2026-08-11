#!/usr/bin/env python
"""Infer repo homepages and update repos.yml.

Rules:
- Preserve real non-generic live homepage URLs already in repos.yml/GitHub.
- If GitHub Pages is enabled, set the Pages URL reported by the GitHub API.
- Treat https://www.hong-yi.me as a stale generic homepage, not a project URL.
- Leave homepage blank when no deployment can be proved.

This tool updates the source-of-truth map. The existing sync workflow applies
non-empty homepage values from repos.yml and preserves blanks.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


GENERIC_HOMEPAGES = {"https://www.hong-yi.me", "https://hong-yi.me"}


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=timeout)


def gh_json(args: list[str]) -> object | None:
    proc = run(["gh", *args], timeout=120)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout or "null")


def live_homepages(owner: str = "hongyime") -> dict[str, str]:
    proc = run([
        "gh", "repo", "list", owner,
        "--limit", "100",
        "--json", "name,homepageUrl",
    ], timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    repos = json.loads(proc.stdout or "[]")
    return {
        f"{owner}/{item['name']}": str(item.get("homepageUrl") or "")
        for item in repos
    }


def read_repo_blocks(path: Path) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_key: str | None = None
    current_lines: list[str] = []
    preamble: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+):\s*$", line)
        if match:
            if current_key is None:
                preamble = current_lines
            else:
                blocks.append((current_key, current_lines))
            current_key = match.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_key is None:
        return [("", current_lines)]
    blocks.insert(0, ("", preamble))
    blocks.append((current_key, current_lines))
    return blocks


def current_homepage(block: list[str]) -> str:
    for line in block:
        match = re.match(r"^  homepage:\s*(.*)$", line)
        if match:
            value = match.group(1).strip()
            if len(value) >= 2 and value[0] in "'\"" and value[-1] == value[0]:
                value = value[1:-1]
            return value
    return ""


def set_homepage(block: list[str], homepage: str) -> list[str]:
    out: list[str] = []
    replaced = False
    for line in block:
        if re.match(r"^  homepage:\s*", line):
            out.append(f'  homepage: "{homepage}"')
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.insert(2, f'  homepage: "{homepage}"')
    return out


def github_pages_homepage(full_name: str) -> str:
    pages = gh_json(["api", f"repos/{full_name}/pages"])
    if isinstance(pages, dict):
        html_url = str(pages.get("html_url") or "")
        if html_url:
            return html_url
    return ""


def apply_live_homepage(full_name: str, homepage: str) -> None:
    proc = run([
        "gh", "api", "-X", "PATCH", f"repos/{full_name}",
        "-f", f"homepage={homepage}",
    ], timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"{full_name}: {(proc.stderr or proc.stdout).strip()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer homepage values into repos.yml.")
    parser.add_argument("--repos-yml", type=Path, default=Path("repos.yml"))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--apply-live", action="store_true", help="patch GitHub homepage fields too")
    args = parser.parse_args()

    blocks = read_repo_blocks(args.repos_yml)
    live = live_homepages()
    changed: list[tuple[str, str, str]] = []
    live_changes: list[tuple[str, str, str]] = []
    output: list[str] = []

    for key, block in blocks:
        if not key:
            output.extend(block)
            continue
        before = current_homepage(block)
        live_homepage = live.get(key, "")
        if live_homepage and live_homepage not in GENERIC_HOMEPAGES:
            after = live_homepage
        else:
            after = github_pages_homepage(key)
        if before in GENERIC_HOMEPAGES:
            before = ""
        if before != after:
            changed.append((key, before, after))
            block = set_homepage(block, after)
        if live_homepage != after:
            live_changes.append((key, live_homepage, after))
        output.extend(block)

    for full_name, before, after in changed:
        print(f"{full_name}: {before or '<blank>'} -> {after or '<blank>'}")
    print(f"changes={len(changed)}")
    if args.apply_live:
        for full_name, before, after in live_changes:
            print(f"live {full_name}: {before or '<blank>'} -> {after or '<blank>'}")
            apply_live_homepage(full_name, after)
        print(f"live_changes={len(live_changes)}")
    elif live_changes:
        print(f"live_changes={len(live_changes)} (pass --apply-live to patch GitHub)")

    if args.write and changed:
        args.repos_yml.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    elif changed:
        print("dry-run only; pass --write to update repos.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
