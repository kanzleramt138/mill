param(
  [Parameter(Position=0, Mandatory=$true)]
  [ValidateSet('start','end','latest')]
  [string]$Command,

  # start
  [Parameter(Mandatory=$false)]
  [string]$Title = "",

  [Parameter(Mandatory=$false)]
  [string]$Slug = "",

  # end
  [Parameter(Mandatory=$false)]
  [string]$Note = "",

  # optional UX
  [Parameter(Mandatory=$false)]
  [switch]$Open
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$docsDir = Join-Path $repoRoot 'docs'
$templatePath = Join-Path $docsDir 'SESSION_TEMPLATE.md'
$sessionsDir = Join-Path $docsDir 'sessions'
$latestPath = Join-Path $docsDir 'SESSION_LATEST.md'

function Ensure-Dirs {
  if (-not (Test-Path $docsDir)) { throw "docs/ directory not found: $docsDir" }
  if (-not (Test-Path $sessionsDir)) {
    New-Item -ItemType Directory -Path $sessionsDir | Out-Null
  }
}

function New-Slug([string]$s) {
  if ([string]::IsNullOrWhiteSpace($s)) { return "" }
  $s = $s.Trim().ToLowerInvariant()
  $s = $s -replace '[^a-z0-9]+' , '-'
  $s = $s -replace '-{2,}', '-'
  $s = $s.Trim('-')
  return $s
}

function Resolve-LatestNotePath {
  # 1) Try parse link target from SESSION_LATEST.md
  if (Test-Path $latestPath) {
    $md = Get-Content -Raw -Path $latestPath
    $m = [regex]::Match($md, '\((docs/sessions/[^)]+\.md)\)')
    if ($m.Success) {
      $rel = $m.Groups[1].Value
      $abs = Join-Path $repoRoot ($rel -replace '/', '\\')
      if (Test-Path $abs) { return $abs }
    }
  }

  # 2) Fallback: newest markdown in docs/sessions
  if (Test-Path $sessionsDir) {
    $files = Get-ChildItem -Path $sessionsDir -Filter '*.md' | Sort-Object LastWriteTime -Descending
    if ($files.Count -gt 0) { return $files[0].FullName }
  }

  return ""
}

function Write-LatestPointer([string]$absNotePath) {
  if ([string]::IsNullOrWhiteSpace($absNotePath)) { throw "No note path provided" }
  if (-not (Test-Path $absNotePath)) { throw "Note not found: $absNotePath" }

  $fileName = Split-Path -Leaf $absNotePath
  $rel = "docs/sessions/$fileName"
  $date = Get-Date -Format 'yyyy-MM-dd'

  $latest = @(
    "# Latest Session Note",
    "",
    "- $date: [$rel]($rel)",
    "",
    "Workflow: [docs/WORKFLOW.md](WORKFLOW.md)",
    "Script: `./scripts/session.ps1 start -Title \"…\"`"
  ) -join "`n"

  Set-Content -Path $latestPath -Value $latest -Encoding UTF8
}

Ensure-Dirs

switch ($Command) {
  'start' {
    if (-not (Test-Path $templatePath)) {
      throw "Template not found: $templatePath"
    }

    $date = Get-Date -Format 'yyyy-MM-dd'
    if ([string]::IsNullOrWhiteSpace($Slug)) {
      $Slug = New-Slug $Title
    }

    $baseName = if ([string]::IsNullOrWhiteSpace($Slug)) { "SESSION_NOTE_$date" } else { "SESSION_NOTE_${date}_$Slug" }
    $fileName = "$baseName.md"
    $notePath = Join-Path $sessionsDir $fileName

    if (Test-Path $notePath) {
      throw "Session note already exists: $notePath"
    }

    $content = Get-Content -Raw -Path $templatePath
    $content = $content -replace '\{\{DATE\}\}', $date
    $content = $content -replace '\{\{TITLE\}\}', ($Title -replace '\$', '$$')

    Set-Content -Path $notePath -Value $content -Encoding UTF8
    Write-LatestPointer -absNotePath $notePath

    Write-Host "Created: $notePath"
    Write-Host "Updated: $latestPath"

    if ($Open) {
      Start-Process $notePath | Out-Null
    }
  }

  'end' {
    $abs = ""
    if (-not [string]::IsNullOrWhiteSpace($Note)) {
      $abs = Join-Path $repoRoot ($Note -replace '/', '\\')
    } else {
      $abs = Resolve-LatestNotePath
    }

    if ([string]::IsNullOrWhiteSpace($abs)) {
      throw "Could not resolve a session note. Pass -Note docs/sessions/<file>.md or run 'start' first."
    }

    Write-LatestPointer -absNotePath $abs
    Write-Host "SESSION_LATEST now points to: $abs"
  }

  'latest' {
    $abs = Resolve-LatestNotePath
    if ([string]::IsNullOrWhiteSpace($abs)) {
      Write-Host "No session note found."
      exit 0
    }
    Write-Host $abs
  }
}
