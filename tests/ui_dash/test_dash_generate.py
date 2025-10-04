"""Test generation tab callback behavior."""
from pathlib import Path
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _context_file(tmp_path: Path, content: str = "Context body") -> Path:
    ctx = tmp_path / "ctx.json"
    ctx.write_text(content, encoding="utf-8")
    return ctx


def test_generate_calls_synthesize(tmp_path, mock_env):
    """Generation callback invokes synthesize_from_context with resolved args."""
    ctx_path = _context_file(tmp_path)
    out_path = tmp_path / "draft.md"

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="Generated draft" ) as mock_synth,
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, returned_out = dash_app.on_generate(1, str(ctx_path), "Summary", "cohere", None, str(out_path), None, None)

    mock_synth.assert_called_once()
    kwargs = mock_synth.call_args.kwargs
    assert kwargs["context_path"] == str(ctx_path)
    assert kwargs["style"] == "Summary"
    assert kwargs["llm_provider"] == "cohere"
    assert out_path.exists()
    assert preview == "Generated draft"
    assert returned_out == str(out_path)
    assert any("Generation complete" in str(alert) for alert in alerts)


def test_generate_with_provider_override(tmp_path, mock_env):
    """Explicit provider overrides stored selections."""
    ctx_path = _context_file(tmp_path)
    out_path = tmp_path / "override.md"

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="text") as mock_synth,
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        dash_app.on_generate(1, str(ctx_path), "", "openai", "gpt-4.1", str(out_path), "cohere", "command-r")

    kwargs = mock_synth.call_args.kwargs
    assert kwargs["llm_provider"] == "openai"
    assert "gpt" in kwargs["llm_model"]


def test_generate_with_stored_provider(tmp_path, mock_env):
    """Stored provider/model are used when per-tab overrides are empty."""
    ctx_path = _context_file(tmp_path)
    out_path = tmp_path / "stored.md"

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="stored text") as mock_synth,
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        dash_app.on_generate(1, str(ctx_path), "", "", "", str(out_path), "anthropic", "claude-3")

    kwargs = mock_synth.call_args.kwargs
    assert kwargs["llm_provider"] == "anthropic"
    assert "claude" in kwargs["llm_model"].lower()


def test_generate_displays_preview(tmp_path, mock_env):
    """Generated text is truncated to preview length and success alert returned."""
    ctx_path = _context_file(tmp_path)
    out_path = tmp_path / "long.md"
    generated = "A" * 600

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value=generated) as mock_synth,
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, returned_out = dash_app.on_generate(1, str(ctx_path), "Detailed", "cohere", None, str(out_path), None, None)

    assert preview == "A" * 500 + "..."
    assert returned_out == str(out_path)
    assert len(alerts) >= 1
    assert any("Generation complete" in str(alert) for alert in alerts)


def test_generate_writes_output_file(tmp_path, mock_env):
    """Output Markdown file is written to the requested path."""
    ctx_path = _context_file(tmp_path)
    out_path = tmp_path / "drafts" / "note.md"

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="Final text") as mock_synth,
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, returned_out = dash_app.on_generate(1, str(ctx_path), "", "cohere", None, str(out_path), None, None)

    assert out_path.exists()
    assert out_path.read_text(encoding="utf-8") == "Final text"
    assert preview == "Final text"
    assert returned_out == str(out_path)


def test_generate_handles_missing_context(tmp_path, mock_env):
    """Missing context path results in warning and no preview."""
    missing = tmp_path / "missing.json"
    out_path = tmp_path / "fail.md"

    status, preview, returned_out = dash_app.on_generate(1, str(missing), "", "cohere", None, str(out_path), None, None)

    assert "Context path not found" in str(status)
    assert preview == ""
    assert returned_out == str(out_path)
