param(
  [Parameter(Mandatory=)][string],
  [string],
  [int] = 100
)

# Resolve repo root and load env
 = 
if (-not ) {  = Join-Path  "data_v2\cloud_downloads" }
. "\scripts\env.ps1"

if (-not :LLAMA_CLOUD_API_KEY) { throw "LLAMA_CLOUD_API_KEY not found" }
 = @{ Authorization = "Bearer :LLAMA_CLOUD_API_KEY" }
New-Item -ItemType Directory -Force -Path  | Out-Null

Write-Host "Fetching files for pipeline: "

# Get all files for this pipeline
 = 
 = @()

do {
   = "https://api.cloud.llamaindex.ai/api/v1/files?pipeline_id=&limit="
  if () {  += "&cursor=" }
  
  Write-Host "Fetching batch..."
   = Invoke-RestMethod -Method GET -Headers  -Uri 
  
  if ( -is [array]) {
     += 
     = 
  } else {
     += .data
     = .next_cursor
  }
} while ()

Write-Host "Found  files to process"

foreach ( in ) {
   = .id
   = .name
  if (-not ) {  = ".pdf" }
   =  -replace '[<>:"/\|?*]', '_'

   = 
  if ( -match '^(WAC|RCW|CFR)') {  = Join-Path  "regulations" }
  elseif ( -match '^(EPA|DOE)') {  = Join-Path  "guidance" }
  elseif ( -match '^(WEF|ASCE|AWWA|MOP)') {  = Join-Path  "standards" }

  New-Item -ItemType Directory -Force -Path  | Out-Null
   = [System.IO.Path]::GetFileNameWithoutExtension()
   = Join-Path  
  New-Item -ItemType Directory -Force -Path  | Out-Null

  Write-Host "nDone! Files saved to: "
