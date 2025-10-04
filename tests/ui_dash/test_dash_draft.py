"""Test draft editor callbacks."""
from pathlib import Path
from types import SimpleNamespace

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _set_trigger(monkeypatch, button_id: str):
    monkeypatch.setattr(dash_app, "ctx", SimpleNamespace(triggered_id=button_id))


def test_draft_load(tmp_path, mock_env, monkeypatch):
    """Loading a draft returns file contents and updates the store."""
    draft_file = tmp_path / "draft.md"
    draft_file.write_text("Existing draft content", encoding="utf-8")
    _set_trigger(monkeypatch, "btn-draft-load")

    text, status, store_value = dash_app.on_draft(1, 0, str(draft_file), "")

    assert text == "Existing draft content"
    assert "Loaded:" in str(status)
    assert store_value == str(draft_file)


def test_draft_save(tmp_path, mock_env, monkeypatch):
    """Saving a draft writes content to disk and returns success status."""
    draft_file = tmp_path / "draft_save.md"
    _set_trigger(monkeypatch, "btn-draft-save")

    text, status, store_value = dash_app.on_draft(0, 1, str(draft_file), "New draft text")

    assert draft_file.exists()
    assert draft_file.read_text(encoding="utf-8") == "New draft text"
    assert text == "New draft text"
    assert "Saved:" in str(status)
    assert store_value == str(draft_file)


def test_draft_updates_store_with_nested_path(tmp_path, mock_env, monkeypatch):
    """Saving to nested path creates directories and updates store data."""
    draft_file = tmp_path / "notes" / "nested_draft.md"
    _set_trigger(monkeypatch, "btn-draft-save")

    _, status, store_value = dash_app.on_draft(0, 2, str(draft_file), "Nested content")

    assert draft_file.exists()
    assert draft_file.read_text(encoding="utf-8") == "Nested content"
    assert "Saved:" in str(status)
    assert store_value == str(draft_file)


def test_draft_handles_missing_file(tmp_path, mock_env, monkeypatch):
    """Loading a non-existent draft returns warning without updating store."""
    missing_file = tmp_path / "missing.md"
    _set_trigger(monkeypatch, "btn-draft-load")

    text, status, store_value = dash_app.on_draft(1, 0, str(missing_file), "")

    assert text == ""
    assert "File not found" in str(status)
    assert store_value is None
