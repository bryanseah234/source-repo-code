# PRD: sourcerepo

## Overview
A central GitHub automation hub that keeps all of Bryan's personal repos in sync. Three staggered cron workflows run every 3 hours, pushing standardized configuration files (GitHub Actions workflows, Dependabot config, issue labels, PR templates, AGENTS.md, MCP config, gitignore rules, and skills cleanup) to every owned non-archived non-fork repository via a shared sync script.

## Goals
- Sync GitHub Actions workflows to all personal repos
- Sync Dependabot configuration and security settings
- Sync issue labels and PR templates
- Sync AGENTS.md and repo-level configuration
- Remove unwanted dot folders and skills from repos
- Clean up MCP config and inject standard gitignore entries
- Run automatically every 3 hours without manual intervention

## Non-Goals
- Syncing forked or archived repos
- Per-repo customization overrides
- Secret rotation
- Deployment pipelines

## User Stories
- As Bryan, I want all my repos to have consistent GitHub Actions, labels, and templates without updating each one manually.
- As Bryan, I want any new repo I create to automatically receive standard configurations within 3 hours.

## Tech Stack
- **Platform**: GitHub Actions
- **Language**: Bash (`.github/scripts/sync-selected-paths.sh`)
- **Trigger**: cron (every 3 hours) + push to relevant paths

## Architecture
```
sourcerepo/
├── .github/
│   ├── workflows/
│   │   ├── sync-repo-settings.yml   # Cron 0 */3 * * *
│   │   ├── sync-mcp.yml             # Cron 20 */3 * * *
│   │   └── sync-skills.yml          # Cron 40 */3 * * *
│   └── scripts/
│       └── sync-selected-paths.sh   # Core sync logic
├── skills-lock.json                 # Pinned skills versions
├── README.md
└── AGENTS.md
```

**Workflow split (staggered to avoid rate limiting):**

| Workflow | Cron | What it syncs |
|----------|------|---------------|
| `sync-repo-settings.yml` | `0 */3 * * *` | Workflows, Dependabot, labels, templates, AGENTS.md, secrets |
| `sync-mcp.yml` | `20 */3 * * *` | MCP config cleanup + gitignore injection |
| `sync-skills.yml` | `40 */3 * * *` | Dot folder cleanup, skills removal, gitignore injection |

## Features (detailed)

### `sync-selected-paths.sh`
- Queries GitHub API for all owned repos (non-archived, non-fork)
- For each repo: checks out, copies target paths, commits+pushes if changed
- Uses GITHUB_TOKEN for authentication

### Repo Discovery
- GitHub API: `GET /user/repos?type=owner&archived=false`
- Filters: `fork == false`, `archived == false`

### Config Pushed
- `.github/workflows/` — standard reusable workflows
- `.github/dependabot.yml` — automated dependency updates
- `.github/ISSUE_TEMPLATE/` and `PULL_REQUEST_TEMPLATE.md`
- `AGENTS.md` — agent instructions
- `.gitignore` additions — standard ignores
- Skills and dot folder removal rules

## Deployment / Run
Runs automatically via GitHub Actions cron. To trigger manually:
- Push to `sourcerepo` main branch
- Or use GitHub Actions "Run workflow" button

## Constraints & Notes
- **GITHUB_TOKEN scope**: needs `repo` scope to push to other repos
- **Rate limits**: staggered crons (0/20/40 min) reduce GitHub API pressure
- **New repos**: picked up automatically within 3 hours of creation
- **skills-lock.json**: pins agent skill versions for consistency across repos
