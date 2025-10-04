# Caliper Retrieval Techniques & Cohere Integration Analysis

## Executive Summary

Caliper implements a **hybrid, multi-modal retrieval architecture** with extensive **Cohere integration** throughout the retrieval and reranking pipeline. The system supports both local and cloud-based retrieval with sophisticated fallback mechanisms.

---

## 1. Core Retrieval Techniques

### 1.1 Vector Search (Semantic Retrieval)
- **Implementation**: Via LlamaIndex's VectorStoreIndex
- **Embedding Provider**: Cohere `embed-v4.0` (primary)
  - Location: `cli_main.py:896-922`
  - Model: `CohereEmbedding(model="embed-v4.0", input_type="search_document")`
  - Batch processing: Configurable via `CALIPER_EMBED_BATCH` (default: 64)
  - Fallback: Local tiny embeddings for offline/smoke testing

### 1.2 BM25 (Lexical/Sparse Retrieval)
- **Custom Implementation**: `judge_components.py:89-136`
  - Pure Python BM25 with configurable k1=1.5, b=0.75
  - IDF computation with smoothing
  - Tokenization with stopword filtering
- **Usage Contexts**:
  - Local retrieval when persistence is enabled
  - "BM25-lite" post-processing of cloud candidates (`--cloud-bm25-lite`)
  - Evidence ranking in judgment components

### 1.3 Hybrid Search
- **Default Mode**: `--search-mode hybrid` (`cli_main.py:2209`)
- **Two Implementations**:
  1. **Local Hybrid** (RRF or Alpha-blend):
     - RRF (Reciprocal Rank Fusion): Default
     - Alpha-blending: Optional via `--use-alpha` flag
     - Configurable dense_k and sparse_k parameters
  
  2. **Cloud Hybrid** (LlamaCloud):
     - Server-side hybrid with configurable alpha (0-1)
     - `dense_similarity_top_k` and `sparse_similarity_top_k` parameters
     - Retrieval modes: chunks, files_via_content, files_via_metadata, auto_routed

### 1.4 Graph-Based Retrieval
- **Implementation**: `retrievers/graph_retriever.py`
- **Technique**: Entity-centric graph traversal
  - Entity detection: Title-cased and ALLCAPS tokens
  - Hop-based expansion (default: 1 hop, max 200 nodes)
  - Knowledge Graph Index from LlamaIndex
- **Fallbacks**:
  - Keyword fallback for specific domains (DMR, I&I queries)
  - File-preference heuristics
  - Arbitrary node sampling when no matches

### 1.5 Query Expansion
- **HyDE (Hypothetical Document Embeddings)**:
  - Enabled by default: `--hyde` flag
  - Location: `cli_main.py:2334-2356`
  - Generates hypothetical answer documents for semantic expansion

- **Multi-Query Expansion**:
  - Uses `MultiParagraphQueryTransform` (4 queries)
  - Location: `cli_main.py:2315-2332`
  - Controlled by `CALIPER_CLOUD_USE_MULTI` env var

### 1.6 Metadata Filtering
- **Filter Inference**: Schema-driven automatic filter inference
  - Flag: `--infer-filters` (enabled by default)
  - JSON filter support: `--filters '{"jurisdiction":"WA"}'`
- **Section Exclusion**: 
  - Default drop: TOC, references, glossary, figures, exhibits
  - Custom: `--exclude-sections` flag

---

## 2. Cohere Integration (Extensive)

### 2.1 Embeddings
**Primary Role**: Document and query embedding generation

**Implementation**:
```python
# cli_main.py:896-922
CohereEmbedding(
    model="embed-v4.0",
    input_type="search_document",
    api_key=cohere_key,
)
```

**Features**:
- Batch processing support (64 docs/batch)
- Search document input type optimization
- Explicit API key passing
- Used for both indexing and query-time retrieval

### 2.2 Reranking (Multi-Level)

#### A. Node-Level Reranking
**Location**: `cli_main.py:2528-2541`

**Implementation**:
```python
from llama_index.postprocessor.cohere_rerank import CohereRerank
rerank_model = os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.5")
rr = CohereRerank(top_n=final_keep, model=rerank_model)
rescored = rr.postprocess_nodes(fused, query_str=question)
```

**Features**:
- Model: `rerank-english-v3.5` (configurable via env var)
- Score-based filtering: `--rerank-min-score` (default: 0.5)
- Automatic fallback to Sentence Transformers if Cohere fails

#### B. Group-Aware Reranking
**Location**: `cli_main.py:2547-2689`

**Chain Configuration**: `--cloud-reranker-chain cohere,st-mini,llm`

