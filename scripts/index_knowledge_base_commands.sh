#!/bin/bash
# Index Knowledge Base Directories One by One
# Run each command individually to monitor progress

echo "📚 Knowledge Base Indexing Commands"
echo "=================================="
echo "Total documents: 37 PDFs across 5 directories"
echo ""
echo "Run these commands one by one:"
echo ""

# 1. Federal Regulations (9 PDFs)
echo "# 1️⃣ Federal Regulations (9 documents)"
echo 'poetry run caliper_v2 ingest knowledge_base/01_federal_regulations --index federal_regs --persist'
echo ""

# 2. State Regulations - Washington (18 PDFs)
echo "# 2️⃣ Washington State Regulations (18 documents)"
echo 'poetry run caliper_v2 ingest knowledge_base/02_state_regulations/washington --index wa_state_regs --persist'
echo ""

# 3. Special Districts (1 PDF)
echo "# 3️⃣ Special Districts (1 document)"
echo 'poetry run caliper_v2 ingest knowledge_base/05_special_districts --index special_districts --persist'
echo ""

# 4. Design Standards (6 PDFs across 3 subdirs)
echo "# 4️⃣ Design Standards - WEF (4 documents)"
echo 'poetry run caliper_v2 ingest knowledge_base/06_design_standards/wef --index design_wef --persist'
echo ""

echo "# 4️⃣ Design Standards - ASCE (1 document)"
echo 'poetry run caliper_v2 ingest knowledge_base/06_design_standards/asce --index design_asce --persist'
echo ""

echo "# 4️⃣ Design Standards - AWWA (1 document)"
echo 'poetry run caliper_v2 ingest knowledge_base/06_design_standards/awwa --index design_awwa --persist'
echo ""

# 5. Technical Reports (3 PDFs)
echo "# 5️⃣ Technical Reports (3 documents)"
echo 'poetry run caliper_v2 ingest knowledge_base/07_technical_reports --index tech_reports --persist'
echo ""

echo "=================================="
echo ""
echo "# 🎯 Or index EVERYTHING at once:"
echo 'poetry run caliper_v2 ingest knowledge_base --index all_regulations --persist'
echo ""

echo "# 📊 After indexing, test with:"
echo 'poetry run caliper_v2 query "What are the biosolids regulations?" --index wa_state_regs --search-mode hybrid'
echo ""

echo "# 🔍 To see available indexes:"
echo 'ls -la data_v2/indexes/'
