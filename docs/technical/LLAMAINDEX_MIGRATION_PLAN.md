# LlamaIndex Migration Comprehensive Plan

> Packaging Decision: Option 1 (Single Poetry project with optional llamaindex group and a separate `caliper_v2` console script). LlamaIndex is installed only when explicitly requested via Poetry group; v1 remains default and unaffected.

## 🎯 Migration Overview

**Goal**: Migrate Caliper from custom RAG to LlamaIndex while maintaining 100% backward compatibility
**Timeline**: 2–3 weeks (accelerated; Option 1 packaging and v2 scaffolding completed within hours)
**Risk Level**: Medium (mitigated by two-system approach and hybrid mode)
**Scope**: Incremental adoption with hybrid mode (run LlamaIndex in shadow for select queries)
**Estimated Costs**: Track LLM API usage (budget target: ≤ $500 for testing); monitor via LlamaIndex observability/evaluation tools

---

## 📋 Phase Completion Criteria

### Phase 1: Environment Setup ✅
Packaging: Option 1 (single project) with optional Poetry group "llamaindex" and a new console script `caliper_v2`.

Accelerated Outcome:
- Completed within a day: pyproject group, caliper_v2 CLI scaffold, CI v2 smoke lane, quickstart, and doc updates.

**Definition of Done**:
- [x] LlamaIndex dependencies isolated under `[tool.poetry.group.llamaindex]` (installed via `poetry install --with llamaindex`)
- [x] `caliper_v2` CLI available (`poetry run caliper_v2 --help`)
- [x] Proof of concept runs successfully using LlamaIndex (5-line ingestion/query) through `caliper_v2` commands
- [ ] Performance baseline established for v1 (latency, throughput, memory, retrieval accuracy)
- [ ] Test data corpus prepared (min 50 documents incl. complex tables/images via LlamaParse)
- [ ] Monitoring & evaluation ready (enable LlamaIndex observability/evals; Prometheus exporters)

**Validation**:
```bash
# Install v2 stack side-by-side
poetry install --with llamaindex

# Inspect v2 CLI
poetry run caliper_v2 --help
poetry run caliper_v2 info

# Run quickstart POC via v2 CLI (in-memory demo)
poetry run caliper_v2 ingest knowledge_base --index demo
poetry run caliper_v2 query "What does the demo document say?"

# Optional: run validation script
python validate_phase1.py
# Should output: All checks passed ✓
```

**Validation**:
```bash
# Run validation script
python validate_phase1.py
# Should output: All checks passed ✓
```

### Phase 2: Service Layer Replacement 🔄
**Definition of Done**:
- [ ] DocumentService processes all v1 formats + 12 new formats (LlamaHub/LlamaParse where applicable)
- [ ] RAGService returns results within 10% of v1 on relevance/faithfulness (evals-based)
- [ ] LLMService supports all v1 providers + 5 new ones; preserves prompt compatibility
- [ ] Unit tests ≥ 80% for fast-suite; critical-path code ≥ 95%; integration tests passing
- [ ] Hybrid mode implemented: LlamaIndex runs in shadow, parity logged with IDs and metrics

**Validation**:
```bash
# Compare outputs with semantic evals
python compare_services.py --tolerance 0.1 --semantic --faithfulness --relevancy
# Should show: All services within tolerance ✓ and eval scores within 10% of v1
```

### Phase 3: Integration and Testing 🧪
Note: With Option 1, v2 runs as a separate CLI (`caliper_v2`) during migration; we will add `--engine` only when promoting v2 pathways into v1 ergonomics.

Accelerated Scheduling:
- Phase 2 targeted duration: ~7–10 days (parallelizable tasks for RAGService/LLMService with stubs).
- Phase 3 targeted duration: ~3–5 days after Phase 2 milestones hit.

