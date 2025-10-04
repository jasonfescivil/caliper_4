@echo off
REM Quick Retrieve - Fast retrieval with Cohere + cloud defaults
REM Usage: scripts\quick_retrieve.bat "your question here"
REM Example: scripts\quick_retrieve.bat "What are NPDES permit requirements?"

setlocal enabledelayedexpansion

cd /d "%~dp0\.."

if "%~1"=="" (
    echo Usage: quick_retrieve.bat "your question"
    echo Example: quick_retrieve.bat "Design flow calculations for WWTPs"
    exit /b 1
)

set QUESTION=%~1

echo ============================================
echo Quick Retrieval with Cohere
echo ============================================
echo Question: %QUESTION%
echo.

REM Generate output filename from timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=!datetime:~0,8!_!datetime:~8,6!
set OUTFILE=data_v2\context\quick_!TIMESTAMP!.json

echo Retrieving...
poetry run caliper_v2 retrieve "%QUESTION%" ^
  --cloud ^
  --indexes federal,state,design_standards ^
  --top-k 16 ^
  --reranker cohere ^
  --reranker-top-n 16 ^
  --out "%OUTFILE%"

if errorlevel 1 (
    echo.
    echo ERROR: Retrieval failed. Check:
    echo   1. Run: scripts\check_system.bat
    echo   2. Verify .env has COHERE_API_KEY and LLAMA_CLOUD_API_KEY
    exit /b 1
)

echo.
echo ============================================
echo Success!
echo ============================================
echo Context saved to: %OUTFILE%
echo.
echo Next steps:
echo   1. Generate: poetry run caliper_v2 generate %OUTFILE%
echo   2. Or review context first: type %OUTFILE%
echo.
