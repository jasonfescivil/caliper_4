"""Test Dash app lifecycle and initialization."""
import pytest


@pytest.mark.unit
class TestDashAppLifecycle:
    """Test Dash application lifecycle."""
    
    def test_app_imports_successfully(self):
        """Test that app module can be imported."""
        try:
            from caliper_v2.ui_dash import app as dash_module
            assert dash_module is not None
        except ImportError as e:
            pytest.skip(f"Dash module not importable: {e}")
    
    def test_app_has_required_attributes(self):
        """Test app has required Dash attributes."""
        from caliper_v2.ui_dash.app import app
        assert hasattr(app, 'layout')
        assert hasattr(app, 'callback')
        assert hasattr(app, 'run') or hasattr(app, 'run_server')
    
    def test_app_title_is_set(self):
        """Test app title is configured."""
        from caliper_v2.ui_dash.app import app
        assert app.title == "Caliper v2 – Dash UI"
    
    def test_stores_defined(self):
        """Test dcc.Store components are defined for state."""
        from caliper_v2.ui_dash.app import stores
        assert stores is not None
    
    def test_provider_options_defined(self):
        """Test provider options are available."""
        from caliper_v2.ui_dash.app import provider_options
        assert provider_options is not None
        assert len(provider_options) >= 5  # At least 5 providers
        
        # Check expected providers
        provider_values = [opt["value"] for opt in provider_options]
        assert "cohere" in provider_values
        assert "openai" in provider_values
        assert "anthropic" in provider_values
