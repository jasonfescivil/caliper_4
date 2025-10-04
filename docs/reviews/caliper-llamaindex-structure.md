# Caliper LlamaIndex - Final Clean Structure

## Current State (After Cleanup)

This is the **single working LlamaIndex implementation** of Caliper.

```
caliper/
├── src/
│   └── caliper_v2/       # The ONLY implementation - LlamaIndex-based
│       ├── cli.py        # Main CLI with hybrid search (just implemented today)
│       └── services/
│           └── persistence.py  # Index path management with BM25 support
│
├── pyproject.toml        # Main project file
│   ├── [tool.poetry.scripts]
│   │   └── caliper_v2 = "caliper_v2.cli:app"  # CLI command
│   └── [tool.poetry.group.llamaindex]          # LlamaIndex dependencies
│
├── data_v2/              # Data directory for indexes
│   └── indexes/          # FAISS and BM25 indexes stored here
│
└── knowledge_base/       # Your regulatory documents
    ├── federal/          # Federal regulations
    ├── wa_state/         # Washington state docs
    └── ...              # Other document categories
```

## What Was Removed

1. **`src/caliper/`** - Original Langchain implementation (removed, you have backup)
2. **`caliper_v2/` at root** - Confusing duplicate folder (removed)

## Current Features (Working Today)

### ✅ Implemented and Working

1. **Document Ingestion**
   - Supports PDF, DOCX, TXT via LlamaIndex
   - Creates both FAISS vector index and BM25 keyword index
   - Persistence to disk with `--persist` flag

2. **Hybrid Search (NEW - Just Added Today)**
   - Three search modes via `--search-mode` flag:
     - `vector` (default): Semantic search
     - `bm25`: Keyword-based search
     - `hybrid`: Combined with reciprocal rank fusion
   - Automatic fallback if BM25 unavailable

3. **Query Capabilities**
   - Natural language questions
   - Source filtering with `--source-filter`
   - Cohere reranking support
   - Local embedding mode for testing

4. **CLI Commands**
   ```bash
   poetry run caliper_v2 info      # Show configuration
   poetry run caliper_v2 ingest    # Index documents
   poetry run caliper_v2 query     # Ask questions
   ```

### ❌ Not Yet Implemented

1. **Citations/Footnotes** - Responses don't show sources
2. **Chat Mode** - Only single Q&A, no conversation
3. **Multiple LLM Providers** - Only OpenAI works
4. **HashCache** - No incremental ingestion yet
5. **Template System** - Not integrated from v1

## How to Use

### Installation
```bash
# Install with LlamaIndex dependencies
poetry install --with llamaindex
```

### Basic Workflow
```bash
# 1. Ingest your documents (creates vector + BM25 indexes)
poetry run caliper_v2 ingest knowledge_base --index regulations --persist

# 2. Query with different search modes
# Vector search (default)
poetry run caliper_v2 query "What are biosolids regulations?" --index regulations

# Keyword search
poetry run caliper_v2 query "biosolids EPA limits" --index regulations --search-mode bm25

# Hybrid search (recommended)
poetry run caliper_v2 query "wastewater discharge requirements" --index regulations --search-mode hybrid

# With source filtering
poetry run caliper_v2 query "discharge limits" --index regulations --search-mode hybrid --source-filter "CFR_133.pdf,EPA_guide.pdf"
```

### Local Testing (No API Keys)
```bash
# Use local embeddings for testing
poetry run caliper_v2 ingest docs --index test --persist --embed-provider local
poetry run caliper_v2 query "test question" --index test --embed-provider local
```

## Environment Variables

Create a `.env` file with:
```env
OPENAI_API_KEY=your_key_here
COHERE_API_KEY=your_key_here  # Optional, for reranking
```

## Next Development Steps

1. **Add Citations** - Show source documents and chunks in responses
2. **Fix Import Structure** - Make CLI help work without llamaindex installed
3. **Add Chat Mode** - Interactive conversations
4. **Multi-Provider Support** - Anthropic, Gemini, Azure
5. **HashCache Integration** - Skip re-indexing unchanged files

## Notes

- The old `src/caliper/commands/__pycache__/` folder remains due to permission issues but contains no source code
- All new development should happen in `src/caliper_v2/`
- The hybrid search implementation is brand new (added today) and may need testing/tuning
