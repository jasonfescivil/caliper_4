@echo off
REM Download cost data for wastewater treatment projects
REM Run this in a SEPARATE Command Prompt to avoid interrupting indexing

echo Downloading Cost Data for Wastewater Treatment...

REM Create directory structure
echo Creating directories...
mkdir "knowledge_base\09_cost_data\epa" 2>nul
mkdir "knowledge_base\09_cost_data\washington_state" 2>nul
mkdir "knowledge_base\09_cost_data\design_tools" 2>nul
mkdir "knowledge_base\09_cost_data\reference" 2>nul

REM EPA Documents
echo Downloading EPA cost guides...
curl -L -o "knowledge_base\09_cost_data\epa\2021_EPA_Small_Community_Cost_Guide.pdf" ^
  "https://www.epa.gov/sites/default/files/2021-03/documents/small-community-guidebook-planning-financing-construction.pdf"

curl -L -o "knowledge_base\09_cost_data\epa\2018_EPA_SRF_Eligibility_Handbook.pdf" ^
  "https://www.epa.gov/sites/default/files/2018-10/documents/cwsrf_eligibility_handbook_2018.pdf"

REM Washington State Documents
echo Downloading Washington State SRF data...
curl -L -o "knowledge_base\09_cost_data\washington_state\2024_WA_SRF_Intended_Use_Plan.pdf" ^
  "https://apps.ecology.wa.gov/publications/documents/2401007.pdf"

curl -L -o "knowledge_base\09_cost_data\washington_state\2023_WA_Water_Quality_Funding_Guidelines.pdf" ^
  "https://apps.ecology.wa.gov/publications/documents/2310001.pdf"

REM USDA Rural Development
echo Downloading USDA Rural Development guides...
curl -L -o "knowledge_base\09_cost_data\reference\USDA_RD_Program_Resources.pdf" ^
  "https://www.rd.usda.gov/sites/default/files/RD_FactSheet_RUS_WEPDirect.pdf"

echo.
echo Cost data download complete!
echo Files downloaded to: knowledge_base\09_cost_data\
echo.
echo After current indexing finishes, run:
echo poetry run caliper_v2 ingest knowledge_base\09_cost_data --index cost_data --persist --llama-parse
pause