**Definition of Done**:
- [ ] 100% of v1 commands work with v2 engine; --engine flag and auto-selection implemented
- [ ] Performance improvement > 20% vs v1 on p95 latency; retrieval accuracy ≥ 95% target
- [ ] Error rate < v1 baseline; evaluation scores stable (±10%)
- [ ] Fallback & circuit breaker validated under load; hybrid mode SxS burn-in complete
- [ ] UAT complete; documentation updated with LlamaIndex-specific guides

**Validation**:
```bash
# Full system test
python run_migration_tests.py --comprehensive
# Should show: All 150 tests passed ✓
```

### Phase 4: Production Transition 🚀
**Definition of Done**:
- [ ] v2 as default for 2 weeks without critical issues
- [ ] Performance metrics meet SLAs
- [ ] Documentation fully updated
- [ ] v1 code archived but accessible
- [ ] Team trained on new system

---

## 🧪 Testing Framework

### RAG-Specific Evals (New)
- Retrieval accuracy: hit rate / MRR using LlamaIndex evaluators
- Faithfulness and hallucination checks
- Semantic similarity parity vs v1 outputs
- Reranker A/B: BM25+embedding vs LlamaIndex rerankers (e.g., Cohere/OpenAI)

### Test Categories

1. **Unit Tests** (per service)
   - Input/output validation
   - Error handling
   - Edge cases

2. **Integration Tests**
   - End-to-end workflows
   - Multi-service interactions
   - Database consistency

3. **Regression Tests**
   - v1/v2 output comparison
   - Performance benchmarks
   - Accuracy metrics

4. **Load Tests**
   - Concurrent operations
   - Memory usage
   - Response times

### Test Data Management
```
test_data/
├── documents/           # Various format test files
│   ├── simple/         # Basic test cases
│   ├── complex/        # Tables, images, etc.
│   └── edge_cases/     # Corrupted, huge files
├── queries/            # Test questions
│   ├── factual.json    # Simple lookups
│   ├── analytical.json # Complex reasoning
│   └── regulatory.json # Domain-specific
└── expected/           # Expected outputs
    ├── v1_baseline/    # Current system outputs
    └── v2_results/     # New system outputs
```

---

## 📊 Performance Benchmarks

Add metric: Retrieval Accuracy (v1 Baseline: 85%, v2 Target: 95%, v2 Stretch: 97%)

| Operation | v1 Baseline | v2 Target | v2 Stretch |
|-----------|-------------|-----------|------------|
| Document Load (PDF) | 5s | 3s | 2s |
| Simple Query | 2s | 1.5s | 1s |
| Complex Query (CoT) | 10s | 8s | 6s |
| Template Generation | 15s | 12s | 10s |
| Memory per Document | 50MB | 30MB | 20MB |
| Retrieval Accuracy | 85% | 95% | 97% |

### Target Metrics

| Operation | v1 Baseline | v2 Target | v2 Stretch |
|-----------|-------------|-----------|------------|
| Document Load (PDF) | 5s | 3s | 2s |
| Simple Query | 2s | 1.5s | 1s |
| Complex Query (CoT) | 10s | 8s | 6s |
| Template Generation | 15s | 12s | 10s |
| Memory per Document | 50MB | 30MB | 20MB |

### Monitoring Dashboard
```python
# Real-time metrics tracking
metrics = {
    "response_time": [],
    "accuracy_score": [],
    "fallback_rate": [],
    "error_rate": [],
    "memory_usage": [],
    "cpu_usage": []
}
```

---

## 🔄 Data Migration Strategy

### Vector Store Migration

Preferred: Wrap existing Weaviate store with LlamaIndex integration to avoid full export/import.

```python
# Integrate existing Weaviate with LlamaIndex (preferred)
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import VectorStoreIndex

def integrate_weaviate(weaviate_client):
    vector_store = WeaviateVectorStore(weaviate_client=weaviate_client)
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(similarity_top_k=5)
    return query_engine
```

Fallback: If full migration is required, use advanced chunking and validate integrity.

