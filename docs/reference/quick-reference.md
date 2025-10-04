# Caliper v2 Quick Reference Guide

## Page 1: Command Reference

### Basic Commands

#### `caliper_v2 info`
Shows system configuration, available providers, and environment status.
```bash
poetry run caliper_v2 info
```

#### `caliper_v2 ingest`
Indexes documents into a searchable database. Supports PDF, DOCX, TXT, and more.
```bash
poetry run caliper_v2 ingest <path> --index <name> [options]
```
**Key Options:**
- `--persist`: Save index to disk (required for reuse)
- `--force`: Re-process all files even if unchanged
- `--embed-provider`: Choose embeddings (openai/local)
- `--llama-parse`: Use LlamaParse for complex PDFs

#### `caliper_v2 query`
Search indexed documents and get AI-synthesized answers with citations.
```bash
poetry run caliper_v2 query "<question>" --index <name> [options]
```
**Key Options:**
- `--llm-provider`: Choose LLM (openai/anthropic/gemini/xai)
- `--llm-model`: Specific model version
- `--search-mode`: vector/bm25/hybrid (default: vector)
- `--top-k`: Number of results to retrieve (default: 10)
- `--expand-query`: Generate query variations interactively
- `--hyde`: Use hypothetical document embeddings
- `--critique-retrieval`: Filter results by relevance

#### `caliper_v2 agent`
Multi-step reasoning across multiple indexes with tool-use capabilities.
```bash
poetry run caliper_v2 agent "<question>" --indexes <idx1,idx2> [options]
```
**Key Options:**
- `--indexes`: Comma-separated list of indexes to search
- `--verbose`: Show agent thinking process
- `--llm-provider`: Choose reasoning LLM

### Advanced Features

#### Multi-Provider LLM Support
```bash
# OpenAI (default)
--llm-provider openai --llm-model gpt-4

# Anthropic Claude
--llm-provider anthropic --llm-model claude-3-opus-20240229

# Google Gemini
--llm-provider gemini --llm-model gemini-1.5-flash

# xAI Grok
--llm-provider xai --llm-model grok-beta
```

#### Search Modes
- **Vector**: Semantic similarity search (understands meaning)
- **BM25**: Keyword-based search (exact matches)
- **Hybrid**: Combines vector + BM25 with reranking

#### Metadata Filtering
```bash
--regulation-filter "CFR 503"  # Filter by regulation
--doc-type "guidance"          # Filter by document type
--date-after "2020-01-01"      # Filter by date
```

---

## Page 2: Example Queries

### Basic Queries

```bash
# Simple factual question
poetry run caliper_v2 query "What are the BOD limits for secondary treatment?" --index federal

# Summarize an index
poetry run caliper_v2 query "Summarize the main topics covered in these documents" --index state

# Search with specific LLM
poetry run caliper_v2 query "Explain biosolids Class A requirements" --index federal --llm-provider gemini
```

### Advanced Queries

```bash
# Query expansion for better results
poetry run caliper_v2 query "wastewater discharge requirements" --index federal --expand-query

# Hypothetical document embeddings (HyDE)
poetry run caliper_v2 query "infiltration and inflow reduction methods" --index technical_reports --hyde

# Critique retrieval for quality control
poetry run caliper_v2 query "NPDES permit application timeline" --index federal --critique-retrieval

# Hybrid search with reranking
poetry run caliper_v2 query "WAC 173-308 monitoring requirements" --index state --search-mode hybrid
```

### Agent Queries (Multi-Index Reasoning)

```bash
# Compare regulations across indexes
poetry run caliper_v2 agent "Compare federal vs Washington state biosolids regulations" --indexes federal,state

# Complex analysis across multiple sources
poetry run caliper_v2 agent "What are all the requirements for a new wastewater treatment plant in Washington?" --indexes federal,state,design_standards --verbose

# Technical assessment with standards
poetry run caliper_v2 agent "Evaluate infiltration/inflow reduction strategies per WEF and EPA guidance" --indexes federal,technical_reports
```

### Real-World Use Cases

```bash
# AKART Analysis
poetry run caliper_v2 agent "What treatment technologies qualify as AKART for small communities?" --indexes state,tekoa,technical_reports

# Permit Compliance Check
poetry run caliper_v2 agent "List all monitoring requirements for NPDES permit WA0023141" --indexes federal,state,tekoa

# Cost Analysis
poetry run caliper_v2 query "What are typical costs for UV disinfection systems?" --index design_standards

# Engineering Report Support
poetry run caliper_v2 agent "Summarize design criteria for lagoon systems per Ecology Orange Book" --indexes state,design_standards
```

### Working with Multiple Providers

```bash
# Fast response with Gemini Flash
poetry run caliper_v2 query "Quick summary of BOD limits" --index federal --llm-provider gemini --llm-model gemini-1.5-flash

# Detailed analysis with Claude
poetry run caliper_v2 agent "Comprehensive review of land application requirements" --indexes federal,state --llm-provider anthropic --llm-model claude-3-opus-20240229

# Cost-effective with OpenAI
poetry run caliper_v2 query "List permit submittal deadlines" --index state --llm-provider openai --llm-model gpt-3.5-turbo
```

### Index Management

```bash
# Create new index from documents
poetry run caliper_v2 ingest knowledge_base/09_cost_data --index cost_data --persist

# Update existing index with new documents
poetry run caliper_v2 ingest new_regulations/ --index federal --persist --force

# Index with advanced parsing for complex PDFs
poetry run caliper_v2 ingest complex_docs/ --index technical --persist --llama-parse
```

## Available Indexes

| Index | Contents | Best For |
|-------|----------|----------|
| `federal` | EPA regulations, CFRs | Federal compliance |
| `state` | Washington WACs, RCWs | State requirements |
| `tekoa` | Tekoa WWTP case study | Project-specific info |
| `technical_reports` | Engineering reports | Technical guidance |
| `design_standards` | ASCE, AWWA, WEF | Design criteria |

## Pro Tips

1. **Always use `--persist`** when ingesting to save indexes for reuse
2. **Use `--verbose`** with agent to see reasoning steps
3. **Try `--expand-query`** when initial results aren't satisfactory
4. **Combine indexes** with agent for comprehensive analysis
5. **Use `--search-mode hybrid`** for acronyms and technical terms
