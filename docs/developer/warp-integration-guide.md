# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Caliper v2 is a Python-based Retrieval-Augmented Generation (RAG) system for regulatory compliance analysis. It focuses on retrieving, analyzing, and judging regulatory content, particularly for engineering and wastewater treatment facility compliance. The system supports both local and cloud-based retrieval using LlamaIndex/LlamaCloud.

## Development Commands

### Environment Setup
```powershell
# Install Poetry (Windows PowerShell)
py -3.11 -m pip install --user pipx
py -3.11 -m pipx ensurepath
# Close/reopen shell, then:
pipx install poetry

# Project setup
poetry --version
poetry env use 3.11
poetry install --with llamaindex
```

### Configuration
```powershell
# Copy environment template and configure API keys
cp .env.example .env
# Edit .env with required provider keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, XAI_API_KEY, COHERE_API_KEY, LLAMA_CLOUD_API_KEY
```

### Core CLI Commands
```powershell
# Main CLI help
poetry run caliper_v2 --help

# Retrieve documents using cloud retrieval with hybrid search
poetry run caliper_v2 retrieve --question-file prompts/my_query.md --indexes "federal,state,design_standards" --cloud --top-k 30 --dense-k 12 --sparse-k 12 --alpha 0.5

# Shorthand retrieval
poetry run caliper_v2 retrieve @prompts/my_query.md --indexes federal

# Enhance retrieved context with outline and diagnostics
poetry run caliper_v2 enhance --in C:\repos\caliper_3\data_v2\context\population_retry.json --out C:\repos\caliper_3\data_v2\context\population_enhanced.json --write-outline --rewrite-spore --suggest-retrieve

# Judge generated content against retrieved context
poetry run caliper_v2 judge --context C:\repos\caliper_3\data_v2\context\population_enhanced.json --generation C:\repos\caliper_3\data_v2\outputs\population_draft.md --out C:\repos\caliper_3\data_v2\judgments\population_judgment.json --strict

# Review workflow combining judge and text lints
poetry run caliper_v2 review --context "C:\repos\caliper_3\data_v2\context\population_retry3.json" --draft "C:\repos\caliper_3\population_procedure3.md" --out-json "C:\repos\caliper_3\data_v2\reviews\population_review.json" --out-md "C:\repos\caliper_3\data_v2\reviews\population_review.md" --strict --max-evidence-per-claim 5
```

### Testing
```powershell
# Run all tests with coverage
poetry run pytest tests/ --cov=src/caliper_v2 --cov-branch --cov-report=xml --cov-report=term-missing -v

# Run specific test files
poetry run pytest tests/test_cli_snapshots.py -v
poetry run pytest tests/test_judge_metrics.py -v

# Run single test
poetry run pytest tests/test_review_report.py::TestReviewReport::test_basic_review -v
```

### UI Development
```powershell



# Launch Dash UI
poetry run python src\caliper_v2\ui_dash\app.py
```

## Architecture Overview

### Core Components

**CLI Layer** (`src/caliper_v2/cli.py`)
- Typer-based CLI with commands: retrieve, enhance, judge, review
- Auto-detects LLM providers based on available API keys
- Handles both cloud and local retrieval modes

**Configuration** (`src/caliper_v2/core/config.py`)
- Pydantic-based settings management with `.env` file support
- Provider API key management and model selection
- Feature flags for hybrid search, reranking, etc.

**Commands** (`src/caliper_v2/commands/`)
- `enhance.py`: Context enhancement with outlines and diagnostics
- `judge.py`: Evidence-based claim validation against retrieved context
- `review.py`: Combined judgment and text linting workflow

**Services** (`src/caliper_v2/services/`)
- `judge_components.py`: Core judgment logic, BM25 indexing, embeddings
- `llama_cloud_index.py`: LlamaCloud integration for hybrid retrieval
- `persistence.py`: Data persistence utilities
- `ui_api.py`: UI backend API layer

**Retrievers** (`src/caliper_v2/retrievers/`)
- `llama_cloud_retriever.py`: Cloud-based retrieval with hybrid search support

### Data Flow Pattern

The system follows a structured 4-step workflow:
1. **Retrieve** → `context.json` (retrieval_session)
2. **Enhance** → `enhanced.json` (outline, gaps, suggestions, spore rewrite)
3. **Generate** → `draft.md` (consume context to generate content)
4. **Judge** → `judgment.json` (verify claims and citations)

### Key Environment Variables

Cloud retrieval requires six index IDs (3 logical indexes × 2 IDs each):
- `FEDERAL_BASE_ID`, `FEDERAL_SUMMARY_ID`
- `STATE_BASE_ID`, `STATE_SUMMARY_ID`
- `DESIGN_BASE_ID`, `DESIGN_SUMMARY_ID`

Provider API keys:
- `LLAMA_CLOUD_API_KEY` (required for cloud retrieval)
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`
- `XAI_API_KEY`, `COHERE_API_KEY`

### Testing Strategy

- **CLI Snapshots** (`test_cli_snapshots.py`): Prevents accidental flag removal
- **Judge Components** (`test_judge_*.py`): Evidence validation, metrics, citations
- **Review Reports** (`test_review_report.py`): End-to-end review workflow
- **Text Linting** (`test_text_lint.py`): Deterministic text quality checks

### Dependencies Management

Uses Poetry with dependency groups:
- **Core**: Basic CLI and retrieval functionality
- **llamaindex**: LlamaIndex ecosystem components (use `--with llamaindex`)
- **dev**: Testing and development tools

Target Python version: 3.11 (supports 3.12/3.13)

### File Structure Patterns

- `data_v2/context/`: Retrieved context JSON files
- `data_v2/outputs/`: Generated drafts and reports
- `data_v2/judgments/`: Judgment reports with claim validation
- `data_v2/reviews/`: Combined review reports (JSON + Markdown)
- `prompts/`: Query templates and instructions

### Provider Integration

The system auto-detects available providers based on API keys:
- OpenAI (GPT models including gpt-5-nano)
- Anthropic (Claude models)
- Google (Gemini models)
- xAI (Grok models)
- Cohere (for embeddings and reranking)

### Windows-Specific Notes

- Uses PowerShell-friendly absolute paths in examples
- File paths use Windows backslashes in documentation
- Environment setup includes Windows-specific Python launcher (`py -3.11`)

## Development Guidelines

Key development practices for this codebase:
- Python 3.11+ with type hints and structured logging
- RAG architecture maintains clear service boundaries between retrieval, enhancement, and judgment
- Comprehensive test coverage including CLI stability tests
- API key management through environment variables only (never commit secrets)
- Windows PowerShell optimized workflows

**Note**: Some documentation may be outdated - always verify current functionality by checking the actual code and running tests.

## Git Workflow

Default remote: `https://github.com/jasonfescivil/caliper_v2.git`
Main branches: `main`, `master`, `develop`, `cohere-support`
CI/CD includes comprehensive testing, mutation testing, and coverage reporting.
