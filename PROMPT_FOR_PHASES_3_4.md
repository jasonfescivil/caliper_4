# Prompt for GPT-Codex: Complete Dash UI Testing (Phases 3-4)

**Context**: Phases 1-2 of the Streamlit removal and Dash UI testing plan have been completed. You need to finish Phases 3-4.

---

## Your Task

Complete the remaining phases of the Streamlit removal and Dash UI testing initiative:

### **Phase 3: Comprehensive Testing Suite** (Priority 1)
Write integration and end-to-end tests for the Dash UI to reach 50+ total passing tests.

### **Phase 4: Documentation & Cleanup** (Priority 2)
Update all remaining documentation files to remove Streamlit references and finalize the transition to Dash UI.

---

## What's Already Done

✅ **Phase 1 Complete**: Streamlit UI removed from codebase  
✅ **Phase 2 Complete**: Testing infrastructure created with 15 passing unit tests

### Current Test Suite (15 tests)
- `tests/ui_dash/test_dash_app_lifecycle.py` - 5 tests (app structure)
- `tests/ui_dash/test_dash_provider_config.py` - 5 tests (provider normalization)
- `tests/ui_dash/test_dash_windows_compat.py` - 5 tests (path handling)

### Available Documentation
- `STREAMLIT_REMOVAL_DASH_TESTING_PLAN.md` - Complete plan with test templates
- `STREAMLIT_REMOVAL_EXECUTION_SUMMARY.md` - What's been done so far
- `tests/ui_dash/conftest.py` - Test fixtures and helpers

### Environment
- **OS**: Windows 11
- **Shell**: PowerShell 7.5.3
- **Python**: 3.11.8 (via Poetry)
- **Working Directory**: `C:\repos\caliper_4`
- **Test Runner**: pytest 8.4.2

---

## Phase 3: Integration Tests (Target: 35+ Additional Tests)

### Required Test Files to Create

Create the following test files in `tests/ui_dash/`:

#### 1. `test_dash_retrieval.py` (8 tests minimum)
Test the retrieval tab functionality:

**Tests to write**:
- [ ] `test_retrieval_command_generation` - Verify CLI command is built correctly
- [ ] `test_retrieval_with_basic_inputs` - Question + indexes + top-k
- [ ] `test_retrieval_with_advanced_options` - Dense-k, sparse-k, alpha, filters
- [ ] `test_retrieval_subprocess_execution` - Mock subprocess.run and verify argv
- [ ] `test_retrieval_updates_store` - Verify store-retrieval-path updated
- [ ] `test_retrieval_displays_preview_table` - Check node preview rendering
- [ ] `test_retrieval_handles_empty_question` - Error validation
- [ ] `test_retrieval_file_output_detection` - Detect newly created files

**Mock Strategy**: Use `@patch("subprocess.run")` and `@patch("pathlib.Path.exists")`

**Code Reference**: 
- Dash app callbacks: Lines 705-788 of `src/caliper_v2/ui_dash/app.py`
- Windows retrieve command: `caliper_v2.services.judge_components.windows_retrieve_command`

#### 2. `test_dash_graph.py` (6 tests minimum)
Test GraphRAG retrieval functionality:

**Tests to write**:
- [ ] `test_graph_retrieval_command_generation` - Basic graph retrieve command
- [ ] `test_graph_retrieval_with_mixing` - Mix with text retrieval enabled
- [ ] `test_graph_retrieval_subprocess_execution` - Verify argv includes graph params
- [ ] `test_graph_retrieval_without_mixing` - Pure graph retrieval
- [ ] `test_graph_updates_store` - Verify store-graph-path updated
- [ ] `test_graph_displays_results` - Check result display

**Code Reference**: Lines 792-910 of `src/caliper_v2/ui_dash/app.py`

#### 3. `test_dash_enhance.py` (5 tests minimum)
Test enhancement tab:

