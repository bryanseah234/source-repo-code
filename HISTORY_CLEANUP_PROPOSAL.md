# History Cleanup Proposal

## Scope

Source: `COMPLIANCE.md`, section `History Hits - Requires Owner Decision`.

- Affected repo: `hongyime/sourcerepo`
- Affected commit marker: `history@63007a14a`
- Category: `handles`

This proposal is intentionally non-destructive. It does not include matched values and does not authorize history rewrite or force push.

## Safe Options

1. Leave history unchanged and document owner acceptance.
   - Best when the value is low-risk, already public, or not actually sensitive after owner review.
   - Keep `COMPLIANCE.md` as the tracking source until the owner records an explicit decision.

2. Remove only current-tree exposure if present.
   - Run the existing current-tree scan first, without printing matched values.
   - If the hit is only historical, no current-tree edit is needed.

3. Prepare a targeted history rewrite in a temporary mirror clone.
   - Use a local, untracked replacement file stored outside commits.
   - Run dry-run first in the temporary mirror only.
   - Proceed to an actual rewrite only after owner approval and downstream coordination.

4. Archive or replace the repo.
   - Lower operational risk than rewriting shared history, but links, stars, forks, releases, and automation may need migration.

## Risks

- Rewriting history changes commit hashes and can break open PRs, forks, tags, release references, deploy pins, and local clones.
- A forced update can overwrite collaborator work if coordination is incomplete.
- Cleanup may not remove copies in forks, caches, package registries, CI logs, local clones, or third-party mirrors.
- Dry-run logs and generated reports must be treated as sensitive if they include raw matched lines; only redacted summaries should be shared.

## Approval Gates

No destructive action should happen until all gates are explicitly approved by the repo owner.

1. Owner confirms the `handles` history hit should be removed rather than accepted.
2. Owner provides or approves the exact replacement/redaction rule through a private channel; do not commit it.
3. Maintainer confirms no protected branches, releases, tags, open PRs, deploy pins, or collaborators will be disrupted without notice.
4. Dry-run output is reviewed using redacted summaries only.
5. Owner explicitly approves the final rewrite and any `--force-with-lease` push.
6. After push, owner approves follow-up notices to collaborators to reclone or reset local copies.

## Dry-Run-First Command Outline

Run from a scratch directory. Do not run these from other repos, and do not print matched values.

```powershell
$work = Join-Path $env:TEMP "sourcerepo-history-cleanup"
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $work | Out-Null

$mirror = Join-Path $work "sourcerepo.git"
git clone --mirror https://github.com/hongyime/sourcerepo.git $mirror
Set-Location $mirror

# Private, untracked file. Populate from owner-approved values without echoing them.
$rules = Join-Path (Get-Location) "history-redactions.txt"
New-Item -ItemType File -Path $rules -Force | Out-Null

# Dry-run only. Review generated metadata for commit counts and changed refs, not raw matched content.
git filter-repo --replace-text $rules --dry-run --force

# Redacted validation summary: path marker and category only.
$scanner = "X:\01 REPOSITORIES\sourcerepo\tools\scan_identity.py"
python $scanner . --json --history |
  python -c "import json,sys; d=json.load(sys.stdin); [print('{} [{}]'.format(h.get('path'), h.get('category'))) for h in d.get('hits', []) if str(h.get('path','')).startswith('history@')]"
```

Only after all approval gates are complete should the same replacement rules be used for a real rewrite in the temporary mirror, followed by a separately approved `git push --force-with-lease --mirror`.
