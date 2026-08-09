# MOLT Layer 0 Ready

Created: 2026-08-09 SGT
Project: sourcerepo
Branch: `molt/state-continuity`
Status: ready for cross-harness proof

## Current State Summary

MOLT Layer 0 is implemented in the source-of-truth repository. The central sync
now preserves the committed `.agents` state surface, `AGENTS.md` tells agents to
read `.agents/STATE.md` first, and thin harness pointers exist for Claude,
Gemini, and Kiro. The next required action is a cold resume proof from another
CLI.

## Important Context

This branch deliberately tracks only durable state files: `.agents/STATE.md`,
`.agents/JOURNAL.md`, and `.agents/handoffs/**`. The generated skills mirror
under `.agents/skills/` remains ignored. `.claude/` also remains local-only
because it can contain private session stores and runtime files.

## Immediate Next Steps

Open a different installed CLI cold and send only this prompt:

```text
resume from X:\01 REPOSITORIES\_shell\PROGRESS.md
```

If that CLI identifies the current MOLT branch, the committed state files, and
the remaining review/push work, Phase 3 proof passes. Do not let the alternate
CLI start SHELL remediation until the central MOLT changes are reviewed.

## Architecture Overview

MOLT Layer 0 uses committed plain-text state for cross-harness continuity. The
source-of-truth repo carries global instructions and state conventions, while
active downstream repos can seed `.agents/STATE.md` only when useful. Handoffs
live in `.agents/handoffs/` and must pass validation before they are committed.

## Critical Files

- `AGENTS.md`
- `.gitignore`
- `.github/scripts/sync-selected-paths.sh`
- `.agents/STATE.md`
- `.agents/JOURNAL.md`
- `.agents/handoffs/2026-08-09-molt-layer0-ready.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.kiro/steering/molt.md`

## Files Modified

The MOLT branch already has commits for the main state layer and proof prompt.
The current remaining MOLT edit is this handoff document plus the state/journal
entries that mention it. The worktree also contains unrelated SHELL scaffold and
audit files; do not mix them into a MOLT commit.

## Decisions Made

`.agents` is the cross-harness state location. Only state, journal, and handoff
files are tracked. The session-handoff local skill was repointed from the
private harness directory to `.agents/handoffs/`, and its validator was made
blocking for secrets and configured identity hits.

## Assumptions Made

The alternate CLI proof is user-driven to avoid spending quota from this
session. The proof only needs to demonstrate that another harness can load the
same state and understand the next safe action.

## Potential Gotchas

Do not commit private harness directories or generated skill mirrors. Do not
print environment secrets. Do not push or open PRs until the user confirms the
cross-harness proof. Keep the SHELL scaffold/audit files separate from MOLT
commits unless the user explicitly asks to combine them.