**Tests to write**:
- [ ] `test_enhance_calls_command` - Mock enhance_cmd.main
- [ ] `test_enhance_with_retrieval_path` - Auto-fill from store
- [ ] `test_enhance_creates_output_file` - Verify enhanced JSON created
- [ ] `test_enhance_updates_store` - Verify store-enhanced-path updated
- [ ] `test_enhance_handles_missing_input` - Error validation

**Code Reference**: Lines 914-929 of `src/caliper_v2/ui_dash/app.py`

#### 4. `test_dash_draft.py` (4 tests minimum)
Test draft editor:

**Tests to write**:
- [ ] `test_draft_load` - Load file into textarea
- [ ] `test_draft_save` - Save textarea to file
- [ ] `test_draft_updates_store` - Verify store-draft-path updated
- [ ] `test_draft_handles_missing_file` - Error handling

**Code Reference**: Lines 933-959 of `src/caliper_v2/ui_dash/app.py`

#### 5. `test_dash_generate.py` (6 tests minimum)
Test generation tab:

**Tests to write**:
- [ ] `test_generate_calls_synthesize` - Mock synthesize_from_context
- [ ] `test_generate_with_provider_override` - Use tab-specific provider
- [ ] `test_generate_with_stored_provider` - Use sidebar provider
- [ ] `test_generate_displays_preview` - First 500 chars shown
- [ ] `test_generate_writes_output_file` - Verify .md file created
- [ ] `test_generate_handles_missing_context` - Error validation

**Code Reference**: Lines 991-1033 of `src/caliper_v2/ui_dash/app.py`

#### 6. `test_dash_review.py` (5 tests minimum)
Test judge & review tab:

**Tests to write**:
- [ ] `test_review_calls_command` - Mock review_cmd.main
- [ ] `test_review_strict_mode` - Verify strict flag passed
- [ ] `test_review_creates_outputs` - JSON + MD files created
- [ ] `test_review_displays_preview` - Markdown preview shown
- [ ] `test_review_handles_missing_inputs` - Error validation

**Code Reference**: Lines 1037-1058 of `src/caliper_v2/ui_dash/app.py`

#### 7. `test_dash_state_management.py` (5 tests minimum)
Test cross-tab state persistence:

**Tests to write**:
- [ ] `test_provider_state_persists` - Provider selection survives tab switch
- [ ] `test_retrieval_flows_to_enhance` - Retrieval path → enhance input
- [ ] `test_enhanced_flows_to_generate` - Enhanced path → generate input
- [ ] `test_generate_output_flows_to_review` - Draft path → review input
- [ ] `test_stores_cleared_on_new_retrieval` - State resets properly

**Code Reference**: Lines 673-681, 915-929 of `src/caliper_v2/ui_dash/app.py`

#### 8. `test_dash_integration.py` (6+ tests minimum)
Test end-to-end workflows:

**Tests to write**:
- [ ] `test_retrieve_to_generate_workflow` - 2-step workflow
- [ ] `test_retrieve_enhance_generate_workflow` - 3-step workflow
- [ ] `test_retrieve_generate_review_workflow` - Full QC workflow
- [ ] `test_graph_to_generate_workflow` - GraphRAG workflow
- [ ] `test_multi_provider_comparison` - Same context, different providers
- [ ] `test_error_recovery_workflow` - Failed retrieval → retry

**Mock Strategy**: Mock all subprocess and file I/O operations

---

## Test Writing Guidelines

### Imports Template
```python
"""Test module description."""
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import json
```

### Test Class Structure
```python
@pytest.mark.integration  # or @pytest.mark.ui, @pytest.mark.slow
class TestFeatureName:
    """Test feature description."""
    
    def test_specific_behavior(self, mock_env, tmp_path):
        """Test that specific behavior works correctly."""
        # Arrange
        
        # Act
        
        # Assert
```

### Mocking Patterns

**Mock subprocess.run**:
```python
@patch("subprocess.run")
def test_something(self, mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Success",
        stderr=""
    )
    # Test code
    assert mock_run.called
```

**Mock file operations**:
```python
@patch("pathlib.Path.exists")
@patch("pathlib.Path.read_text")
def test_file_read(self, mock_read, mock_exists):
    mock_exists.return_value = True
    mock_read.return_value = '{"key": "value"}'
    # Test code
```

