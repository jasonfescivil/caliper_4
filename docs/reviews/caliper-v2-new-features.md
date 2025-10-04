# Caliper v2 New Features Guide

## 🚀 Latest Improvements (August 2025)

### 1. Enhanced Embeddings
- **Upgraded to `text-embedding-3-small`** - Better semantic understanding
- **Automatic API key loading** - No more manual exports needed

### 2. LlamaParse Integration
- **Smart PDF parsing** - Preserves tables, formatting, and structure
- **Use with**: `--llama-parse` flag during ingestion
- **Requires**: `LLAMA_CLOUD_API_KEY` in .env

### 3. Regulatory Metadata Extraction
- **Automatic extraction** of CFR, WAC, RCW numbers
- **Agency and year detection** from filenames and content
- **Enables filtered searches** by regulation type

### 4. Citations System ✅ NEW!
- **Inline citations** - [1], [2] format in responses
- **Source footnotes** - Filename, page, and relevance score
- **Automatic** - No flags needed, works on all queries

### 5. Multi-Index Federation ✅ NEW!
- **Query multiple indexes** simultaneously
- **Intelligent routing** via SubQuestionQueryEngine
- **Simple syntax**: `--index "federal,state,local"`

### 6. Hybrid Search
- **Combines** semantic (vector) and keyword (BM25) search
- **Three modes**: `--search-mode vector|bm25|hybrid`
- **Better precision** for technical regulatory terms

## 📚 Example Commands

### Basic Query with Citations
```bash
poetry run caliper_v2 query "What are the BOD limits for discharge?" --index federal_test
```

### Multi-Index Query
```bash
poetry run caliper_v2 query "Compare federal and state chlorine requirements" --index "federal,state"
```

### Hybrid Search
```bash
poetry run caliper_v2 query "40 CFR 503.13 pathogen reduction requirements" --index federal_test --search-mode hybrid
```

### LlamaParse Ingestion
```bash
poetry run caliper_v2 ingest knowledge_base/01_federal_regulations --index federal --persist --llama-parse
```

### Filter by Source
```bash
poetry run caliper_v2 query "Biosolids land application" --index federal --source-filter "EPA_guide-part503"
```

## 🔧 Configuration

### Required Environment Variables (.env)
```
OPENAI_API_KEY=sk-...
LLAMA_CLOUD_API_KEY=llx-...
COHERE_API_KEY=...  # Optional, for reranking
```

### Index Organization
- `federal` - Federal regulations (CFR, EPA guides)
- `state` - State regulations (WAC, RCW)
- `special_districts` - Local district requirements
- `design_standards` - Engineering standards
- `technical_reports` - Research and guidance docs

## 💡 Best Practices

1. **Use hybrid search** for specific regulation lookups (e.g., "40 CFR 503.13")
2. **Use vector search** for conceptual queries (e.g., "How does disinfection work?")
3. **Use multi-index** for comprehensive compliance checks
4. **Enable LlamaParse** for complex PDFs with tables
5. **Check citations** to verify source accuracy

## 🚧 Coming Soon

- Incremental indexing (HashCache)
- Chat mode with conversation memory
- Export to Word/PDF with formatting
- Web UI for non-technical users
