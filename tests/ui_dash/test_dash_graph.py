"""Test GraphRAG retrieval workflows in Dash UI."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _graph_args(question: str, graph_dir: Path, out_path: Path, mix=False):
    """Return common callback args for graph retrieval."""
    mix_vals = ["mix"] if mix else []
    text_indexes = "design" if mix else ""
    top_k = 30 if mix else 40
    rerank = 10 if mix else 20
    return (
        1,
        question,
        str(graph_dir),
        2,
        150,
        str(out_path),
        mix_vals,
        text_indexes,
        top_k,
        rerank,
        "cohere",
        "command-r-plus",
    )


def _write_graph_result(path: Path):
    data = {
        "retrieval": {
            "nodes": [
                {
                    "text": "Graph node",
                    "score": 0.88,
                    "metadata": {"file_name": "graph.pdf", "page": 3, "section": "Connections"},
                }
            ]
        }
    }
    path.write_text(json.dumps(data))


def test_graph_retrieval_command_generation(tmp_path, mock_env, monkeypatch):
    """Builds graph retrieval command with expected base flags."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    out_path = tmp_path / "graph_out.json"

    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="")):
        command, logs, ui_component, store_value, ret_out = dash_app.on_graph_retrieve(*_graph_args("Find related bridges", graph_dir, out_path))

    assert command.startswith("poetry run caliper_v2 graph retrieve")
    assert f"--graph-dir \"{graph_dir}" in command
    assert f'--out "{out_path}"' in command
    assert "--mix-with-text" not in command
    assert store_value is None
    assert ret_out == str(out_path)
    assert "GraphRAG command failed" in str(ui_component)


def test_graph_retrieval_with_mixing(tmp_path, mock_env, monkeypatch):
    """Mixing text retrieval adds expected flags to command and argv."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    out_path = tmp_path / "graph_mix.json"

    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="")) as mock_subproc:
        command, _, _, _, _ = dash_app.on_graph_retrieve(*_graph_args("Mix graph", graph_dir, out_path, mix=True))

    assert "--mix-with-text" in command
    assert '--text-indexes "design"' in command
    argv = mock_subproc.call_args[0][0]
    assert "--mix-with-text" in argv
    assert "--text-indexes" in argv
    assert "design" in argv


def test_graph_retrieval_subprocess_execution(tmp_path, mock_env, monkeypatch):
    """Subprocess is invoked with shell disabled for graph retrieval."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    out_path = tmp_path / "graph_run.json"

    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="")) as mock_run:
        dash_app.on_graph_retrieve(*_graph_args("Run graph", graph_dir, out_path))

    mock_run.assert_called_once()
    argv, *_ = mock_run.call_args[0]
    assert argv[0:4] == ["poetry", "run", "caliper_v2", "graph"]
    assert mock_run.call_args.kwargs["shell"] is False
    assert mock_run.call_args.kwargs["capture_output"] is True
    assert mock_run.call_args.kwargs["text"] is True


def test_graph_retrieval_without_mixing(tmp_path, mock_env, monkeypatch):
    """Text indexes are ignored unless mixing flag is enabled."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    out_path = tmp_path / "graph_plain.json"

    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="")) as mock_run:
        command, _, _, _, _ = dash_app.on_graph_retrieve(
            1,
            "Plain graph",
            str(graph_dir),
            2,
            150,
            str(out_path),
            [],
            "design",
            40,
            20,
            None,
            None,
        )

    assert "--mix-with-text" not in command
    assert "--text-indexes" not in command
    argv = mock_run.call_args[0][0]
    assert "--mix-with-text" not in argv
    assert "--text-indexes" not in argv


def test_graph_updates_store(tmp_path, mock_env, monkeypatch):
    """Store path updates to the resolved output file when run succeeds."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    out_path = tmp_path / "graph_success.json"
    _write_graph_result(out_path)

    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="done", stderr="")):
        _, logs, ui_component, store_value, ret_out = dash_app.on_graph_retrieve(*_graph_args("Success graph", graph_dir, out_path))

    assert "done" in logs
    assert store_value == str(out_path)
    assert ret_out == str(out_path)
    assert "GraphRAG successful" in str(ui_component)


def test_graph_displays_results(tmp_path, mock_env, monkeypatch):
    """Result table includes metadata from rendered graph retrieval."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    out_path = tmp_path / "graph_preview.json"
    _write_graph_result(out_path)

    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
        _, _, ui_component, _, _ = dash_app.on_graph_retrieve(*_graph_args("Preview graph", graph_dir, out_path))

    component_repr = str(ui_component)
    assert "graph.pdf" in component_repr
    assert "Connections" in component_repr
