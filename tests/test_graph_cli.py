from __future__ import annotations

import subprocess
from pathlib import Path


def test_graph_cli_help_invokes():
    # Ensure the subcommand is registered and help runs without error
    result = subprocess.run(["poetry", "run", "caliper_v2", "graph", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "GraphRAG" in (result.stdout or "")


def test_graph_stats_missing(tmp_path: Path):
    # Stats should error with non-zero if manifest missing
    result = subprocess.run(["poetry", "run", "caliper_v2", "graph", "stats", "--graph-dir", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode != 0