```python
def migrate_vectors():
    weaviate_data = export_weaviate_vectors()
    from llama_index.core.node_parsers import SentenceSplitter
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=128)
    llama_data = transform_to_llamaindex(weaviate_data, node_parser=splitter)
    validate_vector_integrity(weaviate_data, llama_data)
    import_to_llamaindex(llama_data)
```

### Document Metadata Preservation
- Maintain all v1 metadata fields; add `node_id`, `chunk_id`, `parent_id` where applicable
- Record `chunk_size`, `chunk_overlap`, `splitter` in metadata for auditability
- Create mapping table v1 ↔ v2; add migration tests to verify round-trip integrity

---

## 🚨 Rollback Plan

### Immediate Rollback (< 1 hour)
```bash
# Switch default engine back to v1
export DEFAULT_ENGINE=v1
# or
poetry run caliper set-engine v1 --persist
```

### Full Rollback (< 1 day)
1. Restore v1 as default in config
2. Archive v2 code to separate branch
3. Restore v1 dependencies
4. Notify users of temporary rollback
5. Document issues for resolution

### Rollback Triggers
- Error rate > 5% increase
- Performance degradation > 50%
- Evaluation score drop > 10% (faithfulness/relevancy)
- Data corruption detected
- Critical business logic failure

---

## 🔍 Validation Criteria

### Service-Level Validation

#### DocumentService
- [ ] Loads all 15 v1 test documents correctly
- [ ] Processes 12 new formats without errors
- [ ] Maintains metadata extraction accuracy
- [ ] Handles corrupted files gracefully

#### RAGService
- [ ] Returns relevant chunks for 95% of test queries (hit rate / MRR)
- [ ] Maintains source attribution
- [ ] Supports all v1 search modes; integrates LlamaIndex query engine with v1 fallback
- [ ] Adds semantic search improvements; consider reranking and hybrid retrieval

#### LLMService
- [ ] Supports all 4 v1 providers
- [ ] Adds 5+ new providers
- [ ] Maintains prompt templates
- [ ] Handles rate limiting properly

### System-Level Validation
- [ ] All CLI commands produce identical output structure
- [ ] Performance meets or exceeds targets
- [ ] Error messages remain user-friendly
- [ ] Logging maintains v1 format

---

## 📚 Documentation Updates

### LlamaIndex-Specific Guides
- Chunking & Node Parsers: docs.llamaindex.ai for SentenceSplitter, SemanticSplitter
- Vector Stores: Weaviate, FAISS integration patterns and tuning
- Evaluations: Faithfulness/Relevancy evaluators usage in CI
- Observability: Tracing hooks, metrics exporters, dashboards


### User-Facing Docs
1. **README.md** - Add engine selection info
2. **QUICK_START.md** - Update with new features
3. **TROUBLESHOOTING.md** - Add v2-specific issues

### Developer Docs
1. **ARCHITECTURE.md** - Update with LlamaIndex components
2. **API_REFERENCE.md** - Document new capabilities
3. **MIGRATION_GUIDE.md** - For custom extensions

### Internal Docs
1. **RUNBOOK.md** - Operational procedures
2. **MONITORING.md** - New metrics and alerts
3. **PERFORMANCE_TUNING.md** - LlamaIndex optimization

---

## 🎯 Success Metrics

### Technical Success
- ✅ 80% code reduction achieved
- ✅ 15+ document formats supported
- ✅ 20%+ performance improvement
- ✅ Retrieval accuracy ≥ 95%
- ✅ Zero breaking changes to CLI

### Technical Success
- ✅ 80% code reduction achieved
- ✅ 15+ document formats supported
- ✅ 20%+ performance improvement
- ✅ Zero breaking changes to CLI

### Business Success
- ✅ No user disruption during migration
- ✅ Reduced maintenance burden
- ✅ Faster feature development
- ✅ Better scalability

### Risk Mitigation Success
- ✅ Zero data loss incidents
- ✅ < 1% increase in error rate
- ✅ Successful fallback in all test scenarios
- ✅ Rollback tested and validated
