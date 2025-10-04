# Caliper bootstrap for PowerShell (Windows)
# - Creates a local venv with all required deps
# - Adds a 'caliper' function to your PowerShell profile so you can run 'caliper wizard' from any terminal

param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

# Resolve repo root (this script lives in repo\scripts)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

$VenvDir = Join-Path $RepoRoot '.venv_heavy'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'

function Get-PythonExe {
    try {
        $py = (Get-Command py -ErrorAction Stop).Source
        return 'py -3'
    } catch {
        try {
            $p = (Get-Command python -ErrorAction Stop).Source
            return 'python'
        } catch {
            throw "Python 3 not found in PATH. Install from python.org and retry."
        }
    }
}

function Ensure-Venv {
    param([string]$VenvDir, [string]$PyLauncher)
    if (Test-Path $VenvPython -PathType Leaf -and -not $Force) { return }
    if (Test-Path $VenvDir -and $Force) { Remove-Item -Recurse -Force $VenvDir }
    Write-Host "[+] Creating virtual environment at $VenvDir" -ForegroundColor Cyan
    & $PyLauncher -m venv $VenvDir
    & $VenvPython -m pip install -U pip setuptools wheel
    Write-Host "[+] Installing dependencies (this may take a few minutes)..." -ForegroundColor Cyan
    & $VenvPython -m pip install `
        typer==0.15.* loguru==0.7.* python-dotenv==1.* pydantic==2.10.* pydantic-settings==2.7.* `
        tiktoken==0.8.* faiss-cpu==1.8.* cohere==5.* pypdf==5.* nest-asyncio==1.6.* `
        "llama-index==0.12.*" `
        "llama-index-llms-openai==0.2.*" "llama-index-llms-anthropic==0.2.*" "llama-index-llms-gemini==0.2.*" "llama-index-llms-vertex==0.2.*" "llama-index-llms-openai-like==0.2.*" `
        anthropic==0.40.* google-cloud-aiplatform==1.38.* google-auth==2.23.* `
        "llama-index-embeddings-openai==0.2.*" "llama-index-embeddings-cohere==0.2.*" "llama-index-embeddings-huggingface==0.2.*" `
        "llama-index-retrievers-bm25==0.2.*" `
        "llama-index-postprocessor-cohere-rerank==0.2.*" `
        "llama-parse==0.5.*"
}

function Ensure-ProfileFunction {
    param([string]$FunctionName, [string]$Body)
    $profilePath = $PROFILE
    $profileDir = Split-Path -Parent $profilePath
    if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir | Out-Null }
    if (-not (Test-Path $profilePath)) { New-Item -ItemType File -Path $profilePath | Out-Null }
    $content = Get-Content -Path $profilePath -Raw
    if ($content -notmatch "function\s+$FunctionName\s*{") {
        Add-Content -Path $profilePath -Value "`n# added by Caliper bootstrap on $(Get-Date -Format o)"
        Add-Content -Path $profilePath -Value $Body
        Write-Host "[+] Added '$FunctionName' to PowerShell profile: $profilePath" -ForegroundColor Green
    } else {
        Write-Host "[=] '$FunctionName' already present in profile" -ForegroundColor Yellow
    }
}

$py = Get-PythonExe
Ensure-Venv -VenvDir $VenvDir -PyLauncher $py

# Build an absolute path version for the profile function
$RepoRootEsc = $RepoRoot -replace "'", "''"
$VenvPythonEsc = $VenvPython -replace "'", "''"
$func = @"
function caliper {
  param([Parameter(ValueFromRemainingArguments=
  $true)][object[]]
  $Args)
  Set-Location '$RepoRootEsc'
  & '$VenvPythonEsc' run_caliper_v2.py @Args
}
"@

Ensure-ProfileFunction -FunctionName 'caliper' -Body $func

Write-Host "`nDone." -ForegroundColor Green
Write-Host "Restart PowerShell (or run: `. $PROFILE`) then use: caliper wizard" -ForegroundColor Cyan
