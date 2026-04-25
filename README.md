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

## Local tools

| Script | Purpose |
|--------|---------|
| `sync_repos.py` | Pull / clone all GitHub repos locally. Defers diverged branches for interactive resolution. |
| `push_repos.py` | Stage, commit, and push all local repos with changes. Respects branch protection. |
| `02 RunSync.bat` | Runs `sync_repos.py` using portable Git + Python |
| `03 RunPush.bat` | Runs `push_repos.py` using portable Git + Python |

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
