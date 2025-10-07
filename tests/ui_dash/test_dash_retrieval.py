"""Test retrieval tab functionality."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import caliper_v2.ui_dash.app as dash_app


pytestmark = [pytest.mark.integration, pytest.mark.ui]


def _build_default_args(question: str, out_path: Path):
    """Helper to build common callback arguments."""
    return (
        1,
        question,
        "design",
        40,
        20,
        str(out_path),
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


def test_retrieval_command_generation(tmp_path, mock_env, monkeypatch):
    """Verify the retrieval command string includes expected arguments."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    out_path = tmp_path / "context.json"

    mock_result = SimpleNamespace(returncode=1, stdout="mock stdout", stderr="")
    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=mock_result):
        command, logs, ui_component, store_value, ret_out = dash_app.on_retrieve(
            1,
            "How do we comply with bridge design rules?",
            "design,state",
            25,
            10,
            str(out_path),
            "openai",
            "gpt-4o",
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

    assert command.startswith("poetry run caliper_v2")
    assert '--indexes "design,state"' in command
    assert "--llm-provider openai" in command
    assert "--llm-model gpt-4o" in command
    assert command.endswith(f'--out "{out_path}"')
    assert logs.strip() == "mock stdout"
    assert store_value is None
    assert ret_out == str(out_path)
    assert "Retrieval failed" in str(ui_component)


def test_retrieval_with_basic_inputs(sample_retrieval_result, mock_env, monkeypatch):
    """Successful run with basic inputs returns success alert and updates fields."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", sample_retrieval_result.parent)

    mock_result = SimpleNamespace(returncode=0, stdout="retrieval ok", stderr="")
    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=mock_result):
        command, logs, ui_component, store_value, ret_out = dash_app.on_retrieve(
            2,
            "Show me recent design updates",
            "design",
            40,
            20,
            str(sample_retrieval_result),
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

    assert command.startswith("poetry run caliper_v2")
    assert "retrieval ok" in logs
    assert store_value == str(sample_retrieval_result)
    assert ret_out == str(sample_retrieval_result)


def test_retrieval_with_advanced_options(tmp_path, mock_env, monkeypatch):
    """Advanced retrieval options are forwarded to command builders."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    out_path = tmp_path / "advanced.json"

    with (
        patch("caliper_v2.ui_dash.app.windows_retrieve_command", return_value="cmd") as mock_cmd,
        patch("caliper_v2.ui_dash.app.windows_retrieve_argv", return_value=["poetry", "run"]) as mock_argv,
        patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr=""))
    ):
        dash_app.on_retrieve(
            3,
            "Explain dense retrieval",
            "design",
            30,
            15,
            str(out_path),
            "cohere",
            "command-r-plus",
            "auto_routed",
            24,
            50,
            0.35,
            "safety",
            "appendix",
            '{"division": "A"}',
            ["infer"],
            2,
            ["hyde"],
        )

    kwargs = mock_cmd.call_args.kwargs
    assert kwargs["retrieval_mode"] == "auto_routed"
    assert kwargs["dense_k"] == 24
    assert kwargs["sparse_k"] == 50
    assert kwargs["alpha"] == 0.35
    assert kwargs["include_terms"] == "safety"
    assert kwargs["exclude_sections"] == "appendix"
    assert kwargs["filters"] == '{"division": "A"}'
    assert kwargs["infer_filters"] is True
    assert kwargs["expand_queries"] == 2
    assert kwargs["hyde"] is True

    argv_kwargs = mock_argv.call_args.kwargs
    assert argv_kwargs["retrieval_mode"] == "auto_routed"
    assert argv_kwargs["dense_k"] == 24
    assert argv_kwargs["sparse_k"] == 50
    assert argv_kwargs["alpha"] == 0.35
    assert argv_kwargs["include_terms"] == "safety"
    assert argv_kwargs["exclude_sections"] == "appendix"
    assert argv_kwargs["filters"] == '{"division": "A"}'
    assert argv_kwargs["infer_filters"] is True
    assert argv_kwargs["expand_queries"] == 2
    assert argv_kwargs["hyde"] is True


def test_retrieval_subprocess_execution(tmp_path, mock_env, monkeypatch):
    """Subprocess executes with argv returned by windows_retrieve_argv."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    out_path = tmp_path / "context.json"
    expected_argv = ["poetry", "run", "caliper_v2", "retrieve"]

    with (
        patch("caliper_v2.ui_dash.app.windows_retrieve_command", return_value="cmd"),
        patch("caliper_v2.ui_dash.app.windows_retrieve_argv", return_value=expected_argv) as mock_argv,
        patch("caliper_v2.ui_dash.app.subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="")) as mock_run,
    ):
        dash_app.on_retrieve(*_build_default_args("How many violations?", out_path))

    mock_argv.assert_called_once()
    mock_run.assert_called_once_with(expected_argv, shell=False, capture_output=True, text=True)


def test_retrieval_updates_store(sample_retrieval_result, mock_env, monkeypatch):
    """Store output path updates when CLI writes to requested file."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", sample_retrieval_result.parent)

    mock_result = SimpleNamespace(returncode=0, stdout="done", stderr="")
    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=mock_result):
        _, _, _, store_value, ret_out = dash_app.on_retrieve(
            4,
            "Retrieve draft context",
            "design",
            40,
            20,
            str(sample_retrieval_result),
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

    assert store_value == str(sample_retrieval_result)
    assert ret_out == str(sample_retrieval_result)


def test_retrieval_displays_preview_table(sample_retrieval_result, mock_env, monkeypatch):
    """Preview table renders rows from retrieval output."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", sample_retrieval_result.parent)

    mock_result = SimpleNamespace(returncode=0, stdout="ok", stderr="")
    with patch("caliper_v2.ui_dash.app.subprocess.run", return_value=mock_result):
        _, _, ui_component, _, _ = dash_app.on_retrieve(
            5,
            "Preview retrieval",
            "design",
            40,
            20,
            str(sample_retrieval_result),
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

    component_repr = str(ui_component)
    assert "test_design_doc.pdf" in component_repr
    assert "Design Requirements" in component_repr


def test_retrieval_handles_empty_question(tmp_path, mock_env, monkeypatch):
    """Empty questions trigger a validation warning."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    out_path = tmp_path / "context.json"

    command, logs, ui_component, store_value, ret_out = dash_app.on_retrieve(*_build_default_args("", out_path))

    assert command == ""
    assert logs == ""
    assert "Invalid prompt: Prompt cannot be empty." in str(ui_component)
    assert store_value is None
    assert ret_out == str(out_path)


def test_retrieval_file_output_detection(tmp_path, mock_env, monkeypatch):
    """Newly created files are detected when CLI writes a different name."""
    monkeypatch.setitem(dash_app.base_paths, "ctx_dir", tmp_path)
    requested_out = tmp_path / "requested.json"
    generated_out = tmp_path / "generated.json"

    def run_side_effect(argv, shell, capture_output, text):
        data = {
            "retrieval": {
                "nodes": [
                    {
                        "text": "Auto generated",
                        "score": 0.75,
                        "metadata": {"file_name": "auto.pdf", "page": 2, "section": "Auto"},
                    }
                ]
            }
        }
        generated_out.write_text(json.dumps(data))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    with patch("caliper_v2.ui_dash.app.subprocess.run", side_effect=run_side_effect):
        _, _, ui_component, store_value, ret_out = dash_app.on_retrieve(
            6,
            "Detect generated file",
            "design",
            40,
            20,
            str(requested_out),
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

    assert store_value == str(generated_out)
    assert ret_out == str(generated_out)
    assert "generated.json" in str(ui_component)
