@echo off
REM Check System - Validate Caliper environment before starting work
REM Usage: scripts\check_system.bat

echo ============================================
echo Caliper System Check
echo ============================================
echo.

cd /d "%~dp0\.."

echo [1/4] Checking Poetry environment...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Poetry not found. Install with: pipx install poetry
    exit /b 1
)
echo OK: Poetry found

echo.
echo [2/4] Checking Python environment...
poetry run python --version
if errorlevel 1 (
    echo ERROR: Python environment not activated
    exit /b 1
)

echo.
echo [3/4] Running Caliper doctor...
poetry run caliper_v2 doctor
if errorlevel 1 (
    echo WARNING: Doctor found issues. Check API keys in .env
)

echo.
echo [4/4] Checking key directories...
if not exist "data_v2\indexes" (
    echo WARNING: data_v2\indexes not found
) else (
    echo OK: Indexes directory exists
)

if not exist "knowledge_base" (
    echo WARNING: knowledge_base not found
) else (
    echo OK: Knowledge base directory exists
)

echo.
echo ============================================
echo System check complete!
echo ============================================
echo.
echo Ready to use Caliper. Try:
echo   poetry run caliper_v2 retrieve "your question" --cloud
echo.
