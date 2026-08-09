# STATE

**Updated:** 2026-08-09 SGT
**By:** codex / machine: desktop
**Branch:** `molt/state-continuity`
**Ended because:** in progress

---

## Task

Establish MOLT Layer 0 so work can resume across harnesses using committed
plain-text state instead of private session stores.

## Status

`in-progress`

## Done so far

- Added `.agents` preservation to the central sync cleanup.
- Kept `.claude/` local-only and ignored.
- Updated `AGENTS.md` to require reading `.agents/STATE.md` first.
- Removed stale `sync-skills.yml`, `sync-mcp.yml`, and `.claude/skills/`
  references from `AGENTS.md`.

## Next steps

1. Finish harness pointer files.
2. Repoint `session-handoff` from `.claude/handoffs/` to `.agents/handoffs/`.
3. Prove resume behavior from a different harness.

## Decisions made

- Track only `.agents/STATE.md`, `.agents/JOURNAL.md`, and
  `.agents/handoffs/**`; keep `.agents/skills/` ignored to avoid committing a
  large generated skills tree.
- Use `The Prawn Organisation` for organization-facing copyright text.

## Gotchas

- Windows/PowerShell environment; bash has fork issues on this machine.
- Do not put secrets or personal details in `.agents/`.
- Do not rely on `.claude/` for cross-harness state.

## Files in play

- `AGENTS.md`
- `.gitignore`
- `.github/scripts/sync-selected-paths.sh`
- `.agents/STATE.md`
- `.agents/JOURNAL.md`
- `.agents/handoffs/`

## Open questions for the human

- None for Layer 0 at this moment.
