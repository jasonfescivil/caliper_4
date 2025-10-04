# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Caliper v2 is a Python-based RAG (Retrieval-Augmented Generation) system designed for engineering report analysis and generation. It's a single-user application targeting engineering consultants who need to fact-check reports, conduct research, and generate technical content with regulatory compliance focus.

**Key Characteristics:**
- **Single-user, non-scaled application** - No distributed systems concerns
- **Python 3.11-3.13** with Poetry for dependency management
- **Multi-provider LLM support** - OpenAI, Anthropic, Google Gemini, xAI, Cohere
- **Hybrid retrieval** - Local indexes + cloud-based search via LlamaCloud
- **Engineering domain focus** - Wastewater treatment, NPDES permits, regulatory compliance

## Essential Commands

### Environment Setup
```powershell
# Install Poetry (if not installed)
py -3.11 -m pip install --user pipx
py -3.11 -m pipx ensurepath
pipx install poetry

# Project setup
poetry env use 3.11
poetry install --with llamaindex

# Environment configuration
cp .env.example .env
# Edit .env with real API keys
```

### Core Development Commands
```powershell
# Check system health and API keys
poetry run caliper_v2 doctor

# Run comprehensive E2E tests
.\run-tests.ps1

# Run specific test suites
.\run-tests.ps1 basic              # Basic retrieve & generate tests
.\run-tests.ps1 advanced           # Advanced functions (enhance, judge)
.\run-tests.ps1 performance        # Performance & reliability tests
.\run-tests.ps1 -Headed            # Run with browser visible for debugging

# Run Python unit tests
poetry run pytest -q

# Start web UIs for development
poetry run streamlit run src\caliper_v2\ui\app.py           # Streamlit UI
poetry run python -m caliper_v2.ui_dash.app                # Dash UI (port 8050)

# Code quality
pre-commit run --all-files         # Run linting, formatting, security checks
poetry run black src/              # Format code
poetry run ruff check src/         # Lint code
```

### Primary Workflow Commands
```powershell
# Retrieval with cloud indexes
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes federal,state,design_standards --cloud

# Generation from context
poetry run caliper_v2 generate data_v2\context\latest_context.json --style strict-citation

# Enhanced workflow (retrieve → enhance → generate → judge)
poetry run caliper_v2 retrieve @prompts\query.md --cloud --out data_v2\context\ctx.json
poetry run caliper_v2 enhance --in data_v2\context\ctx.json --out data_v2\context\enhanced.json
poetry run caliper_v2 generate data_v2\context\enhanced.json --out outputs\draft.md
poetry run caliper_v2 judge --context data_v2\context\enhanced.json --generation outputs\draft.md --out data_v2\judgments\report.json

# GraphRAG workflows
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2\graph
poetry run caliper_v2 graph retrieve "regulatory requirements" --graph-dir data_v2\graph --mix-with-text
```

## Architecture Overview

### CLI Structure Split
**Critical:** The CLI has a **split architecture** across two files:
- `src\caliper_v2\cli_main.py` - Primary entry point with `retrieve`, `ingest`, `doctor` commands
- `src\caliper_v2\cli.py` - Secondary commands: `enhance`, `judge`, `review`, `generate`

Both support subcommands via Typer:
- `graph` subcommands (GraphRAG operations)
- `report` subcommands (claims extraction, etc.)

### Provider Architecture
**Multi-provider LLM system** via `src\caliper_v2\core\llm_providers.py`:
- **Cohere** - Recommended for retrieval/embeddings (`command-r-plus`)
- **OpenAI** - GPT-4o/GPT-5 support with project scoping
- **Anthropic** - Claude Sonnet 4.5/Opus 4.1 for generation
- **Google Gemini** - Gemini 2.5 Pro for long context
- **xAI** - Grok-4 for fast iteration

Provider selection hierarchy: CLI flags → `.caliper.yml` → environment auto-detection

### Retrieval Architecture
**Hybrid Cloud + Local approach:**
- **LlamaCloud** - Production cloud indexes via `llama_cloud_retriever.py`
  - Federal regulations, state regulations, design standards
  - Requires: `LLAMA_CLOUD_API_KEY`, `FEDERAL_BASE_ID`, `STATE_BASE_ID`, etc.
- **Local GraphRAG** - Knowledge graph retrieval via `graph_retriever.py`
- **BM25 + Vector search** - Hybrid dense/sparse retrieval

### Configuration System
**Centralized config via `.caliper.yml`:**
- Provider defaults and presets (quick-query, engineering-report, etc.)
- Retrieval parameters (top_k, reranker settings)
- Workflow configurations
- Overridable by CLI flags

### Data Flow
```
User Query → Retrieve (LlamaCloud/Local) → Context JSON → 
Enhance (Optional) → Generate (LLM Provider) → Judge (Optional) → Output
```

