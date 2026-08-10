# SHELL — the standard

**Goes to:** `hongyime/sourcerepo/STANDARD.md`
**Applies to:** every repo owned by `hongyime` or `bryanseah234`
**Licence policy:** Apache-2.0, everywhere
**Date:** 2026-08-08 (rev 2 — written after reading `sourcerepo`)

You said you know you want consistency but don't know what the desired state is.
This file is the desired state.

It is deliberately short, and it deliberately **does not restate things
`sourcerepo` already enforces**. A standard that lists solved problems buries the
unsolved ones.

---

## 0. What is already enforced — do not re-implement

`sourcerepo/.github/workflows/sync-repo-settings.yml` runs weekly (Mon 5pm SGT)
and already guarantees, across every non-disabled repo including archived ones:

- Repo settings: issues, wiki, projects, discussions, merge buttons, auto-merge,
  delete-branch-on-merge, forking, downloads
- Synced workflows: `ci`, `codeql`, `scorecard`, `trufflehog`, `semgrep`,
  `bandit`, `heartbeat`, `lfs-guard`, `dependency-review`, `labeler`, `greetings`,
  `summary`, bot auto-merge
- Synced files: `CONTRIBUTING.md`, `SECURITY.md`, `AGENTS.md`, `.gitattributes`,
  `.deepsource.toml`, `.sourcery.yml`, issue/PR templates, dependabot config
- `GH_PAT` propagation
- LFS bloat prevention (two layers)
- Per-repo opt-out via the `keep-lfs` and `no-config-sync` topics

**None of that is in scope for SHELL.** It works. Leave it alone.

---

## 1. Tiers

| Tier | Definition | Detection |
|---|---|---|
| **`external`** | Not your code — clones and forks you keep for reading | `git remote get-url origin` is not under `hongyime/` or `bryanseah234/` |
| **`archived`** | Archived on GitHub | API `archived: true` |
| **`standard`** | Yours, no live deployment | default |
| **`showcase`** | Yours, has a live deployment | listed on theprawnprojects, or `homepage` is a real project URL |

**`external` repos are never touched.** Your local folder holds
`Awesome-React`, `javascript-mastery`, `github-cheat-sheet`, `zaileys`,
`chat-adapter-zaileys`, `pancakeswap-prediction-bot` and others that are not
yours. The remote-URL check is the guard, it runs first, and it has no exceptions.

Tier assignment lives in `sourcerepo/tiers.yml`, generated once then
hand-corrected, and committed so it's reviewable.

---

## 2. Requirements

### R1 — Licence: Apache-2.0 everywhere

- `LICENSE` contains the **full Apache-2.0 text** (~200 lines). Not a stub.
- `NOTICE` contains the copyright line, and it names **the organisation, not
  your legal name**:

  ```
  Copyright 2026 The Prawn Organisation
  ```

  Apache-2.0 convention puts the copyright in `NOTICE` rather than in the body of
  `LICENSE`. That works in your favour: one file to get right, instead of an
  editable line buried in 69 licence bodies. `Copyright (c) 2026 <your legal
  name>` repeated across every repo is the most boring and most consistent
  identity leak you have.

- Add `LICENSE` and `NOTICE` to the sync path list so this self-maintains.
- **Fix `sourcerepo`'s own README**, which currently says "License: MIT" while its
  `LICENSE` file is Apache-2.0.

Six repos have no licence at all: `sgSHIOK2026`, `smucourses`, `smuseats`,
`sgCampusCore2026`, `sgPayNowQR65`, `ticketremaster-f`. No licence means all
rights reserved — the opposite of what a public portfolio repo should say.

### R2 — Description: real, per-repo, ≤ 120 chars

Every repo currently reads *"Give me 1 ⭐ if it's cool."*

**This is not 69 lazy descriptions. It is one hardcoded line overwriting all 69
every Monday.** See §4. Fix the sync first or this requirement is unenforceable.

### R3 — Topics: ≥ 3, from a controlled vocabulary

Committed to `sourcerepo/topics.yml`. Reserve `keep-lfs` and `no-config-sync`,
which are already load-bearing for the sync.

### R4 — README: ≥ 400 bytes, with title, description, and setup

Fix broken links while you're there. `theprawnprojects`'s clone URL points at
`hongyime/prawnprojects.git`, missing the `the`.

### R5 — No personal identifiers

Zero hits from `tools/scan_identity.py` in the working tree.

This is the one requirement nothing currently covers. TruffleHog (already synced
everywhere) finds **secrets** — API keys, tokens. It does not find your name,
phone number, or home address. That gap is the actual reason SHELL exists.

### R6 — `showcase` repos only

- `homepage` = the live URL, not `www.hong-yi.me` (see §4)
- README links the demo in the first 30 lines
- A screenshot or GIF
- Deployment returns 200 (watched by theprawnstatus)

### Not required, on purpose

`CHANGELOG.md` (you don't cut releases), coverage thresholds (most of these are
static sites), and per-repo `CONTRIBUTING`/`SECURITY` (already synced — don't
duplicate).

---

