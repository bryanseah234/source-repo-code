# sourcerepo

Central automation hub for all personal GitHub repositories. Every owned, non-archived, non-fork repo gets configuration, workflows, and hygiene rules synced here automatically every 3 hours.

## How it works

Three sync workflows run on a staggered 3-hour cron and on push to relevant paths. All call the same script: `.github/scripts/sync-selected-paths.sh`.

| Workflow | Purpose | Cron |
|----------|---------|------|
| `sync-repo-settings.yml` | Repo settings, workflows, Dependabot config, labels, templates, AGENTS.md, secrets | `0 */3 * * *` |
| `sync-mcp.yml` | MCP config cleanup + gitignore injection | `20 */3 * * *` |
| `sync-skills.yml` | Dot folder cleanup, skills removal, gitignore injection | `40 */3 * * *` |

## What gets synced to every repo

| Item | Via |
|------|-----|
| GitHub Actions workflows (dependabot-auto-merge, auto-merge-bots, trufflehog, labeler, greetings) | `sync-repo-settings.yml` |
| Dependabot config (all ecosystems, daily) | `sync-repo-settings.yml` |
| Repo settings (auto-merge, delete-on-merge, squash/merge/rebase) | `sync-repo-settings.yml` |
| `GH_PAT` secret (propagated for admin merges) | `sync-repo-settings.yml` |
| Issue templates, PR template | `sync-repo-settings.yml` |
| `CONTRIBUTING.md`, `SECURITY.md`, `AGENTS.md`, `.gitattributes` | `sync-repo-settings.yml` |
| DeepSource + Sourcery config | `sync-repo-settings.yml` |

## What is NOT synced (intentionally local-only)

| Item | Reason |
|------|--------|
| Dot tool folders (`.claude/`, `.windsurf/`, `.roo/`, etc.) | ~40k files — gitignored, each dev manages their own AI tools |
| `skills/`, `skills-lock.json` | AI tool skills — per-developer, not project-specific |
| `docs/`, `templates/` | Reference only, not for collaborators |

The sync script **actively deletes** these from target repos and injects `.gitignore` entries to prevent re-accumulation. This keeps `git status` fast for collaborators.

## Bot PR auto-merge

All bot PRs merge automatically on open — no manual action needed:

| Bot | Workflow |
|-----|---------|
| Dependabot (all versions including major) | `dependabot-auto-merge.yml` |
| Snyk, Sourcery, DeepSource, GitHub Copilot SWE | `auto-merge-bots.yml` |

Both use `GH_PAT` with `--admin` to bypass branch protection rules.

## Setup

1. Create a GitHub PAT with `repo`, `workflow`, and `admin:repo_hook` scopes
2. Add it as `GH_PAT` in this repo: **Settings → Secrets and variables → Actions**
3. `sync-repo-settings.yml` automatically propagates `GH_PAT` to all other repos

## Installed Skills

Skills installed via `npx skills`, tracked in `skills-lock.json` (320+ entries):

| Skill | Purpose |
|-------|---------|
| `web-design-guidelines` | UI/UX, accessibility, frontend review |
| `vercel-react-best-practices` | React/Next.js performance patterns |
| `vercel-composition-patterns` | React component composition |
| `vercel-react-view-transitions` | View transition animations |
| `conventional-commit` | Commit message standards |
| `pin-github-actions` | Pin Actions workflows to SHA |
| `verify-pr-logs` | CI log diagnosis |
| `verify-readme-features` | README vs implementation consistency |
| `diataxis` | Documentation governance |
| `mcp-builder` | MCP server design and build |

Full manifest: [`docs/skills-manifest.md`](docs/skills-manifest.md)

## License

MIT

## Operational details

### Retry and fallback behavior

The sync script (sync-selected-paths.sh) implements:

- **Exponential backoff retry** (3 attempts, 2^n second delays) on git clone and git push operations
- **PR fallback**: if a direct push to the default branch fails (e.g., branch protection), the script creates a sync-<run-id> branch and opens a PR automatically
- **Failure tracking**: clone and push failures are collected and reported at the end of the run

### Cleanup behavior

The sync script performs these cleanup actions on every target repo:

- **Dot directory removal**: deletes all root-level dot items except an explicit exemption list (.git, .github, .editorconfig, package manager configs, linter configs, .env.* templates)
- **Workspace file removal**: recursively deletes all *.code-workspace files
- **Directory removal**: removes skills/, skills-lock.json, docs/, 	emplates/ from git tracking

### Visibility policy

The sync-repo-settings.yml workflow enforces:

- All repos set to **private** by default
- Exception: repos with 	heprawn in the name are set to **public**

### Manual sweep

The uto-merge-bots.yml workflow supports workflow_dispatch to merge ALL open bot PRs across the repo in a single sweep.

### Why sync-mcp and sync-skills are separate workflows

Both sync-mcp.yml and sync-skills.yml run the same cleanup logic (delete dot dirs, inject gitignore). They are staggered at 20-minute intervals (:20 and :40 past the hour) to:

1. Reduce GitHub API rate limit pressure
2. Isolate failures — if one workflow errors, the other still runs
3. Allow independent manual triggers via workflow_dispatch
