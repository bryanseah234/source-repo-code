param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^[A-Za-z0-9._-]+$')]
  [string]$Name,

  [ValidateSet("hongyime", "bryanseah234")]
  [string]$Owner = "hongyime",

  [Parameter(Mandatory = $true)]
  [ValidateLength(1, 120)]
  [string]$Description,

  [ValidateSet("standard", "showcase")]
  [string]$Tier = "standard",

  [string]$Homepage = "",

  [Parameter(Mandatory = $true)]
  [ValidateCount(3, 6)]
  [string[]]$Topics,

  [switch]$Private,

  [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$shellRoot = Split-Path -Parent $PSScriptRoot
$repoPath = Join-Path $RepoRoot $Name
$fullName = "$Owner/$Name"

function Read-TopicList {
  param([string]$Path)

  $topics = New-Object System.Collections.Generic.HashSet[string]
  $inTopics = $false
  foreach ($line in Get-Content -LiteralPath $Path) {
    if ($line -match '^topics:\s*$') {
      $inTopics = $true
      continue
    }
    if ($line -match '^[A-Za-z_-]+:\s*$') {
      $inTopics = $false
    }
    if ($inTopics -and $line -match '^\s*-\s+(.+?)\s*$') {
      [void]$topics.Add($Matches[1])
    }
  }
  return $topics
}

function Add-YamlListItem {
  param(
    [string]$Path,
    [string]$Section,
    [string]$Value
  )

  $lines = [System.Collections.Generic.List[string]]::new()
  $lines.AddRange([string[]](Get-Content -LiteralPath $Path))
  if ($lines -contains "  - $Value") {
    return
  }

  $insertAt = $lines.Count
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -eq "${Section}:") {
      $insertAt = $i + 1
      while ($insertAt -lt $lines.Count -and $lines[$insertAt] -match '^\s+-\s+') {
        $insertAt++
      }
      break
    }
  }
  $lines.Insert($insertAt, "  - $Value")
  Set-Content -LiteralPath $Path -Value $lines -Encoding UTF8
}

function Add-ReposEntry {
  param(
    [string]$Path,
    [string]$FullName,
    [string]$Description,
    [string]$Homepage,
    [string[]]$Topics
  )

  $content = Get-Content -LiteralPath $Path -Raw
  if ($content -match "(?m)^$([regex]::Escape($FullName)):\s*$") {
    throw "$FullName already exists in repos.yml"
  }

  $entry = New-Object System.Collections.Generic.List[string]
  $entry.Add($FullName + ":")
  $entry.Add("  description: `"$Description`"")
  $entry.Add("  homepage: `"$Homepage`"")
  $entry.Add("  topics:")
  foreach ($topic in $Topics) {
    $entry.Add("    - $topic")
  }
  Add-Content -LiteralPath $Path -Value ($entry -join [Environment]::NewLine) -Encoding UTF8
}

if (Test-Path -LiteralPath $repoPath) {
  throw "Path already exists: $repoPath"
}

$allowedTopics = Read-TopicList -Path (Join-Path $shellRoot "topics.yml")
foreach ($topic in $Topics) {
  if (-not $allowedTopics.Contains($topic)) {
    throw "Topic '$topic' is not in topics.yml"
  }
}

if ($Tier -eq "showcase" -and [string]::IsNullOrWhiteSpace($Homepage)) {
  throw "Showcase repos need a real homepage URL"
}

New-Item -ItemType Directory -Path $repoPath | Out-Null
Copy-Item -LiteralPath (Join-Path $shellRoot "LICENSE") -Destination (Join-Path $repoPath "LICENSE")
Copy-Item -LiteralPath (Join-Path $shellRoot "NOTICE") -Destination (Join-Path $repoPath "NOTICE")

$readme = @"
# $Name

$Description

## What It Does

Describe the concrete workflow before publishing.

## Stack

Document the runtime, framework, and important services.

## Setup

Add setup instructions before publishing.

## Deploy

Add deployment instructions or state that this repo is not deployed.

## License

Apache-2.0. See LICENSE and NOTICE.
"@
Set-Content -LiteralPath (Join-Path $repoPath "README.md") -Value $readme -Encoding UTF8

$gitignore = @"
.env
.env.*
!.env.example
node_modules/
.venv/
venv/
dist/
build/
.next/
coverage/
__pycache__/
.pytest_cache/
"@
Set-Content -LiteralPath (Join-Path $repoPath ".gitignore") -Value $gitignore -Encoding UTF8

git -C $repoPath init -b main | Out-Null
git -C $repoPath add README.md LICENSE NOTICE .gitignore
git -C $repoPath commit -m "chore: initialise compliant repository" | Out-Null

$visibility = if ($Private) { "--private" } else { "--public" }
gh repo create $fullName $visibility --source $repoPath --remote origin --push --description $Description

$topicArgs = @()
foreach ($topic in $Topics) {
  $topicArgs += "--add-topic"
  $topicArgs += $topic
}
if ($topicArgs.Count -gt 0) {
  gh repo edit $fullName @topicArgs
}
if (-not [string]::IsNullOrWhiteSpace($Homepage)) {
  gh api -X PATCH "repos/$fullName" -f "homepage=$Homepage" | Out-Null
}

Add-YamlListItem -Path (Join-Path $shellRoot "tiers.yml") -Section $Tier -Value $fullName
Add-ReposEntry -Path (Join-Path $shellRoot "repos.yml") -FullName $fullName -Description $Description -Homepage $Homepage -Topics $Topics

Write-Host "Created $fullName at $repoPath"
Write-Host "Review and commit the tiers.yml/repos.yml changes in sourcerepo."
