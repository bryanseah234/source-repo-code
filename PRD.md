# PRD: Central Repository Automation Hub

## A. Executive Summary

This system serves as a central automation hub that enforces consistent configuration, security scanning, and operational hygiene across all personal GitHub repositories. It operates autonomously via scheduled GitHub Actions workflows, requiring zero manual intervention after initial setup.

## B. System Architecture

`
┌─────────────────────────────────────┐
│         Source Repository           │
│  (Single source of truth)           │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Config Files │  │ Workflows   │ │
│  │ (templates)  │  │ (sync logic)│ │
│  └──────┬───────┘  └──────┬──────┘ │
└─────────┼──────────────────┼────────┘
          │                  │
          ▼                  ▼
┌─────────────────────────────────────┐
│     GitHub Actions (Cron)           │
│                                     │
│  :00 → sync-repo-settings.yml      │
│  :20 → sync-mcp.yml                │
│  :40 → sync-skills.yml             │
│         (every 3 hours)             │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     Target Repositories (all)       │
│                                     │
│  • Config files pushed              │
│  • Dot dirs deleted                 │
│  • .gitignore injected              │
│  • Repo settings enforced           │
│  • GH_PAT secret propagated         │
└─────────────────────────────────────┘
`

**Data Flow:**
1. Source repo stores canonical config files and workflow definitions
2. GitHub Actions cron triggers every 3 hours (staggered at 0/20/40 minutes)
3. Sync script queries GitHub API for all owned non-archived non-fork repos
4. For each target repo: clone → copy configs → delete unwanted items → inject gitignore → commit → push (or open PR on failure)

## C. Feature Matrix

| Feature | Implementation | Trigger |
|---------|---------------|---------|
| Config file sync (workflows, Dependabot, templates, AGENTS.md) | sync-repo-settings.yml + sync-selected-paths.sh | Cron (0 \*/3 \* \* \*) + push to main |
| Repo settings enforcement (private, auto-merge, merge methods) | sync-repo-settings.yml (github-script job) | Cron (0 \*/3 \* \* \*) |
| Secret propagation (GH_PAT to all repos) | sync-repo-settings.yml (propagate-secrets job) | Cron (0 \*/3 \* \* \*) |
| AI dot directory cleanup | sync-mcp.yml + sync-skills.yml | Cron (20,40 \*/3 \* \* \*) |
| .gitignore injection (idempotent) | sync-selected-paths.sh → inject_gitignore_entries() | Every sync run |
| Dependabot PR auto-merge | dependabot-auto-merge.yml | PR events + Build Check completion |
| Bot PR auto-merge (Snyk, Sourcery, DeepSource, Copilot) | uto-merge-bots.yml | PR events + Build Check completion |
| Secret scanning | 	rufflehog.yml | Push, PR, daily at 15:00 UTC |
| Build verification (JS/TS projects) | ci.yml | PR events |
| CodeQL analysis | codeql.yml | Push, PR, scheduled |
| OpenSSF Scorecard | scorecard.yml | Scheduled |
| Dependency review | dependency-review.yml | PR events |

## D. Security and Performance

**Security Measures:**
- TruffleHog scans every push and PR for leaked secrets (blocks merge on detection)
- CodeQL static analysis for code vulnerabilities
- All secrets managed via GitHub Encrypted Secrets (never in source)
- Dependabot + auto-merge ensures dependencies stay current

**Performance Optimizations:**
- Staggered crons (0/20/40 minutes) reduce GitHub API rate limit pressure
- Shallow clones (--depth 1) for target repos minimize network transfer
- Exponential backoff retry (3 attempts) handles transient failures
- PR fallback on push failure ensures no sync is silently lost

## E. Non-Functional Requirements

**Error Handling:**
- set -euo pipefail in bash script — immediate exit on any unhandled error
- Failed clones and pushes tracked in arrays, reported at end of run
- Push failures trigger PR creation as fallback

**Logging:**
- Unstructured echo-based logging to GitHub Actions job output
- Per-repo processing status logged (Skipping/Processing/Pushed/No changes)
- Clone and push failure lists printed at run completion

