# UI Parity Flags — Retrieval and Graph

This document enumerates advanced CLI flags that the Dash UI should expose (pass-through) for full parity.

Retrieval (cloud text)
- --indexes "federal,state,design_standards"
- --top-k INT
- --reranker cohere|none
- --reranker-top-n INT
- --out PATH
- --dense-k INT
- --sparse-k INT
- --alpha FLOAT(0..1)
- --retrieval-mode chunks|files_via_content|files_via_metadata|auto_routed
- --include-terms "comma,separated,terms"
- --exclude-sections "toc,glossary,references,figures"
- --filters '{"jurisdiction":"WA","chapter":"G1"}'
- --infer-filters
- --expand-queries INT
- --hyde / --no-hyde
- --cloud
- --llm-provider PROVIDER (global flags passed to CLI)
- --llm-model MODEL (global flags passed to CLI)

Graph retrieve
- question (positional)
- --graph-dir PATH
- --hops INT (0..2)
- --limit INT
- --out PATH
- --mix-with-text
- --text-indexes "design,state,federal"
- --top-k INT (text)
- --rerank-top-n INT (text)
- --provider PROVIDER (rerank)
- --model MODEL (rerank)

Notes
- The UI should only include flags the user explicitly sets; otherwise default to backend defaults.
- Generated command strings should show the exact flags used for transparency.
