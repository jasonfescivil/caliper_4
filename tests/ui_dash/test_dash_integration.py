"""Integration-style tests covering multi-tab workflows."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _write_json(path: Path, payload: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {}), encoding="utf-8")
    return path


def test_retrieval_enhance_generate_flow(tmp_path, mock_env, monkeypatch):
    """End-to-end flow from retrieval through generate produces draft output."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    retrieval_out = tmp_path / "ctx" / "retrieval.json"

    def _run_retrieval(argv, shell, capture_output, text):
        _write_json(
            retrieval_out,
            {
                "retrieval": {
                    "nodes": [
                        {"text": "answer", "score": 0.9, "metadata": {"file_name": "doc.pdf", "page": 1}}
                    ]
                }
            },
        )
        return SimpleNamespace(returncode=0, stdout="retrieved", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=_run_retrieval):
        _, _, _, retrieve_store, _ = dash_app.on_retrieve(
            1,
            "Describe bridge loads",
            "design",
            40,
            20,
            str(retrieval_out),
            "cohere",
            "command-r-plus",
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

    enhanced_out = tmp_path / "enhanced.json"

    def _run_enhance(**kwargs):
        _write_json(enhanced_out, {"context": "enhanced"})

    with patch("caliper_v2.ui_dash.app.enhance_cmd.main", side_effect=_run_enhance):
        status, enhanced_store, returned_ctx = dash_app.on_enhance(1, "", str(enhanced_out), retrieve_store)

    assert enhanced_store == str(enhanced_out)
    assert returned_ctx == retrieve_store
    assert "Enhanced context" in str(status)

    draft_out = tmp_path / "draft.md"
    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="draft body"),
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, out_value = dash_app.on_generate(
            1,
            enhanced_store,
            "Concise",
            "cohere",
            None,
            str(draft_out),
            None,
            None,
        )

    assert draft_out.exists()
    assert preview == "draft body"
    assert out_value == str(draft_out)
    assert any("Generation complete" in str(alert) for alert in alerts)


