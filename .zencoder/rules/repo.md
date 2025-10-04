---
description: Repository Information Overview
alwaysApply: true
---

# Caliper v2 Information

## Summary
Caliper v2 is a Python-based command-line tool for information retrieval and generation. It leverages LlamaCloud and LlamaIndex for hybrid cloud retrieval, supporting multiple LLM providers (OpenAI, Anthropic, Google Gemini, xAI Grok). The tool allows users to ask natural language questions, retrieve relevant information from specified indexes, and generate synthesized responses.

## Structure
- **src/caliper_v2/**: Main source code with CLI implementation
- **tests/**: Test suite using pytest
- **data_v2/**: Input data and context storage
- **prompts/**: Question/prompt files for retrieval
- **scripts/**: Utility scripts for operations
- **docs/**: Documentation files
- **outputs/**: Generated artifacts

## Language & Runtime
**Language**: Python
**Version**: 3.11-3.13 (3.11 recommended)
**Build System**: Poetry
**Package Manager**: Poetry

## Dependencies
**Main Dependencies**:
- llama-index-core: Core framework for LLM applications
- llama-cloud-services: Managed service for indexing and retrieval
- typer: CLI framework
- loguru: Logging utility
- pydantic: Data validation and settings management
- google-generativeai: Google Generative AI integration
- cohere: Cohere API integration

**Development Dependencies**:
- pytest: Testing framework
- ruff: Linting
- black: Code formatting
- isort: Import sorting
- mypy: Type checking

## Build & Installation
```bash
# Install Poetry (if not already installed)
python -m pip install --user pipx
pipx install poetry

# Setup project
poetry env use 3.11
poetry install --with llamaindex

# Configure environment
cp .env.example .env
# Edit .env with API keys
```

## Usage & Operations
**Key Commands**:
```bash
# Get help
poetry run caliper_v2 --help

# Retrieve information
poetry run caliper_v2 retrieve --question-file prompts/q.md --indexes "federal,state,design_standards" --cloud --top-k 30

# Generate from context
poetry run caliper_v2 generate data_v2/context/<file>.json --style strict-citation

# Enhance retrieved context
poetry run caliper_v2 enhance --in data_v2/context/file.json --out data_v2/context/enhanced.json --write-outline --rewrite-spore

# Judge generated content
poetry run caliper_v2 judge --context data_v2/context/enhanced.json --generation data_v2/outputs/draft.md --out data_v2/judgments/judgment.json --strict

# Run UI
poetry run streamlit run src/caliper_v2/ui/app.py
poetry run python src/caliper_v2/ui_dash/app.py
```

## Testing
**Framework**: pytest (unit/integration tests) + Playwright (E2E tests)
**Test Location**: tests/
**Naming Convention**: test_*.py (pytest), *.spec.ts (Playwright E2E)
**Test Categories**:
- **Unit/Integration**: pytest for core functionality
- **E2E Web UI**: Playwright tests for Dash UI across all providers
- **CLI Integration**: Playwright tests for command-line workflows
- **Performance**: Response time and reliability testing
- **System Prompt Workflows**: Comprehensive validation of documented workflows

**Run Commands**:
```bash
# Run all pytest tests
poetry run pytest

# Run all E2E tests with Playwright
npm test
npx playwright test

# Run specific E2E test suites
npm run test:basic          # Core retrieve/generate workflow
npm run test:advanced       # Advanced functions (enhance/judge/review)
npm run test:performance    # Performance and reliability tests
npm run test:cli           # CLI command integration tests

# Run with visual debugging
.\run-tests.ps1 -Headed

# Run specific providers only
npx playwright test --grep "OpenAI|Anthropic"
```

## Configuration
**Environment**: .env file (copied from .env.example)
**Required Keys**:
- LLM Provider API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
- LLAMA_CLOUD_API_KEY for cloud retrieval
- Index IDs for cloud retrieval (FEDERAL_BASE_ID, STATE_BASE_ID, etc.)

## Features
- Hybrid cloud retrieval with LlamaCloud/LlamaIndex
- Multiple LLM provider support (OpenAI, Anthropic, Google Gemini, xAI)
- Context enhancement and judgment
- Graph-based knowledge retrieval
- Web UI options (Streamlit and Dash)
- Comprehensive testing and validation tools