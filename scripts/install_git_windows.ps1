Param(
    [switch]$CheckOnly,
    [switch]$Install
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

function Test-GitInstalled {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) { return $true }
    # Common install path
    if (Test-Path "C:\Program Files\Git\bin\git.exe") { return $true }
    if (Test-Path "C:\Program Files (x86)\Git\bin\git.exe") { return $true }
    return $false
}

if ($CheckOnly) {
    if (Test-GitInstalled) {
        Write-Info "Git is installed and available."
        exit 0
    } else {
        Write-Warn "Git is NOT installed or not on PATH."
        exit 1
    }
}

if ($Install) {
    if (Test-GitInstalled) {
        Write-Info "Git already installed. Nothing to do."
        exit 0
    }

    try {
        # Ensure TLS 1.2 for GitHub downloads
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    } catch {}

    $url = "https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe"
    $out = Join-Path $env:TEMP "Git-64-bit.exe"
    Write-Info "Downloading Git for Windows from: $url"
    try {
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Warn "Invoke-WebRequest failed: $($_.Exception.Message)"
        if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
            Write-Info "Falling back to BITS transfer..."
            Start-BitsTransfer -Source $url -Destination $out
        } else {
            Write-Err "Could not download Git installer. Please download manually from https://git-scm.com/download/win"
            exit 1
        }
    }

    if (-not (Test-Path $out)) {
        Write-Err "Download failed. No installer found at $out"
        exit 1
    }

    Write-Info "Starting Git installer (you may see a UAC prompt)..."
    $args = @(
        "/VERYSILENT",
        "/NORESTART",
        "/SP-",
        "/CLOSEAPPLICATIONS",
        "/RESTARTAPPLICATIONS"
    )
    try {
        $p = Start-Process -FilePath $out -ArgumentList $args -Wait -PassThru
        Write-Info "Installer exited with code $($p.ExitCode)"
    } catch {
        Write-Err "Failed to start installer: $($_.Exception.Message)"
        exit 1
    }

    # Refresh PATH in current session if needed
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    if (Test-GitInstalled) {
        Write-Host "`nGit installation appears successful." -ForegroundColor Green
        git --version
        Write-Info "If 'git' is not recognized in this terminal, close and reopen the terminal."
        exit 0
    } else {
        Write-Err "Git still not detected after installation. Try restarting your machine, or install manually from https://git-scm.com/download/win"
        exit 1
    }
}

Write-Host "Usage:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\install_git_windows.ps1 -CheckOnly"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\install_git_windows.ps1 -Install"