def test_retrieval_and_graph_stores_isolated(tmp_path, mock_env, monkeypatch):
    """Graph retrieval store does not overwrite text retrieval store."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    graph_out = tmp_path / "graph.json"

    def _run_graph(argv, shell, capture_output, text):
        _write_json(graph_out, {"retrieval": {"nodes": []}})
        return SimpleNamespace(returncode=0, stdout="graph", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=_run_graph):
        _, _, _, graph_store, _ = dash_app.on_graph_retrieve(
            1,
            "Graph question",
            str(graph_dir),
            2,
            150,
            str(graph_out),
            ["mix"],
            "design",
            35,
            15,
            "anthropic",
            "claude",
        )

    assert graph_store == str(graph_out)

    text_out = tmp_path / "text.json"

    def _run_text(argv, shell, capture_output, text):
        _write_json(text_out, {"retrieval": {"nodes": []}})
        return SimpleNamespace(returncode=0, stdout="text", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=_run_text):
        _, _, _, text_store, _ = dash_app.on_retrieve(
            1,
            "Text question",
            "design",
            20,
            10,
            str(text_out),
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

    assert text_store == str(text_out)
    assert text_store != graph_store


def test_generate_then_review_round_trip(tmp_path, mock_env):
    """Generated draft can immediately feed review command."""
    ctx_path = _write_json(tmp_path / "ctx.json", {"context": "value"})
    draft_out = tmp_path / "draft.md"

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="draft text"),
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, draft_store = dash_app.on_generate(
            1,
            str(ctx_path),
            "Formal",
            "cohere",
            None,
            str(draft_out),
            None,
            None,
        )

    assert draft_store == str(draft_out)
    assert draft_out.read_text(encoding="utf-8") == "draft text"

    review_json = tmp_path / "review.json"
    review_md = tmp_path / "review.md"

    def _run_review(**kwargs):
        _write_json(review_json, {"score": 1})
        review_md.write_text("review report", encoding="utf-8")
        return {"json": str(review_json), "md": str(review_md)}

    with patch("caliper_v2.ui_dash.app.review_cmd.main", side_effect=_run_review):
        status, md_preview, stored_json, stored_md = dash_app.on_review(
            1,
            str(ctx_path),
            draft_store,
            str(review_json),
            str(review_md),
            ["strict"],
            5,
        )

    assert "Review complete" in str(status)
    assert md_preview == "review report"
    assert stored_json == str(review_json)
    assert stored_md == str(review_md)


def test_provider_selection_normalizes_generate(tmp_path, mock_env, monkeypatch):
    """Provider normalization feeds generate callback with updated model."""
    monkeypatch.setattr(dash_app, "ctx", SimpleNamespace(triggered_id="btn-apply-provider"))
    provider, model, _ = dash_app.on_apply_provider(1, 0, 0, "openai", "gpt-4")

    ctx_file = _write_json(tmp_path / "ctx.json")
    out_file = tmp_path / "out.md"

    with (
        patch("caliper_v2.ui_dash.app.synthesize_from_context", return_value="text"),
        patch("caliper_v2.core.llm_providers.configure_llm_provider"),
    ):
        alerts, preview, out_value = dash_app.on_generate(
            1,
            str(ctx_file),
            "",
            provider,
            model,
            str(out_file),
            None,
            None,
        )

    assert preview == "text"
    assert out_file.exists()
    assert out_value == str(out_file)
    assert provider == "openai"
    assert "gpt" in model


def test_retrieval_retry_after_failure(tmp_path, mock_env, monkeypatch):
    """Failed retrieval leaves store empty; a subsequent attempt can succeed."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    target = tmp_path / "context.json"

    # --- First attempt: Fails ---
    failure_result = SimpleNamespace(returncode=1, stdout="", stderr="error")
    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=failure_result) as mock_run:
        _, _, _, store_value, _ = dash_app.on_retrieve(
            1, "Fail once", "design", 40, 20, str(target), None, None, None, None, None, None, "", "", "", [], None, []
        )
        assert store_value is None, "Store value should be None after a failed retrieval"
        assert mock_run.call_count == 1

    # --- Second attempt: Succeeds ---
    def succeeding_run(argv, shell, capture_output, text):
        # Simulate the subprocess creating the output file
        out_path_arg = argv[argv.index("--out") + 1]
        _write_json(Path(out_path_arg), {"retrieval": {"nodes": []}})
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=succeeding_run) as mock_run:
        _, _, _, store_value, _ = dash_app.on_retrieve(
            2, "Succeed now", "design", 40, 20, str(target), None, None, None, None, None, None, "", "", "", [], None, []
        )
        assert store_value == str(target), "Store value should be the target path after a successful retrieval"
        assert mock_run.call_count == 1


def test_graph_mix_flow(tmp_path, mock_env, monkeypatch):
    """Graph retrieval mixing produces preview output and store path."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    graph_out = tmp_path / "graph_mix.json"

    def _run_graph(argv, shell, capture_output, text):
        _write_json(
            graph_out,
            {
                "retrieval": {
                    "nodes": [
                        {"text": "graph node", "score": 0.8, "metadata": {"file_name": "graph.pdf", "page": 2}}
                    ]
                }
            },
        )
        return SimpleNamespace(returncode=0, stdout="mix", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=_run_graph):
        command, logs, ui_component, store_value, ret_out = dash_app.on_graph_retrieve(
            1,
            "Mix question",
            str(graph_dir),
            2,
            120,
            str(graph_out),
            ["mix"],
            "design",
            30,
            12,
            "cohere",
            "command-r-plus",
        )

    assert "--mix-with-text" in command
    assert store_value == str(graph_out)
    component_repr = str(ui_component)
    assert "graph.pdf" in component_repr
    assert "GraphRAG successful" in component_repr
