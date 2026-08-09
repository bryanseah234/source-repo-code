# JOURNAL

- 2026-08-09: Chose committed `.agents/STATE.md` plus `.agents/handoffs/` for
  cross-harness state because private harness stores do not survive tool
  switches or machine switches.
- 2026-08-09: Kept `.agents/skills/` ignored because MOLT needs durable state,
  not a large generated skills mirror committed into every repo.
- 2026-08-09: Added a committed MOLT handoff under `.agents/handoffs/` so
  future harnesses can resume from either `_shell/PROGRESS.md` or the repo-local
  handoff.
