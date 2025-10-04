# Streamlit UI Removal & Dash UI Testing Plan

**Date**: 2025-09-30  
**Objective**: Remove Streamlit UI completely and establish comprehensive testing for Dash UI as the primary web interface

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Streamlit Removal](#phase-1-streamlit-removal)
3. [Phase 2: Dash UI Testing Infrastructure](#phase-2-dash-ui-testing-infrastructure)
4. [Phase 3: Comprehensive Testing Suite](#phase-3-comprehensive-testing-suite)
5. [Phase 4: Documentation & Cleanup](#phase-4-documentation--cleanup)
6. [Testing Checklist](#testing-checklist)
7. [Rollback Plan](#rollback-plan)

---

## Executive Summary

### Current State
- **Streamlit UI**: `src/caliper_v2/ui/app.py` - 200+ lines, thin CLI wrapper
- **Dash UI**: `src/caliper_v2/ui_dash/app.py` - 1085 lines, feature-complete
- **Dependencies**: Both `streamlit` and `dash` in `pyproject.toml`
- **Documentation**: Both UIs documented separately

### Target State
- **Streamlit UI**: Completely removed
- **Dash UI**: Primary UI with comprehensive test coverage
- **Dependencies**: `streamlit` removed from all dependency specifications
- **Documentation**: Single UI guide focusing on Dash

### Success Criteria
- ✅ All Streamlit code removed
- ✅ Dash UI passes 50+ automated tests
- ✅ All 5 core workflows tested end-to-end
- ✅ Documentation updated and accurate
- ✅ No regression in CLI functionality

---

## Phase 1: Streamlit Removal

### 1.1 Code Removal

#### Files to Delete
```
src/caliper_v2/ui/
├── __init__.py          # DELETE
└── app.py               # DELETE
```

**Command**:
```powershell
Remove-Item -Path "C:\repos\caliper_4\src\caliper_v2\ui" -Recurse -Force
```

#### Import References to Remove

**Search for Streamlit imports**:
```powershell
Get-ChildItem -Path "C:\repos\caliper_4" -Recurse -Include *.py,*.md | Select-String -Pattern "streamlit" -CaseSensitive:$false
```

**Expected locations to check**:
- `README.md` (line 152-153)
- `QUICK_START.md` (no references expected)
- `docs/index.md` (lines 11-12, 20)
- `docs/user/streamlit-ui-guide.md` (entire file - DELETE)
- `docs/developer/contributing-lite.md` (lines 18-19)
- `docs/developer/dash-ui-development.md` (line 167 reference)

### 1.2 Dependency Cleanup

#### pyproject.toml Updates

**Current** (line 13):
```toml
streamlit = "^1.37.0"
```

**Action**: Remove the entire line

**Verification**:
```powershell
poetry lock --no-update
poetry install
# Verify streamlit is not installed
poetry show | Select-String -Pattern "streamlit"
```

### 1.3 Docker Configuration Updates

#### docker-compose.yml

**Current** (line 53):
```yaml
# Use 'docker compose exec app poetry run streamlit run src/caliper/ui/app.py --server.port=8501 --server.address=0.0.0.0' for UI
```

**Replace with**:
```yaml
# Use 'docker compose exec app poetry run python src/caliper_v2/ui_dash/app.py' for Dash UI
# Note: Dash UI runs on port 8050 by default
```

**Add port mapping** (after line 24):
```yaml
    ports:
      - "8501:8501"  # Remove this line
      - "8050:8050"  # Add this for Dash UI
```

### 1.4 Documentation References

#### Files to Update

1. **README.md** (lines 146-156)
   - Remove Streamlit UI section entirely
   - Update with Dash UI instructions

2. **docs/index.md** (lines 11-12, 20)
   - Remove Streamlit references
   - Update links to Dash UI guide

3. **docs/user/streamlit-ui-guide.md**
   - **Action**: DELETE this file

4. **docs/developer/contributing-lite.md** (lines 18-19)
   - Remove Streamlit from development stack

5. **docs/developer/dash-ui-development.md** (line 167)
   - Remove cross-reference to Streamlit guide

---

## Phase 2: Dash UI Testing Infrastructure

### 2.1 Test File Structure

Create comprehensive test suite:

```
tests/ui_dash/
├── __init__.py
├── conftest.py                      # Fixtures and test config
├── test_dash_app_lifecycle.py       # App startup/shutdown
├── test_dash_provider_config.py     # Provider selection/config
├── test_dash_retrieval.py           # Retrieval tab
├── test_dash_graph.py               # GraphRAG retrieval
├── test_dash_enhance.py             # Enhancement tab
├── test_dash_draft.py               # Draft editor
├── test_dash_generate.py            # Generation tab
├── test_dash_review.py              # Judge & Review tab
├── test_dash_integration.py         # End-to-end workflows
├── test_dash_windows_compat.py      # Windows-specific tests
└── test_dash_state_management.py    # Cross-tab state
```

### 2.2 Testing Dependencies

Add to `pyproject.toml` (in `[tool.poetry.group.dev.dependencies]` if exists, or create):

```toml
[tool.poetry.group.test.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-dash = "^4.5.0"            # Dash testing utilities
playwright = "^1.40.0"             # Browser automation
pytest-mock = "^3.12.0"            # Mocking
pytest-cov = "^4.1.0"              # Coverage reporting
freezegun = "^1.4.0"               # Time mocking
```

### 2.3 Test Configuration

**pytest.ini**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --cov=src/caliper_v2/ui_dash
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    ui: UI interaction tests
    slow: Slow-running tests
    windows: Windows-specific tests
```

---

## Phase 3: Comprehensive Testing Suite

### 3.1 Unit Tests

#### test_dash_app_lifecycle.py

**Purpose**: Verify app initialization and basic structure

```python
"""Test Dash app lifecycle and initialization."""
import pytest
from dash.testing.application_runners import import_app


class TestDashAppLifecycle:
    """Test Dash application lifecycle."""
    
    def test_app_imports_successfully(self):
        """Test that app module can be imported."""
        from caliper_v2.ui_dash import app
        assert app is not None
    
    def test_app_has_required_attributes(self):
        """Test app has required Dash attributes."""
        from caliper_v2.ui_dash.app import app
        assert hasattr(app, 'layout')
        assert hasattr(app, 'callback')
        assert hasattr(app, 'run')
    
    def test_app_title_is_set(self):
        """Test app title is configured."""
        from caliper_v2.ui_dash.app import app
        assert app.title == "Caliper v2 – Dash UI"
    
    def test_stores_defined(self):
        """Test dcc.Store components are defined for state."""
        from caliper_v2.ui_dash.app import stores
        assert stores is not None
        # Check for expected store IDs
        # (inspect stores.children for dcc.Store components)
    
    def test_tabs_defined(self):
        """Test all required tabs are defined."""
        from caliper_v2.ui_dash.app import app
        # Navigate layout and verify 5 tabs exist
        # Retrieval, Enhance, Draft, Generate, Review
    
    @pytest.mark.slow
    def test_app_starts_successfully(self, dash_duo):
        """Test app starts without errors."""
        app = import_app("caliper_v2.ui_dash.app")
        dash_duo.start_server(app)
        assert dash_duo.server_url
        dash_duo.wait_for_page()
```

#### test_dash_provider_config.py

**Purpose**: Test provider selection and configuration

```python
"""Test provider configuration functionality."""
import pytest
from unittest.mock import patch, MagicMock


class TestProviderConfiguration:
    """Test provider selection and configuration."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment with API keys."""
        monkeypatch.setenv("COHERE_API_KEY", "test_cohere_key")
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    
    def test_provider_dropdown_has_all_providers(self, dash_duo):
        """Test provider dropdown includes all supported providers."""
        from caliper_v2.ui_dash.app import provider_options
        expected = ["cohere", "openai", "anthropic", "gemini", "xai", "grok"]
        provider_values = [opt["value"] for opt in provider_options]
        for provider in expected:
            assert provider in provider_values
    
    def test_normalize_provider_model_cohere(self):
        """Test Cohere provider normalization."""
        from caliper_v2.ui_dash.app import _normalize_provider_model
        prov, mdl, alerts = _normalize_provider_model("cohere", None)
        assert prov == "cohere"
        assert mdl == "command-a-reasoning-08-2025"
    
    def test_normalize_provider_model_openai(self):
        """Test OpenAI provider normalization."""
        from caliper_v2.ui_dash.app import _normalize_provider_model
        prov, mdl, alerts = _normalize_provider_model("openai", "gpt-4")
        assert prov == "openai"
        assert mdl == "gpt-4o"
        assert len(alerts) > 0  # Should have normalization alert
    
    def test_normalize_provider_model_anthropic(self):
        """Test Anthropic provider normalization."""
        from caliper_v2.ui_dash.app import _normalize_provider_model
        prov, mdl, alerts = _normalize_provider_model("anthropic", None)
        assert prov == "anthropic"
        assert mdl == "claude-opus-4-1-20250805"
    
    @patch("caliper_v2.ui_dash.app.configure_llm_provider")
    def test_apply_provider_callback(self, mock_configure, dash_duo, mock_env):
        """Test apply provider callback updates stores."""
        from caliper_v2.ui_dash.app import app
        dash_duo.start_server(app)
        
        # Simulate provider selection and apply
        dash_duo.select_dcc_dropdown("#inp-provider", value="cohere")
        dash_duo.wait_for_element("#btn-apply-provider")
        dash_duo.find_element("#btn-apply-provider").click()
        
        # Verify store updated and success message shown
        dash_duo.wait_for_text_to_equal("#provider-status", "Configured provider")
```

### 3.2 Integration Tests

#### test_dash_retrieval.py

**Purpose**: Test cloud text retrieval workflow

```python
"""Test retrieval tab functionality."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json


class TestRetrievalWorkflow:
    """Test retrieval workflow integration."""
    
    @pytest.fixture
    def sample_retrieval_result(self, tmp_path):
        """Create sample retrieval result."""
        result = {
            "type": "retrieval_session",
            "question": "Test question",
            "indexes": ["design"],
            "retrieval": {
                "nodes": [
                    {
                        "text": "Sample node text",
                        "score": 0.95,
                        "metadata": {
                            "file_name": "test.pdf",
                            "page": 1,
                            "section": "Introduction"
                        }
                    }
                ]
            }
        }
        output_path = tmp_path / "retrieval.json"
        output_path.write_text(json.dumps(result))
        return output_path
    
    @patch("subprocess.run")
    def test_retrieval_executes_command(self, mock_run, dash_duo, tmp_path):
        """Test retrieval executes CLI command correctly."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Retrieval successful",
            stderr=""
        )
        
        from caliper_v2.ui_dash.app import app
        dash_duo.start_server(app)
        
        # Navigate to retrieval tab (it's default)
        dash_duo.wait_for_element("#ret-question")
        
        # Fill in question
        question_input = dash_duo.find_element("#ret-question")
        question_input.send_keys("What are design standards?")
        
        # Set output path
        out_input = dash_duo.find_element("#ret-out")
        out_input.clear()
        out_input.send_keys(str(tmp_path / "test_retrieval.json"))
        
        # Click retrieve button
        dash_duo.find_element("#btn-retrieve").click()
        
        # Wait for results
        dash_duo.wait_for_element("#ret-result", timeout=10)
        
        # Verify subprocess.run was called with correct args
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "caliper_v2" in call_args
        assert "retrieve" in call_args
    
    def test_retrieval_displays_node_preview(self, dash_duo, sample_retrieval_result):
        """Test retrieval displays node preview table."""
        # Mock successful retrieval to return sample_retrieval_result
        # Verify table is rendered with correct columns and data
        pass
    
    def test_retrieval_updates_store(self, dash_duo, sample_retrieval_result):
        """Test retrieval updates dcc.Store with output path."""
        # Verify store-retrieval-path is updated after successful retrieval
        pass
```

#### test_dash_graph.py

**Purpose**: Test GraphRAG retrieval workflow

```python
"""Test GraphRAG retrieval functionality."""
import pytest
from unittest.mock import patch, MagicMock


class TestGraphRetrievalWorkflow:
    """Test GraphRAG workflow integration."""
    
    @patch("subprocess.run")
    def test_graph_retrieval_basic(self, mock_run, dash_duo, tmp_path):
        """Test basic graph retrieval without text mixing."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="GraphRAG retrieval successful",
            stderr=""
        )
        
        from caliper_v2.ui_dash.app import app
        dash_duo.start_server(app)
        
        # Fill in question
        dash_duo.find_element("#ret-question").send_keys("Test query")
        
        # Fill graph settings
        dash_duo.find_element("#graph-dir").send_keys(str(tmp_path / "graph"))
        dash_duo.find_element("#graph-hops").send_keys("2")
        dash_duo.find_element("#graph-limit").send_keys("100")
        
        # Click graph button
        dash_duo.find_element("#btn-graph").click()
        
        # Wait for results
        dash_duo.wait_for_element("#ret-graph-result", timeout=15)
        
        # Verify command execution
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "graph" in call_args
        assert "retrieve" in call_args
    
    @patch("subprocess.run")
    def test_graph_retrieval_with_text_mixing(self, mock_run, dash_duo):
        """Test graph retrieval with cloud text mixing."""
        # Enable mix-with-text checkbox
        # Verify additional CLI args for text indexes, top-k, rerank
        pass
```

### 3.3 End-to-End Tests

#### test_dash_integration.py

**Purpose**: Test complete workflows from start to finish

```python
"""Test end-to-end workflows."""
import pytest
from pathlib import Path
import json
from unittest.mock import patch


class TestCompleteWorkflows:
    """Test complete user workflows."""
    
    @pytest.mark.slow
    @patch("subprocess.run")
    @patch("caliper_v2.commands.enhance.main")
    @patch("caliper_v2.services.ui_api.synthesize_from_context")
    def test_retrieve_enhance_generate_workflow(
        self, mock_synth, mock_enhance, mock_run, dash_duo, tmp_path
    ):
        """Test Retrieve → Enhance → Generate workflow."""
        # Mock retrieval result
        retrieval_path = tmp_path / "retrieval.json"
        retrieval_path.write_text(json.dumps({
            "type": "retrieval_session",
            "question": "Test",
            "indexes": ["design"],
            "retrieval": {"nodes": []}
        }))
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Mock enhance result
        enhanced_path = tmp_path / "enhanced.json"
        mock_enhance.return_value = enhanced_path
        
        # Mock generate result
        mock_synth.return_value = "Generated text content"
        
        from caliper_v2.ui_dash.app import app
        dash_duo.start_server(app)
        
        # Step 1: Retrieve
        dash_duo.find_element("#ret-question").send_keys("Test question")
        dash_duo.find_element("#btn-retrieve").click()
        dash_duo.wait_for_element("#ret-result", timeout=10)
        
        # Step 2: Navigate to Enhance tab
        dash_duo.find_element('a[data-value="tab-enhance"]').click()
        dash_duo.wait_for_element("#enh-ctx")
        
        # Verify retrieval path auto-filled
        # Click enhance button
        dash_duo.find_element("#btn-enhance").click()
        dash_duo.wait_for_text_to_equal("#enh-status", "Enhanced", timeout=10)
        
        # Step 3: Navigate to Generate tab
        dash_duo.find_element('a[data-value="tab-generate"]').click()
        dash_duo.wait_for_element("#gen-ctx")
        
        # Verify context path auto-filled
        dash_duo.find_element("#btn-generate").click()
        dash_duo.wait_for_element("#gen-preview", timeout=20)
        
        # Verify all mocks were called
        assert mock_run.called
        assert mock_enhance.called
        assert mock_synth.called
    
    @pytest.mark.slow
    def test_full_qc_workflow(self, dash_duo, tmp_path):
        """Test Retrieve → Generate → Judge workflow."""
        # Complete workflow with QC check at end
        pass
```

### 3.4 UI Interaction Tests

#### test_dash_state_management.py

**Purpose**: Test cross-tab state persistence

```python
"""Test state management across tabs."""
import pytest


class TestStateManagement:
    """Test dcc.Store state management."""
    
    def test_provider_state_persists_across_tabs(self, dash_duo):
        """Test provider selection persists when switching tabs."""
        from caliper_v2.ui_dash.app import app
        dash_duo.start_server(app)
        
        # Select provider
        dash_duo.select_dcc_dropdown("#inp-provider", value="anthropic")
        dash_duo.find_element("#inp-model").send_keys("claude-opus-4-1")
        dash_duo.find_element("#btn-apply-provider").click()
        
        # Switch to Generate tab
        dash_duo.find_element('a[data-value="tab-generate"]').click()
        dash_duo.wait_for_element("#gen-provider")
        
        # Verify provider is pre-filled
        gen_provider = dash_duo.find_element("#gen-provider").get_attribute("value")
        assert gen_provider == "anthropic"
    
    def test_retrieval_path_flows_to_enhance(self, dash_duo, tmp_path):
        """Test retrieval output path flows to enhance input."""
        # Mock successful retrieval
        # Navigate to enhance tab
        # Verify context input is pre-filled with retrieval output
        pass
    
    def test_enhanced_path_flows_to_generate(self, dash_duo):
        """Test enhanced output path flows to generate input."""
        # Mock successful enhance
        # Navigate to generate tab
        # Verify context input is pre-filled with enhanced output
        pass
```

### 3.5 Windows-Specific Tests

#### test_dash_windows_compat.py

**Purpose**: Verify Windows path handling and command execution

```python
"""Test Windows-specific functionality."""
import pytest
from pathlib import Path


@pytest.mark.windows
class TestWindowsCompatibility:
    """Test Windows-specific features."""
    
    def test_path_cleaning(self):
        """Test path cleaning handles Windows paths correctly."""
        from caliper_v2.ui_dash.app import _clean_path_str
        
        # Test quoted path
        assert _clean_path_str('"C:\\\\test\\\\path"') == "C:\\\\test\\\\path"
        
        # Test path with spaces
        assert _clean_path_str("C:\\\\Program Files\\\\test") == "C:\\\\Program Files\\\\test"
    
    def test_windows_retrieve_command_generation(self):
        """Test Windows-safe retrieve command generation."""
        from caliper_v2.services.judge_components import windows_retrieve_command
        
        cmd = windows_retrieve_command(
            question="Test question",
            indexes=["design"],
            out_path="C:\\\\test\\\\output.json",
            top_k=40,
            rerank_top_n=20
        )
        
        # Verify proper quoting for Windows
        assert "poetry run caliper_v2 retrieve" in cmd
        assert "Test question" in cmd
    
    @patch("subprocess.run")
    def test_subprocess_execution_on_windows(self, mock_run, dash_duo):
        """Test subprocess.run works with Windows paths."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Execute retrieval with Windows path
        # Verify subprocess.run receives correct argv (list, not shell string)
        pass
```

---

## Phase 4: Documentation & Cleanup

### 4.1 Create New Dash UI User Guide

**File**: `docs/user/dash-ui-guide.md`

```markdown
# Caliper v2 Dash UI Guide

## Overview

The Dash UI is the primary web interface for Caliper v2, providing a modern, 
interactive workflow for document retrieval and generation.

## Quick Start

### Launching the UI

From the repository root:

\`\`\`powershell
poetry run python src/caliper_v2/ui_dash/app.py
\`\`\`

The UI will start on `http://localhost:8050`

### First-Time Setup

1. **Check Environment**: Click "Doctor" button to verify API keys
2. **Select Provider**: Choose your preferred LLM provider (Cohere recommended)
3. **Apply Configuration**: Click "Apply" to activate provider

## Workflow Tabs

### 🔎 Retrieval Tab

**Purpose**: Search indexes for relevant information

**Steps**:
1. Enter your question in the text area
2. Select indexes (comma-separated): `federal,state,design`
3. Configure retrieval settings:
   - Top-K: Number of results (default: 40)
   - Rerank Top-N: Results to rerank (default: 20)
4. Click "Run Retrieval"

**Advanced Options** (accordion):
- Retrieval Mode: chunks, files_via_content, auto_routed
- Dense K / Sparse K: Hybrid search parameters
- Alpha: Blend factor (0.0 = sparse only, 1.0 = dense only)
- Include Terms: Comma-separated required terms
- Exclude Sections: Skip TOC, glossary, etc.

**GraphRAG Retrieval**:
- Enable for entity-based retrieval from local knowledge graph
- Mix with text retrieval for hybrid approach

### ✨ Enhance Tab

**Purpose**: Improve retrieved context with outline and diagnostics

**Steps**:
1. Context path is auto-filled from retrieval
2. Specify enhanced output path
3. Click "Enhance Context"

**Output**: Enhanced JSON with outline, rewritten spores, follow-up suggestions

### ✍️ Draft Tab

**Purpose**: Manual editing workspace

**Features**:
- Load existing draft from file
- Edit in monospace text area
- Save changes back to file

### 🧪 Generate Tab

**Purpose**: AI-powered generation from context

**Steps**:
1. Context path is auto-filled from enhance (or retrieval)
2. Select generation style: strict-citation, outline, quote-heavy
3. Choose provider/model (or use default from sidebar)
4. Click "Generate"

**Preview**: First 500 characters displayed immediately

### ⚖️ Judge & Review Tab

**Purpose**: Quality control and evaluation

**Steps**:
1. Specify context path
2. Specify draft path
3. Configure options:
   - Strict Mode: Require stronger evidence
   - Max Evidence per Claim: Cap evidence snippets
4. Click "Run Full Review"

**Output**: 
- JSON judgment report
- Markdown review with metrics and recommendations

## Provider Configuration

### Supported Providers

- **Cohere**: Best for retrieval (embeddings + reranking)
- **OpenAI**: GPT-5, GPT-4o (fast, reliable)
- **Anthropic**: Claude Opus 4.1, Sonnet 4.5 (highest quality)
- **Google Gemini**: 2.5 Pro (long context)
- **xAI Grok**: Grok-4 (fast iteration)

### Model Selection

Leave model blank to use provider defaults, or specify:
- Cohere: `command-r-plus`
- OpenAI: `gpt-5`, `gpt-4o`
- Anthropic: `claude-opus-4-1-20250805`, `claude-sonnet-4-5`
- Gemini: `gemini-2.5-pro`
- xAI: `grok-4`

## Troubleshooting

### "No API key found"

**Solution**: Check `.env` file contains required keys

\`\`\`powershell
notepad .env
\`\`\`

Run Doctor command for diagnostics:
\`\`\`powershell
poetry run caliper_v2 doctor
\`\`\`

### Retrieval Fails

**Common causes**:
- LlamaCloud index IDs not configured
- Network connectivity issues
- Invalid index name

**Solution**: Verify `.env` has index IDs:
\`\`\`
FEDERAL_BASE_ID=<uuid>
FEDERAL_SUMMARY_ID=<uuid>
STATE_BASE_ID=<uuid>
STATE_SUMMARY_ID=<uuid>
DESIGN_BASE_ID=<uuid>
DESIGN_SUMMARY_ID=<uuid>
\`\`\`

### Generation Errors

**Common causes**:
- Provider API rate limits
- Model not available in your tier
- Empty context

**Solution**: 
- Check provider status page
- Try different model
- Verify context file has nodes

## Advanced Features

### File Upload

Use "Load File" button on Retrieval tab to load questions from `.md` files

### Path Conventions

- Retrieval outputs: `data_v2/context/context_*.json`
- Enhanced contexts: `data_v2/context/enhanced_*.json`
- Generated drafts: `outputs/drafts/draft_*.md`
- Review reports: `outputs/reviews/review_*.json` and `.md`

### Command Preview

Expand "Generated Command" accordions to see exact CLI commands executed

## Keyboard Shortcuts

- `Ctrl+S` in Draft tab: Save (when textarea is focused)
- `Tab`: Navigate between form fields
- `Enter`: Submit forms (on buttons)

## Performance Tips

1. **Smaller top-k values**: Faster retrieval (but less comprehensive)
2. **Disable reranking**: Skip for speed during exploration
3. **Use presets**: `.caliper.yml` for common configurations
4. **Local caching**: Repeated queries leverage cache

## Related Documentation

- [Command Reference](../reference/command-reference.md)
- [Architecture Overview](../developer/architecture-overview.md)
- [Quick Start Guide](quick-start-guide.md)
```

### 4.2 Update Root Documentation

#### README.md Updates

**Replace lines 146-156** with:

```markdown
## User Interfaces

### Dash UI

A modern web interface for Caliper v2 workflows:

\`\`\`bash
poetry run python src/caliper_v2/ui_dash/app.py
\`\`\`

The UI runs on `http://localhost:8050` and provides:
- Interactive retrieval configuration
- Provider/model selection
- Real-time command preview
- GraphRAG integration
- Complete workflow: Retrieve → Enhance → Generate → Judge

For detailed instructions, see [Dash UI Guide](docs/user/dash-ui-guide.md).
```

#### docs/index.md Updates

**Replace lines 11-12 and 20** with references to Dash UI guide only

### 4.3 Update Docker Documentation

Add Dash UI instructions to `docker-compose.yml` comments and `docs/user/installation-guide.md`

---

## Testing Checklist

### Pre-Removal Verification
- [ ] Verify Streamlit UI currently works
- [ ] Document any Streamlit-specific features not in Dash UI
- [ ] Backup current state: `git commit -am "Pre-Streamlit-removal checkpoint"`

### Removal Phase
- [ ] Delete `src/caliper_v2/ui/` directory
- [ ] Remove `streamlit` from `pyproject.toml`
- [ ] Run `poetry lock --no-update && poetry install`
- [ ] Verify `poetry show | grep streamlit` returns empty
- [ ] Delete `docs/user/streamlit-ui-guide.md`
- [ ] Update all documentation references

### Dash UI Test Execution

#### Unit Tests (10+ tests)
- [ ] App imports successfully
- [ ] App has required attributes
- [ ] All tabs defined
- [ ] All dcc.Store components defined
- [ ] Provider dropdown populated
- [ ] Provider normalization logic
- [ ] Path cleaning utility
- [ ] Preview node function
- [ ] Default paths function
- [ ] App starts without errors

#### Component Tests (15+ tests)
- [ ] Provider apply callback
- [ ] Provider self-test (Cohere)
- [ ] Doctor button execution
- [ ] Load prompt from file
- [ ] Retrieval command generation
- [ ] Retrieval subprocess execution
- [ ] Retrieval result display
- [ ] Graph retrieval command generation
- [ ] Graph retrieval with mixing
- [ ] Enhance callback
- [ ] Draft load/save
- [ ] Generate callback
- [ ] Generate preview display
- [ ] Judge callback
- [ ] Review markdown display

#### Integration Tests (10+ tests)
- [ ] Retrieve → store updates
- [ ] Retrieve → Enhance data flow
- [ ] Enhance → Generate data flow
- [ ] Retrieve → Generate → Judge workflow
- [ ] Graph retrieve → Generate workflow
- [ ] Provider state persists across tabs
- [ ] Error handling displays correctly
- [ ] Long-running operations show progress
- [ ] Concurrent tab operations don't interfere
- [ ] Browser back/forward maintains state

#### Windows-Specific Tests (5+ tests)
- [ ] Path cleaning with quotes
- [ ] Path cleaning with spaces
- [ ] Windows retrieve command generation
- [ ] Subprocess execution with Windows paths
- [ ] File separators handled correctly

#### UI Interaction Tests (10+ tests)
- [ ] Tab switching works
- [ ] Form validation displays errors
- [ ] Buttons disable during processing
- [ ] Success alerts display
- [ ] Error alerts display
- [ ] Accordions expand/collapse
- [ ] Checkboxes toggle correctly
- [ ] Dropdowns populate and select
- [ ] Text inputs accept and clear
- [ ] File paths with special chars

### Manual Testing Scenarios

#### Scenario 1: First-Time User
1. [ ] Launch Dash UI
2. [ ] Click Doctor button
3. [ ] Select provider
4. [ ] Run simple retrieval
5. [ ] View results
6. [ ] Generate from context

#### Scenario 2: Engineering Report Workflow
1. [ ] Load question from file
2. [ ] Configure retrieval (3 indexes, top-k 40, rerank 20)
3. [ ] Run retrieval
4. [ ] Enhance context
5. [ ] Generate with Claude Sonnet 4.5
6. [ ] Judge quality
7. [ ] Review metrics

#### Scenario 3: GraphRAG Research
1. [ ] Enter complex query
2. [ ] Configure GraphRAG (2 hops, 200 limit)
3. [ ] Enable mix with text
4. [ ] Run graph retrieval
5. [ ] Generate from mixed context

#### Scenario 4: Multi-Provider Comparison
1. [ ] Retrieve once
2. [ ] Generate with OpenAI
3. [ ] Generate with Anthropic (same context)
4. [ ] Generate with Gemini (same context)
5. [ ] Compare outputs

#### Scenario 5: Error Recovery
1. [ ] Attempt retrieval with invalid index
2. [ ] Verify error message
3. [ ] Correct index and retry
4. [ ] Attempt generate with missing API key
5. [ ] Verify error guidance
6. [ ] Set key and retry

### Performance Testing
- [ ] Retrieval completes in < 30s (40 nodes, with rerank)
- [ ] Generate completes in < 60s (Claude Sonnet 4.5)
- [ ] Tab switching is instant (< 200ms)
- [ ] Page load time < 3s on localhost
- [ ] Memory usage stable over 1 hour session

### Cross-Browser Testing (Optional)
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if Mac available)

---

## Rollback Plan

### If Dash UI Testing Fails

**Scenario**: Critical bugs found that block all workflows

**Action Steps**:

1. **Restore Streamlit**:
   ```powershell
   git revert HEAD  # Revert removal commit
   poetry install
   ```

2. **Document Issues**:
   - Create GitHub issues for each Dash UI bug
   - Prioritize by severity (P0, P1, P2)

3. **Hotfix Plan**:
   - Keep both UIs temporarily
   - Fix Dash UI bugs
   - Re-test before final Streamlit removal

### If Dependency Conflicts

**Scenario**: `poetry install` fails after `streamlit` removal

**Action Steps**:

1. **Check lock file**:
   ```powershell
   poetry lock --check
   ```

2. **Regenerate lock**:
   ```powershell
   poetry lock --no-update
   ```

3. **If still failing**:
   ```powershell
   # Restore streamlit temporarily
   poetry add streamlit^1.37.0
   # Document conflict
   # Resolve dependency tree manually
   ```

---

## Execution Timeline

### Estimated Duration: 2-3 Days

#### Day 1: Preparation & Removal (4 hours)
- [ ] Morning: Review plan, backup current state
- [ ] Morning: Execute Phase 1 (Streamlit removal)
- [ ] Afternoon: Set up Phase 2 (test infrastructure)
- [ ] Afternoon: Write initial unit tests (10 tests)

#### Day 2: Core Testing (6-8 hours)
- [ ] Morning: Write component tests (15 tests)
- [ ] Afternoon: Write integration tests (10 tests)
- [ ] Evening: Write Windows-specific tests (5 tests)
- [ ] Evening: Write UI interaction tests (10 tests)

#### Day 3: Manual Testing & Documentation (4-6 hours)
- [ ] Morning: Execute manual test scenarios (5 scenarios)
- [ ] Afternoon: Update documentation (Phase 4)
- [ ] Afternoon: Final verification and cleanup
- [ ] Evening: Create summary report

---

## Success Metrics

### Quantitative
- **Test Coverage**: ≥ 80% for `ui_dash/app.py`
- **Test Count**: ≥ 50 automated tests passing
- **Manual Scenarios**: 5/5 scenarios completed successfully
- **Performance**: All operations within target times
- **Zero Regressions**: CLI functionality unaffected

### Qualitative
- **Documentation**: Clear, accurate, complete
- **Error Messages**: Helpful and actionable
- **User Experience**: Smooth workflows, intuitive UI
- **Maintainability**: Tests are clear and well-structured

---

## Post-Completion Tasks

1. **Announce Changes**:
   - Update CHANGELOG.md
   - Create GitHub release notes
   - Update project README badges

2. **Monitor Issues**:
   - Watch for user-reported bugs (first 2 weeks)
   - Quick response time for critical issues

3. **Future Enhancements**:
   - Consider playwright E2E tests for critical paths
   - Add visual regression tests (screenshots)
   - Implement CI/CD test runs

---

## Appendix: Test Command Quick Reference

### Run All Tests
```powershell
poetry run pytest tests/ui_dash/ -v
```

### Run Specific Test File
```powershell
poetry run pytest tests/ui_dash/test_dash_retrieval.py -v
```

### Run Tests with Coverage
```powershell
poetry run pytest tests/ui_dash/ --cov=src/caliper_v2/ui_dash --cov-report=html
```

### Run Only Fast Tests
```powershell
poetry run pytest tests/ui_dash/ -m "not slow"
```

### Run Only Windows Tests
```powershell
poetry run pytest tests/ui_dash/ -m windows
```

### Run Tests and Stop on First Failure
```powershell
poetry run pytest tests/ui_dash/ -x
```

---

**End of Plan**
