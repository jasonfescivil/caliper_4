# Caliper RAG Architecture

Service boundaries (conceptual)
- Provider config: caliper_v2/core/llm_providers.py
- CLI & UX: caliper_v2/cli.py (Typer-based)
- Persistence helpers: caliper_v2/services/persistence (IndexPathResolver, HashCache)
- Index artifacts: data_v2/indexes/<name> (FAISS storage + optional BM25 pickle)

Indexing & nodes
- Reader: LlamaIndex SimpleDirectoryReader; optional LlamaParse for PDFs (LLAMA_CLOUD_API_KEY required).
- Chunking: SimpleNodeParser.from_defaults(chunk_size, chunk_overlap).
- Embeddings: default OpenAI text-embedding-3-small; allow 'local' stub for offline smoke tests.
- Vector index: VectorStoreIndex.
- BM25: optional, built from same nodes; persisted as pickle.

Retrieval
- Modes: vector (default), bm25, hybrid (reciprocal rank fusion of vector and bm25 results).
- Reranking: optional Cohere Rerank if API key present.
- Metadata filters: source file, regulation, document type.

Persistence
- Vector index persisted to FAISS dir; BM25 retriever pickled separately.
- HashCache used to skip unchanged files during re-ingest.

Failure policy
- Missing OpenAI key: fail fast with clear instruction and offer explicit user choice to proceed with --embed-provider local when triggered interactively (future enhancement).
