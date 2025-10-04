@echo off
REM Generate Section - Create report section from context file
REM Usage: scripts\generate_section.bat <context_file> [provider] [model]
REM Example: scripts\generate_section.bat data_v2\context\treatment.json anthropic claude-sonnet-4-5

setlocal

cd /d "%~dp0\.."

if "%~1"=="" (
    echo Usage: generate_section.bat ^<context_file^> [provider] [model]
    echo.
    echo Examples:
    echo   generate_section.bat data_v2\context\treatment.json
    echo   generate_section.bat data_v2\context\treatment.json anthropic claude-sonnet-4-5
    echo   generate_section.bat data_v2\context\treatment.json openai gpt-5
    echo.
    echo Available providers: openai, anthropic, gemini, xai, cohere
    exit /b 1
)

set CONTEXT_FILE=%~1
set PROVIDER=%~2
set MODEL=%~3

if not exist "%CONTEXT_FILE%" (
    echo ERROR: Context file not found: %CONTEXT_FILE%
    echo.
    echo Run retrieval first:
    echo   scripts\quick_retrieve.bat "your question"
    exit /b 1
)

REM Extract filename without path and extension for output naming
for %%F in ("%CONTEXT_FILE%") do set BASENAME=%%~nF

REM Generate output filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set OUTFILE=outputs\%BASENAME%_gen_%TIMESTAMP%.md

echo ============================================
echo Generate Section
echo ============================================
echo Context: %CONTEXT_FILE%
if not "%PROVIDER%"=="" (
    echo Provider: %PROVIDER%
    if not "%MODEL%"=="" echo Model: %MODEL%
)
echo Output: %OUTFILE%
echo.

REM Build command
set CMD=poetry run caliper_v2 generate "%CONTEXT_FILE%" --style strict-citation --out "%OUTFILE%"

if not "%PROVIDER%"=="" (
    set CMD=!CMD! --llm-provider %PROVIDER%
)

if not "%MODEL%"=="" (
    set CMD=!CMD! --llm-model %MODEL%
)

echo Generating...
%CMD%

if errorlevel 1 (
    echo.
    echo ERROR: Generation failed. Check:
    echo   1. Provider API key in .env
    echo   2. Run: scripts\check_system.bat
    exit /b 1
)

echo.
echo ============================================
echo Success!
echo ============================================
echo Section generated: %OUTFILE%
echo.
echo Next steps:
    echo   1. Review: type %OUTFILE%
echo   2. Judge quality: poetry run caliper_v2 judge --context %CONTEXT_FILE% --generation %OUTFILE%
echo.
