# Load the JSON file
$jsonPath = "G:\My Drive\caliper\llama-cloud-history.json"
$data = Get-Content $jsonPath -Raw | ConvertFrom-Json

# Extract unique jobs with their details
$uniqueJobs = @{}

foreach ($job in $data.jobs) {
    $jobId = $job.job_record.id
    $fileName = $job.job_record.parameters.original_file_name
    $status = $job.job_record.status
    $createdAt = $job.job_record.created_at
    
    # Only track successful jobs
    if ($status -eq "SUCCESS" -and $fileName) {
        # Use the most recent job for each file
        if (-not $uniqueJobs.ContainsKey($fileName) -or $uniqueJobs[$fileName].created_at -lt $createdAt) {
            $uniqueJobs[$fileName] = @{
                id = $jobId
                created_at = $createdAt
                file_name = $fileName
            }
        }
    }
}

# Group by file type/category
$categories = @{
    "WAC" = @()
    "RCW" = @()
    "CFR" = @()
    "EPA" = @()
    "DOE" = @()
    "WEF" = @()
    "ASCE" = @()
    "AWWA" = @()
    "MOP" = @()
    "Other" = @()
}

foreach ($file in $uniqueJobs.Keys) {
    $job = $uniqueJobs[$file]
    $found = $false
    
    foreach ($category in $categories.Keys) {
        if ($file -match "^$category") {
            $categories[$category] += $job
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        $categories["Other"] += $job
    }
}

# Output results
Write-Host "=== UNIQUE LLAMAPARSE JOBS BY CATEGORY ===" -ForegroundColor Cyan
Write-Host "Total unique files: $($uniqueJobs.Count)" -ForegroundColor Yellow
Write-Host ""

foreach ($category in $categories.Keys | Sort-Object) {
    $jobs = $categories[$category]
    if ($jobs.Count -gt 0) {
        Write-Host "$category ($($jobs.Count) files):" -ForegroundColor Green
        foreach ($job in $jobs | Sort-Object -Property file_name) {
            Write-Host "  $($job.file_name)"
            Write-Host "    Job ID: $($job.id)" -ForegroundColor Gray
        }
        Write-Host ""
    }
}

# Export to CSV for easy use
$exportData = @()
foreach ($file in $uniqueJobs.Keys | Sort-Object) {
    $job = $uniqueJobs[$file]
    $exportData += [PSCustomObject]@{
        FileName = $job.file_name
        JobId = $job.id
        CreatedAt = $job.created_at
    }
}

$csvPath = "G:\My Drive\caliper\llamaparse_jobs.csv"
$exportData | Export-Csv -Path $csvPath -NoTypeInformation
Write-Host "Exported job list to: $csvPath" -ForegroundColor Cyan

# Generate download commands
$scriptPath = "G:\My Drive\caliper\download_all_jobs.ps1"
$commands = @()
$commands += "# Auto-generated script to download all LlamaParse artifacts"
$commands += ""

foreach ($category in $categories.Keys | Sort-Object) {
    $jobs = $categories[$category]
    if ($jobs.Count -gt 0) {
        $commands += "# $category files"
        foreach ($job in $jobs | Sort-Object -Property file_name) {
            $commands += "Write-Host 'Downloading: $($job.file_name)' -ForegroundColor Yellow"
            $commands += ".\download_llamaparse_artifacts.ps1 -JobId '$($job.id)' -FileName '$($job.file_name)' -OutDir 'G:\My Drive\caliper\knowledge_base\downloads'"
            $commands += ""
        }
    }
}

$commands | Out-File -FilePath $scriptPath -Encoding UTF8
Write-Host "Generated download script: $scriptPath" -ForegroundColor Cyan