Key directories:
- `data_v2\context\` - Retrieval context files
- `data_v2\indexes\` - Local vector indexes  
- `outputs\` - Generated reports and drafts
- `knowledge_base\` - Source documents for ingestion

## Testing Strategy

### Playwright E2E Tests
**Primary testing approach** using Playwright for web UI testing:
- **Browser coverage:** Chromium, Firefox, WebKit
- **Provider coverage:** All 5 LLM providers tested
- **Complexity level:** Medium engineering questions (WWTP design, NPDES permits)

### Test Suites
1. **Basic** (`multi-provider-retrieve-generate.spec.ts`) - Core retrieve → generate workflow
2. **Advanced** (`advanced-functions.spec.ts`) - Full workflow with enhance/judge
3. **Performance** (`performance-reliability.spec.ts`) - Response times, stability
4. **UI Validation** (`ui-validation.spec.ts`) - Interface components

### Quality Gates
- **Performance:** < 2min retrieval, < 3min generation
- **Success rates:** ≥ 80% across providers
- **Output validation:** Minimum 200 chars, relevant keywords
- **File structure:** Valid JSON context, proper markdown

## Key Development Patterns

### Error Handling Philosophy
- **Graceful degradation** - System continues with reduced functionality
- **Provider fallbacks** - Auto-detect working API keys
- **Retry logic** - Built into LLM provider calls
- **Validation at boundaries** - Input validation, output structure checks

### Configuration Loading
```python
# Environment precedence: .env → settings → auto-detection
from caliper_v2.core.env import load_env
from caliper_v2.core.config import settings
```

### Provider Selection Pattern
```python
# CLI flags override config files override env detection
provider, model, source = _resolve_llm_from_flags_or_settings(cli_provider, cli_model)
```

### Stable ID Generation
Uses content-addressable IDs for reproducibility:
- `stable_document_id()` - Based on file path normalization
- `stable_passage_id()` - Based on content + position hashing

## Docker Development

### Local Development Stack
```powershell
# Start Weaviate + app services
docker-compose up -d

# Execute CLI commands in container
docker-compose exec app poetry run caliper_v2 doctor

# Start Streamlit UI in container
docker-compose exec app poetry run streamlit run src/caliper/ui/app.py --server.port=8501 --server.address=0.0.0.0
```

## Common Issues & Solutions

### API Key Management
```powershell
# Check API key status
poetry run caliper_v2 doctor

# Keys required in .env:
# OPENAI_API_KEY, ANTHROPIC_API_KEY, COHERE_API_KEY
# GEMINI_API_KEY, XAI_API_KEY, LLAMA_CLOUD_API_KEY
```

### Cloud Index Issues
```powershell
# Verify cloud index IDs in .env
# FEDERAL_BASE_ID, FEDERAL_SUMMARY_ID
# STATE_BASE_ID, STATE_SUMMARY_ID  
# DESIGN_BASE_ID, DESIGN_SUMMARY_ID
```

### Performance Tuning
- **Cohere for retrieval** - Best embedding quality
- **Claude Sonnet 4.5** - Best balance of speed/quality for generation  
- **Claude Opus 4.1** - Highest quality for final QC/judging
- **Timeout settings** - Configurable via `CALIPER_LLM_TIMEOUT_S`

## Important Code Locations

### Core Entry Points
- `src\caliper_v2\cli_main.py` - Main CLI commands
- `src\caliper_v2\cli.py` - Secondary CLI commands  
- `src\caliper_v2\ui\app.py` - Streamlit UI
- `src\caliper_v2\ui_dash\app.py` - Dash UI

### Provider Integration
- `src\caliper_v2\core\llm_providers.py` - Multi-provider LLM setup
- `src\caliper_v2\core\config.py` - Settings and configuration
- `src\caliper_v2\core\env.py` - Environment loading

### Retrieval System  
- `src\caliper_v2\retrievers\llama_cloud_retriever.py` - Cloud retrieval
- `src\caliper_v2\retrievers\graph_retriever.py` - GraphRAG retrieval
- `src\caliper_v2\commands\graph_cli.py` - Graph commands

### Quality & Enhancement
- `src\caliper_v2\commands\enhance.py` - Context enhancement
- `src\caliper_v2\commands\judge.py` - Quality assessment
- `src\caliper_v2\commands\review.py` - Report review

## Engineering Domain Context

This system specializes in **environmental engineering** and **regulatory compliance**:
- **NPDES permits** - National Pollutant Discharge Elimination System
- **WWTP design** - Wastewater Treatment Plant engineering
- **G1 requirements** - Specific regulatory compliance standards
- **I&I investigations** - Inflow and Infiltration studies
- **Biosolids management** - Wastewater treatment byproducts

The knowledge base contains federal regulations (EPA), state regulations (WA Dept. Ecology), and design standards. Generated content requires strict citation of regulatory sources.

## Development Workflow Best Practices

1. **Always run `poetry run caliper_v2 doctor`** before development
2. **Test with multiple providers** - Don't assume one provider works for all
3. **Use `.caliper.yml` presets** - Avoid repetitive CLI flag specification  
4. **Validate outputs** - Check JSON structure and content quality
5. **Run E2E tests** - Use `.\run-tests.ps1 basic` for quick validation
6. **Check performance** - Monitor response times, especially for GPT-5/Claude Opus

## Security Considerations

- **Never commit API keys** - Use `.env` (git-ignored)
- **Secrets in environment only** - Load via `caliper_v2.core.env`
- **Provider scoping** - OpenAI org/project isolation supported
- **Pre-commit hooks** - Security scanning with detect-secrets
- **Minimal permissions** - Single-user application design