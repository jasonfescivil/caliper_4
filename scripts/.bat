@echo off
echo Creating knowledge base folder structure...

REM Create main topic directories
mkdir "knowledge_base\design_criteria" 2>nul
mkdir "knowledge_base\treatment_processes" 2>nul
mkdir "knowledge_base\hydraulics_hydrology" 2>nul
mkdir "knowledge_base\site_evaluation" 2>nul
mkdir "knowledge_base\regulatory_compliance" 2>nul
mkdir "knowledge_base\construction_specs" 2>nul
mkdir "knowledge_base\operations_maintenance" 2>nul
mkdir "knowledge_base\economics_financing" 2>nul

REM Create README files for each directory
echo # Design Criteria > "knowledge_base\design_criteria\README.md"
echo Chapter-specific design standards and criteria >> "knowledge_base\design_criteria\README.md"

echo # Treatment Processes > "knowledge_base\treatment_processes\README.md"
echo Biological, chemical, and physical treatment documents >> "knowledge_base\treatment_processes\README.md"

echo # Hydraulics and Hydrology > "knowledge_base\hydraulics_hydrology\README.md"
echo Flow calculations, pump stations, and hydraulic design >> "knowledge_base\hydraulics_hydrology\README.md"

echo # Site Evaluation > "knowledge_base\site_evaluation\README.md"
echo Geotechnical, environmental site data, and assessment >> "knowledge_base\site_evaluation\README.md"

echo # Regulatory Compliance > "knowledge_base\regulatory_compliance\README.md"
echo Permits, effluent limits, and monitoring requirements >> "knowledge_base\regulatory_compliance\README.md"

echo # Construction Specifications > "knowledge_base\construction_specs\README.md"
echo Materials, construction standards, and specifications >> "knowledge_base\construction_specs\README.md"

echo # Operations and Maintenance > "knowledge_base\operations_maintenance\README.md"
echo O&M manuals, staffing requirements, and procedures >> "knowledge_base\operations_maintenance\README.md"

echo # Economics and Financing > "knowledge_base\economics_financing\README.md"
echo Cost estimation, lifecycle analysis, and financing >> "knowledge_base\economics_financing\README.md"

echo.
echo Folder structure created successfully!
echo.
dir /b knowledge_base
pause
