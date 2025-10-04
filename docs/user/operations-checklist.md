# Caliper v2 Operations Checklist

## Cold-start (Windows/Poetry)

- **Install Poetry and env** (see [README.md](../../README.md))
  - Python 3.11 recommended (supports 3.12/3.13 too)
  - Install Poetry via pipx
  
- **Create .env file**
  - Copy `.env.example` → `.env`, fill in API keys
  - Minimal useful variables:
    - `LLAMA_CLOUD_API_KEY` (for cloud retrieval)
    - `COHERE_API_KEY` (for reranking, optional)
    - Provider keys as needed (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`)
  
- **Build environment**
  ```powershell
  poetry env use 3.11
  poetry install --with llamaindex
  ```
  
- **Materialize indexes (local)**
  ```powershell
  poetry run caliper_v2 ingest knowledge_base --index design_standards --persist --bm25-pickle
  ```
  
- **Cloud index IDs** (if using cloud)
  - Set these variables in your `.env` file:
    - `FEDERAL_BASE_ID`, `FEDERAL_SUMMARY_ID`
    - `STATE_BASE_ID`, `STATE_SUMMARY_ID`
    - `DESIGN_BASE_ID`, `DESIGN_SUMMARY_ID`

## Daily Operations

- **Ingest new documents**
  ```powershell
  poetry run caliper_v2 ingest <folder-or-file> --index <n> --persist --bm25-pickle
  ```
  - HashCache ensures idempotence (services/persistence.HashCache)
  
- **Re-index rules**
  - Re-run ingest when files change (force with `--force` to bypass cache)
  
- **Verify index freshness**
  - Check timestamps under `data_v2/indexes/<index>` (faiss/, bm25_index.pkl)

## Smoke Tests

Run these standard queries to verify system functionality:

### Cloud Standard (G1)
```powershell
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state,design_standards" --cloud --dense-k 12 --sparse-k 12 --alpha 0.5 --rerank-top-n 12 --out data_v2/context/g1_cloud.json
```

### Local Design
```powershell
poetry run caliper_v2 retrieve "Infiltration basin drawdown criteria" --indexes design_standards --search-mode hybrid --top-k 60 --reranker st-mini --out data_v2/context/drawdown_local.json
```

### Graph Mixed
```powershell
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph
poetry run caliper_v2 graph retrieve "Define peak hour factor" --graph-dir data_v2/graph --out data_v2/context/graph_ctx.json
```

## Diagnostics

When troubleshooting retrieval results:

- **CLI flags**
  - `--verbose` to enable more logs
  - `--exclude-sections` to drop toc/glossary/etc.
  - `--filters JSON` and `--infer-filters` (cloud)
  
- **Dump retrieved contexts**
  - Retrieval already writes JSON to `data_v2/context/*.json`
  - Inspect fields: id, score, metadata
  
- **Token/latency stats**
  - Not captured by default
  - Consider enabling structured logging around LLM calls

## One-command Trace Reproduction

Use the helper script to run environment/deps, static sweep, and runtime traces:

```powershell
scripts\review_capture.ps1
```

Outputs go to `.artifacts/review-junie/<timestamp>/`

## Observability & Ops Notes

- **Logging**
  - Uses loguru for logging
  - Colored CLI output via typer
  - Consider adding JSON logs with time, stage, latency
  
- **Reproducibility**
  - Settings extra fields allowed (core/config.py)
  - Record key flags and env keys used in the context JSON's source block when possible

## Executive Summary

1. Use ingest → retrieve → generate → judge sequence; each stage writes durable artifacts under data_v2/.
2. The review_capture.ps1 script captures transcripts for quick audits.
3. Prefer cloud hybrid with cautious rerank; local path works fully offline (st-mini rerank).
4. Smoke tests cover standards, design criteria, and graph lookup.
5. Add structured logging around retrieval/rerank/LLM for future latency/token tracking.

## 90-day Roadmap

- **Now**
  - Land review_capture.ps1 and document flags
  - Enable --verbose in smoke scripts
  
- **Next**
  - Add timing and token counters to context JSON
  - Add log retention policy
  
- **Later**
  - Integrate basic metrics (Prometheus/OpenTelemetry)
  - Add trace IDs across stages