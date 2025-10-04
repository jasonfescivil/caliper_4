# Tekoa Files Organization Plan

## Naming Convention
Format: `YEAR_AGENCY_DocumentType_Location_Description.pdf`

## File Organization and Renaming Commands

### 1. Create Tekoa-Specific Subdirectory
```bash
mkdir -p knowledge_base/08_case_studies/tekoa_wastewater
```

### 2. Regulatory/Permits → `08_case_studies/tekoa_wastewater/permits`
```bash
mkdir -p knowledge_base/08_case_studies/tekoa_wastewater/permits

# NPDES Permit Files
mv "knowledge_base/07_technical_reports/WA0023141_Tekoa_Permit_2014-06-01 (1).pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/permits/2014_Ecology_NPDES_Permit_WA0023141_Tekoa.pdf"

mv "knowledge_base/07_technical_reports/WA0023141_Tekoa_Permit_Extension_2020-06-15.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/permits/2020_Ecology_NPDES_Permit_Extension_WA0023141_Tekoa.pdf"

mv "knowledge_base/07_technical_reports/WA0023141_Tekoa_Noncompliance_Notification_2016-03-10.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/permits/2016_Ecology_Noncompliance_Notice_WA0023141_Tekoa.pdf"
```

### 3. Operations & Maintenance → `08_case_studies/tekoa_wastewater/operations`
```bash
mkdir -p knowledge_base/08_case_studies/tekoa_wastewater/operations

# O&M Manuals
mv "knowledge_base/07_technical_reports/Addendum_Tekoa_STP_OM_Manual.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/operations/2023_Tekoa_STP_OM_Manual_Addendum.pdf"

mv "knowledge_base/07_technical_reports/Addendum to Tekoa Sewage Treatment Plant O & M Manual.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/operations/2023_Tekoa_STP_OM_Manual_Addendum_duplicate.pdf"
```

### 4. Engineering Reports → `08_case_studies/tekoa_wastewater/engineering`
```bash
mkdir -p knowledge_base/08_case_studies/tekoa_wastewater/engineering

# I&I and Facility Studies
mv "knowledge_base/07_technical_reports/CityofTekoa_InfluentStation_SurveyReport.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/engineering/2022_Tekoa_Influent_Station_Survey_Report.pdf"

mv "knowledge_base/07_technical_reports/Appendix 2 2017 Tekoa I-I Reduction Cost Estimate.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/engineering/2017_Tekoa_II_Reduction_Cost_Estimate.pdf"

mv "knowledge_base/07_technical_reports/Tekoa Study.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/engineering/2023_Tekoa_Wastewater_Facility_Study.pdf"
```

### 5. Environmental Studies → `08_case_studies/tekoa_wastewater/environmental`
```bash
mkdir -p knowledge_base/08_case_studies/tekoa_wastewater/environmental

# Receiving Water and Environmental Studies
mv "knowledge_base/07_technical_reports/Hangman Creek receiving water study.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/environmental/2022_Hangman_Creek_Receiving_Water_Study.pdf"

mv "knowledge_base/07_technical_reports/Tekoa Shoreline Management Plan.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/environmental/2020_Tekoa_Shoreline_Management_Plan.pdf"

# Handle the directory (if it contains files)
# mv "knowledge_base/07_technical_reports/Hangman Creek Reports" \
#    "knowledge_base/08_case_studies/tekoa_wastewater/environmental/hangman_creek_reports"
```

## Desktop.ini for Windows Explorer Metadata
```bash
# Create desktop.ini for the main Tekoa folder
cat > "knowledge_base/08_case_studies/tekoa_wastewater/desktop.ini" << EOF
[.ShellClassInfo]
InfoTip=Tekoa WWTP Case Study - Population 820, Oxidation Ditch to Hangman Creek
IconResource=%SystemRoot%\system32\SHELL32.dll,4
EOF
```

## Indexing Commands

### 1. Index All Tekoa Documents at Once
```bash
poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater --index tekoa --persist --llama-parse
```

### 2. Or Index by Category
```bash
# Permits and Compliance
poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/permits --index tekoa_permits --persist --llama-parse

# Operations Documents
poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/operations --index tekoa_operations --persist --llama-parse

# Engineering Studies
poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/engineering --index tekoa_engineering --persist --llama-parse

# Environmental Studies
poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/environmental --index tekoa_environmental --persist --llama-parse
```

### 3. Create Combined Case Study Index
```bash
# Index all case studies including Tekoa
poetry run caliper_v2 ingest knowledge_base/08_case_studies --index case_studies --persist --llama-parse
```

## Updated AKART Analysis Command

Now you can include Tekoa-specific data:

```bash
poetry run caliper_v2 agent "Prepare a complete AKART analysis for the Town of Tekoa, WA (2025 population ≈ 820). Use the actual Tekoa NPDES permit limits from WA0023141, the 2016 noncompliance issues, the I&I reduction cost estimates from 2017, and the Hangman Creek receiving water study. [Rest of your original prompt...]" --indexes "federal,state,design_standards,tekoa" --verbose > tekoa_akart_analysis.md
```

## File Review Notes

1. **Duplicate O&M Manual** - You have two files with the same content but different names
2. **Hangman Creek Reports** - This appears to be a directory, check if it contains additional files
3. **Missing Years** - I estimated years for some files based on content, adjust if needed
4. **NPDES Permit** - The "(1)" in filename suggests there might be other versions

## Benefits of This Organization

1. **Case Study Structure** - All Tekoa documents in one place
2. **Categorical Subdivision** - Easy to find permits vs. studies vs. operations
3. **Consistent Naming** - Year_Agency_Type_Location pattern
4. **Searchable** - Both by index name and metadata
5. **Expandable** - Can add more case studies in parallel structure
