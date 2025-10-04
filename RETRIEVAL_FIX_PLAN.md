# Retrieval System Fix - Implementation Plan

## Issues Identified

Based on analysis of `ccaliper4.json` and `cli.py`:

### Issue 1: Control Flow Bug (CRITICAL)
**Lines**: ~1489-1570 in `src/caliper_v2/cli.py`

**Problem**: Simple cloud retrieval path executes first and returns early, preventing sophisticated logic from running.

**Simple Path** (currently executes):
```python
if cloud:
    retriever = LlamaCloudRetriever(...)
    fused = list(retriever.retrieve(question, limit=top_k) or [])
    # Basic Cohere rerank
    # Empty spore generation
    # RETURN HERE ← Never reaches sophisticated logic!
```

**Sophisticated Path** (never reached):
```python
# Lines 1580+
# - Respects --indexes parameter
# - Query expansion (Multi-Query + HyDE)
# - Summary-first routing (_sfirst_retrieve)
# - Per-index retrieval with domain terms
# - Full spore generation with reasoning
# - Per-node spore generation
```

**Impact**:
- Your request for `design,federal,state` indexes ignored
- Only got state index (DOE Orange Book)
- No WEF/design documents retrieved
- Empty spore: `"spore": {}`
- HyDE/query expansion disabled

### Issue 2: Index Selection Ignored (HIGH)
**Root Cause**: Simple path doesn't use the sophisticated multi-index routing logic.

**Expected Behavior**:
```python
for name in scoped_indexes:  # ['design', 'federal', 'state']
    b_id, s_id = _cloud_ids_for_index(name)
    base = LlamaCloudIndex(index_id=b_id)
    summ = LlamaCloudIndex(index_id=s_id)
    # Summary-first retrieval per index
    res = _sfirst_retrieve(q_use, base, summ, ...)
    buckets += res
```

**Actual Behavior**: Simple path ignores index list entirely.

### Issue 3: Empty Spore Generation (HIGH)
**Root Cause**: Simple path has minimal spore logic that produces empty dict.

**Expected Spore Structure**:
```json
{
  "summary": "Top sources selected based on...",
  "rationale_bullets": [
    "Covers primary regulatory sections",
    "Includes adjacent sections for context",
    "Combines lexical and semantic matches"
  ],
  "confidence": 0.7
}
```

**Expected Per-Node Spores**:
```json
{
  "reason": "Cites WAC 173-240-060; Section: C2-1.2.1 Design Flow Rates; p.260; WWTP guidance",
  "confidence": 0.75
}
```

## Fix Strategy

### Phase 1: Remove Buggy Simple Path
**Action**: Comment out or delete lines ~1489-1570

**Rationale**: This path is fundamentally broken and prevents all advanced features from working.

### Phase 2: Ensure Sophisticated Path Always Runs
**Action**: Remove the early return, ensure cloud retrieval flows to sophisticated logic

**Changes**:
1. Remove `if cloud:` block that returns early
2. Ensure sophisticated path handles cloud retrieval by default
3. Keep all advanced features active (query expansion, HyDE, summary-first routing)

### Phase 3: Fix Default Spore Behavior
**Action**: Change `--no-spore` default to always generate spores

**Changes**:
```python
no_spore: bool = typer.Option(False, "--no-spore", ...)  # Already correct
node_spore: bool = typer.Option(True, "--node-spore/--no-node-spore", ...)  # Already correct
```

Ensure spore generation logic runs for all cloud retrievals.

### Phase 4: Add Domain Term Boosting
**Action**: Include WEF/design-specific terms in query expansion

**Changes**:
```python
domain_terms = [
    # DOE terms
    "G1", "General Sewer Plan", "Engineering Report",
    "WAC 173-240-050", "WAC 173-240-060", "WAC 173-240-070",
    # WEF terms
    "WEF", "MOP", "Manual of Practice", "Water Environment Federation",
    "Design of Municipal Wastewater Treatment Plants",
    # Lift station specific
    "firm capacity", "pump station", "redundancy", "backup pump",
    "peak hourly flow", "design flow rates"
]
```

## Expected Results After Fix

### Test Query
```bash
caliper_v2 retrieve "how is the firm capacity of a sewer lift station designed? compare whatever method is described in the department of ecology's criteria for sewage works designs and all available WEF guidance. List the relevant federal and state regulations" \
  --indexes design,federal,state \
  --cloud \
  --top-k 40 \
  --reranker cohere \
  --out test_fixed.json
```

