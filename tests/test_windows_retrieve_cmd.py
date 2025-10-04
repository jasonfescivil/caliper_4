from __future__ import annotations

from pathlib import Path
import sys
# Ensure src/ is on sys.path for direct module imports under Poetry
ROOT = Path(__file__).resolve().parents[1]
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from caliper_v2.services.judge_components import windows_retrieve_command, windows_retrieve_argv


def test_retrieve_cmd_includes_advanced_flags():
    cmd = windows_retrieve_command(
        "What is alpha blend?",
        ["design"],
        "C:/tmp/out.json",
        top_k=50,
        rerank_top_n=24,
        llm_provider="cohere",
        llm_model="command-a-reasoning-08-2025",
        retrieval_mode="auto_routed",
        dense_k=12,
        sparse_k=12,
        alpha=0.5,
        include_terms="planning, horizon",
        exclude_sections="toc,glossary",
        filters='{"jurisdiction":"WA"}',
        infer_filters=True,
        expand_queries=4,
        hyde=False,
    )
    # Ensure key flags appear in the command string
    assert "--retrieval-mode auto_routed" in cmd
    assert "--dense-k 12" in cmd and "--sparse-k 12" in cmd
    assert "--alpha 0.5" in cmd
    assert "--include-terms \"planning, horizon\"" in cmd
    assert "--exclude-sections \"toc,glossary\"" in cmd
    assert "--filters '{\"jurisdiction\":\"WA\"}'" in cmd
    assert "--infer-filters" in cmd
    assert "--expand-queries 4" in cmd
    assert "--no-hyde" in cmd


def test_retrieve_argv_includes_advanced_flags():
    argv = windows_retrieve_argv(
        "What is alpha blend?",
        ["design"],
        "C:/tmp/out.json",
        top_k=50,
        rerank_top_n=24,
        llm_provider="cohere",
        llm_model="command-a-reasoning-08-2025",
        retrieval_mode="auto_routed",
        dense_k=12,
        sparse_k=12,
        alpha=0.5,
        include_terms="planning, horizon",
        exclude_sections="toc,glossary",
        filters='{"jurisdiction":"WA"}',
        infer_filters=True,
        expand_queries=4,
        hyde=False,
    )
    s = " ".join(argv)
    assert "--retrieval-mode auto_routed" in s
    assert "--dense-k 12" in s and "--sparse-k 12" in s
    assert "--alpha 0.5" in s
    assert "--include-terms planning, horizon" in s
    assert "--exclude-sections toc,glossary" in s
    assert "--filters {\"jurisdiction\":\"WA\"}" in s
    assert "--infer-filters" in s
    assert "--expand-queries 4" in s
    assert "--no-hyde" in s
