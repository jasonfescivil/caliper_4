from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich import print

from caliper_v2.services.local_kb import LocalKnowledgeBase

app = typer.Typer(
    name="kb",
    help="Local Knowledge Base commands (SQLite-backed)",
    no_args_is_help=True,
)


@app.command(name="build-kb", help="Build the local KB from the knowledge_base/ directory")
def build_kb(
    kb_dir: Path = typer.Option(
        "knowledge_base/",
        "--kb-dir",
        "-d",
        help="Directory containing .md and .txt files to index.",
    ),
    db_path: Path = typer.Option(
        "data_v2/kb_v1.sqlite",
        "--db-path",
        "-db",
        help="Path to the SQLite database file.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-indexing of all files."),
):
    """Builds or updates the local knowledge base."""
    kb = LocalKnowledgeBase(db_path=db_path)
    logger.info(f"Using KB at: {kb.paths.db_path.resolve()}")

    if not kb_dir.exists() or not kb_dir.is_dir():
        logger.error(f"Knowledge base directory not found: {kb_dir}")
        raise typer.Exit(1)

    # TODO: Add hash-based incremental build
    stats = kb.index_corpus(kb_dir, file_hashes=None)
    print(f"KB build complete. Stats: {stats}")


@app.command(name="kb-retrieve", help="Retrieve from the local KB")
def kb_retrieve(
    question: str = typer.Argument(..., help="Question to ask the KB"),
    limit: int = typer.Option(10, "--limit", "-k", help="Number of results to return"),
    db_path: Path = typer.Option(
        "data_v2/kb_v1.sqlite",
        "--db-path",
        "-db",
        help="Path to the SQLite database file.",
    ),
    merge_with: Optional[Path] = typer.Option(
        None,
        "--merge-with",
        "-m",
        help="Path to a JSON file with text search results to fuse with.",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Path to save the results as a JSON file."
    ),
):
    """Retrieves documents from the local KB and optionally fuses with other results."""
    kb = LocalKnowledgeBase(db_path=db_path)
    logger.info(f"Querying KB: '{question}'")
    kb_hits = kb.search(question, limit=limit)

    if merge_with:
        if not merge_with.exists():
            logger.error(f"Merge file not found: {merge_with}")
            raise typer.Exit(1)
        logger.info(f"Fusing with results from: {merge_with}")
        text_hits_data = json.loads(merge_with.read_text())
        text_hits = text_hits_data.get("results", [])
        fused_results = LocalKnowledgeBase.fuse(kb_hits, text_hits, limit=limit)
        results = {"question": question, "results": fused_results}
    else:
        results = {"question": question, "results": kb_hits}

    if output:
        output.write_text(json.dumps(results, indent=2))
        logger.info(f"Results saved to: {output}")
    else:
        print(json.dumps(results, indent=2))
