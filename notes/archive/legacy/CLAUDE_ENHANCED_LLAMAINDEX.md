# Enhanced CLAUDE.md for LlamaIndex Migration

Optimized for Caliper’s engineering charter: Docker-optional, Typer CLI, FAISS-first with optional Weaviate, Pydantic settings, Loguru logging, and fast test suite (<60s, ≥60% coverage). Use feature flags; avoid breaking changes.

## 📚 Essential Migration Documents

Before working on any migration tasks, familiarize yourself with:

1. **LLAMAINDEX_MIGRATION_SUMMARY.md** - Quick overview and daily checklist
2. **LLAMAINDEX_MIGRATION_PLAN.md** - Detailed phase-by-phase plan
3. **LLAMAINDEX_TESTING_SUITE.md** - Tests plus RAG evals
4. **LLAMAINDEX_MONITORING_GUIDE.md** - Metrics, alerts, debug CLI
5. **LLAMAINDEX_DEPENDENCY_MANAGEMENT.md** - Pins, groups, validation scripts
6. **LLAMAINDEX_ROLLBACK_RECOVERY.md** - Rollback and recovery runbooks
7. **LLAMAINDEX_PROGRESS_TRACKER.md** - Live progress and KPIs

## 🎯 Migration Principles

### The Prime Directive
Never break existing functionality. Every change must maintain 100% backward compatibility. Prefer hybrid shadow and canary before switching defaults.

### The Three Laws of Migration
1. **Test First**: Write tests before implementing any v2 feature
2. **Fallback Always**: Every v2 call must have v1 fallback
3. **Monitor Everything**: Log metrics for every operation

## 📋 Daily Migration Workflow

### 1. Start of Day Checklist
```bash
poetry run caliper diagnose --migration-status
pytest -m "not slow" -q
python compare_engines.py "EPA BOD limits" --shadow
```

Expected:
- v1 engine: healthy
- v2 engine: healthy
- fallback: active
- tests: passing
- phase: 2 (shadow)
- v2 traffic: 10%

### 2. Before Any Code Change
Ask yourself:
- Does this maintain CLI compatibility?
- Is there a test for this change?
- What happens if v2 fails?
- How will we monitor this?

### 3. Implementation Pattern
```python
# ALWAYS use this pattern for new v2 features (metrics + fallback)
import time
from loguru import logger
from caliper.core.config import settings
from monitoring.metrics import MetricsCollector, QueryMetrics

metrics = MetricsCollector()

def operation_with_migration(request):
    """Every operation must support both engines with metrics and fallback."""
    engine = get_engine_for_request(request)  # "llamaindex" | "v1"
    start = time.time()
    try:
        if engine == "llamaindex" and v2_healthy():
            result = v2_implementation(request)
            fb = False
        else:
            result = v1_implementation(request)
            fb = engine == "llamaindex"  # shadow fallback path
        metrics.record(QueryMetrics(
            query_id=request.id, engine=engine, operation="query",
            start_time=start, end_time=time.time(), success=True, fallback_used=fb
        ))
        return result
    except Exception as e:
        metrics.record(QueryMetrics(
            query_id=request.id, engine=engine, operation="query",
            start_time=start, end_time=time.time(), success=False, fallback_used=True, error_message=str(e)
        ))
        if engine == "llamaindex":
            logger.warning(f"v2 failed, falling back to v1: {e}")
            return v1_implementation(request)
        raise
```

## 🧪 Testing Requirements

For every new feature:
1. Unit test in isolation (mock network/LLMs; HF_HUB_OFFLINE=1)
2. Integration test across services
3. Comparison test: v1 vs v2 outputs (semantic parity)
4. Performance test: p95 latency target; memory profile
5. Fallback/circuit breaker tests
6. RAG evals: retrieval accuracy and faithfulness

### Test Template
```python
def test_feature_name(v1_engine, v2_engine, test_input):
    """Test v2 implementation with v1 comparison and evals."""
    v1_result = run_with_engine(test_input, engine="v1")
    v2_result = run_with_engine(test_input, engine="llamaindex")
    assert_semantically_equivalent(v1_result, v2_result)
    assert v2_result.duration < v1_result.duration * 1.2
    with mock_v2_failure():
        fb = run_with_engine(test_input, engine="llamaindex")
        assert fb.engine_used == "v1"
    # RAG eval example
    from llama_index.core.evaluation import FaithfulnessEvaluator
    ev = FaithfulnessEvaluator()
    score = ev.evaluate(v2_result.text, v2_result.context)
    assert score.value >= 0.9
```

## 📊 Progress Tracking

### After Each Task
Update the migration progress:
```bash
# Mark task complete
python update_progress.py --task "implement_document_service_v2" --status complete

# Run validation
python validate_phase.py --phase 2

# Update metrics dashboard
python update_dashboard.py
```

### Phase Transition Checklist
Before moving to next phase:
- [ ] All phase tasks complete
- [ ] All tests passing
- [ ] Performance targets met
- [ ] No increase in error rate
- [ ] Documentation updated
- [ ] Team sign-off obtained

## 🚨 Emergency Procedures

### If You Break Something
1. **Don't Panic** - The fallback will handle it
2. **Rollback Your Change** - `git revert HEAD`
3. **Check Metrics** - `python check_impact.py`
4. **Fix Forward** - Write test, then fix
5. **Document** - Update runbook with learning

### Red Flags That Require Immediate Action
- Error rate > 5% increase
- Performance degradation > 50%
- Fallback rate > 20%
- Any data corruption
- CLI commands failing

## 🎯 Current Phase Focus

### Phase 2: Service Layer Replacement + Hybrid Shadow
Priorities:
1. Replace DocumentService with LlamaIndex loaders/LlamaParse
2. Ensure all v1 formats work; add 12 new formats via LlamaHub
3. Maintain exact metadata; add chunk_id/parent_id and chunking params
4. Add comprehensive tests and evals pipeline
5. Validate p95 latency improvement and retrieval accuracy ≥ 95%
6. Implement hybrid shadow SxS parity logs before traffic shift

### Success Looks Like
```bash
# Both engines equivalent; auto-selection prefers v2 when healthy
poetry run caliper qa "test" --engine v1
poetry run caliper qa "test" --engine llamaindex
poetry run caliper qa "test"  # Auto-selects best engine (feature-flag)
```

## 💡 LlamaIndex Best Practices

DO:
- Use built-in document loaders and LlamaParse for complex PDFs
- Prefer VectorStoreIndex wrapping existing Weaviate; avoid full export
- Enable caching and rerankers where it improves retrieval
- Use structured outputs and standardized metadata
- Track eval metrics (faithfulness/retrieval) in CI

DON'T:
- Recreate v1’s custom implementations
- Bypass LlamaIndex abstractions
- Ignore framework patterns or observability hooks
- Sacrifice compatibility or fast-suite constraints
- Skip fallback or circuit breaker patterns

## 📝 Code Review Checklist

Before submitting PR:
- [ ] Tests written and passing (fast-suite); external calls mocked
- [ ] Both engines tested; parity script updated
- [ ] Fallback and circuit breaker verified
- [ ] Metrics + eval instrumentation added
- [ ] Documentation updated; runbooks adjusted
- [ ] No breaking changes; flags default safe
- [ ] Performance validated (p95 and memory)
- [ ] Error handling complete; Loguru logging present

## 🎉 Remember

This migration is about:
- **Evolution, not revolution** - Gradual, safe changes
- **User first** - No disruption to workflows
- **Quality over speed** - Better to be safe than sorry
- **Learn and adapt** - Document everything

You're not just migrating code, you're building a better future for Caliper!
