# AUDIT.md — sourcerepo

Generated: 20260524

---

## 0. FILESYSTEM HEALTH REPORT

### Corrupted Files

| File Path | Type | Severity | Recovery Recommendation |
|-----------|------|----------|------------------------|
| (none) | — | — | — |

No corrupted files detected. All zero-byte files are __init__.py markers in Python skill packages (standard pattern).

### Orphaned Files

| File Path | Reason Flagged | Recommended Action |
|-----------|---------------|-------------------|
| (none) | — | — |

No orphaned .tmp, .bak, .old, .swp, or .lock files detected in tracked files.

### Sync Artifacts

| File Path | Suspected Cause | Recommended Action |
|-----------|----------------|-------------------|
| (none) | — | — |

No conflict copies or sync artifacts detected.

---

## 1. MASTER FEATURE MAP (SOURCE OF TRUTH)

### Core Operational Files

| File Path | Purpose | Key Functions | Inputs/Outputs | External Dependencies |
|-----------|---------|---------------|----------------|----------------------|
| .github/scripts/sync-selected-paths.sh | Core sync engine — clones all owned repos, copies config files, deletes dot dirs, injects gitignore, commits+pushes | copy_if_exists(), orce_stage_path(), delete_unlisted_dot_items(), delete_code_workspace_files(), inject_gitignore_entries(), etry() | Input: SYNC_ITEMS env var (pipe-delimited src\|dst pairs), GH_PAT. Output: git commits pushed to target repos | GitHub CLI (gh), GitHub API, jq |
| .github/workflows/sync-repo-settings.yml | Configures repo settings (visibility, merge options, descriptions) for all owned repos; propagates GH_PAT secret; syncs general config files | Three jobs: configure-repo-settings, propagate-secrets, orce-sync-general-config | Input: GH_PAT secret. Output: Updated repo settings + pushed config files | GitHub API (Octokit via github-script@v7), GitHub CLI |
| .github/workflows/sync-mcp.yml | Removes AI dot dirs + injects gitignore in all repos (no file sync) | Single job: orce-sync-mcp using sync-selected-paths.sh with empty SYNC_ITEMS | Input: GH_PAT. Output: Cleaned repos with updated gitignore | GitHub CLI |
| .github/workflows/sync-skills.yml | Identical to sync-mcp.yml — removes dot dirs + injects gitignore | Single job: orce-sync-skills | Input: GH_PAT. Output: Same as sync-mcp | GitHub CLI |
| .github/workflows/trufflehog.yml | Secret scanning on push/PR/daily schedule | Single job running trufflehog@v3.95.2 | Input: repo source. Output: Pass/fail (blocks PRs if secrets found) | trufflesecurity/trufflehog action |
| .github/workflows/dependabot-auto-merge.yml | Auto-merges Dependabot PRs after build passes | Two paths: --auto on PR open, --admin after build success | Input: PR events + workflow_run. Output: Merged PRs | GitHub CLI |
| .github/workflows/auto-merge-bots.yml | Auto-merges PRs from snyk-bot, sourcery-ai, deepsource-autofix, copilot-swe-agent | Three jobs: on-open (--auto), after-build (--admin), manual sweep | Input: PR events. Output: Merged bot PRs | GitHub CLI |
| .github/workflows/ci.yml | Build check for JS/TS PRs — detects package manager, installs deps, runs build | Single job with multi-step detection (npm/pnpm/bun) | Input: PR source. Output: Build pass/fail | Node.js, npm/pnpm/bun |
| .github/workflows/codeql.yml | CodeQL security analysis | (standard CodeQL template) | Input: source. Output: Security findings | GitHub CodeQL |
| .github/workflows/scorecard.yml | OpenSSF Scorecard | (standard template) | Input: repo. Output: Security score | ossf/scorecard-action |
| .github/workflows/dependency-review.yml | Reviews dependency changes in PRs | (standard template) | Input: PR diff. Output: Advisory alerts | actions/dependency-review-action |
| .github/workflows/greetings.yml | Welcomes first-time contributors | (standard template) | Input: issue/PR events. Output: Comment | actions/first-interaction |
| .github/workflows/labeler.yml | Auto-labels PRs based on changed paths | (standard template) | Input: PR. Output: Labels | actions/labeler |
| .github/workflows/summary.yml | PR summary generation | (standard template) | Input: PR. Output: Summary comment | (TBD — not inspected) |

### Configuration Files (Synced to Target Repos)

| File Path | Purpose |
|-----------|---------|
| .github/dependabot_config.yml | Dependabot configuration template covering 14 ecosystems (daily updates at 15:00 UTC) |
| .github/dependabot.yml | Likely copy of above (both tracked) |
| .deepsource.toml | DeepSource static analysis config — enables 17 analyzers |
| .sourcery.yml | Sourcery AI code review config (minimal — acknowledges location) |
| .github/labels.yml | Label definitions for all repos |
| .github/greetings.yml | Greeting message config |
| .github/FUNDING.yml | GitHub Sponsors config |
| .github/ISSUE_TEMPLATE/bug_report.md | Bug report template |
| .github/ISSUE_TEMPLATE/feature_request.md | Feature request template |
| .github/pull_request_template.md | PR template |
| .gitattributes | Git attribute config |
| CONTRIBUTING.md | Contribution guidelines |
| SECURITY.md | Security policy |
| AGENTS.md | AI agent configuration |

### Documentation Files

| File Path | Purpose |
|-----------|---------|
| README.md | Project overview and usage instructions |
| PRD.md | Product Requirements Document |
| docs/skills-manifest.md | Full list of installed skills |
| docs/mcp-support-matrix.md | MCP support documentation |
| .github/skills/ (20 files) | Skill documentation for GitHub-hosted skills |

### Skills Directory (1300+ tracked files)

| File Path | Purpose |
|-----------|---------|
| skills/ | AI agent skills installed via 
px skills — content files (markdown, Python scripts, XSD schemas, fonts, images) |
| skills-lock.json | Pinned versions of all installed skills |

