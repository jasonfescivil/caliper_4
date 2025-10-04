@echo off
setlocal
echo [!] Windows launcher is deprecated. Caliper is WSL-only now.
echo     Run from WSL: /mnt/c/dev/caliper/scripts/caliper_wsl.sh ^<args^>
echo     Example: bash -lc "/mnt/c/dev/caliper/scripts/caliper_wsl.sh wizard"
echo.
echo Press any key to close...
pause >nul
exit /b 1
REM Caliper launcher (Windows) — heavy profile with full LlamaIndex stack via local venv
REM - Creates .venv_heavy if missing and installs all required packages
REM - Runs the CLI with your arguments

pushd %~dp0

set "VENV_DIR=.venv_heavy"

REM Detect Python launcher or fallback to python
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  set "PY_EXE=py -3"
) else (
  set "PY_EXE=python"
)

REM Create venv if missing
if not exist "%VENV_DIR%" (
  echo [+] Creating virtual environment (%VENV_DIR%) and installing dependencies...
  %PY_EXE% -m venv "%VENV_DIR%" || (
    echo [!] Failed to create virtual environment. Ensure Python 3 is installed and on PATH.
    echo.
    echo Press any key to close...
    pause >nul
    popd & exit /b 1
  )
  call "%VENV_DIR%\Scripts\python.exe" -m pip install -U pip setuptools wheel
  call "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.heavy.txt
  if %ERRORLEVEL% NEQ 0 (
    echo [!] Dependency install failed.
    echo.
    echo Press any key to close...
    pause >nul
    popd & exit /b 1
  )
)

REM Default to wizard when no arguments provided (double-click)
set "ARGS=%*"
if "%ARGS%"=="" set "ARGS=wizard"

echo [+] Running Caliper... (args: %ARGS%)
"%VENV_DIR%\Scripts\python.exe" run_caliper_v2.py %ARGS%
set EXITCODE=%ERRORLEVEL%

echo.
echo Exit code: %EXITCODE%. Press any key to close...
pause >nul

popd
exit /b %EXITCODE%
