# Caliper v2

A command-line tool for information retrieval and generation using hybrid cloud retrieval and GraphRAG.

## Quick Start

Run Caliper locally with Poetry (installed via pipx). This repo targets Python 3.11–3.13.

### Prerequisites

- Python: 3.11 recommended (supports 3.12/3.13 too)
- pipx: to install Poetry isolated from system Python

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

Clone and enter the repo, then:

```bash
poetry --version
poetry env use 3.11
poetry install --with llamaindex
```

### Environment Configuration

Copy `.env.example` to `.env` and fill in real keys. `.env` is git-ignored.

```bash
cp .env.example .env
# Edit .env with provider API keys (OpenAI, Anthropic, Gemini, XAI, etc.).
```

## Basic Usage

### CLI Help

```bash
poetry run caliper_v2 --help
```

### Retrieve Information

```bash
# Basic retrieval with cloud indexes
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state,design_standards" --cloud

# Retrieval with a question file
poetry run caliper_v2 retrieve --question-file prompts/my_query.md --indexes "federal,state,design_standards" --cloud --top-k 30

# Shorthand for question file
poetry run caliper_v2 retrieve @prompts/my_query.md --indexes federal
```

### Generate from Context

```bash
poetry run caliper_v2 generate data_v2/context/file.json --style strict-citation
```

## Documentation

For more detailed documentation, please refer to the following resources:

- [Installation Guide](docs/user/installation-guide.md): Detailed installation instructions
- [Quick Start Guide](docs/user/quick-start-guide.md): Get started quickly with Caliper v2
- [Operations Checklist](docs/user/operations-checklist.md): Day-to-day operations guide
- [Command Reference](docs/reference/command-reference.md): Comprehensive command reference
- [Architecture Overview](docs/developer/architecture-overview.md): Technical architecture details
- [Contributing Guidelines](CONTRIBUTING.md): How to contribute to the project

### Workflow Examples

- [Retrieval Workflow](docs/workflows/retrieval-workflow.md): Complete retrieval workflow example
- [GraphRAG Workflow](docs/workflows/graphrag-workflow.md): Building and querying knowledge graphs

## Key Features

### Hybrid Cloud Retrieval (LlamaCloud/LlamaIndex)

Caliper forwards hybrid retrieval parameters to LlamaCloud to blend dense + sparse search on cloud indexes.

```bash
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" \
  --indexes "federal,state,design_standards" --cloud \
  --dense-k 12 --sparse-k 12 --alpha 0.5 --rerank-top-n 12
```

Required env vars for cloud retrieval:
- `LLAMA_CLOUD_API_KEY`
- `FEDERAL_BASE_ID`, `FEDERAL_SUMMARY_ID`
- `STATE_BASE_ID`, `STATE_SUMMARY_ID`
- `DESIGN_BASE_ID`, `DESIGN_SUMMARY_ID`

### Enhance and Judge (Post-retrieval Tooling)

After running retrieve, you can enhance the context and judge the generated draft.

#### Enhance

```bash
poetry run caliper_v2 enhance --in data_v2/context/file.json --out data_v2/context/enhanced.json --write-outline --rewrite-spore --review-spores --suggest-retrieve
```

#### Judge

```bash
poetry run caliper_v2 judge --context data_v2/context/enhanced.json --generation data_v2/outputs/draft.md --out data_v2/judgments/judgment.json --strict
```

### GraphRAG (Local Knowledge Graph)

Build and query a local knowledge graph from a corpus of documents.

```bash
# Build a local graph
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph

# Retrieve from the graph
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --out data_v2/context/graph_ctx.json

# Mix with cloud text retrieval
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --mix-with-text --text-indexes design --top-k 40 --rerank-top-n 20 --out data_v2/context/graphmix_ctx.json
```

## User Interfaces

### Dash UI

A modern web interface for Caliper v2 workflows:

```bash
poetry run python src/caliper_v2/ui_dash/app.py
```

The UI runs on `http://localhost:8050` and provides:
- Interactive retrieval configuration
- Provider/model selection
- Real-time command preview
- GraphRAG integration
- Complete workflow: Retrieve → Enhance → Generate → Judge

For detailed instructions, see [Dash UI Guide](docs/user/dash-ui-guide.md).

## Security

- `.env` is ignored by git. Never commit real secrets. If you suspect exposure, rotate keys.

## Notes

- Provider defaults: if you leave the model blank, Caliper chooses a safe default per provider (OpenAI → gpt-4o).
- If you have multiple Pythons installed, pin the venv with `poetry env use 3.11`.
- Pre-commit (optional): `pipx install pre-commit && pre-commit install`.