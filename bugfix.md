# bugfix.md — sourcerepo

Generated: 20260524

## Issues from AUDIT.md

| # | Issue | Severity | Root Cause | Impact | Status |
|---|-------|----------|-----------|--------|--------|
| 1 | README references non-existent local scripts (sync_repos.py, push_repos.py, batch files) | P3 | Documentation drift — files exist locally but are not tracked in git | Confuses contributors who clone the repo | Open |
| 2 | .gitignore has no comment explaining it targets OTHER repos, not this one | P3 | Missing context | New contributors confused why tracked files appear in .gitignore | Open |
| 3 | Ghost features undocumented (PR fallback, retry logic, sweep job, isTheprawn visibility rule) | P3 | Incremental feature additions without doc updates | Operational blind spots | Open |
| 4 | sync-mcp.yml and sync-skills.yml are functionally identical | P3 | Historical separation that lost its purpose | Maintenance confusion | Open |
| 5 | No failure notification mechanism | P2 | Never implemented | Sync failures go unnoticed for up to 3 hours | Open |
| 6 | GitHub Actions pinned by tag not SHA | P2 | Convenience over security | Supply-chain attack surface | Open |
| 7 | PAT propagation blast radius undocumented | P2 | Security model assumed but not written down | If PAT leaks, all repos are affected | Open |

