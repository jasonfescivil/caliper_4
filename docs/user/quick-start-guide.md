# Caliper v2 Quick Start Guide

This guide will help you get started with Caliper v2 quickly.

## Prerequisites

- **Python**: 3.11 recommended (supports 3.12/3.13 too)
- **pipx**: To install Poetry isolated from system Python

## Installation

### Install Poetry

#### Windows (PowerShell)

```powershell
py -3.11 -m pip install --user pipx
py -3.11 -m pipx ensurepath
# Close/reopen shell, then:
pipx install poetry
```

#### macOS/Linux

```bash
python3.11 -m pip install --user pipx
pipx ensurepath
exec "$SHELL" -l
pipx install poetry
```

### Project Setup

Clone and enter the repository, then:

```powershell
poetry --version
poetry env use 3.11
poetry install --with llamaindex
```

### Environment Configuration

Copy `.env.example` to `.env` and fill in real API keys:

```powershell
cp .env.example .env
# Edit .env with your text editor
```

Required API keys:
- `LLAMA_CLOUD_API_KEY` (for cloud retrieval)
- Provider keys as needed (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`)

For cloud retrieval, also set these index IDs:
- `FEDERAL_BASE_ID`, `FEDERAL_SUMMARY_ID`
- `STATE_BASE_ID`, `STATE_SUMMARY_ID`
- `DESIGN_BASE_ID`, `DESIGN_SUMMARY_ID`

## Basic Usage

### CLI Help

```powershell
poetry run caliper_v2 --help
```

### Retrieve Information

#### From Cloud Indexes

```powershell
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state,design_standards" --cloud --dense-k 12 --sparse-k 12 --alpha 0.5 --rerank-top-n 12
```

#### Using a Question File

```powershell
poetry run caliper_v2 retrieve --question-file prompts/my_query.md --indexes "federal,state,design_standards" --cloud --top-k 30
```

Shorthand also works:

```powershell
poetry run caliper_v2 retrieve @prompts/my_query.md --indexes federal
```

### Generate from Context

```powershell
poetry run caliper_v2 generate data_v2/context/file.json --style strict-citation
```

### Enhance Retrieved Context

```powershell
poetry run caliper_v2 enhance --in data_v2/context/file.json --out data_v2/context/enhanced.json --write-outline --rewrite-spore --review-spores --suggest-retrieve
```

### Judge Generated Content

```powershell
poetry run caliper_v2 judge --context data_v2/context/enhanced.json --generation data_v2/outputs/draft.md --out data_v2/judgments/judgment.json --strict
```

## GraphRAG Workflow

### Build a Local Graph

```powershell
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph
```

### Retrieve from the Graph

```powershell
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --out data_v2/context/graph_ctx.json
```

### Mix Graph with Cloud Text Retrieval

```powershell
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --mix-with-text --text-indexes design --top-k 40 --rerank-top-n 20 --out data_v2/context/graphmix_ctx.json
```

## Using the UI

### Dash UI

```powershell
poetry run python src\caliper_v2\ui_dash\app.py
```

## Troubleshooting

### Check Environment

```powershell
poetry run caliper_v2 doctor
```

### Display Runtime Information

```powershell
poetry run caliper_v2 info
```

## Notes

- If you leave the model blank, Caliper chooses a safe default per provider (OpenAI → gpt-4o)
- If you have multiple Pythons installed, pin the venv with `poetry env use 3.11`
- Never commit real secrets in `.env`. If you suspect exposure, rotate keys