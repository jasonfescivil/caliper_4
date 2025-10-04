param(
  [Parameter(Mandatory=$true)][string]$PipelineId,     # e.g. 03f7...24aa
  [Parameter(Mandatory=$true)][string]$OutDir,         # e.g. G:\llama_downloads
  [switch]$Artifacts,                                   # download MD/JSON/XLSX from parse jobs
  [switch]$Originals,                                   # download original uploaded files
  [string]$BaseUrl = "https://api.cloud.llamaindex.ai/api/v1",
  [int]$Limit = 100
)

function Load-DotEnv {
  $envPath = Join-Path $PSScriptRoot ".env"
  if (-not (Test-Path $envPath)) {
    $envPath = Join-Path $PSScriptRoot "..\.env"
  }

  if (Test-Path $envPath) {
    Write-Host "Loading .env file from $envPath"
    Get-Content $envPath | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' -and -not $_.StartsWith('#') } | ForEach-Object {
      $name, $val = $_ -split '=', 2
      $trimmedVal = $val.Trim()
      if ($trimmedVal.StartsWith('"') -and $trimmedVal.EndsWith('"')) {
        $trimmedVal = $trimmedVal.Substring(1, $trimmedVal.Length - 2)
      } elseif ($trimmedVal.StartsWith("'") -and $trimmedVal.EndsWith("'")) {
        $trimmedVal = $trimmedVal.Substring(1, $trimmedVal.Length - 2)
      }
      if (-not (Test-Path "env:$name")) {
        Set-Item -Path "env:$name" -Value $trimmedVal
        Write-Host ("    Loaded: " + $name)
      }
    }
  } else {
    Write-Warning ".env file not found."
  }
}

# Load .env first
Load-DotEnv

if (-not $env:LLAMA_CLOUD_API_KEY) {
  throw "Set `$env:LLAMA_CLOUD_API_KEY first (or ensure it is in .env)."
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Invoke-LI {
  param([string]$Path, [string]$Method="GET", [hashtable]$Body=$null)
  $headers = @{ Authorization = "Bearer $env:LLAMA_CLOUD_API_KEY" }
  $uri = "$BaseUrl$Path"
  Write-Host "API Call: $Method $uri"
  if ($Method -eq "GET") {
    return Invoke-RestMethod -Method GET -Headers $headers -Uri $uri -ErrorAction Stop
  } else {
    return Invoke-RestMethod -Method $Method -Headers $headers -Uri $uri -Body ($Body|ConvertTo-Json -Depth 8) -ContentType "application/json"
  }
}

function Sanitize([string]$name) {
  $bad = [IO.Path]::GetInvalidFileNameChars() -join ''
  return ($name -replace "[$bad]", "_")
}

# ---------- ORIGINAL FILES ----------
function Download-Originals {
  Write-Host "Listing pipeline documents..."
  $cursor = $null
  $docs = @()

  do {
    $path = "/pipelines/$PipelineId/documents?limit=$Limit"
    if ($cursor) { $path += "&cursor=$cursor" }
    $resp = Invoke-LI -Path $path
    $docs += $resp.data
    $cursor = $resp.next_cursor
  } while ($cursor)
  Write-Host "Found $($docs.Count) documents to check for originals."

  foreach ($d in $docs) {
    # Expect either file_id or original filename somewhere in the doc
    $fileId = $d.file_id
    $name   = $d.source_file_name
    if (-not $fileId) { continue }

    try {
      # Many APIs return a presigned URL or a small JSON with it; try the common patterns:
      $presigned = Invoke-LI -Path "/files/$fileId/content"
      $url = if ($presigned.url) { $presigned.url } else { $presigned }  # handle raw string or object
      $fname = Sanitize($name ? $name : "$($d.document_id).bin")
      $out = Join-Path $OutDir $fname
      Write-Host "Downloading original: $fname"
      Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing | Out-Null
    } catch {
      Write-Warning "Failed original for doc_id=$($d.document_id): $($_.Exception.Message)"
    }
  }
}

# ---------- PARSE ARTIFACTS ----------
function Download-Artifacts {
  Write-Host "Listing parse jobs for pipeline..."
  $cursor = $null
  $jobs = @()

  do {
    $path = "/pipelines/$PipelineId/jobs?limit=$Limit"
    if ($cursor) { $path += "&cursor=$cursor" }
    $resp = Invoke-LI -Path $path
    # keep only parsing jobs if job.type/name is present
    foreach ($j in $resp.data) {
      if ($j.job_name -and $j.job_name -eq "parsing") { $jobs += $j }
      elseif ($j.type -and $j.type -match "parsing") { $jobs += $j }
    }
    $cursor = $resp.next_cursor
  } while ($cursor)
  Write-Host "Found $($jobs.Count) parsing jobs to download artifacts from."

  foreach ($j in $jobs) {
    $jobId = $j.id
    # best-effort: fetch details to get original filename
    $name = $null
    try {
      $det = Invoke-LI -Path "/parsing/job/$jobId/details"
      $name = $det.file_name
    } catch {}

    if (-not $name) { $name = "job_$jobId" }
    $stem = Sanitize([IO.Path]::GetFileNameWithoutExtension($name))
    $dir  = Join-Path $OutDir $stem
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    $artifacts = @("markdown","json","xlsx")
    foreach ($kind in $artifacts) {
      $out = Join-Path $dir "$stem.$kind"
      try {
        Write-Host "Downloading $kind -> $out"
        $headers = @{ Authorization = "Bearer $env:LLAMA_CLOUD_API_KEY" }
        $uri = "$BaseUrl/parsing/job/$jobId/result/$kind"
        Invoke-WebRequest -Headers $headers -Uri $uri -OutFile $out -UseBasicParsing | Out-Null
      } catch {
        Write-Warning "No $kind for $stem ($jobId): $($_.Exception.Message)"
      }
    }
  }
}

if (-not $Artifacts -and -not $Originals) {
  Write-Host "Nothing to do. Use -Artifacts and/or -Originals."
  exit 1
}

if ($Originals) { Download-Originals }
if ($Artifacts) { Download-Artifacts }

Write-Host "Done. Files in $OutDir"
