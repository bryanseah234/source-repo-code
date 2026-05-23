# design.md — sourcerepo

Generated: 20260524

## Planned Changes

### 1. Documentation Fixes (P3)
- Remove "Local tools" section from README.md (these scripts are not version-controlled here)
- Add explanatory comment to .gitignore clarifying source-repo vs target-repo scope
- Document ghost features in README.md: PR fallback on push failure, retry with exponential backoff, sweep job, isTheprawn visibility exception, delete_code_workspace_files behavior

### 2. Security Documentation (P2)
- Add PAT security model section to SECURITY.md documenting: scope, blast radius, rotation policy, and the --admin merge pattern

### 3. No Code Changes Required
- The sync-mcp/sync-skills duplication is intentional (staggered crons prevent rate limiting) — document the rationale rather than merge
- GitHub Actions SHA pinning is a trade-off — document the decision rather than implementing it (auto-updates via Dependabot would break with SHA pinning)
- Failure notifications would require additional infrastructure (Slack webhook) — out of scope for this audit, flagged for future

## Dependencies
None. All changes are documentation-only.

## Risk Assessment
Zero risk — all changes are markdown edits with no behavioral impact.