**Mock Caliper functions**:
```python
@patch("caliper_v2.commands.enhance.main")
def test_enhance(self, mock_enhance, tmp_path):
    mock_enhance.return_value = tmp_path / "enhanced.json"
    # Test code
    assert mock_enhance.called
```

### Use Fixtures
Available in `conftest.py`:
- `mock_env` - Pre-set API keys and index IDs
- `sample_retrieval_result(tmp_path)` - Sample JSON file
- `tmp_path` - Temporary directory (built-in pytest fixture)

---

## Phase 4: Documentation Cleanup

### Files That Need Updates

#### 1. `docs/index.md`
**Lines to check**: 11-12, 20  
**Task**: Remove any Streamlit references, update links to point to `dash-ui-guide.md`

#### 2. `docs/developer/contributing-lite.md`
**Lines to check**: 18-19  
**Task**: Remove Streamlit from development stack list

#### 3. `docs/developer/dash-ui-development.md`
**Line to check**: 167  
**Task**: Remove cross-reference to Streamlit guide

#### 4. Create `CHANGELOG.md` Entry
Add entry documenting the breaking change:

```markdown
## [Unreleased]

### Breaking Changes
- **Removed Streamlit UI**: The Streamlit-based web UI has been completely removed. 
  Users must now use the Dash UI instead. Launch with: 
  `poetry run python src/caliper_v2/ui_dash/app.py` (port 8050)

### Added
- Comprehensive test suite for Dash UI (50+ tests)
- Dash UI user guide documentation

### Changed
- Docker port mapping: 8501 → 8050 (Dash UI)
- README updated with Dash UI instructions

### Removed
- `src/caliper_v2/ui/` directory (Streamlit UI)
- `streamlit` dependency from pyproject.toml
- `docs/user/streamlit-ui-guide.md`

Migration: See `docs/user/dash-ui-guide.md` for Dash UI usage.
```

### Verification Commands

Run these to find remaining Streamlit references:
```powershell
# Search all code files
Get-ChildItem -Path "C:\repos\caliper_4\src" -Recurse -Include *.py | Select-String -Pattern "streamlit" -CaseSensitive:$false

# Search all documentation
Get-ChildItem -Path "C:\repos\caliper_4\docs" -Recurse -Include *.md | Select-String -Pattern "streamlit" -CaseSensitive:$false

# Search configuration files
Get-ChildItem -Path "C:\repos\caliper_4" -Include *.yml,*.yaml,*.toml,*.ini -Recurse | Select-String -Pattern "streamlit" -CaseSensitive:$false
```

---

## Success Criteria

### Phase 3 Complete When:
- [ ] 50+ total tests passing (current: 15, need: 35+ more)
- [ ] All 8 integration test files created
- [ ] Test execution time < 5 seconds for full suite
- [ ] No test failures or warnings (except deprecation warnings)
- [ ] All tests documented with clear docstrings

### Phase 4 Complete When:
- [ ] Zero Streamlit references in `docs/` directory
- [ ] Zero Streamlit references in `src/` directory
- [ ] CHANGELOG.md entry created
- [ ] All documentation links verified working
- [ ] README.md accurately reflects current UI state

---

## Commands to Run

### Create a test file
```powershell
New-Item -Path "C:\repos\caliper_4\tests\ui_dash\test_dash_retrieval.py" -ItemType File
```

### Run tests as you write them
```powershell
# Run specific file
poetry run pytest tests/ui_dash/test_dash_retrieval.py -v

# Run all tests
poetry run pytest tests/ui_dash/ -v

# Run with coverage
poetry run pytest tests/ui_dash/ --cov=src/caliper_v2/ui_dash --cov-report=term-missing
```

### Verify documentation updates
```powershell
# Read a file
Get-Content "C:\repos\caliper_4\docs\index.md"

# Search for pattern
Select-String -Path "C:\repos\caliper_4\docs\index.md" -Pattern "streamlit"
```

---

## Expected Timeline

