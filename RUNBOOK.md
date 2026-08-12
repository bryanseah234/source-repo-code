# SHELL Runbook

Operational notes for maintaining the repository standard from `sourcerepo`.

## Onboard a Repo

Use the helper when creating a new owned repo. It creates the GitHub repo from
`hongyime/theprawntemplate`, then registers it in this source repo:

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

- creates the local repo from `hongyime/theprawntemplate`
- refreshes `README.md`, `LICENSE`, `NOTICE`, and `.gitignore`
- commits the compliant project skeleton on `main`
- creates and pushes the GitHub repo
- applies description, homepage, and topics
- appends the repo to `tiers.yml` and `repos.yml`
- runs the identity scan and compliance check

After it runs, review the `tiers.yml` and `repos.yml` diff in `sourcerepo`, then
commit through a `shell/...` branch and PR.

If the GitHub template is unavailable, rerun with `-NoTemplate` to use the local
fallback scaffold.

Only pass `-SeedState` when the new repo has active cross-agent work. That copies
`.agents/STATE.template.md` to `.agents/STATE.md`. Do not seed empty state files
for repos that are not actively being handed between agents.

Before opening the PR, verify the repo starts compliant:

```powershell
python .\tools\scan_identity.py "X:\01 REPOSITORIES\example-repo" --quiet
python .\tools\check_repo.py "X:\01 REPOSITORIES\example-repo" --json
```

If either command fails, fix the repo before publishing it as part of the
managed estate. Do not add a repo to `tiers.yml` or `repos.yml` until its
description, topics, licence, notice, README, and identity scan are ready.

## Maintain the Template Repo

The template source lives in:

```text
tools/templates/theprawntemplate/
```

Publish it to GitHub with:

```powershell
cd "X:\01 REPOSITORIES\sourcerepo"
pwsh -File .\tools\publish_template_repo.ps1
```

This creates or updates `hongyime/theprawntemplate`, copies the current
`LICENSE` and `NOTICE`, and marks the GitHub repo as a template repository.

The template is intentionally small. It is for teammates and collaborators to
start cleanly, not for copying `sourcerepo` internals. Shared workflows, labels,
security config, and agent policy still come from the normal source sync.

People who create a repo from the GitHub UI should still ask a maintainer to add
the new repo to `repos.yml` and `tiers.yml`, or rerun `tools/new_repo.ps1` for
the official managed path.

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
- `tools/workspace/collect_readmes.py` - collects local README files into
  chunked context files under the workspace `Readme/` folder.
- `tools/workspace/run_source_sync.ps1` - manually dispatches the idempotent
  `sourcerepo` cross-repo sync workflow without waiting for the weekly schedule.

From the workspace root:

```powershell
python .\sourcerepo\tools\workspace\sync_workspace.py --workspace "X:\01 REPOSITORIES"
python .\sourcerepo\tools\workspace\push_workspace.py --workspace "X:\01 REPOSITORIES"
python .\sourcerepo\tools\workspace\collect_readmes.py --workspace "X:\01 REPOSITORIES"
```

To run the GitHub fan-out sync immediately:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\sourcerepo\tools\workspace\run_source_sync.ps1
```

Use `-Watch` to wait for completion, or `-NoArchived` to skip archived repos.
The workflow is idempotent: target repos with no file/settings drift produce no
commit and are skipped.

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
