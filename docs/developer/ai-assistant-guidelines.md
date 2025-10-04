# Caliper v2 AI Assistant Guidelines

This document provides guidelines for AI assistants working with the Caliper v2 repository.

## Project Structure & Module Organization

- **Source**: `src/caliper_v2/` (Typer CLI in `cli.py`; entry via `pyproject.toml` script `caliper_v2`).
- **Tests**: `tests/` (pytest); shared fixtures under `tests/fixtures/`.
- **Data/outputs**: inputs and context in `data_v2/`, generated artifacts in `outputs/`.
- **Scripts**: tooling in `scripts/`; local wrapper `run_caliper_v2.py`.
- **Docs**: `README.md` for quickstart; deeper notes in `docs/`.

## Build, Test, and Development Commands

- **Setup env**: `poetry env use 3.11 && poetry install --with llamaindex`
- **CLI help**: `poetry run caliper_v2 --help`
- **Retrieve (cloud)**: `poetry run caliper_v2 retrieve --question-file prompts/q.md --indexes "federal,state,design_standards" --cloud --top-k 30`
- **Generate from context**: `poetry run caliper_v2 generate data_v2/context/<file>.json --style strict-citation`
- **Test**: `poetry run pytest -q`
- **Lint/format**: `poetry run ruff . && poetry run black . && poetry run isort .`
- **Type check**: `poetry run mypy src`
- **Env doctor**: `poetry run caliper_v2 doctor`

## Coding Style & Naming Conventions

- **Python version**: 3.11+
- **Formatting**: Black (line length 100) and isort (profile=black)
- **Linting**: Ruff
- **Type checking**: mypy (ignore missing third‑party imports)
- **Naming conventions**:
  - Files and functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Module organization**: Modules under `src/`; tests named `tests/test_*.py`

## Testing Guidelines

- **Framework**: pytest
- **Test principles**: Keep tests fast and close to changed code
- **Naming**: Name tests `test_*`; use `tmp_path` for temporary files
- **CLI stability**: Snapshots live in `tests/test_cli_snapshots.py`; update when flags/help change

## Commit & Pull Request Guidelines

- **Commit format**: Follow Conventional Commits (e.g., `feat(scope): …`, `fix(scope): …`, `docs: …`, `chore: …`)
- **PR requirements**: Include purpose, linked issue, relevant logs/screenshots (especially CLI output), and exact run steps (`poetry run …`)
- **CLI changes**: If CLI help changes, refresh snapshots and update `README.md` examples

## Security & Configuration Tips

- **Environment setup**: Copy `.env.example` to `.env`. Set provider keys (`OPENAI_API_KEY`, `COHERE_API_KEY`, `LLAMA_CLOUD_API_KEY`). Never commit secrets.
- **Cloud retrieval**: Set `<NAME>_BASE_ID` and `<NAME>_SUMMARY_ID` per logical index (e.g., `DESIGN_BASE_ID`).
- **Environment verification**: Use `poetry run caliper_v2 doctor` to verify environment and provider resolution.