<!-- AUTO-GENERATED FROM .ide/rules/05-indexing-retrieval.md | Do not edit here. -->
<!-- Edit .ide/rules/*.md and run scripts/sync_ide_rules.py -->

# Indexing & Retrieval Details

Ingest
- Input: directory path (recursive). LlamaParse used only if LLAMA_CLOUD_API_KEY present.
- Metadata enrichment: extract basic regulatory markers (CFR/WAC/RCW), agency hints, year.
- HashCache avoids re-processing unchanged files (when available).
- Persistence: FAISS vector index + optional BM25 pickle per index.

Query
- Single-index selection for now (wizard narrows to one index when multiple are chosen).
- Retrieval budget controlled by --top-k; hybrid mode fuses vector+bm25 with Reciprocal Rank Fusion.
- Optional reranking via Cohere when COHERE_API_KEY is present (--reranker cohere).
- Response synthesis: TreeSummarize with citation format.

Filters
- source_filter: filters by file_path substring
- regulation_filter: maps to cfr_parts/wac_sections/rcw_sections/regulation metadata
- doc_type_filter: federal | state | technical | guidance (lowercase values)

Reranking
- Cohere Rerank enabled when COHERE_API_KEY is present; model "rerank-english-v3.0".

HyDE & expansion
- HyDE requires active LLM; generated hypothetical doc used as additional query.
- Query expansion can be interactive or automatic.
