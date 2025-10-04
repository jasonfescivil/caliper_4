"""Test cross-tab state management for Dash UI."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _set_trigger(monkeypatch, trigger_id: str):
    """Set dash callback context for button triggering."""
    monkeypatch.setattr(dash_app, "ctx", SimpleNamespace(triggered_id=trigger_id))


def _make_json(path: Path, payload: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {"ok": True}), encoding="utf-8")
    return path


def test_provider_state_prefills_generate_controls(monkeypatch):
    """Provider selection persists through the generate tab sync callback."""
    _set_trigger(monkeypatch, "btn-apply-provider")
    provider, model, status = dash_app.on_apply_provider(1, 0, 0, "anthropic", "claude-opus-4-1")

    assert provider == "anthropic"
    assert model == "claude-opus-4-1"
    assert status  # status list contains alerts

    gen_provider, gen_model = dash_app.sync_generate_controls("tab-generate", provider, model)
    assert gen_provider == "anthropic"
    assert gen_model == "claude-opus-4-1"


def test_retrieval_store_serves_enhance_input(tmp_path, mock_env, monkeypatch):
    """Retrieval output path flows into enhance callback when input blank."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    request_out = tmp_path / "retrieval.json"

    def _fake_run(argv, shell, capture_output, text):
        _make_json(request_out, {"retrieval": {"nodes": []}})
        return SimpleNamespace(returncode=0, stdout="done", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=_fake_run):
        _, _, _, store_value, _ = dash_app.on_retrieve(
            1,
            "Retrieve state",
            "design",
            40,
            20,
            str(request_out),
            None,
            None,
            None,
            None,
            None,
            None,
            "",
            "",
            "",
            [],
            None,
            [],
        )

    assert store_value == str(request_out)

    enhanced_out = tmp_path / "enhanced.json"
    with patch("caliper_v2.ui_dash.app.enhance_cmd.main") as mock_main:
        status, enhanced_store, ctx_value = dash_app.on_enhance(1, "", str(enhanced_out), store_value)

    mock_main.assert_called_once()
    assert enhanced_store == str(enhanced_out)
    assert ctx_value == str(request_out)
    assert "Enhanced context written" in str(status)


def test_enhanced_path_drives_generation(tmp_path, mock_env):
    """Enhanced store path can be used directly for generation callback."""
    ctx_path = _make_json(tmp_path / "ctx.json")
    enhanced_out = tmp_path / "enhanced.json"

    def _fake_enhance(**kwargs):
        _make_json(enhanced_out, {"context": "enhanced"})
        return {"json": kwargs}

    with patch("caliper_v2.ui_dash.app.enhance_cmd.main", side_effect=_fake_enhance):
        status, enhanced_store, returned_ctx = dash_app.on_enhance(1, str(ctx_path), str(enhanced_out), None)

    assert enhanced_store == str(enhanced_out)
    assert returned_ctx == str(ctx_path)

    draft_out = tmp_path / "draft.md"
    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="draft text"),
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, returned_out = dash_app.on_generate(
            1,
            str(enhanced_store),
            "Formal",
            "cohere",
            None,
            str(draft_out),
            None,
            None,
        )

    assert draft_out.exists()
    assert preview == "draft text"
    assert returned_out == str(draft_out)
    assert any("Generation complete" in str(alert) for alert in alerts)


def test_draft_store_used_for_review(tmp_path, mock_env, monkeypatch):
    """Draft store output becomes review input without rewriting path."""
    ctx_file = _make_json(tmp_path / "ctx.json")
    draft_file = tmp_path / "draft.md"
    draft_file.write_text("draft body", encoding="utf-8")

    _set_trigger(monkeypatch, "btn-draft-save")
    text, status, store_value = dash_app.on_draft(0, 1, str(draft_file), "draft body")

    assert store_value == str(draft_file)
    assert "Saved" in str(status)

    out_json = tmp_path / "review.json"
    out_md = tmp_path / "review.md"

    def _fake_review(**kwargs):
        _make_json(out_json, {})
        Path(out_md).write_text("report", encoding="utf-8")
        return kwargs

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_fake_review):
        status, md_preview, stored_json, stored_md = dash_app.on_review(
            1,
            str(ctx_file),
            store_value,
            str(out_json),
            str(out_md),
            [],
            5,
        )

    assert stored_json == str(out_json)
    assert stored_md == str(out_md)
    assert md_preview == "report"
    assert "Review complete" in str(status)


def test_review_store_outputs_round_trip(tmp_path, mock_env):
    """Review outputs can be re-used as inputs for subsequent actions."""
    ctx_file = _make_json(tmp_path / "ctx.json")
    draft_file = tmp_path / "draft.md"
    draft_file.write_text("draft", encoding="utf-8")
    out_json = tmp_path / "first.json"
    out_md = tmp_path / "first.md"

    def _fake_review(**kwargs):
        _make_json(out_json, {"ok": True})
        Path(out_md).write_text("initial", encoding="utf-8")
        return {"json": str(out_json), "md": str(out_md)}

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_fake_review):
        status, md_preview, stored_json, stored_md = dash_app.on_review(
            1,
            str(ctx_file),
            str(draft_file),
            str(out_json),
            str(out_md),
            ["strict"],
            4,
        )

    assert stored_json == str(out_json)
    assert stored_md == str(out_md)
    assert "initial" in md_preview
    assert "Review complete" in str(status)
