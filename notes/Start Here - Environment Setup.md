# Environment Setup

This project targets Python 3.11 and uses Poetry for dependency and virtualenv management. Install Poetry via pipx so it stays isolated from your project environments.

## Windows (PowerShell)

1) Install Python 3.11
- winget install Python.Python.3.11
- Verify: `py -3.11 -V`

2) Install pipx and Poetry
- `py -3.11 -m pip install --user pipx`
- `pipx ensurepath`  (then open a new terminal)
- `pipx install poetry`

3) Create venv and install
- `cd C:\\repos\\caliper`
- `poetry env use 3.11`
- `poetry install --with llamaindex`

4) Verify environment
- `poetry run caliper_v2 providers`
- `poetry run caliper_v2 doctor`
- `poetry run caliper_v2 info`

5) Optional smoke ingest (no OpenAI required)
- `poetry run caliper_v2 ingest test_docs --index smoke --persist --embed-provider local`
- `poetry run caliper_v2 query "hello" --index smoke --search-mode hybrid`

Notes
- .env is auto‑loaded; set keys like `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `LLAMA_CLOUD_API_KEY`.
- Avoid mixing pip installs into the Poetry venv. If required: `poetry run pip install <pkg>`.
- The legacy `requirements.heavy.txt` uses different pins; keep it only for a separate, throwaway venv.

## WSL / Linux

1) Install Python 3.11
- Ubuntu: `sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-distutils`
- Verify: `python3.11 -V`

2) Install pipx and Poetry
- `python3.11 -m pip install --user pipx`
- `~/.local/bin/pipx ensurepath` (restart shell)
- `pipx install poetry`

3) Create venv and install
- `cd /mnt/c/repos/caliper`
- `poetry env use /usr/bin/python3.11`
- `poetry install --with llamaindex`

4) Verify environment
- `poetry run caliper_v2 providers`
- `poetry run caliper_v2 doctor`
- `poetry run caliper_v2 info`

5) Optional smoke ingest (no OpenAI required)
- `poetry run caliper_v2 ingest test_docs --index smoke --persist --embed-provider local`
- `poetry run caliper_v2 query "hello" --index smoke --search-mode hybrid`

## Keys and Providers
- Provider auto-detection: If `OPENAI_API_KEY` is present, defaults to OpenAI; otherwise falls back to Anthropic/Gemini if those keys are set.
- Override with flags: `--llm-provider` and `--llm-model`, or env vars `CALIPER_LLM_PROVIDER`, `CALIPER_LLM_MODEL`.
- LlamaCloud index IDs: set `DESIGN_BASE_ID`, `DESIGN_SUMMARY_ID` (and similar) if you want cloud retrieval by logical index name.

## Troubleshooting
- Poetry picking wrong Python: `poetry env use 3.11` (Windows) or exact path (Linux).
- PATH issues on Windows after pipx: run `pipx ensurepath` and open a new terminal.
- Missing embeddings: run with `--embed-provider local` for smoke tests without OpenAI.