- **Phase 3 Integration Tests**: 4-6 hours
  - test_dash_retrieval.py: 45 min
  - test_dash_graph.py: 30 min
  - test_dash_enhance.py: 30 min
  - test_dash_draft.py: 20 min
  - test_dash_generate.py: 45 min
  - test_dash_review.py: 30 min
  - test_dash_state_management.py: 45 min
  - test_dash_integration.py: 60 min

- **Phase 4 Documentation**: 1-2 hours
  - Find/fix Streamlit references: 30 min
  - Update documentation files: 30 min
  - Create CHANGELOG: 20 min
  - Final verification: 20 min

**Total Estimated Time**: 5-8 hours

---

## Useful Code References

### Dash App Structure
- **Main app**: `src/caliper_v2/ui_dash/app.py` (1,085 lines)
- **Helper functions**: `_normalize_provider_model()`, `_clean_path_str()`, `_preview_nodes()`
- **Callbacks**: Lines 572-1076 contain all callback definitions

### Test Examples
- **Unit test patterns**: `tests/ui_dash/test_dash_app_lifecycle.py`
- **Mock patterns**: `tests/ui_dash/test_dash_windows_compat.py`
- **Fixtures**: `tests/ui_dash/conftest.py`

### Plan Document
- **Full test templates**: `STREAMLIT_REMOVAL_DASH_TESTING_PLAN.md` (lines 203-643)
- **Testing checklist**: Lines 889-1017

---

## Git Workflow

After completing each phase:

```powershell
# Add all new/modified files
git add tests/ui_dash/*.py docs/**/*.md CHANGELOG.md

# Commit Phase 3
git commit -m "test: Add integration tests for Dash UI (Phase 3 complete)

Added 35+ integration tests:
- Retrieval workflow tests (8 tests)
- GraphRAG retrieval tests (6 tests)
- Enhancement tests (5 tests)
- Draft editor tests (4 tests)
- Generation tests (6 tests)
- Review tests (5 tests)
- State management tests (5 tests)
- End-to-end workflows (6 tests)

Total: 50+ passing tests"

# Commit Phase 4
git commit -m "docs: Remove all Streamlit references and finalize Dash UI docs

- Removed Streamlit references from all docs
- Updated cross-references to Dash UI guide
- Created CHANGELOG.md entry for breaking change
- Verified all documentation links working

Closes: Streamlit removal initiative"
```

---

## Final Checklist

Before marking complete:

### Phase 3
- [ ] Created all 8 integration test files
- [ ] All tests have clear docstrings
- [ ] No hardcoded paths (use tmp_path, fixtures)
- [ ] All mocks are properly cleaned up
- [ ] Test suite runs in < 5 seconds
- [ ] No test failures
- [ ] Git commit created

### Phase 4
- [ ] Searched and removed all Streamlit references
- [ ] Updated 3 documentation files minimum
- [ ] Created CHANGELOG.md entry
- [ ] Verified no broken links
- [ ] Git commit created

### Overall
- [ ] Total tests >= 50
- [ ] Test success rate = 100%
- [ ] Documentation accurate and complete
- [ ] Plan marked as 100% complete
- [ ] Execution summary updated

---

## Questions or Issues?

If you encounter problems:

1. **Import errors**: Check that `poetry install` was run
2. **Module not found**: Ensure `src/caliper_v2` is in Python path
3. **Dash not available**: The app file is at `src/caliper_v2/ui_dash/app.py`
4. **Test fails unexpectedly**: Check mock setup - subprocess, file I/O, Caliper functions
5. **Can't find file**: Use absolute paths: `C:\repos\caliper_4\...`

Reference the plan (`STREAMLIT_REMOVAL_DASH_TESTING_PLAN.md`) for complete test code examples.

---

## Start Here

**Step 1**: Create `tests/ui_dash/test_dash_retrieval.py` with 8 tests  
**Step 2**: Run tests and verify they pass  
**Step 3**: Continue with remaining test files  
**Step 4**: Update documentation files  
**Step 5**: Create final summary and commit

Good luck! 🚀
