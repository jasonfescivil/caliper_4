param(
  [Parameter(Mandatory=$true)][string]$PipelineId
)

# Load .env
$envPath = Join-Path $PSScriptRoot ".env"
if (Test-Path $envPath) {
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

# Get pipeline info
Write-Host "=== PIPELINE INFO ==="
$pipelineUri = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId"
try {
  $pipeline = Invoke-RestMethod -Method GET -Headers $headers -Uri $pipelineUri
  $pipeline | ConvertTo-Json -Depth 10
} catch {
  Write-Host "Pipeline info failed: $_"
}

# Get documents raw
Write-Host "`n=== DOCUMENTS RAW JSON ==="
$docsUri = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId/documents?limit=2"
try {
  $docs = Invoke-RestMethod -Method GET -Headers $headers -Uri $docsUri
  $docs | ConvertTo-Json -Depth 10
} catch {
  Write-Host "Documents failed: $_"
}

# Get jobs raw
Write-Host "`n=== JOBS RAW JSON ==="
$jobsUri = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId/jobs?limit=2"
try {
  $jobs = Invoke-RestMethod -Method GET -Headers $headers -Uri $jobsUri
  $jobs | ConvertTo-Json -Depth 10
} catch {
  Write-Host "Jobs failed: $_"
}

# Try files endpoint
Write-Host "`n=== FILES ENDPOINT ==="
$filesUri = "https://api.cloud.llamaindex.ai/api/v1/files?pipeline_id=$PipelineId&limit=2"
try {
  $files = Invoke-RestMethod -Method GET -Headers $headers -Uri $filesUri
  $files | ConvertTo-Json -Depth 10
} catch {
  Write-Host "Files endpoint failed: $_"
}