**Implementation Details**:
- **Groups** formed by: (parent_id, file_name, section)
- **Representative text** generation (max 2000 chars/group)
- **Cohere rerank** applied to group representative texts
- **Confidence scores** attached to individual nodes in groups
- **Metadata enrichment**: `rerank_confidence` field added

**Sophisticated Features**:
- Preserves document structure
- Applies reranking at section/document level
- Falls back to Sentence Transformer mini models
- Maintains node order within groups

#### C. BM25-Lite Post-Processing
**Location**: `cli_main.py:2691-2732`

**Purpose**: Apply lightweight lexical scoring over cloud retrieval results

**Flow**:
1. Extract clean text from cloud candidates
2. Build BM25 index from candidate pool
3. Score candidates against query
4. Filter by `--bm25-lite-min-score` threshold
5. Preserve high-scoring candidates

---

## 3. Retrieval Architecture

### 3.1 Multi-Index Routing
**Pattern**: Retrieve from multiple indexes, then fuse

**Implementation** (`cli_main.py:2265-2507`):
1. **Per-Index Retrieval**:
   - Parallel retrieval from: federal, state, design_standards
   - Each index: base + summary indices (2-tier hierarchy)
   
2. **Summary-First Strategy** (`_sfirst_retrieve`):
   - Query summary index first (smaller, faster)
   - Use results to select relevant sections
   - Retrieve detailed chunks from base index
   - Per-group sampling for diversity

3. **Cross-Index Fusion**:
   - Deduplicate by passage_id
   - Merge scores and metadata
   - Apply unified reranking

### 3.2 Cloud vs Local Routing
**Decision Logic** (`cli_main.py:2272-2283`):
- **Cloud Mode**: If `LLAMA_CLOUD_API_KEY` exists AND at least one index has cloud IDs
- **Local Mode**: Fallback when cloud unavailable
- **Explicit Override**: `--cloud` or `--local` flags

**LlamaCloud Features**:
- Server-side hybrid search
- Server-side reranking (optional)
- File-level and chunk-level retrieval modes
- Filter inference
- Advanced retrieval parameters (dense_k, sparse_k, alpha)

### 3.3 Diversity Mechanisms

#### MMR (Maximal Marginal Relevance)
**Location**: `cli_main.py:2720-2747`

**Purpose**: Reduce redundancy in retrieved results

**Algorithm**:
- Compute pairwise similarity between candidate embeddings
- Iteratively select candidates that maximize:
  - Relevance to query (high similarity)
  - Novelty relative to already-selected (low similarity)
- Lambda parameter controls relevance/diversity tradeoff

#### Per-Group Sampling
**Location**: `cli_main.py:2428-2500`

**Strategy**:
- Group results by (file, section)
- Sample up to N per group (default: 18)
- Ensures diverse source coverage
- Prevents single-file domination

---

## 4. Cohere API Utilization Matrix

| Component | Cohere Product | Model | Purpose | Fallback |
|-----------|---------------|-------|---------|----------|
| **Embeddings** | Embed | `embed-v4.0` | Index & query embedding | Local tiny embeddings |
| **Node Rerank** | Rerank | `rerank-english-v3.5` | Initial candidate reranking | Sentence Transformers |
| **Group Rerank** | Rerank | `rerank-english-v3.5` | Section-level reranking | ST-mini → LLM |
| **Evidence Rerank** | Rerank | `rerank-english-v3.5` | Claim evidence scoring | BM25 + embeddings |

**API Key Management**:
- Environment variable: `COHERE_API_KEY`
- Explicit key passing to avoid env resolution issues
- Graceful degradation when key missing

---

## 5. Advanced Retrieval Features

### 5.1 Context Spore Generation
**Location**: `cli_main.py:2037-2196`

**Purpose**: LLM-generated retrieval justification

**Components**:
- **Summary**: High-level retrieval rationale
- **Rationale bullets**: Specific reasons for relevance
- **Confidence score**: 0.0-1.0 quality estimate

**Per-Node Spores**:
- Optional: `--node-spore` flag
- Individual justifications for each retrieved chunk
- Heuristic fallback when LLM unavailable
- Generic phrase detection and replacement

### 5.2 Trace & Monitoring
**Flag**: `--trace`

**Output**: `.trace.json` with:
- Elapsed time metrics
- Candidate counts at each stage
- Reranking scores
- Filter effectiveness

### 5.3 Citation Enrichment
**Location**: `cli_main.py:2733-2767`

**Features**:
- Extracts structured citations from retrieved nodes
- Groups by (file, page, section)
- Preserves source metadata for generation phase
- Supports inline citation rendering

