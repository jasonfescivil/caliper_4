"""Test provider configuration functionality."""
import pytest


@pytest.mark.unit
class TestProviderConfiguration:
    """Test provider selection and configuration."""
    
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
    
    def test_normalize_provider_model_gemini(self):
        """Test Gemini provider normalization."""
        from caliper_v2.ui_dash.app import _normalize_provider_model
        prov, mdl, alerts = _normalize_provider_model("gemini", None)
        assert prov == "gemini"
        assert mdl == "gemini-2.5-pro-preview"
    
    def test_normalize_provider_model_xai(self):
        """Test xAI provider normalization."""
        from caliper_v2.ui_dash.app import _normalize_provider_model
        prov, mdl, alerts = _normalize_provider_model("xai", None)
        assert prov == "xai"
        assert mdl == "grok-4-fast-reasoning"
