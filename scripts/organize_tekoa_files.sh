#!/bin/bash
# Script to organize Tekoa files into proper knowledge base structure

echo "🗂️ Organizing Tekoa Case Study Files..."

# Create directory structure
echo "Creating directories..."
mkdir -p knowledge_base/08_case_studies/tekoa_wastewater/{permits,operations,engineering,environmental}

# Move and rename permit files
echo "📋 Moving permit files..."
mv "knowledge_base/07_technical_reports/WA0023141_Tekoa_Permit_2014-06-01 (1).pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/permits/2014_Ecology_NPDES_Permit_WA0023141_Tekoa.pdf" 2>/dev/null

mv "knowledge_base/07_technical_reports/WA0023141_Tekoa_Permit_Extension_2020-06-15.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/permits/2020_Ecology_NPDES_Permit_Extension_WA0023141_Tekoa.pdf" 2>/dev/null

mv "knowledge_base/07_technical_reports/WA0023141_Tekoa_Noncompliance_Notification_2016-03-10.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/permits/2016_Ecology_Noncompliance_Notice_WA0023141_Tekoa.pdf" 2>/dev/null

# Move and rename O&M files
echo "🔧 Moving operations files..."
mv "knowledge_base/07_technical_reports/Addendum_Tekoa_STP_OM_Manual.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/operations/2023_Tekoa_STP_OM_Manual_Addendum.pdf" 2>/dev/null

# Remove duplicate if exists
if [ -f "knowledge_base/07_technical_reports/Addendum to Tekoa Sewage Treatment Plant O & M Manual.pdf" ]; then
    echo "Removing duplicate O&M manual..."
    rm "knowledge_base/07_technical_reports/Addendum to Tekoa Sewage Treatment Plant O & M Manual.pdf"
fi

# Move and rename engineering studies
echo "⚙️ Moving engineering files..."
mv "knowledge_base/07_technical_reports/CityofTekoa_InfluentStation_SurveyReport.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/engineering/2022_Tekoa_Influent_Station_Survey_Report.pdf" 2>/dev/null

mv "knowledge_base/07_technical_reports/Appendix 2 2017 Tekoa I-I Reduction Cost Estimate.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/engineering/2017_Tekoa_II_Reduction_Cost_Estimate.pdf" 2>/dev/null

mv "knowledge_base/07_technical_reports/Tekoa Study.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/engineering/2023_Tekoa_Wastewater_Facility_Study.pdf" 2>/dev/null

# Move and rename environmental studies
echo "🌊 Moving environmental files..."
mv "knowledge_base/07_technical_reports/Hangman Creek receiving water study.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/environmental/2022_Hangman_Creek_Receiving_Water_Study.pdf" 2>/dev/null

mv "knowledge_base/07_technical_reports/Tekoa Shoreline Management Plan.pdf" \
   "knowledge_base/08_case_studies/tekoa_wastewater/environmental/2020_Tekoa_Shoreline_Management_Plan.pdf" 2>/dev/null

# Handle Hangman Creek Reports directory if it exists
if [ -d "knowledge_base/07_technical_reports/Hangman Creek Reports" ]; then
    echo "Moving Hangman Creek Reports directory..."
    mv "knowledge_base/07_technical_reports/Hangman Creek Reports" \
       "knowledge_base/08_case_studies/tekoa_wastewater/environmental/hangman_creek_reports" 2>/dev/null
fi

# Create desktop.ini for Windows metadata
echo "💾 Creating metadata..."
cat > "knowledge_base/08_case_studies/tekoa_wastewater/desktop.ini" << EOF
[.ShellClassInfo]
InfoTip=Tekoa WWTP Case Study - Population 820, Oxidation Ditch to Hangman Creek
IconResource=%SystemRoot%\system32\SHELL32.dll,4
EOF

# Set desktop.ini as hidden/system file on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    attrib +h +s "knowledge_base/08_case_studies/tekoa_wastewater/desktop.ini" 2>/dev/null
fi

echo "✅ File organization complete!"
echo ""
echo "📚 Next steps:"
echo "1. Review the organized files in: knowledge_base/08_case_studies/tekoa_wastewater/"
echo "2. Index the Tekoa documents:"
echo "   poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater --index tekoa --persist --llama-parse"
echo ""
echo "3. Or index by category:"
echo "   poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/permits --index tekoa_permits --persist --llama-parse"
echo "   poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/operations --index tekoa_operations --persist --llama-parse"
echo "   poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/engineering --index tekoa_engineering --persist --llama-parse"
echo "   poetry run caliper_v2 ingest knowledge_base/08_case_studies/tekoa_wastewater/environmental --index tekoa_environmental --persist --llama-parse"
