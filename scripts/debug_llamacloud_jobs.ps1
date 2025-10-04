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
$uri = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId/jobs?limit=10"

Write-Host "Fetching jobs for pipeline: $PipelineId"
$resp = Invoke-RestMethod -Method GET -Headers $headers -Uri $uri

Write-Host "`nFound $($resp.data.Count) jobs:"
foreach ($job in $resp.data) {
  Write-Host "`nJob ID: $($job.id)"
  Write-Host "  Status: $($job.status)"
  Write-Host "  Type: $($job.type)"
  Write-Host "  Job Name: $($job.job_name)"
  Write-Host "  Created: $($job.created_at)"
  
  # Show all properties to see what's available
  Write-Host "  All properties:"
  $job.PSObject.Properties | ForEach-Object {
    Write-Host "    $($_.Name): $($_.Value)"
  }
}

# Also check documents
Write-Host "`n`nChecking pipeline documents..."
$uri2 = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId/documents?limit=5"
$resp2 = Invoke-RestMethod -Method GET -Headers $headers -Uri $uri2
Write-Host "Found $($resp2.data.Count) documents"

foreach ($doc in $resp2.data) {
  Write-Host "`nDocument:"
  Write-Host "  ID: $($doc.id)"
  Write-Host "  File Name: $($doc.file_name)"
  Write-Host "  Status: $($doc.status)"
  Write-Host "  All properties:"
  $doc.PSObject.Properties | ForEach-Object {
    Write-Host "    $($_.Name): $($_.Value)"
  }
}

# Try alternative parsing endpoints
Write-Host "`n`nTrying parsing/jobs endpoint..."
try {
  $uri3 = "https://api.cloud.llamaindex.ai/api/v1/parsing/jobs?pipeline_id=$PipelineId&limit=5"
  $resp3 = Invoke-RestMethod -Method GET -Headers $headers -Uri $uri3
  Write-Host "Found $($resp3.data.Count) parsing jobs via /parsing/jobs"
  
  foreach ($job in $resp3.data) {
    Write-Host "`nParsing Job:"
    Write-Host "  ID: $($job.id)"
    Write-Host "  File Name: $($job.file_name)"
    Write-Host "  Status: $($job.status)"
  }
} catch {
  Write-Host "  /parsing/jobs endpoint failed: $_"
}

# Check if documents have parsing results directly
Write-Host "`n`nChecking if documents have direct download links..."
foreach ($doc in $resp2.data | Select-Object -First 1) {
  try {
    # Try markdown download
    $mdUri = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId/documents/$($doc.id)/result/markdown"
    Write-Host "  Trying: $mdUri"
    $testMd = Invoke-WebRequest -Headers $headers -Uri $mdUri -Method HEAD
    Write-Host "  Markdown available! Status: $($testMd.StatusCode)"
  } catch {
    Write-Host "  Markdown not available via document endpoint"
  }
}
