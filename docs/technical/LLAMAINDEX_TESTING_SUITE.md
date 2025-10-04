# LlamaIndex Migration Testing Suite

## 🧪 Comprehensive Test Framework

Aligned with Caliper fast-suite constraints (<60s, offline by default) and ≥60% global coverage gate. External HTTP/LLM calls must be mocked; set HF_HUB_OFFLINE=1 in tests.

### Test Structure
```
tests/
├── unit/
│   ├── test_document_service_v2.py
│   ├── test_rag_service_v2.py
│   ├── test_llm_service_v2.py
│   ├── test_fallback_mechanism.py
│   └── test_settings_and_flags.py
├── integration/
│   ├── test_end_to_end_workflows.py
│   ├── test_cli_compatibility.py
│   ├── test_engine_switching.py
│   └── test_data_consistency.py
├── regression/
│   ├── test_v1_v2_parity.py
│   ├── test_performance_regression.py
│   └── test_accuracy_regression.py
├── rag_evals/   # New: LlamaIndex evals for faithfulness/relevancy
│   ├── test_retrieval_accuracy.py
│   ├── test_faithfulness.py
│   └── test_semantic_similarity.py
├── load/
│   ├── test_concurrent_operations.py
│   ├── test_memory_usage.py
│   └── test_scalability.py
└── fixtures/
    ├── documents/
    ├── queries/
    └── expected_outputs/
```

---

## 📋 Test Cases by Service

### DocumentService Tests

```python
# test_document_service_v2.py
import pytest
from pathlib import Path
from caliper_v2.services.document_service import DocumentService, DocumentError

class TestDocumentServiceV2:
    @pytest.fixture
    def service(self):
        return DocumentService()

    def test_pdf_loading(self, service, expected_v1_output):
        """Test PDF loading maintains v1 compatibility"""
        doc = service.load_document(Path("tests/fixtures/documents/test.pdf"))
        assert doc.text == expected_v1_output
        assert doc.metadata["source"] == "test.pdf"

    def test_new_format_support(self, service):
        """Test new formats not in v1"""
        formats = [".epub", ".rtf", ".odt", ".html", ".xml"]
        for fmt in formats:
            doc = service.load_document(Path(f"tests/fixtures/documents/test{fmt}"))
            assert isinstance(doc.text, str) and len(doc.text) > 0

    def test_corrupted_file_handling(self, service):
        """Test graceful handling of corrupted files with clear error"""
        with pytest.raises(DocumentError) as e:
            service.load_document(Path("tests/fixtures/documents/corrupted.pdf"))
        assert "corrupted" in str(e.value).lower()

    def test_metadata_preservation(self, service):
        """Ensure all v1 metadata is preserved and v2 adds chunking fields"""
        doc = service.load_document(Path("tests/fixtures/documents/metadata_rich.pdf"))
        required_fields = ["source", "page_count", "author", "title"]
        for field in required_fields:
            assert field in doc.metadata
        # v2 additions
        for f in ["chunk_id", "parent_id", "chunk_size", "chunk_overlap"]:
            assert f in doc.metadata
```

### RAGService Tests

```python
# test_rag_service_v2.py
import pytest

class TestRAGServiceV2:
    def test_query_accuracy_semantic(self, rag_service, v1_baseline, test_queries):
        """Compare v2 accuracy against v1 baseline using semantic and eval metrics."""
        for q in test_queries:
            v1_results = v1_baseline[q.id]
            v2_results = rag_service.query(q.text)

            assert calculate_relevance(v2_results) >= calculate_relevance(v1_results) * 0.95
            assert all(chunk.source in v1_results.sources for chunk in v2_results.chunks[:3])

    def test_retrieval_hit_rate(self, rag_service, labeled_qas):
        """Use LlamaIndex evaluator to compute retrieval hit rate."""
        from llama_index.core.evaluation.retrieval.eval import RetrieverEvaluator
        ev = RetrieverEvaluator()
        score = ev.evaluate_dataset(rag_service, labeled_qas)
        assert score["hit_rate"] >= 0.95

    def test_performance_improvement(self, rag_service, benchmark):
        """Ensure v2 meets performance targets (p95 latency)."""
        def _run():
            rag_service.query("complex regulatory question")
        result = benchmark(_run)
        assert result < 2.0  # seconds

    def test_hybrid_search_compatibility(self, rag_service):
        """Test that hybrid search works as in v1."""
        results = rag_service.query(
            "specific keyword AND semantic meaning",
            search_type="hybrid",
            alpha=0.5
        )
        assert len(results) > 0
        assert results[0].score > 0.7
```

### Fallback Mechanism Tests

