# SHELL Runbook

Operational notes for maintaining the repository standard from `sourcerepo`.

## Onboard a Repo

Use the helper when creating a new owned repo:

```powershell
cd "X:\01 REPOSITORIES\sourcerepo"
pwsh -File .\tools\new_repo.ps1 `
  -Name "example-repo" `
  -Owner "hongyime" `
  -Description "Short real description under 120 characters." `
  -Tier "standard" `
  -Topics python,tool,automation `
  -RepoRoot "X:\01 REPOSITORIES"
```

For a showcase repo, pass `-Tier showcase -Homepage "https://..."`.

The script:

- creates the local repo with `README.md`, `LICENSE`, `NOTICE`, and `.gitignore`
- commits the compliant skeleton on `main`
- creates and pushes the GitHub repo
- applies description, homepage, and topics
- appends the repo to `tiers.yml` and `repos.yml`

After it runs, review the `tiers.yml` and `repos.yml` diff in `sourcerepo`, then
commit through a `shell/...` branch and PR.

Before opening the PR, verify the repo starts compliant:

```powershell
python .\tools\scan_identity.py "X:\01 REPOSITORIES\example-repo" --quiet
python .\tools\check_repo.py "X:\01 REPOSITORIES\example-repo" --json
```

If either command fails, fix the repo before publishing it as part of the
managed estate. Do not add a repo to `tiers.yml` or `repos.yml` until its
description, topics, licence, notice, README, and identity scan are ready.

## Resume a Cut-off Session

Every long-running agent run should have a progress file outside target repos,
for example:

```powershell
X:\01 REPOSITORIES\_shell\WRAPUP-PROGRESS.md
```

When a CLI is cut off or quota-exhausted:

1. Open a new CLI pointed at `X:\01 REPOSITORIES`.
2. Say exactly which progress file to read, for example:

   ```text
   resume from X:\01 REPOSITORIES\_shell\WRAPUP-PROGRESS.md
   ```

3. Before changing files, the new CLI should verify:
   - current repo and branch
   - latest Git status
   - last completed step in the progress file
   - any explicit STOP gate or approval recorded there
4. If the repo has `.agents/STATE.md`, read it next. If it references a handoff
   under `.agents/handoffs/`, read that handoff before acting.
5. Update the progress file before replying and after each meaningful step.

Do not resume from chat memory alone. Treat chat summaries, tool-local memory,
and harness-specific databases as helpful hints only; Git state plus the
progress file plus `.agents/` are the durable record.

## Update `SHELL_IDENTITY`

`SHELL_IDENTITY` is the source for the identity scanner. Never commit it and
never paste its value into issues, logs, PRs, or chat.

Local machine:

```powershell
notepad $PROFILE
```

Add or update the profile assignment there, then restart PowerShell. Do not place
the value in any repo file.

GitHub Actions secret:

```powershell
gh secret set SHELL_IDENTITY --repo hongyime/sourcerepo
```

Paste the value only into the `gh secret set` prompt.

Verify configuration without printing the value:

```powershell
if ($env:SHELL_IDENTITY) { "SHELL_IDENTITY is set" } else { "SHELL_IDENTITY is missing" }
```

## Install the Pre-commit Hook

Install once per machine:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.githooks" | Out-Null
Copy-Item "X:\01 REPOSITORIES\sourcerepo\githooks\pre-commit" "$env:USERPROFILE\.githooks\pre-commit" -Force
Copy-Item "X:\01 REPOSITORIES\sourcerepo\tools\scan_identity.py" "$env:USERPROFILE\.githooks\scan_identity.py" -Force
git config --global core.hooksPath "$env:USERPROFILE\.githooks"
```

The hook blocks commits when the working tree contains configured identity
matches. It reports file, line, and category, not the matched value.

## When Compliance Fails

Open `COMPLIANCE.md` and separate the failure type first.

Licence failures:

- add the full Apache-2.0 `LICENSE`
- add `NOTICE` with `Copyright 2026 The Prawn Organisation`

Description/topic failures:

- update `repos.yml`
- apply metadata with `gh repo edit` or let the sync workflow apply it
- keep topics within `topics.yml`
- preserve `keep-lfs` and `no-config-sync` if present

README failures:

- keep good existing prose
- add a title, real description, setup, deploy or non-deploy note, and licence
- fix broken links while editing

Working-tree identity hits:

- remove or replace the value in the current tree
- use `The Prawn Organisation` for organisation-facing ownership text
- rerun `python tools\scan_identity.py <repo> --json`

History identity hits:

- do not rewrite history automatically
- decide per repo: accept, privatise, delete, or explicitly approve history
  rewrite as a separate operation

Command errors or scanner timeouts:

- inspect the repo size and generated files
- add `.shellignore` only for generated corpora where presence is not linkage
- do not weaken `tools/scan_identity.py` to make a timeout disappear

## Visibility Policy

Visibility is an explicit `repos.yml` policy enforced by the weekly settings sync.

Recommended policy:

- Public: the default for portfolio projects, demos, static sites, open datasets,
  and public utilities that pass the identity scan.
- Private: add `visibility: private` in `repos.yml` for private operations,
  credentials-adjacent automation, projects with unclear exposure risk, private
  data workflows, or repos with unresolved history identity decisions.
- Archived: keep the existing archive state; sync handles unarchive and
  re-archive for config updates.

Do not restore the old private-except-`theprawn` rule; it does not match today’s
estate.

## Weekly Operations

Run compliance manually:

```powershell
gh workflow run "SHELL Compliance" --repo hongyime/sourcerepo
```

Run config sync manually:

```powershell
gh workflow run "Sync Repo Settings & General Config to All Repos" --repo hongyime/sourcerepo -f include_archived=true
```

The compliance workflow commits `COMPLIANCE.md` with `[skip ci]` when the report
changes.

## Workspace Scripts

The root `X:\01 REPOSITORIES` batch files are launchers only. The maintained
implementations live here:

- `tools/workspace/sync_workspace.py` - clone/fetch/fast-forward only; never
  deletes local folders.
- `tools/workspace/push_workspace.py` - reports dirty/ahead repos; never
  auto-commits and never bypasses hooks.
- `tools/workspace/infer_homepages.py` - infers project homepages from live
  GitHub metadata and GitHub Pages.

From the workspace root:

```powershell
python .\sourcerepo\tools\workspace\sync_workspace.py --workspace "X:\01 REPOSITORIES"
python .\sourcerepo\tools\workspace\push_workspace.py --workspace "X:\01 REPOSITORIES"
```

To push clean, ahead-only owned repos after reviewing the report:

```powershell
python .\sourcerepo\tools\workspace\push_workspace.py --workspace "X:\01 REPOSITORIES" --push
```

The old generic homepage `https://www.hong-yi.me` is treated as stale metadata,
not as a project homepage. To update `repos.yml` with provable deployment URLs:

```powershell
cd "X:\01 REPOSITORIES\sourcerepo"
python .\tools\workspace\infer_homepages.py
python .\tools\workspace\infer_homepages.py --write
```

To also patch GitHub live homepage fields to match the inferred state:

```powershell
python .\tools\workspace\infer_homepages.py --write --apply-live
```

Homepage policy:

- GitHub Pages enabled: `https://hongyime.github.io/<repo>/`
- Vercel/custom deployment: the real deployment URL
- No provable deployment: blank

Do not set every repo homepage to `https://www.hong-yi.me`; that recreates the
old one-size-fits-all metadata problem.
