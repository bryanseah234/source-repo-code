# sourcerepo

Central automation hub for all personal GitHub repositories. Every owned, non-disabled repo gets configuration, workflows, and hygiene rules synced from here on a weekly cadence.

## How it works

**Single workflow, weekly cron, cascade-safe.**

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `sync-repo-settings.yml` | Repo settings + secrets + config files across all repos | Weekly Mon 5pm SGT + manual dispatch |

Underlying script: [`.github/scripts/sync-selected-paths.sh`](.github/scripts/sync-selected-paths.sh)

### Why weekly and not hourly?

Previously ran every 3 hours across 3 workflows → hit spending limit repeatedly. The cost-optimised weekly schedule + `[skip ci]` on downstream commits (to prevent fan-out cascade) cut Actions usage by an estimated 60–75%.

### Cascade prevention

The sync script commits config files to every target repo with `chore(config): sync from sourcerepo [skip ci]`. The `[skip ci]` marker tells GitHub Actions to skip triggering downstream workflows (CI, CodeQL, Scorecard, etc) in each target repo. Without this, one sync run would fan out to trigger 90+ repos × N workflows = quota-exhausting.

## What gets synced

Every non-disabled repo (**including archived** — see below) receives:

| Item | Source path |
|------|-------------|
| GitHub Actions workflows | `.github/workflows/ci.yml`, `codeql.yml`, `scorecard.yml`, `trufflehog.yml`, `heartbeat.yml`, `lfs-guard.yml`, `dependabot-auto-merge.yml`, `auto-merge-bots.yml`, `dependency-review.yml`, `summary.yml`, `labeler.yml`, `greetings.yml` |
| Dependabot config | `.github/dependabot_config.yml` → `.github/dependabot.yml` |
| Issue + PR templates | `.github/ISSUE_TEMPLATE/*`, `.github/pull_request_template.md` |
| Community files | `CONTRIBUTING.md`, `SECURITY.md`, `AGENTS.md` |
| Config | `.gitattributes`, `.deepsource.toml`, `.sourcery.yml`, `.github/labels.yml`, `.github/greetings.yml`, `.github/FUNDING.yml`, `LICENSE`, `NOTICE` |

**Also propagates:**
- Repo settings (auto-merge, delete-on-merge, discussions, wiki, issues, description, homepage)
- `GH_PAT` secret (for cross-repo automation)

## Archived repos

The sync handles archived repos via **unarchive → sync → re-archive** dance:

