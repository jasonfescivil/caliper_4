# CONTRIBUTING (Lite) - Caliper Single-User Workflow

This is a lightweight guide for a single user on Windows using Poetry.

Prereqs
- Python 3.11 (recommended)
- Poetry
- .env with provider API keys and LLAMA_CLOUD_API_KEY (if using cloud retrieval)

Setup
`powershell
poetry env use 3.11
poetry install --with llamaindex
`

Quick run
- CLI help: poetry run caliper_v2 --help
- Dash UI: poetry run python src\caliper_v2\ui_dash\app.py

Testing
- Run a focused test (fast):
`powershell
poetry run pytest tests/test_schemas_smoke.py -q
`
- Run Dash UI tests:
`powershell
poetry run pytest tests/ui_dash -q
`
- Run full suite (slower, may need keys):
`powershell
poetry run pytest -q
`

Commit workflow
`powershell
git add -A
git commit -m "feat: <short description>"
`

Troubleshooting
- Keys missing: run poetry run caliper_v2 doctor or check .env.
- Dash UI retrieval created no file: the UI falls back to newest file under data_v2\context; check logs accordion.
- Tests failing due to external deps: run only the focused test above.
