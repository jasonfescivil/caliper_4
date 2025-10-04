# Caliper v2 Command Reference

This document provides a comprehensive reference for all Caliper v2 commands.

## Main Commands

### Help

Display help information for Caliper v2.

```powershell
poetry run caliper_v2 --help
```

### Retrieve

Retrieve information from specified indexes.

```powershell
poetry run caliper_v2 retrieve [OPTIONS] [QUESTION]
```

#### Key Options

- `--question-file PATH`: Read question from a file (shorthand: @file.md)
- `--indexes TEXT`: Comma-separated list of indexes to search (e.g., "federal,state,design_standards")
- `--cloud / --no-cloud`: Use LlamaCloud for retrieval
- `--top-k INTEGER`: Number of results to return (default: 20)
- `--dense-k INTEGER`: Number of dense retrieval results (cloud only)
- `--sparse-k INTEGER`: Number of sparse retrieval results (cloud only)
- `--alpha FLOAT`: Blend factor between dense and sparse (0.0-1.0, cloud only)
- `--cloud-rerank / --no-cloud-rerank`: Enable/disable server-side reranking (cloud only)
- `--rerank-top-n INTEGER`: Number of results to rerank (cloud only)
- `--reranker TEXT`: Reranker to use (local only, default: "cohere,st-mini" or "st-mini")
- `--out PATH`: Output file path for retrieval session JSON

#### Examples

```powershell
# Basic retrieval with a question string
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state" --cloud

# Retrieval with a question file
poetry run caliper_v2 retrieve --question-file prompts/q.md --indexes "federal,state,design_standards" --cloud --top-k 30

# Shorthand for question file
poetry run caliper_v2 retrieve @prompts/q.md --indexes federal

# Hybrid retrieval with tuning
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state,design_standards" --cloud --dense-k 12 --sparse-k 12 --alpha 0.5 --rerank-top-n 12
```

### Generate

Generate a response from a retrieval context.

```powershell
poetry run caliper_v2 generate [OPTIONS] CONTEXT_FILE
```

#### Key Options

- `--style TEXT`: Generation style (e.g., "strict-citation")
- `--out PATH`: Output file path for generated content

#### Examples

```powershell
poetry run caliper_v2 generate data_v2/context/file.json --style strict-citation
```

### Enhance

Transform retrieval_session JSON into enhanced_retrieval with additional features.

```powershell
poetry run caliper_v2 enhance [OPTIONS]
```

#### Key Options

- `--in PATH`: Input retrieval session JSON file
- `--out PATH`: Output enhanced retrieval JSON file
- `--write-outline / --no-write-outline`: Generate an outline
- `--rewrite-spore / --no-rewrite-spore`: Rewrite the global spore
- `--review-spores / --no-review-spores`: Review and rewrite per-node spores
- `--suggest-retrieve / --no-suggest-retrieve`: Suggest follow-up retrievals

#### Examples

```powershell
poetry run caliper_v2 enhance --in data_v2/context/file.json --out data_v2/context/enhanced.json --write-outline --rewrite-spore --review-spores --suggest-retrieve
```

### Judge

Assess a generated draft against retrieved context and emit a claim-level judgment report.

```powershell
poetry run caliper_v2 judge [OPTIONS]
```

#### Key Options

- `--context PATH`: Context file (retrieval_session or enhanced_retrieval JSON)
- `--generation PATH`: Generated content file
- `--out PATH`: Output judgment report JSON file
- `--strict / --no-strict`: Require stronger evidence to mark supported
- `--max-evidence-per-claim INTEGER`: Cap final evidence snippets per claim
- `--bm25-k INTEGER`: BM25 candidate pool size before blending
- `--embed-strategy TEXT`: Include embeddings in candidate selection
- `--per-source-cap INTEGER`: Limit candidate snippets per source before LLM adjudication
- `--claims-json PATH`: Optional pre-extracted claims

#### Examples

```powershell
poetry run caliper_v2 judge --context data_v2/context/enhanced.json --generation data_v2/outputs/draft.md --out data_v2/judgments/judgment.json --strict
```

### Review

Run a quick, lightweight review on a human-written draft section.

```powershell
poetry run caliper_v2 review [OPTIONS]
```

#### Key Options

- `--context PATH`: Context file (retrieval_session or enhanced_retrieval JSON)
- `--draft PATH`: Draft content file
- `--out-json PATH`: Output review report JSON file
- `--out-md PATH`: Output review report Markdown file
- `--strict / --no-strict`: Require stronger evidence to mark supported
- `--max-evidence-per-claim INTEGER`: Cap final evidence snippets per claim

#### Examples

```powershell
poetry run caliper_v2 review --context data_v2/context/file.json --draft data_v2/outputs/draft.md --out-json data_v2/reviews/review.json --out-md data_v2/reviews/review.md --strict --max-evidence-per-claim 5
```

### Doctor

Check the environment and configuration for potential issues.

```powershell
poetry run caliper_v2 doctor
```

### Info

Display information about the runtime environment.

```powershell
poetry run caliper_v2 info
```

## Graph Commands

### Graph Build

Build a local graph from a corpus folder of Markdown/CSV/XLSX.

```powershell
poetry run caliper_v2 graph build [OPTIONS]
```

#### Key Options

- `--corpus PATH`: Corpus directory
- `--out PATH`: Output directory for the graph
- `--table-max-rows INTEGER`: Maximum number of rows to include in tabular previews
- `--excel-all-sheets / --no-excel-all-sheets`: Ingest all sheets of Excel files

#### Examples

```powershell
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph
```

### Graph Retrieve

Retrieve from the graph to a retrieval_session JSON.

```powershell
poetry run caliper_v2 graph retrieve [OPTIONS] QUESTION
```

#### Key Options

- `--graph-dir PATH`: Graph directory
- `--out PATH`: Output file path for retrieval session JSON
- `--mix-with-text / --no-mix-with-text`: Mix graph context with cloud text retrieval
- `--text-indexes TEXT`: Comma-separated list of indexes for text retrieval
- `--top-k INTEGER`: Number of results to return
- `--rerank-top-n INTEGER`: Number of results to rerank

#### Examples

```powershell
# Basic graph retrieval
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --out data_v2/context/graph_ctx.json

# Mix graph with cloud text retrieval
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --mix-with-text --text-indexes design --top-k 40 --rerank-top-n 20 --out data_v2/context/graphmix_ctx.json
```

### Graph Export-Cloud

Export documents from LlamaCloud to a local Markdown corpus.

```powershell
poetry run caliper_v2 graph export-cloud [OPTIONS]
```

### Graph Build-Cloud

Build a KG from exported cloud documents.

```powershell
poetry run caliper_v2 graph build-cloud [OPTIONS]
```

### Graph Stats

Display statistics about the graph.

```powershell
poetry run caliper_v2 graph stats [OPTIONS]
```

## UI Commands

### Dash UI

Launch the Dash UI.

`powershell
poetry run python src\caliper_v2\ui_dash\app.py
`

