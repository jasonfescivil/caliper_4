# 📚 Remaining Indexing Commands

## ✅ Completed
- ✓ Federal Regulations (9 PDFs, 595 nodes)

## 🔄 Remaining Commands

### First, load the API key (if starting a new shell):
```bash
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d'=' -f2)
```

### 2️⃣ Washington State Regulations (18 PDFs)
```bash
poetry run caliper_v2 ingest knowledge_base/02_state_regulations/washington --index wa_state_regs --persist
```

### 3️⃣ Special Districts (1 PDF)
```bash
poetry run caliper_v2 ingest knowledge_base/05_special_districts --index special_districts --persist
```

### 4️⃣ Design Standards - WEF (4 PDFs)
```bash
poetry run caliper_v2 ingest knowledge_base/06_design_standards/wef --index design_wef --persist
```

### 4️⃣ Design Standards - ASCE (1 PDF)
```bash
poetry run caliper_v2 ingest knowledge_base/06_design_standards/asce --index design_asce --persist
```

### 4️⃣ Design Standards - AWWA (1 PDF)
```bash
poetry run caliper_v2 ingest knowledge_base/06_design_standards/awwa --index design_awwa --persist
```

### 5️⃣ Technical Reports (3 PDFs)
```bash
poetry run caliper_v2 ingest knowledge_base/07_technical_reports --index tech_reports --persist
```

## 🔍 Test Your New Federal Index!

```bash
# Test with hybrid search
poetry run caliper_v2 query "What are the EPA biosolids requirements?" --index federal_regs --search-mode hybrid

# Test keyword search
poetry run caliper_v2 query "40 CFR 503" --index federal_regs --search-mode bm25

# Test semantic search
poetry run caliper_v2 query "How do I estimate infiltration and inflow?" --index federal_regs --search-mode vector
```

## 📊 Progress
- ✅ Federal Regulations: 595 nodes indexed
- ⏳ State Regulations: 18 PDFs pending
- ⏳ Special Districts: 1 PDF pending
- ⏳ Design Standards: 6 PDFs pending
- ⏳ Technical Reports: 3 PDFs pending

Total: 9/37 documents indexed (24%)

## 💡 Tips
- Each index takes 1-3 minutes depending on PDF sizes
- The state regulations folder is the largest (18 PDFs)
- You can test queries immediately after each index
- All indexes are independent - order doesn't matter
