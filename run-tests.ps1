# Caliper v2 E2E Test Runner Script
# Usage: .\run-tests.ps1 [suite] [options]

param(
    [string]$Suite = "all",
    [switch]$Headed = $false,
    [switch]$Debug = $false,
    [string]$Browser = "chromium",
    [int]$Workers = 1
)

Write-Host "Caliper v2 E2E Test Runner" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Ensure we're in the right directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

# Ensure output directory exists
if (!(Test-Path "outputs")) {
    New-Item -ItemType Directory -Path "outputs" -Force
    Write-Host "Created outputs directory" -ForegroundColor Green
}

# Build the Playwright command
$playwrightCmd = "npx playwright test"

# Add browser selection
$playwrightCmd += " --project=$Browser"

# Add worker configuration
$playwrightCmd += " --workers=$Workers"

# Add headed mode if requested
if ($Headed) {
    $playwrightCmd += " --headed"
}

# Add debug mode if requested
if ($Debug) {
    $playwrightCmd += " --debug"
}

# Add reporter configuration
$playwrightCmd += " --reporter=line"

# Select test suite
switch ($Suite.ToLower()) {
    "basic" {
        $playwrightCmd += " tests/e2e/multi-provider-retrieve-generate.spec.ts"
        Write-Host "Running basic retrieve & generate tests..." -ForegroundColor Yellow
    }
    "advanced" {
        $playwrightCmd += " tests/e2e/advanced-functions.spec.ts"
        Write-Host "Running advanced functions tests..." -ForegroundColor Yellow
    }
    "performance" {
        $playwrightCmd += " tests/e2e/performance-reliability.spec.ts"
        Write-Host "Running performance & reliability tests..." -ForegroundColor Yellow
    }
    "all" {
        $playwrightCmd += " tests/e2e/"
        Write-Host "Running all E2E tests..." -ForegroundColor Yellow
    }
    default {
        $playwrightCmd += " tests/e2e/$Suite"
        Write-Host "Running custom test suite: $Suite" -ForegroundColor Yellow
    }
}

Write-Host "Command: $playwrightCmd" -ForegroundColor Gray
Write-Host ""

# Start the Dash UI in background if not already running
Write-Host "Checking if Dash UI is running..." -ForegroundColor Blue
$dashProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*ui_dash*" }

if (-not $dashProcess) {
    Write-Host "Starting Dash UI server..." -ForegroundColor Blue
    $dashJob = Start-Job -ScriptBlock {
        Set-Location $using:projectRoot
        poetry run python -m caliper_v2.ui_dash.app
    }
    
    # Wait for server to start
    Write-Host "Waiting for Dash UI to start..." -ForegroundColor Blue
    Start-Sleep -Seconds 10
    
    # Test if server is responding
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8050" -TimeoutSec 10 -ErrorAction Stop
        Write-Host "Dash UI is running (HTTP $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Warning "Could not verify Dash UI is running. Tests may fail."
    }
} else {
    Write-Host "Dash UI already running" -ForegroundColor Green
}

# Run the tests
Write-Host ""
Write-Host "Executing tests..." -ForegroundColor Blue
Write-Host "==================" -ForegroundColor Blue

try {
    # Execute the Playwright command
    $result = Invoke-Expression $playwrightCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ All tests passed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Some tests failed (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error running tests: $($_.Exception.Message)" -ForegroundColor Red
}

# Clean up background job if we started it
if ($dashJob) {
    Write-Host ""
    Write-Host "Cleaning up Dash UI process..." -ForegroundColor Blue
    Stop-Job $dashJob -ErrorAction SilentlyContinue
    Remove-Job $dashJob -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Test execution completed." -ForegroundColor Cyan

# Show test results location
if (Test-Path "playwright-report") {
    Write-Host "📊 HTML report available at: .\playwright-report\index.html" -ForegroundColor Cyan
}

if (Test-Path "test-results") {
    Write-Host "📁 Test artifacts available in: .\test-results\" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1                    # Run all tests" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1 basic              # Run basic tests only" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1 -Headed            # Run with browser visible" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1 performance -Browser firefox  # Run perf tests in Firefox" -ForegroundColor Gray