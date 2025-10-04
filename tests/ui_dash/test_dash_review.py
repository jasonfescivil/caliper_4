"""Test review tab callback logic."""
from pathlib import Path
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _create_file(path: Path, content: str = "{}") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _review_args(ctx: Path, draft: Path, out_json: Path, out_md: Path, strict_vals=None, max_ev=5):
    return (
        1,
        str(ctx),
        str(draft),
        str(out_json),
        str(out_md),
        strict_vals or [],
        max_ev,
    )


def test_review_calls_command(tmp_path, mock_env):
    """Review command is invoked with sanitized arguments."""
    ctx = _create_file(tmp_path / "ctx.json", "context")
    draft = _create_file(tmp_path / "draft.md", "draft text")
    out_json = tmp_path / "review.json"
    out_md = tmp_path / "review.md"

    def _fake_review(**kwargs):
        Path(kwargs["out_json"]).write_text("{}", encoding="utf-8")
        Path(kwargs["out_md"]).write_text("Report", encoding="utf-8")
        return {"json": kwargs["out_json"], "md": kwargs["out_md"]}

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_fake_review) as mock_main:
        status, md_preview, stored_json, stored_md = dash_app.on_review(*_review_args(ctx, draft, out_json, out_md, max_ev=7))

    mock_main.assert_called_once()
    kwargs = mock_main.call_args.kwargs
    assert kwargs["context_path"] == str(ctx)
    assert kwargs["draft_path"] == str(draft)
    assert kwargs["out_json"] == str(out_json)
    assert kwargs["out_md"] == str(out_md)
    assert kwargs["strict"] is False
    assert kwargs["max_evidence_per_claim"] == 7
    assert "Review complete" in str(status)
    assert md_preview == "Report"
    assert stored_json == str(out_json)
    assert stored_md == str(out_md)


def test_review_strict_mode(tmp_path, mock_env):
    """Strict checkbox enables strict flag in review command."""
    ctx = _create_file(tmp_path / "ctx.json", "context")
    draft = _create_file(tmp_path / "draft.md", "draft text")
    out_json = tmp_path / "strict.json"
    out_md = tmp_path / "strict.md"

    def _fake_review(**kwargs):
        Path(kwargs["out_json"]).write_text("{}", encoding="utf-8")
        Path(kwargs["out_md"]).write_text("Strict report", encoding="utf-8")
        return kwargs

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_fake_review) as mock_main:
        status, md_preview, stored_json, stored_md = dash_app.on_review(*_review_args(ctx, draft, out_json, out_md, strict_vals=["strict"], max_ev=3))

    kwargs = mock_main.call_args.kwargs
    assert kwargs["strict"] is True
    assert kwargs["max_evidence_per_claim"] == 3
    assert "Review complete" in str(status)
    assert "Strict report" in md_preview
    assert stored_json == str(out_json)
    assert stored_md == str(out_md)


def test_review_creates_outputs(tmp_path, mock_env):
    """Callback surfaces alternate output paths returned by command."""
    ctx = _create_file(tmp_path / "ctx.json", "context")
    draft = _create_file(tmp_path / "draft.md", "draft text")
    out_json = tmp_path / "requested.json"
    out_md = tmp_path / "requested.md"
    alt_json = tmp_path / "alt" / "review.json"
    alt_md = tmp_path / "alt" / "review.md"

    def _fake_review(**kwargs):
        _create_file(alt_json, "{}")
        _create_file(alt_md, "Alt review")
        return {"json": str(alt_json), "md": str(alt_md)}

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_fake_review):
        status, md_preview, stored_json, stored_md = dash_app.on_review(*_review_args(ctx, draft, out_json, out_md))

    assert stored_json == str(alt_json)
    assert stored_md == str(alt_md)
    assert "Alt review" in md_preview
    assert "Review complete" in str(status)


def test_review_displays_preview(tmp_path, mock_env):
    """Markdown preview contents are returned to the UI."""
    ctx = _create_file(tmp_path / "ctx.json", "context")
    draft = _create_file(tmp_path / "draft.md", "draft text")
    out_json = tmp_path / "preview.json"
    out_md = tmp_path / "preview.md"

    def _fake_review(**kwargs):
        Path(kwargs["out_json"]).write_text("{}", encoding="utf-8")
        Path(kwargs["out_md"]).write_text("Preview content", encoding="utf-8")
        return kwargs

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_fake_review):
        status, md_preview, stored_json, stored_md = dash_app.on_review(*_review_args(ctx, draft, out_json, out_md))

    assert md_preview == "Preview content"
    assert stored_json == str(out_json)
    assert stored_md == str(out_md)
    assert "Review complete" in str(status)


def test_review_handles_missing_inputs(tmp_path, mock_env):
    """Missing context or draft returns warning and no stored outputs."""
    ctx = tmp_path / "missing_ctx.json"
    draft = tmp_path / "missing_draft.md"
    out_json = tmp_path / "unused.json"
    out_md = tmp_path / "unused.md"

    status, md_preview, stored_json, stored_md = dash_app.on_review(*_review_args(ctx, draft, out_json, out_md))

    assert "Context or Draft path not found" in str(status)
    assert md_preview == ""
    assert stored_json is None
    assert stored_md is None
