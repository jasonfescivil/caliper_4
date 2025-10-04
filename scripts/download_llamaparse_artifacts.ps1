param(
  [Parameter(Mandatory=$true)][string]$JobId,
  [string]$OutDir = ".",
  [string]$FileName = ""
)

# Load .env
$envPath = Join-Path $PSScriptRoot ".env"
if (Test-Path $envPath) {
  Write-Host "Loading .env file..."
  Get-Content $envPath | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
    $name, $val = $_ -split '=', 2
    $trimmedVal = $val.Trim().Trim('"').Trim("'")
    if (-not (Test-Path "env:$name")) {
      Set-Item -Path "env:$name" -Value $trimmedVal
    }
  }
}

if (-not $env:LLAMA_CLOUD_API_KEY) {
  throw "LLAMA_CLOUD_API_KEY not found"
}

$headers = @{ Authorization = "Bearer $env:LLAMA_CLOUD_API_KEY" }
$baseUrl = "https://api.cloud.llamaindex.ai/api/v1"

# Create output directory
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "Downloading artifacts for job: $JobId"

# If no filename provided, try to get it from job details
if (-not $FileName) {
  try {
    Write-Host "Fetching job details..."
    $jobInfo = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/parsing/job/$JobId/details"
    if ($jobInfo.file_name) {
      $FileName = $jobInfo.file_name
      Write-Host "Found filename: $FileName"
    } else {
      # Try alternative endpoint
      $jobInfo2 = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/parsing/job/$JobId"
      if ($jobInfo2.file_name) {
        $FileName = $jobInfo2.file_name
        Write-Host "Found filename: $FileName"
      }
    }
  } catch {
    Write-Host "Could not get filename from job details"
  }
  
  # If still no filename, use job ID
  if (-not $FileName) {
    Write-Host "Using job ID as filename base"
    $FileName = "job_$JobId"
  }
}

# Clean filename for filesystem
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
$baseName = $baseName -replace '[<>:"/\\|?*]', '_'

# Ensure we have a valid basename
if (-not $baseName -or $baseName -eq "") {
  $baseName = "job_$JobId"
}

# Create subdirectory for this document
$docDir = Join-Path $OutDir $baseName
New-Item -ItemType Directory -Force -Path $docDir | Out-Null

# Download all available artifacts
$artifacts = @{
  "markdown" = ".md"
  "text" = ".txt"
  "json" = ".json"
  "images" = "_images.zip"
  "layout" = "_layout.json"
  "xlsx" = ".xlsx"
  "pdf" = "_parsed.pdf"
}

foreach ($type in $artifacts.Keys) {
  $outFile = Join-Path $docDir "$baseName$($artifacts[$type])"
  
  Write-Host "Downloading $type..."
  try {
    $uri = "$baseUrl/parsing/job/$JobId/result/$type"
    Invoke-WebRequest -Headers $headers -Uri $uri -OutFile $outFile -UseBasicParsing
    Write-Host "  ✓ Downloaded $type"
  } catch {
    Write-Host "  ✗ Failed to download $type"
    if (Test-Path $outFile) { Remove-Item $outFile }
  }
}

Write-Host "`nDone! Files saved to: $docDir"