---

## 6. Retrieval Technique Completeness

| Technique | Implementation Status | Depth | Notes |
|-----------|---------------------|-------|-------|
| **Vector (Dense)** | ✅ Complete | Full | Cohere embed-v4.0, batch processing |
| **BM25 (Sparse)** | ✅ Complete | Full | Custom impl, tunable parameters |
| **Hybrid (Dense+Sparse)** | ✅ Complete | Full | RRF & alpha-blend modes |
| **Reranking** | ✅ Complete | Full | Multi-stage, group-aware, fallbacks |
| **Query Expansion** | ✅ Complete | Full | HyDE + Multi-query |
| **Graph Traversal** | ✅ Complete | Partial | Entity-based, 1-hop, keyword fallback |
| **MMR Diversity** | ✅ Complete | Full | Embedding-based similarity reduction |
| **Metadata Filtering** | ✅ Complete | Full | Schema-driven, inference support |
| **Hierarchical Routing** | ✅ Complete | Full | Summary-first, 2-tier indices |

---

## 7. Cohere-Specific Optimizations

### 7.1 Input Type Specification
```python
CohereEmbedding(
    model="embed-v4.0",
    input_type="search_document",  # Optimizes for retrieval
    ...
)
```

### 7.2 Rerank Model Selection
- Default: `rerank-english-v3.5` (latest multilingual)
- Configurable: `COHERE_RERANK_MODEL` env var
- Automatic API key detection and validation

### 7.3 Batch Processing
- Embeddings: 64 documents/batch (configurable)
- Reduces API calls and latency
- Automatic batching via LlamaIndex integration

### 7.4 Error Handling & Fallbacks
**Pattern**: Try Cohere → ST-mini → LLM → Heuristic

**Example**:
```python
try:
    # Cohere rerank
    rescored = CohereRerank(...).postprocess_nodes(...)
except Exception:
    # Fallback to Sentence Transformers
    rescored = _st_rerank_nodes(..., model_key="st-mini")
```

---

## 8. Key Findings

### Strengths
1. **Deep Cohere Integration**: Embeddings + reranking across entire pipeline
2. **Sophisticated Fallbacks**: Multiple levels of degradation
3. **Group-Aware Reranking**: Maintains document structure during reranking
4. **Hybrid Flexibility**: Multiple fusion strategies (RRF, alpha-blend)
5. **Query Expansion**: HyDE + multi-query for recall improvement
6. **Diversity Mechanisms**: MMR + per-group sampling

### Gaps
1. **Cohere Rerank API v2**: Not yet using latest v2 features (relevance signals, structured output)
2. **Cohere Command**: No usage of Cohere's generative models for retrieval augmentation
3. **Cohere Chat API**: Not leveraging conversational retrieval patterns
4. **Fine-tuned Embeddings**: No custom embedding model training

### Recommendations
1. **Upgrade to Rerank API v2**: Access relevance signals and document-level scoring
2. **Add Cohere Command-R**: Use for query reformulation and context synthesis
3. **Implement Cohere RAG Connector**: Leverage native RAG capabilities
4. **Add Cohere Classify**: For query intent classification and routing
5. **Enable Cohere Streaming**: For real-time reranking in interactive UIs

---

## 9. Code References

### Primary Files
- **`cli_main.py`**: Main retrieval command (lines 2199-2885)
- **`judge_components.py`**: BM25, embeddings, evidence ranking
- **`llm_providers.py`**: Cohere LLM and embedding configuration
- **`graph_retriever.py`**: Graph-based retrieval
- **`llama_cloud_retriever.py`**: Cloud retrieval wrapper

### Configuration
- **Embeddings**: `COHERE_API_KEY`, `CALIPER_EMBED_BATCH`
- **Reranking**: `COHERE_RERANK_MODEL`, `CALIPER_CLOUD_RERANKER_CHAIN`
- **Query Expansion**: `CALIPER_CLOUD_USE_MULTI`, `CALIPER_CLOUD_USE_HYDE`

---

## Conclusion

Caliper implements a **production-grade, Cohere-centric retrieval system** with:
- Full vector, sparse, and hybrid search capabilities
- Multi-stage reranking with Cohere Rerank v3.5
- Sophisticated fallback mechanisms
- Query expansion (HyDE + multi-query)
- Diversity mechanisms (MMR + sampling)
- Group-aware reranking for structural preservation

The Cohere integration is **extensive and well-architected**, with proper error handling, batching, and optimization. The system demonstrates advanced RAG engineering with clear separation of concerns and multiple layers of quality control.