### Expected JSON Output
```json
{
  "type": "retrieval_session",
  "version": 1,
  "question": "...",
  "indexes": ["design", "federal", "state"],
  "search_mode": "cloud",
  "requested_top_k": 40,
  "final_kept": 40,
  "top_k": 40,
  "reranker": "cohere",
  "retrieval": {
    "nodes": [
      {
        "node_id": "...",
        "document_id": "...",
        "score": 0.85,
        "text": "From WEF MOP 8...",
        "metadata": {
          "file_name": "WEF_MOP_8_Design_Pumping.pdf",
          "page": 142,
          "section": "Firm Capacity Design",
          "index": "design",
          "document_title": "WEF Manual of Practice No. 8",
          "publisher": "Water Environment Federation"
        },
        "spore": {
          "reason": "Cites WEF MOP 8 firm capacity equation; Section: Pump Station Design; p.142; Directly addresses firm capacity calculation methodology",
          "confidence": 0.92
        }
      },
      {
        "node_id": "...",
        "text": "From DOE Orange Book...",
        "metadata": {
          "file_name": "DOE_Orange_Book_Design_Standards.pdf",
          "page": 260,
          "section": "C2-1.2.1 Design Flow Rates",
          "index": "state",
          "agency": "WA Ecology"
        },
        "spore": {
          "reason": "Cites WAC 173-240-060; Section: C2-1.2.1; p.260; WA state requirements for lift station firm capacity",
          "confidence": 0.88
        }
      },
      {
        "node_id": "...",
        "text": "Federal regulations under 40 CFR...",
        "metadata": {
          "file_name": "40_CFR_403_Federal_Pretreatment.pdf",
          "index": "federal"
        },
        "spore": {
          "reason": "Cites 40 CFR 403; Federal pretreatment standards applicable to lift stations",
          "confidence": 0.75
        }
      }
    ],
    "spore": {
      "summary": "Retrieved documents span WEF design guidance (MOP 8), Washington State regulations (DOE Orange Book Chapter C2), and federal standards (40 CFR). These sources provide comprehensive coverage of firm capacity design methodologies from industry best practices, state requirements, and federal compliance perspectives.",
      "rationale_bullets": [
        "WEF MOP 8 provides detailed firm capacity calculation methodology and industry standards",
        "DOE Orange Book Chapter C2 specifies Washington State requirements per WAC 173-240",
        "Federal regulations establish baseline requirements for lift station design",
        "Sources include adjacent sections providing upstream/downstream context for holistic understanding",
        "Hybrid retrieval ensured balance between technical specifications and regulatory compliance"
      ],
      "confidence": 0.85
    },
    "citations": [
      {"file": "WEF_MOP_8_Design_Pumping.pdf", "page": 142, "section": "Firm Capacity Design"},
      {"file": "DOE_Orange_Book_Design_Standards.pdf", "page": 260, "section": "C2-1.2.1 Design Flow Rates"},
      {"file": "40_CFR_403_Federal_Pretreatment.pdf", "page": 15, "section": "General Pretreatment Regulations"}
    ]
  }
}
```

### Key Improvements
1. ✅ **All 3 indexes represented**: design (WEF), state (DOE), federal (EPA/CFR)
2. ✅ **Rich session-level spore**: Explains WHY these sources were chosen and HOW they work together
3. ✅ **Per-node spores**: Each node has reasoning with citations (CFR, WAC, RCW detection), section info, page numbers
4. ✅ **Higher node count**: 40 nodes from 3 indexes vs 11 from 1 index
5. ✅ **Better diversity**: Not all from DOE Orange Book
6. ✅ **WEF content appears**: Design guidance from Water Environment Federation

## Implementation Steps for Overnight Run

### Step 1: Backup Current cli.py
```bash
cd c:/repos/caliper_4
copy src\caliper_v2\cli.py src\caliper_v2\cli.py.backup
```

### Step 2: Apply Fix (Remove Lines 1489-1570)
Comment out the buggy simple cloud path:
```python
# if cloud:
#     api_key = os.getenv("LLAMA_CLOUD_API_KEY")
#     if not api_key:
#         typer.secho("LLAMA_CLOUD_API_KEY environment variable not set.", fg=typer.colors.RED)
#         raise typer.Exit(code=1)
#     ...
#     [DELETE ALL CODE UNTIL LINE ~1570]
#     ...
#     typer.echo(str(out_path))
#     return  # ← THIS EARLY RETURN MUST GO
```

Ensure cloud retrieval falls through to sophisticated logic starting around line 1580.

### Step 3: Test with Your Original Query
```bash
poetry run python -m caliper_v2.cli retrieve "how is the firm capacity of a sewer lift station designed? compare whatever method is described in the department of ecology's criteria for sewage works designs and all available WEF guidance. List the relevant federal and state regulations" --indexes design,federal,state --cloud --top-k 40 --reranker cohere --out c:\repos\caliper_4\data_v2\context\test_fixed.json
```

### Step 4: Verify Results
Check `test_fixed.json`:
- ✅ `"indexes": ["design", "federal", "state"]` (not just state)
- ✅ `"spore": {...}` has summary, rationale_bullets, confidence
- ✅ Each node has `"spore": {"reason": "...", "confidence": 0.X}`
- ✅ Nodes from WEF documents (design index) present
- ✅ `"final_kept": 40` (not 11)

### Step 5: Update Dash UI (If Needed)
If Dash UI calls retrieve via subprocess, no changes needed.
If it calls Python function directly, ensure it uses fixed logic.

## Success Criteria

- [x] Fix applied to cli.py
- [ ] Test query runs successfully
- [ ] JSON contains all 3 indexes
- [ ] Spore generation works (session + per-node)
- [ ] WEF documents appear in results
- [ ] Node count matches requested top_k
- [ ] Dash UI works with fixed logic

## Rollback Plan

If fix causes issues:
```bash
copy src\caliper_v2\cli.py.backup src\caliper_v2\cli.py
```

## Notes

- The sophisticated path already has ALL the features you need
- The simple path is just broken and should be removed
- No breaking changes to API or command structure
- Fix is surgical: remove early return, let sophisticated logic run
