# bugfix.md — sourcerepo

Generated: 20260524

## Issues from AUDIT.md

| # | Issue | Severity | Root Cause | Impact | Status |
|---|-------|----------|-----------|--------|--------|
| 1 | README references non-existent local scripts | P3 | Documentation drift | Confuses contributors | FIXED |
| 2 | .gitignore has no comment explaining scope | P3 | Missing context | Developer confusion | FIXED |
| 3 | Ghost features undocumented | P3 | Incremental additions without doc updates | Operational blind spots | FIXED |
| 4 | sync-mcp.yml and sync-skills.yml duplication unexplained | P3 | Historical separation | Maintenance confusion | FIXED |
| 5 | PAT propagation blast radius undocumented | P2 | Security model assumed | If PAT leaks, all repos affected | FIXED |
| 6 | No failure notification mechanism | P2 | Never implemented | Sync failures go unnoticed | OPEN (out of scope — requires Slack webhook) |
| 7 | GitHub Actions pinned by tag not SHA | P2 | Convenience over security | Supply-chain attack surface | OPEN (trade-off accepted — Dependabot auto-updates) |