```python
# test_fallback_mechanism.py
import logging

class TestFallbackMechanism:
    def test_automatic_fallback_on_error(self, mock_v2_failure, caplog):
        """Test v2 failure triggers v1 fallback with clear log."""
        with mock_v2_failure, caplog.at_level(logging.WARNING):
            result = query_with_fallback("test query")
        assert result.engine_used == "v1"
        assert any("falling back to v1" in rec.message.lower() for rec in caplog.records)

    def test_fallback_overhead(self, benchmark):
        """Fallback path adds <100ms overhead."""
        def _run():
            query_with_fallback("test query", force_fallback=True)
        duration = benchmark(_run)
        assert duration < 0.1

    def test_fallback_result_quality(self):
        """Fallback maintains result quality envelope."""
        v2_result = query_v2("test query")
        fb = query_with_fallback("test query", force_fallback=True)
        assert_semantically_equivalent(v2_result, fb)
        assert fb.sources == v2_result.sources
```

---

## 🔄 Regression Test Suite

### Output Comparison Tests

```python
# test_v1_v2_parity.py
def test_regulatory_query_parity():
    """Test regulatory queries produce equivalent results"""
    test_queries = [
        "What are the effluent limits for BOD?",
        "Explain monitoring requirements",
        "Compare state vs federal standards"
    ]

    for query in test_queries:
        v1_result = run_v1_engine(query)
        v2_result = run_v2_engine(query)

        # Semantic similarity check
        similarity = calculate_semantic_similarity(v1_result, v2_result)
        assert similarity > 0.90, f"Query '{query}' similarity only {similarity}"

        # Source overlap check
        v1_sources = extract_sources(v1_result)
        v2_sources = extract_sources(v2_result)
        overlap = len(v1_sources & v2_sources) / len(v1_sources)
        assert overlap > 0.80, f"Source overlap only {overlap}"
```

### Performance Regression Tests

```python
# test_performance_regression.py
def test_batch_processing_performance():
    """Ensure v2 handles batch operations efficiently"""
    documents = load_test_documents(count=100)

    start = time.time()
    v1_results = process_batch_v1(documents)
    v1_time = time.time() - start

    start = time.time()
    v2_results = process_batch_v2(documents)
    v2_time = time.time() - start

    assert v2_time < v1_time * 1.1  # Allow 10% variance
    assert len(v2_results) == len(v1_results)
```

---

## 🚀 Load Testing

### Concurrent Operations Test

```python
# test_concurrent_operations.py
import statistics
import pytest
@pytest.mark.load
def test_concurrent_queries():
    """Test system under concurrent load"""
    import concurrent.futures

    queries = generate_test_queries(count=50)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_query, q) for q in queries]
        results = [f.result() for f in futures]

    assert len(results) == 50

    errors = [r for r in results if getattr(r, "error", None)]
    assert len(errors) / len(results) < 0.02  # < 2% error rate

    response_times = [r.duration for r in results if not getattr(r, "error", None)]
    assert statistics.mean(response_times) < 3.0  # Average < 3s
    assert statistics.stdev(response_times) < 1.0  # Consistent performance
```

---

## 📊 Test Execution Strategy

### Daily Tests (CI/CD)
```bash
# Fast suite on every commit (no network, offline mode)
pytest -m "not slow" tests/unit/ -q
pytest -m "not slow" tests/integration/test_cli_compatibility.py -q
```

### Nightly Tests
```bash
# Comprehensive regression suite with evals
pytest tests/regression/ -v --benchmark-compare
pytest tests/rag_evals/ -v
```

### Weekly Tests
```bash
# Full load and stress testing
pytest tests/load/ -v --maxfail=1 --durations=25
```

### Pre-Release Tests
```bash
# Complete suite with coverage gate
pytest tests/ -v --cov=caliper_v2 --cov-report=term-missing
python validate_migration_ready.py
```

Environment knobs for CI:
- HF_HUB_OFFLINE=1
- CALIPER_USE_WEAVIATE=false (default FAISS)
- CALIPER_ENGINE=llamaindex (or v1 for parity runs)
---

## 🎯 Test Success Criteria

### Phase 2 Exit Criteria
- Unit test coverage ≥ 80% fast-suite; ≥ 95% critical-path modules
- All integration tests passing
- No performance regression > 10%
- Fallback & circuit breaker validated

### Phase 3 Exit Criteria
- 100% CLI compatibility verified (--engine flag + auto-select)
- Load tests show < 2% error rate
- Memory usage reduced by 20%
- All regression tests passing; eval scores within ±10% of v1

### Phase 4 Exit Criteria
- 2 weeks of stable canary (10% → 100% ramp)
- Zero critical bugs
- Performance SLAs met (p95)
- User acceptance confirmed; documentation updated
