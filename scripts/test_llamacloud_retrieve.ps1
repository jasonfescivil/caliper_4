param(
  [string]$Query = "WAC 173-219",
  [string]$PipelineId = "03f712a9-68d1-42ba-9dcf-499ae5ec24aa"
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

$headers = @{ 
  Authorization = "Bearer $env:LLAMA_CLOUD_API_KEY"
  "Content-Type" = "application/json"
}

# Test retrieve endpoint
$uri = "https://api.cloud.llamaindex.ai/api/v1/pipelines/$PipelineId/retrieve"

$body = @{
  query = $Query
  similarity_top_k = 3
  dense_similarity_top_k = 3
  sparse_similarity_top_k = 3
  alpha = 0.5
  enable_reranking = $true
  rerank_top_n = 8
} | ConvertTo-Json

Write-Host "Testing retrieve endpoint for pipeline: $PipelineId" -ForegroundColor Cyan
Write-Host "Query: $Query" -ForegroundColor Yellow
Write-Host ""

try {
  $response = Invoke-RestMethod -Method POST -Headers $headers -Uri $uri -Body $body
  
  Write-Host "=== RESPONSE STRUCTURE ===" -ForegroundColor Green
  $response | ConvertTo-Json -Depth 10 | Out-String | Write-Host
  
  # Extract and show metadata fields
  if ($response.nodes) {
    Write-Host "`n=== METADATA FIELDS IN NODES ===" -ForegroundColor Green
    $metadataFields = @{}
    
    foreach ($node in $response.nodes) {
      if ($node.metadata) {
        foreach ($prop in $node.metadata.PSObject.Properties) {
          $metadataFields[$prop.Name] = $true
        }
      }
    }
    
    Write-Host "Available metadata fields:" -ForegroundColor Cyan
    $metadataFields.Keys | Sort-Object | ForEach-Object {
      Write-Host "  - $_"
    }
    
    # Show sample node metadata
    if ($response.nodes.Count -gt 0) {
      Write-Host "`n=== SAMPLE NODE METADATA ===" -ForegroundColor Green
      $response.nodes[0].metadata | ConvertTo-Json -Depth 5 | Out-String | Write-Host
    }
  }
  
} catch {
  Write-Host "Error: $_" -ForegroundColor Red
  if ($_.Exception.Response) {
    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "Response: $responseBody" -ForegroundColor Red
  }
}

# Also test what filters might be available
Write-Host "`n=== TESTING WITH METADATA FILTER ===" -ForegroundColor Green
$bodyWithFilter = @{
  query = $Query
  similarity_top_k = 3
  filters = @{
    doc_type = "regulation"
  }
} | ConvertTo-Json -Depth 5

try {
  $response2 = Invoke-RestMethod -Method POST -Headers $headers -Uri $uri -Body $bodyWithFilter
  Write-Host "Filter test successful! Filter on 'doc_type' works." -ForegroundColor Green
} catch {
  Write-Host "Filter test failed. Metadata filtering might not be configured." -ForegroundColor Yellow
}
