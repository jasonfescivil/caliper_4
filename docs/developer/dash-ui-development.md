# Caliper v2 Dash/Plotly UI Development Guide

This guide covers development and maintenance of the Dash/Plotly UI wrapper for Caliper v2.

## Overview

The Dash UI is a wrapper around the existing Caliper v2 CLI workflow. It orchestrates the Retrieve ? Enhance ? Draft ? Generate ? Judge & Review flow without changing business logic.

### Goals
- Provide a Dash/Plotly interface that mirrors Caliper CLI workflows
- Keep the UI as a thin layer: all heavy lifting remains in Caliper services and commands
- Support Windows-first ergonomics (paths, quoting, subprocess execution) and expose CLI transparency

### Current Status
- Entry point: src\caliper_v2\ui_dash\app.py
- Five production tabs: Retrieval, GraphRAG, Enhance, Draft, Generate, Judge & Review
- Cross-tab state managed with dcc.Store components for provider/model and output paths
- 60 automated tests in 	ests/ui_dash/ cover lifecycle, providers, Windows compatibility, retrieval/graph/enhance/draft/generate/review flows, state management, and end-to-end integration

## Architecture

### Framework & Components
- **Framework**: Dash 2.x + dash-bootstrap-components
- **Server**: Built-in Flask server provided by Dash
- **State management**: dcc.Store and tab switching via dcc.Tabs

### Backend Integration
- **Retrieval**: Windows-friendly CLI via windows_retrieve_command / windows_retrieve_argv
- **GraphRAG**: CLI wrapper that mixes text retrieval when requested
- **Enhance**: caliper_v2.commands.enhance.main
- **Generate**: caliper_v2.services.ui_api.synthesize_from_context
- **Judge & Review**: caliper_v2.commands.review.main
- **Environment**: Keys loaded through .env / settings during app startup

### File Structure
`
src/caliper_v2/ui_dash/
+-- app.py          # Dash application (layout + callbacks)
`

## Prerequisites

- Windows PowerShell
- Python 3.11–3.13
- Poetry
- Dependencies: dash, dash-bootstrap-components, and Caliper runtime deps (installed via Poetry)

## Setup and Installation

`powershell
poetry install
`

Create a .env file with required keys:
`
LLAMA_CLOUD_API_KEY=...
# Optional provider keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.
`

## Feature Parity

The Dash UI implements full CLI parity for:
- Cloud retrieval (text) with advanced options (retrieval mode, dense/sparse k, filters, HyDE, expand queries)
- GraphRAG retrieval with optional text mixing
- Context enhancement with outline/spore generation
- Draft editing (load/save) with Windows-safe paths
- Content generation with provider/model overrides and preview pane
- Judge & Review with strict mode, evidence caps, and Markdown preview

## Implementation Notes

### Windows Compatibility
- All filesystem inputs are sanitized via _clean_path_str
- Subprocess calls use argv lists (shell=False) and log command output
- Context directories (data_v2/context, outputs/) are resolved via _default_paths

### State Management
- Provider/model selections stored in store-provider / store-model
- Retrieval, graph, enhance, draft, and review outputs cached in dedicated stores
- Generate tab synchronizes provider/model when selected

### Error Handling
- Empty inputs return dbc.Alert warnings without mutating stores
- CLI/Subprocess failures surface stderr in the logs textarea
- File detection logic falls back to newest *.json in context directory when CLI renames outputs

### Performance Considerations
- CLI invocations run asynchronously from the UI event loop
- Node preview trims to 40 rows for responsive tables

## Testing Strategy

Automated coverage lives in 	ests/ui_dash/:
- Lifecycle, provider normalization, and Windows compatibility unit tests
- Retrieval, GraphRAG, Enhance, Draft, Generate, Review tab tests with heavy mocking
- State management tests verifying cross-tab store flow
- Integration tests chaining multiple tabs (e.g., retrieval ? enhance ? generate ? review)

Run tests with:
`powershell
poetry run pytest tests/ui_dash -q
`

## Deployment

Run the Dash server locally:
`powershell
poetry run python src/caliper_v2/ui_dash/app.py
`

The app listens on http://127.0.0.1:8050 by default.

## Related Documentation

- [Dash UI Guide](../user/dash-ui-guide.md)
- [Architecture Overview](architecture-overview.md)
- [Command Reference](../reference/command-reference.md)
