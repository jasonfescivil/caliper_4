# Claude Documentation Update Task

## Context
You are updating the Caliper v2 (LlamaIndex migration) documentation based on a recent project state analysis. The project is migrating from Langchain to LlamaIndex, with a parallel development approach that doesn't affect the existing v1 functionality.

## Current Project State Summary

### ✅ What's Actually Working
1. **Basic CLI** - `caliper_v2` commands: `info`, `ingest`, `query` (single index only)
2. **Dual Mode Operation**:
   - Local embeddings mode: `--embed-provider local` (no API keys needed)
   - OpenAI mode: Works with proper .env configuration
3. **Index Persistence** - Directories created via `IndexPathResolver`, but save/load not wired
4. **Document Ingestion** - PDF, DOCX, TXT via SimpleDirectoryReader

### ❌ What's Not Working
1. **Multi-index queries** - Missing dependency: `llama-index-question-gen-openai`
2. **FAISS persistence** - Logic incomplete (directories created but not saved/loaded)
3. **HashCache** - Schema exists but not integrated with CLI
4. **Advanced features** - Documented but not implemented

### 🔧 Recent Fixes Applied
- Fixed `index_resolver` undefined variable in `cli.py` line 545
- Added resolver initialization at function scope in query command

## Documentation Updates Needed

### 1. Update `PROJECT_STATE_SUMMARY.md`
- Change Phase 2 progress from "75%" to "60%"
- Add missing dependency to requirements
- Update "What's Working Now" section to reflect multi-index limitation
- Add note about `index_resolver` fix

### 2. Update `LLAMAINDEX_PROGRESS_TRACKER.md`
- Change "FAISS save/load wiring" from 30% to 10% (directories only)
- Add new task: "Fix multi-index dependency issue"
- Update test coverage to reflect actual state (~25% not 30%)

### 3. Create/Update `KNOWN_ISSUES.md`
```markdown
# Known Issues and Fixes

## Multi-Index Query Error
**Issue**: `ImportError: llama-index-question-gen-openai package cannot be found`
**Fix**: Add to pyproject.toml:
```toml
[tool.poetry.group.llamaindex.dependencies]
llama-index-question-gen-openai = "^0.1.3"
```

## FAISS Persistence Not Working
**Issue**: Indexes don't persist between runs
**Status**: Directories created, save/load logic pending
**Workaround**: Re-ingest documents each session
```

### 4. Update `pyproject.toml`
Add missing dependency to the llamaindex group:
```toml
[tool.poetry.group.llamaindex.dependencies]
llama-index-core = "^0.10.57"
llama-index-readers-file = "^0.1.4"
llama-index-vector-stores-faiss = "^0.1.2"
llama-index-llms-openai = "^0.1.19"
llama-index-embeddings-openai = "^0.1.7"
llama-index-question-gen-openai = "^0.1.3"  # ADD THIS LINE
```

### 5. Update CLI Examples
Replace optimistic examples with working ones:
```bash
# WORKING: Single index query
poetry run caliper_v2 query "What are AKART requirements?" --index state

# NOT YET WORKING: Multi-index (needs dependency)
poetry run caliper_v2 query "Compare federal and state requirements" --index "federal,state"

# WORKING: Local mode (no API keys)
poetry run caliper_v2 ingest docs --index demo --persist --embed-provider local
poetry run caliper_v2 query "What's in the index?" --index demo --embed-provider local
```

## Code Changes Needed (Priority Order)

### 1. Fix Multi-Index Dependency (Immediate)
```bash
poetry add llama-index-question-gen-openai --group llamaindex
```

### 2. Complete FAISS Persistence
In `src/caliper_v2/cli.py`, after line 283 (in ingest command):
```python
# Add after creating the index
if persist and index_paths:
    vs_index.storage_context.persist(persist_dir=str(index_paths.faiss_dir))
    logger.info("Persisted index to {}", index_paths.faiss_dir)
```

### 3. Wire HashCache
In `src/caliper_v2/cli.py`:
```python
# Import at top
from caliper_v2.services.persistence import HashCache

# In ingest command, before processing files:
hash_cache = HashCache(index_name=index)
for file_path in file_paths:
    if not force and hash_cache.is_cached(str(file_path)):
        logger.info("Skipping unchanged file: {}", file_path)
        continue
    # ... process file ...
    hash_cache.update(str(file_path))
```

## Testing Commands to Verify Fixes

```bash
# Test 1: Multi-index after dependency fix
poetry install --with llamaindex
poetry run caliper_v2 query "What are discharge limits?" --index "federal,state"

# Test 2: Persistence
poetry run caliper_v2 ingest knowledge_base/02_state_regulations --index state --persist
# Restart shell
poetry run caliper_v2 query "WAC requirements" --index state  # Should work without re-ingesting

# Test 3: Hash cache (after implementation)
poetry run caliper_v2 ingest knowledge_base --index kb --persist
poetry run caliper_v2 ingest knowledge_base --index kb --persist  # Should skip unchanged files
```

## Additional Context for Implementation

1. The project uses Poetry with optional dependency groups
2. GitHub Actions has a separate CI lane for v2 tests
3. The architecture maintains v1/v2 separation for safety
4. Focus on making existing features work before adding new ones
5. All LlamaIndex imports use lazy loading to avoid breaking v1

## Files to Review
- `src/caliper_v2/cli.py` - Main CLI implementation
- `src/caliper_v2/services/persistence.py` - HashCache and IndexPathResolver
- `pyproject.toml` - Dependency management
- All `LLAMAINDEX_*.md` files - Planning documents

## Success Criteria
1. Multi-index queries work without errors
2. Indexes persist between CLI sessions
3. Documentation accurately reflects current state
4. All examples in docs are tested and working
5. Known issues are documented with workarounds

---
*Note: This analysis was performed on 2025-08-06. The codebase may have evolved since then.*
