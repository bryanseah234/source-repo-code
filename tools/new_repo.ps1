param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^[A-Za-z0-9._-]+$')]
  [string]$Name,

  [string]$Owner = "hongyime",
  [string]$Description = "",
  [string[]]$Topics = @(),
  [switch]$Private
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$repoPath = Join-Path (Get-Location) $Name

if (Test-Path -LiteralPath $repoPath) {
  throw "Path already exists: $repoPath"
}

New-Item -ItemType Directory -Path $repoPath | Out-Null
Copy-Item -LiteralPath (Join-Path $root "LICENSE") -Destination (Join-Path $repoPath "LICENSE")
Copy-Item -LiteralPath (Join-Path $root "NOTICE") -Destination (Join-Path $repoPath "NOTICE")

@"
# $Name

$Description

## Setup

Add setup instructions before publishing.

## Usage

Add usage instructions before publishing.

## License

Apache-2.0. See LICENSE and NOTICE.
"@ | Set-Content -LiteralPath (Join-Path $repoPath "README.md") -Encoding utf8

@"
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
"@ | Set-Content -LiteralPath (Join-Path $repoPath ".gitignore") -Encoding utf8

git -C $repoPath init | Out-Null
git -C $repoPath add README.md LICENSE NOTICE .gitignore
git -C $repoPath commit -m "chore: initialise compliant repository" | Out-Null

$visibility = if ($Private) { "--private" } else { "--public" }
gh repo create "$Owner/$Name" $visibility --source $repoPath --remote origin --push --description $Description

foreach ($topic in $Topics) {
  gh repo edit "$Owner/$Name" --add-topic $topic
}

Write-Host "Created $Owner/$Name at $repoPath"
