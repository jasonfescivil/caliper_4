# Caliper v2 — Code Review and Current Capabilities (2025-09-23)

## Overview

Caliper v2 is a Python 3.11–3.13 project organized around a CLI-first workflow, with a Dash/Plotly UI wrapper complementing the CLI. It supports two primary retrieval modes:
- Cloud text retrieval via LlamaCloud across multiple logical indexes (federal, state, design_standards, etc.).
- Local GraphRAG over a persisted KnowledgeGraphIndex built from a local corpus of Markdown/CSV/XLSX, with optional union to cloud text retrieval followed by lightweight reranking.

The end-to-end workflow follows: retrieve → enhance → generate → judge → review. The UIs are pure wrappers around the same business logic used by the CLI.

## Key Components and Findings

### 1) CLI entrypoint (src/caliper_v2/cli.py)
- Provides the main commands, including retrieve, generate, judge, review, and auxiliary utilities.
- Loads .env early to ensure provider keys are available.
- Offers extensive options for cloud retrieval, including hybrid parameters (dense/sparse, alpha), server-side reranking, lexical includes, and post-processing. Defaults are sensible and guardrails exist (e.g., provider defaults and warnings for incorrect models).
- Implements "spore" generation: a single LLM call to summarize why the retrieval set is coherent and relevant. Also supports per-node spore when enabled.
- Cohere/OpenAI integration via LlamaIndex Settings is present (embeddings and LLM selection where applicable).

### 2) GraphRAG commands (src/caliper_v2/commands/graph_cli.py)
- Sub-CLI for graph operations: build, retrieve, export-cloud, build-cloud, stats.
- graph build:
  - Ingests Markdown, CSV, and XLSX from a corpus directory.
  - Exposes tabular controls: table_max_rows, excel_all_sheets, and table_rows_strategy (head/tail/head_tail/sample/all).
  - Persists a graph (manifest.json, hash cache, storage).
- graph retrieve:
  - Loads the persisted graph; finds candidate entities from query; expands neighbors up to hops (0–2 typical); hydrates back to text nodes.
  - Optional mix_with_text to fetch cloud text and union with graph nodes; optional LLM-based rerank of the union.
  - Outputs a retrieval_session JSON compatible with the rest of the workflow.
- export-cloud and build-cloud:
  - Export documents from LlamaCloud to a local Markdown corpus and optionally build a KG from it. Useful for reproducible, local GraphRAG experiments.

### 3) Graph builder (src/caliper_v2/graph/builder.py)
- Purpose: construct a knowledge graph from local corpus content.
- Highlights:
  - Supports CSV/XLSX ingestion with per-sheet Markdown previews and metadata. Columns are normalized and units are parsed from headers like "(mgd)".
  - Tabular controls: as_table_markdown, table_max_rows, excel_all_sheets, table_rows_strategy; strategy supports head/tail/head_tail/sample/all for scalable previews.
  - Entity detection: heuristics for acronyms and title-cased phrases with stopword filtering; frequency thresholds and caps to avoid explosion.
  - Relation extraction: heuristic co-occurrence between entities within sections; MENTIONS edges from sections to entities; DEFINED_IN reverse links.
  - LlamaIndex integration:
    - Builds Documents from sections and constructs a KnowledgeGraphIndex without invoking LLM triplet extraction (no-op extractor), then upserts heuristic edges.
    - Persist/resume with progress and a file hash cache for incremental builds.
  - Embeddings: attempts to configure Cohere embeddings if available (graceful fallback).
- Outputs: manifest.json with stats; docstore/graph store; file hash cache; build progress.

### 4) Graph schema (src/caliper_v2/graph/schema.py)
- Defines data classes for EntityNode, SectionNode, GraphEdge, EntityMention, GraphMetadata.
- Enumerates relation and extractor types.
- Provides to_dict for GraphMetadata so manifest.json is structured and versioned.

### 5) Graph retriever (src/caliper_v2/retrievers/graph_retriever.py)
- Loads the stored KnowledgeGraphIndex from a persist dir.
- Robustly selects the correct KG from index_store.json variants.
- Simple query entity detection (ALLCAPS and Title Case → canonical forms), then neighbor expansion and hydration back to text snippets shaped like Caliper nodes.
- Supports limit caps and tolerates multiple LlamaIndex versions.

### 6) LlamaCloud wrapper (src/caliper_v2/services/llama_cloud_index.py)
- Thin wrapper for the official llama-cloud-services SDK; reads LLAMA_CLOUD_API_KEY and optional base URL.
- as_retriever forwards hybrid parameters; retrieve uses as_retriever().

### 7) Dash UI
- Dash wrapper lives at src\caliper_v2\ui_dash\app.py and invokes the existing command adapters.

### 8) Dash/Plotly UI
- README and docs state an alternative Dash UI: src\caliper_v2\ui_dash\app.py, with a dedicated runbook at docs/dash_ui.md.
- Finding: src\caliper_v2\ui_dash\app.py is currently not present in the repository, while docs and README reference it. The docs/dash_ui.md describes intended behavior and usage, implying this UI is planned or existed previously but is currently missing. This is the primary gap preventing Dash usage "as-is".

## Security and Config
- .env is git-ignored; load_env is called early; provider keys are read from environment.
- README warns about unsafe model names and explains provider defaults.

## Windows-first ergonomics
- CLI examples and paths are Windows-safe (PowerShell). The graph CLI mix step uses a windows_retrieve_argv helper for proper quoting/args.

## Current Capabilities Summary
- Retrieval
  - Cloud: hybrid dense/sparse with tunable k and alpha, server-side rerank.
  - Graph: local KG from Markdown/CSV/XLSX with sheet metadata; union with cloud and local rerank when configured.
- Enhance
  - Adds outline, diagnostics, a rewritten spore, and per-node spore reviews; also suggests follow-up retrievals.
- Generate
  - Consumes retrieval_session or enhanced_retrieval JSON; generation styles supported in UIs.
- Judge
  - Claim-level adjudication with evidence; configurable caps, embedding strategy, strictness.
- Review
  - Combines judge metrics, deterministic text lints, and a readable Markdown report for engineers.

## Notable Strengths
- Clear separation between business logic (CLI/services) and UI wrappers.
- Reproducibility via persisted retrieval context, enhanced context, and build manifests.
- Practical graph ingestion improvements for tabular engineering data.
- Cloud/local blending allows richer contexts while remaining verifiable.

## Limitations / Risks
- Dash UI missing code: README/docs reference a Dash app that is not present, blocking immediate Dash use.
- Graph relation extraction is heuristic-only; LLM triplet extraction is not implemented (placeholder). This is acceptable for MVP but limits graph semantics.
- Entity detection is heuristic and may over/under-detect; MIN_FREQUENCY tuning may be needed per corpus.
- Rerank quality depends on provider availability (Settings.llm must be configured) and simplified scoring prompts.
- Advanced doc types (PDF with layout, figures) are not handled in the local graph ingest pathway; the cloud path covers these via LlamaCloud.

## Opportunities
- Maintain the Dash app scaffold and reuse the existing command adapters.
- Add a compact entity browser and per-source sheet/column filters in the graph retrieval view.
- Optional LLM triplet extraction for graph enrichment under a strict budget.
- Add a simple KG visualization (Plotly) with evidence drilldown.

## Action Items (short)
- Documented below in the companion plan (docs/dash_ui_functional_plan.md) how to bring the Dash UI to full parity and beyond, with impact/risk/time/report-writing ratings per function.
- Consider adding an existence check in README/Dash runbook noting the current absence of src\caliper_v2\ui_dash\app.py until it is reintroduced.