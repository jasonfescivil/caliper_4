<#
  cleanup_sweeper.ps1

  Organizes stray files at the repo root into consistent locations.
  - Dry-run by default. Use -Execute to actually move files.
  - Writes a plan to logs/cleanup_<timestamp>_(plan|executed).txt

  Examples
    PS> .\scripts\cleanup_sweeper.ps1            # show plan only
    PS> .\scripts\cleanup_sweeper.ps1 -Execute   # perform moves
#>

param(
  [switch] $Execute
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogDir = Join-Path $RepoRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$planSuffix = if ($Execute) { "_executed.txt" } else { "_plan.txt" }
$PlanPath = Join-Path $LogDir ("cleanup_" + $Timestamp + $planSuffix)

# Ensure targets
$Targets = @{
  Metadata = Join-Path $RepoRoot "data_v2\metadata"
  Jobs     = Join-Path $RepoRoot "data_v2\jobs"
  Logs     = Join-Path $RepoRoot "logs"
  NotesLg  = Join-Path $RepoRoot "notes\archive\legacy"
  Tests    = Join-Path $RepoRoot ("archive\" + $Timestamp + "\tests")
  Misc     = Join-Path $RepoRoot ("archive\" + $Timestamp + "\misc")
}
$Targets.GetEnumerator() | ForEach-Object { New-Item -ItemType Directory -Force -Path $_.Value | Out-Null }

# Keep lists
$KeepDirs = @('src','scripts','notes','docs','knowledge_base','data_v2','outputs','archive','logs','.venv','.mypy_cache','.ruff_cache','.pytest_cache','.cursor','.ide','.github','.obsidian','.vscode')
$KeepFiles = @('run_caliper_v2.py','pyproject.toml','poetry.lock','requirements.heavy.txt','.gitattributes','.gitignore','.pre-commit-config.yaml','README.md','README_local_quickstart.md','.env','Dockerfile','docker-compose.yml')

# Helper: plan or move
$Plan = @()
function Plan-Move {
  param([string] $From,[string] $To)
  $Plan += [PSCustomObject]@{ From=$From; To=$To }
  if ($Execute) {
    try {
      $destDir = Split-Path -Parent $To
      if ($destDir -and -not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
      }
      Move-Item -Force -LiteralPath $From -Destination $To
    } catch {
      Write-Warning "Failed to move '$From' -> '$To': $($_.Exception.Message)"
    }
  }
}

# Scan root, non-recursive files
Get-ChildItem -LiteralPath $RepoRoot -Force -File | ForEach-Object {
  $name = $_.Name
  $full = $_.FullName
  $ext = ($_.Extension + "").ToLower()

  if ($KeepFiles -contains $name) { return }
  if ($name -like 'README*.md' -and $name -ne 'README_local_quickstart.md') { return }

  # Rules
  if ($name -like '*.ps1' -or $name -like '*.sh' -or $name -like '*.bat') {
    if ($_.DirectoryName -ne (Join-Path $RepoRoot 'scripts')) {
      Plan-Move -From $full -To (Join-Path (Join-Path $RepoRoot 'scripts') $name)
      return
    }
  }
  if ($name -like '*.log') {
    Plan-Move -From $full -To (Join-Path $Targets.Logs $name)
    return
  }
  if ($name -like 'metadata_*' -or $name -like '*metadata*.csv') {
    Plan-Move -From $full -To (Join-Path $Targets.Metadata $name)
    return
  }
  if ($name -like 'jobs_*.csv' -or $name -eq 'llama-cloud-history.json' -or $name -like 'll_*mapping*.csv') {
    Plan-Move -From $full -To (Join-Path $Targets.Jobs $name)
    return
  }
  if ($name -like 'test_*') {
    Plan-Move -From $full -To (Join-Path $Targets.Tests $name)
    return
  }
  if ($ext -eq '.md' -and $name -notlike 'README*.md') {
    Plan-Move -From $full -To (Join-Path $Targets.NotesLg $name)
    return
  }

  # Default: archive misc (be safe)
  Plan-Move -From $full -To (Join-Path $Targets.Misc $name)
}

# Scan root, non-recursive directories
Get-ChildItem -LiteralPath $RepoRoot -Force -Directory | ForEach-Object {
  $name = $_.Name
  if ($KeepDirs -contains $name) { return }
  switch -Regex ($name) {
    '^logs?$' { return }
    default {
      $to = Join-Path $Targets.Misc $name
      if ($Execute) {
        try { Move-Item -Force -LiteralPath $_.FullName -Destination $to } catch { }
      } else {
        $Plan += [PSCustomObject]@{ From=$_.FullName; To=$to }
      }
    }
  }
}

# Output plan
$out = ($Plan | Sort-Object From | Format-Table -AutoSize | Out-String)
$out | Tee-Object -FilePath $PlanPath | Out-Host
Write-Host ([Environment]::NewLine + "Plan saved to: $PlanPath") -ForegroundColor Cyan
if ($Execute) { Write-Host "EXECUTED: files moved." -ForegroundColor Green } else { Write-Host "DRY-RUN: no changes made." -ForegroundColor Yellow }

