@echo off
REM Launch Dash UI - Start the Caliper Dash web interface
REM Usage: scripts\launch_dash.bat [port]
REM Example: scripts\launch_dash.bat 8050

setlocal

cd /d "%~dp0\.."

set PORT=%~1
if "%PORT%"=="" set PORT=8050

echo ============================================
echo Launching Caliper Dash UI
echo ============================================
echo.
echo Port: %PORT%
echo URL: http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

REM Set the port via environment variable
set DASH_PORT=%PORT%

REM Launch the Dash app
poetry run python -m src.caliper_v2.ui_dash.app

echo.
echo Dash UI stopped.