## 3. Where your identity data lives — never in a file

`scan_identity.py` reads `$SHELL_IDENTITY`, a semicolon-separated string:

```
phones=+6591234567;emails=you@gmail.com;names=Your Legal Name;handles=bryanseah234
```

| Context | Source |
|---|---|
| Your three machines | `$env:SHELL_IDENTITY` in your PowerShell profile |
| CI | GitHub Actions secret `SHELL_IDENTITY`, on **`sourcerepo` only** |

**No file containing your personal details exists anywhere**, so there is nothing
to accidentally `git add`. The scanner refuses to run (exit 2) rather than
reporting a false clean when unconfigured, and reports unknown category names so a
typo like `phone=` can't silently disable it.

It matches your **specific values**, not value shapes — normalised so
`+65 9123 4567`, `9123-4567`, and `91234567` are one needle, and
`you+github@gmail.com` matches `you@gmail.com`. A generated `+65` corpus does not
fire. A `<input type="tel">` does not fire. Your number in a comment does.

**Presence is not linkage.** Your own number inside an exhaustive generated range
isn't a leak — it's one row of a computed space, not a fact about you. A
`.shellignore` at the repo root declares generated corpora. Same principle as the
NRIC datasets in SPAWN.

### Where the scan runs

**Centrally, in `sourcerepo` only** — a weekly job that clones every repo and
scans it. Not synced into 69 repos, because that would mean putting the identity
secret in 69 places. One secret, one repo.

Plus a local pre-commit hook, installed once per machine:

```powershell
git config --global core.hooksPath "$env:USERPROFILE\.githooks"
```

The hook is what actually protects you: a leak caught in CI is already in your
history. A leak caught pre-commit never happened.

---

## 4. The two hardcoded values that must change

In `sync-repo-settings.yml`, around line 113:

```js
description: "Give me 1 ⭐ if it's cool.",
homepage: "https://www.hong-yi.me",
```

These are applied to **every repo, every week**. Consequences:

- R2 is impossible. Write 69 good descriptions today, lose all of them Monday.
- R6 is impossible. No showcase repo can point at its own deployment.

**Fix:** move both to a per-repo map committed in `sourcerepo`, and have the sync
look up each repo, falling back to leaving the existing value **untouched** rather
than overwriting with a default.

You have already fixed this exact class of bug once. The `private: !isTheprawn`
line was reverting manual visibility changes every Monday, and the 2026-08-04
comment records removing it for precisely that reason. `description` and
`homepage` are the same bug, still live.

---

## 5. Maintenance

| Layer | When | LLM? | Catches |
|---|---|---|---|
| Content pass | Once, now | Yes | READMEs, descriptions, topics |
| Pre-commit hook | Every local commit | No | Identity leaks, before they exist |
| Existing sync | Weekly | No | Settings and config drift *(already working)* |
| Compliance report | Weekly | No | Bad READMEs, missing licence, missing topics |

The last one is the other real gap: the sync **pushes** config but never
**reports** what's non-compliant. Push without report means you never find out
what's broken. `check_repo.py` plus a written report to
`sourcerepo/COMPLIANCE.md` closes it.

---

## 6. New repos

`sourcerepo` is **not** a template repo and should not become one — its `skills/`
tree is the point, and you don't want 178 skills copied into every new project.

Instead: a `shell new <name>` script in `sourcerepo/tools/` that creates the repo,
writes `LICENSE` + `NOTICE` + README skeleton + `.gitignore`, sets description and
topics, and registers it in `tiers.yml`. Making the compliant path the *fastest*
path is the only thing that reliably works at 2am.

The weekly compliance report is the backstop: any repo in the org missing from
`tiers.yml` gets flagged as un-onboarded.

---

## 7. Definition of done

- [ ] `description` and `homepage` no longer hardcoded in the sync (§4)
- [ ] `STANDARD.md`, `tiers.yml`, `topics.yml`, `tools/` committed to `sourcerepo`
- [ ] `SHELL_IDENTITY` secret set on `sourcerepo`; env var set on all 3 machines
- [ ] Pre-commit hook installed on all 3 machines
- [ ] Every repo tiered; `external` excluded
- [ ] Zero identity hits across non-`external` repos (working tree)
- [ ] History identity hits **triaged and decided per repo** — not auto-fixed
- [ ] All non-archived repos on Apache-2.0 with `NOTICE` naming the org
- [ ] `LICENSE` + `NOTICE` added to the sync path list
- [ ] 69 real descriptions; ≥3 topics each
- [ ] `sourcerepo` README licence line corrected to Apache-2.0
- [ ] Visibility policy reconciled — README claims private-except-`theprawn`, but
      enforcement was removed 2026-08-04 and many `sg*` repos are public today.
      Decide which is true; it determines what is actually exposed.
- [ ] Weekly compliance report green

**On git history:** rewriting it breaks every clone and fork and invalidates every
commit SHA. The scanner reports history hits because you need to know; it never
fixes them. For 2020 coursework the honest options are accept, privatise, or
delete the repo. Those are decisions, not tasks.