1. Detect archived flag via API
2. `PATCH archived=false`
3. Clone, apply changes, push
4. `PATCH archived=true` — restore archived state
5. On failure to re-archive, exit non-zero + surface loudly (so it's fixable)

To skip archived repos on a specific run: manual dispatch with `include_archived=false`.

## Per-repo opt-outs — GitHub Topics

Set a topic on a specific repo to change its sync behavior. Topics survive across sync runs (they're metadata on GitHub's side, not files).

| Topic | Effect |
|---|---|
| `keep-lfs` | Sync **skips** overwriting `.gitattributes` and installing `lfs-guard.yml`. The workflow (if already present) detects the topic at runtime and exits as a no-op. Use when a repo genuinely needs Git LFS. |
| `no-config-sync` | Sync **skips all config file operations** for this repo. Repo still receives settings and secrets from the other jobs but files stay untouched. Use for repos you want to fully control by hand. |

### Setting a topic

Via CLI:
```bash
gh repo edit hongyime/<repo> --add-topic keep-lfs
gh repo edit hongyime/<repo> --add-topic no-config-sync
```

Via UI: repo page → click gear icon next to **About** → Topics field → add → save.

### Removing a topic

```bash
gh repo edit hongyime/<repo> --remove-topic keep-lfs
```

Or via UI, same location.

### Listing topics for all your repos

```bash
gh api "user/repos?per_page=100&affiliation=owner" --paginate \
  --jq '.[] | {name, topics}'
```

## LFS accident prevention

Two layers stop new Git LFS bloat:

1. **`.gitattributes` template** (synced to every repo without `keep-lfs`): explicit `-filter -diff -merge` rules for 20+ common binary patterns (`*.png`, `*.jpg`, `*.mp4`, `*.log`, `*.txt`, `*.zip`, etc). Prevents accidental LFS auto-capture even if a `git lfs track` command is run.

2. **`lfs-guard.yml`** (synced to every repo without `keep-lfs`): CI workflow that scans HEAD for Git LFS pointer files on every push and PR. Fails the check if any exist, with a clear error message and opt-out instructions.

**Why this matters:** the pokemoncards repo hit 11.6 GB LFS = 1187% of free quota, blocking all LFS downloads across ALL repos on the account. Recovery required delete+recreate of the repo (loses stars/issues/PRs/watchers) OR a GitHub Support ticket (3-day wait). The guard makes the accident impossible.

## Bot PR auto-merge

Bot PRs merge automatically. Both workflows use `GH_PAT` with `--admin` to bypass branch protection:

| Bot | Workflow |
|-----|----------|
| Dependabot | `dependabot-auto-merge.yml` |
| Snyk, Sourcery, DeepSource, GitHub Copilot SWE | `auto-merge-bots.yml` |

## Setup (first-time)

1. Create a **classic** GitHub PAT with scopes: `repo`, `workflow`, `admin:repo_hook`, `delete_repo`
2. Add as `GH_PAT` in this repo: Settings → Secrets → Actions
3. Run `sync-repo-settings.yml` manually (workflow_dispatch, include_archived=true) to propagate everything
4. `GH_PAT` is auto-propagated to all other repos on subsequent runs

## Manual operations

Sync now (all repos including archived):
```bash
gh workflow run "Sync Repo Settings & General Config to All Repos" --repo hongyime/sourcerepo -f include_archived=true
```

Merge all open bot PRs across account:
```bash
gh workflow run "Auto-merge Bot PRs" --repo hongyime/sourcerepo
```

## Local sync (X: drive)

Two scripts on the X:\01 REPOSITORIES root drive user machines pull all repos locally including archived ones (read-only ops are safe on archived).

- `02 RunSync.bat` → runs `sync_repos.py` — clones missing repos, pulls current branch
- `03 RunPush.bat` → runs `push_repos.py` — auto-commits local changes, pushes

## Retry and failure behavior

- Exponential backoff (3 attempts, 2^n s delays) on clone and push
- PR fallback if direct push fails (protected branch): opens `sync-<run-id>` branch + PR
- Clone, push, and re-archive failures collected and reported at end of run
- Re-archive failures exit the script non-zero to surface loudly

## Visibility policy

Visibility is **not** currently enforced by `sync-repo-settings.yml`.

Current practical policy:

- Repos intended as portfolio, demos, datasets, or public utilities may remain public.
- Repos containing private operations, credentials-adjacent automation, private data workflows, or unclear exposure risk should be private.
- Compliance reports should flag visibility drift for human review rather than flipping visibility automatically.
- Do not restore the old private-except-`theprawn` enforcement without a deliberate review; many `sg*` and showcase repos are intentionally public today.

## Cleanup performed on every target repo

- Delete unlisted dot items at root (except exemption list: `.github/`, `.gitignore`, `.gitattributes`, `.editorconfig`, `.nvmrc`, `.node-version`, `.python-version`, `.tool-versions`, `.prettier*`, `.eslint*`, `.stylelint*`, `.babel*`, `.browserslistrc`, `.dockerignore`, `.npmrc`, `.yarnrc*`, `.pnpmfile.cjs`, `.env.example`, `.env.template`, `.env.sample`, `.sourcery.yml`, `.deepsource.toml`, `.htaccess`)
- Delete all `*.code-workspace` files recursively
- Remove `skills/`, `skills-lock.json`, and `docs/` from tracking
- Inject `.gitignore` entries to prevent re-accumulation

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
