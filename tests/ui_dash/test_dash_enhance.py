"""Test enhancement tab callbacks."""
from pathlib import Path
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _create_context(tmp_path: Path, name: str = "retrieval.json") -> Path:
    ctx = tmp_path / name
    ctx.write_text("{}")
    return ctx


def test_enhance_calls_command(tmp_path, mock_env):
    """Enhance command is invoked with expected keyword arguments."""
    ctx_path = _create_context(tmp_path)
    out_path = tmp_path / "enhanced.json"

    with patch("caliper_v2.ui_dash.app.enhance_cmd.main") as mock_main:
        status, store_value, returned_ctx = dash_app.on_enhance(1, str(ctx_path), str(out_path), None)

    mock_main.assert_called_once_with(
        in_path=str(ctx_path),
        out_path=str(out_path),
        write_outline=True,
        rewrite_spore=True,
        suggest_retrieve=True,
    )
    assert "Enhanced context written" in str(status)
    assert store_value == str(out_path)
    assert returned_ctx == str(ctx_path)


def test_enhance_with_retrieval_path(tmp_path, mock_env):
    """Stored retrieval path is used when ctx input is empty."""
    stored_ctx = _create_context(tmp_path, "stored.json")
    out_path = tmp_path / "enhanced_from_store.json"

    with patch("caliper_v2.ui_dash.app.enhance_cmd.main") as mock_main:
        status, store_value, returned_ctx = dash_app.on_enhance(1, "", str(out_path), str(stored_ctx))

    mock_main.assert_called_once()
    assert mock_main.call_args.kwargs["in_path"] == str(stored_ctx)
    assert store_value == str(out_path)
    assert returned_ctx == str(stored_ctx)
    assert "Enhanced context written" in str(status)


def test_enhance_creates_output_file(tmp_path, mock_env):
    """Enhance callback surfaces success after command writes output file."""
    ctx_path = _create_context(tmp_path)
    out_path = tmp_path / "nested" / "enhanced.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _fake_main(in_path: str, out_path: str, **kwargs):
        Path(out_path).write_text("{\"status\": \"ok\"}")

    with patch("caliper_v2.ui_dash.app.enhance_cmd.main", side_effect=_fake_main):
        status, store_value, returned_ctx = dash_app.on_enhance(1, str(ctx_path), f'"{out_path}"', None)

    assert out_path.exists()
    assert store_value == str(out_path)
    assert returned_ctx == str(ctx_path)
    assert hasattr(status, "children")
    assert str(out_path) in str(status.children)


def test_enhance_updates_store(tmp_path, mock_env):
    """Output store reflects sanitized paths even when quoted."""
    ctx_path = _create_context(tmp_path, "quoted.json")
    out_path = tmp_path / "quoted-enhanced.json"

    with patch("caliper_v2.ui_dash.app.enhance_cmd.main"):
        status, store_value, returned_ctx = dash_app.on_enhance(1, f'"{ctx_path}"', f'"{out_path}"', None)

    assert store_value == str(out_path)
    assert returned_ctx == str(ctx_path)
    assert "Enhanced context written" in str(status)


def test_enhance_handles_missing_input(tmp_path, mock_env):
    """Missing context path returns validation warning and no store data."""
    out_path = tmp_path / "should_not_write.json"

    status, store_value, returned_ctx = dash_app.on_enhance(1, " ", str(out_path), None)

    assert "Context path not found" in str(status)
    assert store_value is None
    assert returned_ctx.strip() == ""
