# 📚 Knowledge Base Indexing Commands

## Quick Copy-Paste Commands

### 1️⃣ Federal Regulations (9 PDFs, ~3-5 min)
```bash
poetry run caliper_v2 ingest knowledge_base/01_federal_regulations --index federal_regs --persist
```

### 2️⃣ Washington State Regulations (18 PDFs, ~5-8 min)
```bash
poetry run caliper_v2 ingest knowledge_base/02_state_regulations/washington --index wa_state_regs --persist
```

### 3️⃣ Special Districts (1 PDF, ~1 min)
```bash
poetry run caliper_v2 ingest knowledge_base/05_special_districts --index special_districts --persist
```

### 4️⃣ Design Standards

#### WEF Standards (4 PDFs, ~2-3 min)
```bash
poetry run caliper_v2 ingest knowledge_base/06_design_standards/wef --index design_wef --persist
```

#### ASCE Standards (1 PDF, ~1 min)
```bash
poetry run caliper_v2 ingest knowledge_base/06_design_standards/asce --index design_asce --persist
```

#### AWWA Standards (1 PDF, ~1 min)
```bash
poetry run caliper_v2 ingest knowledge_base/06_design_standards/awwa --index design_awwa --persist
```

### 5️⃣ Technical Reports (3 PDFs, ~2 min)
```bash
poetry run caliper_v2 ingest knowledge_base/07_technical_reports --index tech_reports --persist
```

## 🚀 Alternative Approaches

### Index Everything at Once (~15-20 min)
```bash
poetry run caliper_v2 ingest knowledge_base --index all_regulations --persist
```

### Index with Local Embeddings (Faster, No API)
```bash
# Add --embed-provider local to any command above
poetry run caliper_v2 ingest knowledge_base/01_federal_regulations --index federal_regs --persist --embed-provider local
```

### Combine Multiple Directories
```bash
# All design standards together
poetry run caliper_v2 ingest knowledge_base/06_design_standards --index all_design_standards --persist
```

## 🔍 Useful Commands After Indexing

### Check Available Indexes
```bash
ls -la data_v2/indexes/
```

### Test Federal Regulations
```bash
poetry run caliper_v2 query "What are the EPA biosolids requirements?" --index federal_regs --search-mode hybrid
```

### Test State Regulations
```bash
poetry run caliper_v2 query "What are the WAC requirements for wastewater discharge?" --index wa_state_regs --search-mode hybrid
```

### Test Design Standards
```bash
poetry run caliper_v2 query "What does WEF recommend for infiltration analysis?" --index design_wef --search-mode hybrid
```

### Search Across Multiple Indexes
```bash
# Note: This requires modifying the CLI to support multiple indexes
# For now, use the all_regulations index for comprehensive searches
```

## 📊 Index Statistics

| Directory | Documents | Est. Time (OpenAI) | Est. Time (Local) |
|-----------|-----------|-------------------|-------------------|
| Federal Regulations | 9 PDFs | 3-5 min | 1-2 min |
| WA State Regulations | 18 PDFs | 5-8 min | 2-3 min |
| Special Districts | 1 PDF | 1 min | <1 min |
| Design Standards (all) | 6 PDFs | 3-4 min | 1-2 min |
| Technical Reports | 3 PDFs | 2 min | 1 min |
| **Total** | **37 PDFs** | **15-20 min** | **5-8 min** |

## 💡 Tips

1. **Start small**: Index one directory first to test
2. **Use local embeddings** for testing: Add `--embed-provider local`
3. **Monitor progress**: Each PDF will show processing status
4. **Check logs**: Look for "Created BM25 index" and "Persisted vector index"
5. **Reindex anytime**: Running the same command overwrites the previous index

## 🎯 Recommended Order

1. Start with federal_regs (good test set)
2. Then wa_state_regs (larger set)
3. Then design standards (technical content)
4. Finally special districts and tech reports

Ready to start indexing! 🚀
