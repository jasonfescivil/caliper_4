from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from caliper_v2.graph.builder import GraphBuilder
from caliper_v2.retrievers.graph_retriever import GraphRetriever

app = typer.Typer(help="GraphRAG commands (non-disruptive to core flows)")


def _dir(p: str) -> Path:
    q = Path(p).resolve()
    q.mkdir(parents=True, exist_ok=True)
    return q


@app.command("build")
def graph_build(
    corpus: str = typer.Option("knowledge_base", help="Folder containing .md/.csv/.xlsx source files"),
    out: str = typer.Option("data_v2/graph", help="Where to persist the graph index"),
    provider: str = typer.Option("cohere", help="LLM provider for extraction (openai|cohere|gemini|anthropic|grok)"),
    relation_mode: str = typer.Option("heuristic", help="heuristic|llm|hybrid"),
    k_hop: int = typer.Option(1, min=0, max=3, help="Intended exploration depth for later retrieval"),
    rebuild: bool = typer.Option(False, help="Ignore file hash cache and rebuild graph"),
    table_max_rows: int = typer.Option(200, help="Max rows to preview per table (CSV/XLSX)"),
    excel_all_sheets: bool = typer.Option(True, help="When ingesting Excel, include all sheets as separate sections"),
    table_rows_strategy: str = typer.Option("head", help="How to preview rows: head|tail|head_tail|sample|all"),
) -> None:
    """Build a knowledge graph from a local corpus without affecting other flows."""
    try:
        out_dir = _dir(out)
        gb = GraphBuilder(
            corpus_dir=corpus,
            out_dir=str(out_dir),
            relation_mode=relation_mode,
            llm_provider=provider,
            k_hop=k_hop,
            rebuild=rebuild,
            table_max_rows=table_max_rows,
            excel_all_sheets=excel_all_sheets,
            table_rows_strategy=table_rows_strategy,
        )
        stats = gb.build()
        typer.secho(f"Graph built to {out_dir}", fg=typer.colors.GREEN)
        typer.echo(stats)
    except Exception as exc:
        logger.exception("Graph build failed: {}", exc)
        typer.secho(f"Graph build failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("retrieve")
def graph_retrieve(
    question: str = typer.Argument(..., help="Question to retrieve context for"),
    graph_dir: str = typer.Option("data_v2/graph", help="Persisted graph directory"),
    hops: int = typer.Option(1, min=0, max=2, help="Hop expansion for neighborhood"),
    limit: int = typer.Option(200, min=1, max=2000, help="Max nodes to return"),
    out: Optional[str] = typer.Option(None, help="Write retrieval_session JSON to this path"),
    mix_with_text: bool = typer.Option(False, help="Union graph results with cloud text retrieval"),
    text_indexes: str = typer.Option("design", help="Comma-separated index names for text retrieval when mixing"),
    top_k: int = typer.Option(40, help="Text retrieval top-k"),
    rerank_top_n: int = typer.Option(20, help="Union size to keep after LLM rerank"),
    provider: Optional[str] = typer.Option(None, help="Override LLM provider for rerank"),
    model: Optional[str] = typer.Option(None, help="Override LLM model for rerank"),
) -> None:
    """Retrieve a small subgraph context and emit a retrieval_session-shaped JSON.

    When --mix-with-text is given, performs a cloud text retrieval and unions the two
    result sets, then does a lightweight LLM-based rerank to trim to rerank_top_n.
    """
    try:
        import json
        gr = GraphRetriever(persist_dir=graph_dir, hops=hops, limit=limit)
        pack_graph = gr.retrieve(question)
        graph_nodes = (pack_graph.get("retrieval") or {}).get("nodes") or []

        mixed_nodes = list(graph_nodes)

        if mix_with_text:
            try:
                from caliper_v2.services.judge_components import windows_retrieve_argv  # type: ignore
                import subprocess, tempfile
                idxs = [s.strip() for s in (text_indexes or "").split(",") if s.strip()]
                tmp_out = Path(tempfile.gettempdir()) / "caliper_graphmix_ctx.json"
                argv = windows_retrieve_argv(question, idxs, str(tmp_out), int(top_k), int(rerank_top_n), provider, model)
                result = subprocess.run(argv, shell=False, capture_output=True, text=True)
                if result.returncode == 0 and tmp_out.exists():
                    try:
                        text_pack = json.loads(tmp_out.read_text(encoding="utf-8"))
                        text_nodes = (text_pack.get("retrieval") or {}).get("nodes") or []
                        # Union by (file, section, first 40 chars hash)
                        def _key(n: dict) -> str:
                            md = n.get("metadata", {})
                            f = str(md.get("file_name") or md.get("file_path") or "")
                            s = str(md.get("section") or md.get("header") or md.get("heading") or "")
                            t = (n.get("text") or "")[:40]
                            import hashlib
                            return f"{f}|{s}|{hashlib.sha1(t.encode('utf-8',errors='ignore')).hexdigest()[:8]}"
                        seen = { _key(n): True for n in mixed_nodes }
                        for n in text_nodes:
                            k = _key(n)
                            if k not in seen:
                                mixed_nodes.append(n)
                                seen[k] = True
                    except Exception:
                        pass
            except Exception as exc:
                logger.warning("Text retrieval mixing skipped: {}", exc)

            # Optional LLM rerank of union
            try:
                from llama_index.core import Settings as _Settings  # type: ignore
                if provider or model:
                    from caliper_v2.core.llm_providers import configure_llm_provider
                    configure_llm_provider(provider or "openai", model=model)
                if getattr(_Settings, "llm", None) is not None and mixed_nodes:
                    scored = []
                    prefix = (
                        "Rate PASSAGE relevance to the Question from 0.0 to 1.0.\n"
                        f"Question: {question}\nReturn only a number.\n"
                    )
                    for n in mixed_nodes:
                        snippet = (n.get("text") or "")[:1200]
                        try:
                            r = _Settings.llm.complete(prefix + "PASSAGE:\n" + snippet + "\nSCORE:")
                            raw = getattr(r, "text", str(r)).strip()
                            import re
                            m = re.search(r"\d+(?:\.\d+)?", raw)
                            score = float(m.group(0)) if m else 0.5
                        except Exception:
                            score = 0.5
                        scored.append((score, n))
                    scored.sort(key=lambda t: float(t[0]), reverse=True)
                    mixed_nodes = [n for _, n in scored[: max(1, int(rerank_top_n))]]
            except Exception:
                pass

        out_pack = {
            "type": "retrieval_session",
            "question": question,
            "retrieval": {"nodes": mixed_nodes[: limit]},
            "source": {"graph": str(graph_dir), "mixed": bool(mix_with_text)},
        }

        payload = json.dumps(out_pack, ensure_ascii=False, indent=2)
        if out:
            p = Path(out).resolve()
            # Only create parent directory if it's not the current directory
            if p.parent != Path("."):
                p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(payload, encoding="utf-8")
            typer.secho(f"Wrote retrieval_session to {p}", fg=typer.colors.GREEN)
        else:
            typer.echo(payload)
    except Exception as exc:
        logger.exception("Graph retrieve failed: {}", exc)
        typer.secho(f"Graph retrieve failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("export-cloud")
def graph_export_cloud(
    indexes: str = typer.Option(..., help="Comma-separated LlamaCloud index names"),
    out_corpus: str = typer.Option("data_v2/cloud_corpus", help="Where to write exported Markdown corpus"),
    layer: str = typer.Option("base", help="LlamaCloud layer: base|summary (informational)"),
    max_docs: Optional[int] = typer.Option(None, help="Limit docs per index (for testing)"),
    resume: bool = typer.Option(True, help="Resume from previous cache"),
) -> None:
    """Export documents from LlamaCloud indexes to a local Markdown corpus."""
    try:
        from caliper_v2.services.llama_cloud_export import LlamaCloudExporter  # type: ignore
        idxs = [s.strip() for s in indexes.split(",") if s.strip()]
        exp = LlamaCloudExporter(out_corpus=out_corpus, indexes=idxs, layer=layer, max_docs=max_docs, resume=resume)
        res = exp.export()
        typer.secho(f"Export complete: {res}", fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"Export failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("build-cloud")
def graph_build_cloud(
    indexes: str = typer.Option(..., help="Comma-separated LlamaCloud index names"),
    out_corpus: str = typer.Option("data_v2/cloud_corpus", help="Where to write exported Markdown corpus"),
    graph_out: str = typer.Option("data_v2/graph_cloud", help="Where to persist the graph index"),
    provider: str = typer.Option("cohere", help="LLM provider for extraction"),
    relation_mode: str = typer.Option("heuristic", help="heuristic|llm|hybrid"),
    k_hop: int = typer.Option(1, min=0, max=3),
    max_docs: Optional[int] = typer.Option(None, help="Limit docs per index for testing"),
) -> None:
    """Export from LlamaCloud and immediately build a local KG from the exported corpus."""
    try:
        from caliper_v2.services.llama_cloud_export import LlamaCloudExporter  # type: ignore
        idxs = [s.strip() for s in indexes.split(",") if s.strip()]
        exp = LlamaCloudExporter(out_corpus=out_corpus, indexes=idxs, max_docs=max_docs)
        exp.export()
        # Always rebuild for a clean, deterministic graph from the exported corpus
        gb = GraphBuilder(corpus_dir=out_corpus, out_dir=graph_out, relation_mode=relation_mode, llm_provider=provider, k_hop=k_hop, rebuild=True)
        stats = gb.build()
        typer.secho(f"Build complete. Graph at {graph_out}", fg=typer.colors.GREEN)
        typer.echo(stats)
    except Exception as exc:
        typer.secho(f"Build-cloud failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("stats")
def graph_stats(graph_dir: str = typer.Option("data_v2/graph", help="Persisted graph directory")) -> None:
    """Print a quick manifest of the graph build."""
    try:
        import json
        p = Path(graph_dir) / "manifest.json"
        if not p.exists():
            typer.secho(f"No manifest at {p}", fg=typer.colors.RED)
            raise typer.Exit(code=2)
        d = json.loads(p.read_text(encoding="utf-8"))
        typer.echo(json.dumps(d, indent=2))
    except Exception as exc:
        typer.secho(f"Stats read failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
