# STATE

**Updated:** 2026-08-09 SGT
**By:** codex / machine: desktop
**Branch:** `molt/state-continuity`
**Ended because:** ready for cross-harness proof with committed handoff

---

## Task

Establish MOLT Layer 0 so work can resume across harnesses using committed
plain-text state instead of private session stores.

## Status

`ready-for-review`

## Done so far

- Added `.agents` preservation to the central sync cleanup.
- Kept `.claude/` local-only and ignored.
- Updated `AGENTS.md` to require reading `.agents/STATE.md` first.
- Removed stale `sync-skills.yml`, `sync-mcp.yml`, and `.claude/skills/`
  references from `AGENTS.md`.
- Added thin pointer files for Claude, Gemini, and Kiro.
- Seeded `theprawnprojects/.agents/STATE.md` as the first active repo state
  file.
- Repointed local `session-handoff` skill copies from `.claude/handoffs/` to
  `.agents/handoffs/` and made validation block on secret or identity hits.
- Added a committed handoff document under `.agents/handoffs/` so a cold
  harness has a compact resume target in addition to this state file.

## Next steps

1. Prove resume behavior from a different harness by asking it to read
   `X:\01 REPOSITORIES\_shell\PROGRESS.md`.
2. Ask that harness to also read the latest handoff in `.agents/handoffs/`.
3. If the harness picks up the current state, push/open PRs for the MOLT
   branches.
4. Keep SHELL remediation paused until central sync/state changes are reviewed.

Exact Phase 3 proof prompt to paste into a different CLI:

```text
resume from X:\01 REPOSITORIES\_shell\PROGRESS.md
```

## Decisions made

- Track only `.agents/STATE.md`, `.agents/JOURNAL.md`, and
  `.agents/handoffs/**`; keep `.agents/skills/` ignored to avoid committing a
  large generated skills tree.
- Use `The Prawn Organisation` for organization-facing copyright text.

## Gotchas

- Windows/PowerShell environment; bash has fork issues on this machine.
- Do not put secrets or personal details in `.agents/`.
- Do not rely on `.claude/` for cross-harness state.
- `_shell/PROGRESS.md` is outside a Git repo on this machine; it cannot be
  committed unless `_shell` becomes a repo or the file is copied into a repo.
- `sourcerepo` still has uncommitted SHELL scaffold/audit files from the Claude
  SHELL run. They are separate from the MOLT commit.
- Local Git config previously had credential-bearing remote URL entries; they
  were removed, leaving only `remote.origin.url`.

## Files in play

- `AGENTS.md`
- `.gitignore`
- `.github/scripts/sync-selected-paths.sh`
- `.agents/STATE.md`
- `.agents/JOURNAL.md`
- `.agents/handoffs/`
- `.agents/handoffs/2026-08-09-molt-layer0-ready.md`
- `X:\01 REPOSITORIES\theprawnprojects\.agents\STATE.md`
- `X:\01 REPOSITORIES\_shell\PROGRESS.md`

## Open questions for the human

- Which alternate harness should perform the proof: Gemini, Claude, Kiro, or
  another installed CLI?
