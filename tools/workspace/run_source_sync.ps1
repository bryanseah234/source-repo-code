param(
  [switch]$NoArchived,
  [switch]$Watch
)

$ErrorActionPreference = "Stop"

$repo = "hongyime/sourcerepo"
$workflow = "sync-repo-settings.yml"
$includeArchived = if ($NoArchived) { "false" } else { "true" }

Write-Host "Triggering source sync workflow..."
Write-Host "Repo: $repo"
Write-Host "Workflow: $workflow"
Write-Host "Include archived: $includeArchived"

gh workflow run $workflow --repo $repo -f include_archived=$includeArchived

Start-Sleep -Seconds 5
$run = gh run list --repo $repo --workflow $workflow --limit 1 --json databaseId,status,conclusion,createdAt,url |
  ConvertFrom-Json |
  Select-Object -First 1

if (-not $run) {
  Write-Host "Workflow was triggered, but no run was returned yet. Check GitHub Actions."
  exit 0
}

Write-Host ""
Write-Host "Run: $($run.databaseId)"
Write-Host "Status: $($run.status)"
Write-Host "URL: $($run.url)"

if ($Watch) {
  gh run watch $run.databaseId --repo $repo --exit-status
}
