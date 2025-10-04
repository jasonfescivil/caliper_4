# Map index IDs to their names/categories
$indexMap = @{
    "03f712a9-68d1-42ba-9dcf-499ae5ec24aa" = @{
        name = "wa-2025-08-16-managed"
        patterns = @("WAC", "RCW", "Washington", "WA_", "DOE_", "Ecology")
        outDir = "G:\My Drive\caliper\knowledge_base\02_state_regulations"
    }
    "344b98a7-f9ff-4e8e-83c7-128f6ecdd5a4" = @{
        name = "federal-2025-08-16-managed"  
        patterns = @("CFR", "EPA_", "Federal")
        outDir = "G:\My Drive\caliper\knowledge_base\01_federal_regulations"
    }
    "b45e47a4-c2ae-4812-b8ab-e01f3c946855" = @{
        name = "design-guidance-2025-08-16-managed"
        patterns = @("WEF", "ASCE", "AWWA", "MOP", "Design", "Manual")
        outDir = "G:\My Drive\caliper\knowledge_base\06_design_standards"
    }
    "747cbce6-035d-461a-8b95-df6dafadcfc2" = @{
        name = "wa-2025-08-16-managed_summary"
        patterns = @()  # Likely summary index
        outDir = "G:\My Drive\caliper\knowledge_base\02_state_regulations"
    }
    "742e122c-3551-4187-9a9e-0ead017c019f" = @{
        name = "federal-2025-08-16-managed_summary"
        patterns = @()  # Likely summary index
        outDir = "G:\My Drive\caliper\knowledge_base\01_federal_regulations"
    }
    "40769edc-dd33-4ec8-b148-e631865e163e" = @{
        name = "design-guidance-2025-08-16-managed_summary"
        patterns = @()  # Likely summary index
        outDir = "G:\My Drive\caliper\knowledge_base\06_design_standards"
    }
}

# Load the JSON file
$jsonPath = "G:\My Drive\caliper\llama-cloud-history.json"
$data = Get-Content $jsonPath -Raw | ConvertFrom-Json

# Extract unique successful jobs
$uniqueJobs = @{}

foreach ($job in $data.jobs) {
    $jobId = $job.job_record.id
    $fileName = $job.job_record.parameters.original_file_name
    $status = $job.job_record.status
    $createdAt = $job.job_record.created_at
    
    if ($status -eq "SUCCESS" -and $fileName) {
        if (-not $uniqueJobs.ContainsKey($fileName) -or $uniqueJobs[$fileName].created_at -lt $createdAt) {
            $uniqueJobs[$fileName] = @{
                id = $jobId
                created_at = $createdAt
                file_name = $fileName
            }
        }
    }
}

# Categorize files by index based on patterns
$jobsByIndex = @{}
foreach ($indexId in $indexMap.Keys) {
    $jobsByIndex[$indexId] = @()
}

foreach ($file in $uniqueJobs.Keys) {
    $job = $uniqueJobs[$file]
    $assigned = $false
    
    # Try to match file to an index based on patterns
    foreach ($indexId in $indexMap.Keys) {
        if ($indexMap[$indexId].patterns.Count -eq 0) { continue }
        
        foreach ($pattern in $indexMap[$indexId].patterns) {
            if ($file -match $pattern) {
                $jobsByIndex[$indexId] += $job
                $assigned = $true
                break
            }
        }
        if ($assigned) { break }
    }
}

# Output results
Write-Host "=== LLAMAPARSE JOBS BY INDEX ===" -ForegroundColor Cyan
Write-Host ""

foreach ($indexId in $indexMap.Keys) {
    $index = $indexMap[$indexId]
    $jobs = $jobsByIndex[$indexId]
    
    if ($index.patterns.Count -gt 0) {  # Skip summary indexes
        Write-Host "$($index.name) (Index: $indexId)" -ForegroundColor Green
        Write-Host "  Files: $($jobs.Count)"
        Write-Host "  Output Dir: $($index.outDir)"
        Write-Host ""
        
        # Generate download script for this index
        if ($jobs.Count -gt 0) {
            $scriptPath = "G:\My Drive\caliper\download_$($index.name)_jobs.ps1"
            $commands = @()
            $commands += "# Download script for $($index.name)"
            $commands += "# Index ID: $indexId"
            $commands += ""
            
            foreach ($job in $jobs | Sort-Object -Property file_name) {
                $commands += "Write-Host 'Downloading: $($job.file_name)' -ForegroundColor Yellow"
                $commands += ".\download_llamaparse_artifacts.ps1 -JobId '$($job.id)' -FileName '$($job.file_name)' -OutDir '$($index.outDir)\downloads'"
                $commands += ""
            }
            
            $commands | Out-File -FilePath $scriptPath -Encoding UTF8
            Write-Host "  Generated download script: $scriptPath" -ForegroundColor Cyan
            
            # Export job list for this index
            $csvPath = "G:\My Drive\caliper\jobs_$($index.name).csv"
            $jobs | ForEach-Object {
                [PSCustomObject]@{
                    FileName = $_.file_name
                    JobId = $_.id
                    CreatedAt = $_.created_at
                }
            } | Export-Csv -Path $csvPath -NoTypeInformation
            Write-Host "  Exported job list: $csvPath" -ForegroundColor Cyan
        }
        Write-Host ""
    }
}

# Create a master script that runs metadata generation for each index
$masterScript = @"
# Master script to generate metadata for all indexes

Write-Host 'Generating metadata for State Regulations...' -ForegroundColor Green
python scripts/build_llamacloud_metadata.py ``
  --root "G:\My Drive\caliper\knowledge_base\02_state_regulations" ``
  --out "G:\My Drive\caliper\metadata_wa_index.csv" ``
  --include-json-only ``
  --file-path-mode basename

Write-Host 'Generating metadata for Federal Regulations...' -ForegroundColor Green  
python scripts/build_llamacloud_metadata.py ``
  --root "G:\My Drive\caliper\knowledge_base\01_federal_regulations" ``
  --out "G:\My Drive\caliper\metadata_federal_index.csv" ``
  --include-json-only ``
  --file-path-mode basename

Write-Host 'Generating metadata for Design Standards...' -ForegroundColor Green
python scripts/build_llamacloud_metadata.py ``
  --root "G:\My Drive\caliper\knowledge_base\06_design_standards" ``
  --out "G:\My Drive\caliper\metadata_design_index.csv" ``
  --include-json-only ``
  --file-path-mode basename

Write-Host 'Done! Upload these CSVs to their respective indexes in LlamaCloud:' -ForegroundColor Cyan
Write-Host '  - metadata_wa_index.csv -> wa-2025-08-16-managed (03f712a9-68d1-42ba-9dcf-499ae5ec24aa)'
Write-Host '  - metadata_federal_index.csv -> federal-2025-08-16-managed (344b98a7-f9ff-4e8e-83c7-128f6ecdd5a4)'
Write-Host '  - metadata_design_index.csv -> design-guidance-2025-08-16-managed (b45e47a4-c2ae-4812-b8ab-e01f3c946855)'
"@

$masterScript | Out-File -FilePath "G:\My Drive\caliper\generate_all_metadata.ps1" -Encoding UTF8
Write-Host "Created master metadata generation script: generate_all_metadata.ps1" -ForegroundColor Magenta
