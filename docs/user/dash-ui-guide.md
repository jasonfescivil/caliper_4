# Caliper v2 Dash UI Guide

The Dash UI provides a tabbed web interface for the Caliper v2 workflow. It runs locally and wraps the existing CLI commands so you can retrieve, enhance, generate, and review content without leaving the browser.

## Launching the UI

`powershell
poetry run python src\caliper_v2\ui_dash\app.py
`

The app binds to http://127.0.0.1:8050 by default. Use Ctrl+C in the terminal to stop the server.

## Tabs and Workflow

### 1. Retrieval
- Query indexes with cloud retrieval (question, indexes, top-k, rerank)
- Advanced options: retrieval mode, dense/sparse k, alpha, include/exclude terms, filters, HyDE, query expansion
- Shows generated CLI command, captured logs, and a preview table of retrieved nodes
- Saves the output path to be reused by other tabs

### 2. GraphRAG
- Run graph retrieval against a local knowledge graph directory
- Optional "Mix with Cloud Text" adds hybrid retrieval with text indexes and rerank controls
- Displays CLI command, logs, and node preview table
- Stores the graph retrieval output path

### 3. Enhance
- Calls caliper_v2.commands.enhance.main to enrich a retrieval session
- Accepts context path (auto-filled from retrieval tab when available) and output path
- Produces success/failure alerts and updates the stored enhanced context path

### 4. Draft
- Load and save Markdown drafts with Windows-safe path handling
- Uses dcc.Store to remember the last draft path for other tabs

### 5. Generate
- Runs synthesize_from_context with provider/model overrides and optional style text
- Prefers tab-specific provider/model fields but falls back to selections stored in the sidebar
- Writes a Markdown draft, shows a 500-character preview, and surfaces alerts (including provider configuration issues)

### 6. Judge & Review
- Executes caliper_v2.commands.review.main to produce JSON + Markdown review outputs
- Supports strict mode toggle and max evidence per claim setting
- Displays review status and Markdown preview, and stores output paths for downstream use

## Cross-Tab State

The following stateful values persist as you move between tabs:
- Provider/model selection (store-provider, store-model)
- Retrieval, Graph, Enhance, Draft, and Review output paths
- Provider/model sync for the Generate tab

## Troubleshooting

- **Missing files**: Tabs return warning alerts without mutating state when input files are missing.
- **CLI errors**: Logs accordion contains stdout/stderr; commands execute with shell=False.
- **New file detection**: Retrieval callbacks look for newly created JSON files if the requested output name was renamed by the CLI.

## Related Resources
- [Developer Dash UI Guide](../developer/dash-ui-development.md)
- [Command Reference](../reference/command-reference.md)
