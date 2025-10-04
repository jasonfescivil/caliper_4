from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import typer
from loguru import logger

# LlamaCloud Services
import llama_cloud_services

# LlamaIndex Cohere
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere

from caliper_v2.retrievers.llama_cloud_retriever import LlamaCloudRetriever


# Load .env early so OPENAI_API_KEY, etc. are present even if settings import fails
try:
    from caliper_v2.core.env import load_env  # type: ignore

    if load_env():
        logger.info("Loaded .env from project root or nearest parent")
except Exception as _env_exc:
    # Non-fatal; downstream doctor command will highlight missing keys
    logger.debug("Env load error (non-fatal): {}", _env_exc)

# Optional settings import (do not hard crash if pydantic_settings missing)
try:
    from caliper_v2.core.config import settings  # type: ignore
except Exception as exc:  # pragma: no cover
    logger.warning("Failed to import caliper_v2.core.config.settings: {}", exc)
    settings = None  # type: ignore

app = typer.Typer(help="Caliper v2 CLI")

# Sub-app for GraphRAG (optional)
from caliper_v2.commands import graph_cli as graph_cli_app  # type: ignore
app.add_typer(graph_cli_app.app, name="graph", help="GraphRAG commands (experimental, non-disruptive)")

CONTEXT_ROOT = Path("data_v2/context").resolve()
CONTEXT_ROOT.mkdir(parents=True, exist_ok=True)
CATALOG_ROOT = CONTEXT_ROOT / "catalogs"
CATALOG_ROOT.mkdir(parents=True, exist_ok=True)


def _extract_question_from_file(path: Path, max_chars: int = 16000) -> str:
    """Read question/instructions from a text/markdown file.

    Heuristics:
    - If YAML front matter exists and contains a 'question:' key, use its value.
    - Otherwise return the whole file (trimmed).
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        raise FileNotFoundError(f"Failed to read question file: {exc}")

    s = text.strip()
    # Naive YAML front matter extraction
    if s.startswith("---\n"):
        try:
            end = s.find("\n---", 4)
            if end != -1:
                header = s[4:end].splitlines()
                for line in header:
                    if line.strip().lower().startswith("question:"):
                        val = line.split(":", 1)[1].strip()
                        return val[:max_chars].strip()
        except Exception:
            pass
    return s[:max_chars].strip()


def _load_bm25_index_safe(*_args, **_kwargs):
    raise RuntimeError("Local BM25 is not supported in cloud-only Caliper")


def _setup_logging() -> None:
    logger.debug("caliper_v2 CLI starting up")


def _setup_environment() -> None:
    """Apply settings -> env mapping if keys not already set."""
    if not settings:
        return
    mapping = {
        "openai_api_key": "OPENAI_API_KEY",  # pragma: allowlist secret
        "cohere_api_key": "COHERE_API_KEY",  # pragma: allowlist secret
        "llama_cloud_api_key": "LLAMA_CLOUD_API_KEY",  # pragma: allowlist secret
        "anthropic_api_key": "ANTHROPIC_API_KEY",  # pragma: allowlist secret
        "gemini_api_key": "GEMINI_API_KEY",  # pragma: allowlist secret
        "google_api_key": "GOOGLE_API_KEY",  # pragma: allowlist secret
        "xai_api_key": "XAI_API_KEY",  # pragma: allowlist secret
    }
    for attr, env_name in mapping.items():
        val = getattr(settings, attr, None)
        if val and not os.getenv(env_name):
            os.environ[env_name] = val  # type: ignore
            logger.debug("Set {} from settings", env_name)


def _cloud_ids_for_index(name: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (base_id, summary_id) from environment for a logical index name.

    Supports aliases like 'design_standards' -> 'design'.
    """
    aliases = {
        "design_standards": "design",
        "design_guidance": "design",
    }
    key = aliases.get(name.lower(), name.lower())
    base_id = os.getenv(f"{key.upper()}_BASE_ID")
    summary_id = os.getenv(f"{key.upper()}_SUMMARY_ID")
    return base_id, summary_id


def _auto_detect_provider() -> Tuple[Optional[str], Optional[str]]:
    if os.getenv("OPENAI_API_KEY"):
        return "openai", "gpt-5-nano"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic", None
    if (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    ):
        return "gemini", None
    if os.getenv("XAI_API_KEY"):
        return "grok", None
    return None, None


def _resolve_llm_from_flags_or_settings(
    cli_llm_provider: Optional[str],
    cli_llm_model: Optional[str],
) -> Tuple[Optional[str], Optional[str], str]:
    if cli_llm_provider or cli_llm_model:
        return cli_llm_provider, cli_llm_model, "cli"
    set_llm_provider = getattr(settings, "llm_provider", None) if settings else None
    set_llm_model = getattr(settings, "llm_model", None) if settings else None
    if set_llm_provider or set_llm_model:
        return set_llm_provider, set_llm_model, "settings"
    # Explicit environment overrides take precedence over auto-detection
    env_override_provider = os.getenv("CALIPER_LLM_PROVIDER")
    env_override_model = os.getenv("CALIPER_LLM_MODEL")
    if env_override_provider or env_override_model:
        return env_override_provider, env_override_model, "env"
    env_provider, env_model = _auto_detect_provider()
    if env_provider or env_model:
        return env_provider, env_model, "env"
    return None, None, "none"


def _apply_llm_provider(llm_provider: Optional[str], llm_model: Optional[str]) -> None:
    """Configure provider/model. Also allow model-only updates.

    If provider is None but a model is supplied, attempt to reuse the current
    provider resolution (env/settings) to reconfigure with the new model.
    """
    try:
        from caliper_v2.core.llm_providers import configure_llm_provider  # type: ignore

        if not llm_provider and llm_model:
            # Reuse current resolution to get provider when only model is given
            prov, _, _ = _resolve_llm_from_flags_or_settings(None, None)
            if prov:
                configure_llm_provider(prov, model=llm_model)
                return
        if llm_provider:
            configure_llm_provider(llm_provider, model=llm_model)
    except Exception as e:
        logger.warning("Failed to configure LLM provider '{}': {}", llm_provider or "(auto)", e)


def _provider_choices() -> List[str]:
    return ["openai", "anthropic", "gemini", "grok"]


def _list_existing_indexes() -> List[str]:
    # Local indexes removed in cloud-only Caliper
    return []


def _slugify(text: str, max_len: int = 60) -> str:
    import re as _re

    s = _re.sub(r"[^a-zA-Z0-9-_]+", "-", text).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "query"


def _utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _llm_rerank_nodes(nodes: List[Any], question: str, top_n: int) -> List[Any]:
    """Lightweight LLM-based reranker if official class not available.

    Strategy: ask the configured LLM to score each snippet on a 0-1 scale and return the best top_n.
    """
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        return nodes[:top_n]
    if getattr(_Settings, "llm", None) is None:
        return nodes[:top_n]

    prompt_prefix = (
        "You are ranking passages for a legal/regulatory question.\n"
        f"Question: {question}\n"
        "For each PASSAGE, return ONLY a float in [0.0,1.0] that reflects how directly it answers the question with explicit section/page info when present.\n"
    )
    scored: List[Tuple[float, Any]] = []
    for n in nodes:
        text_getter = getattr(n.node, "get_text", None) if hasattr(n, "node") else None
        snippet = text_getter() if callable(text_getter) else getattr(n.node, "text", "")
        sample = snippet[:1200]
        try:
            r = _Settings.llm.complete(prompt_prefix + "\nPASSAGE:\n" + sample + "\nSCORE:")
            raw = getattr(r, "text", str(r)).strip()
            # Extract first float-like number
            import re as _re

            m = _re.search(r"\d+(?:\.\d+)?", raw)
            score = float(m.group(0)) if m else 0.5
            score = max(0.0, min(1.0, score))
        except Exception:
            score = 0.5
        scored.append((score, n))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [n for _, n in scored[:max(1, top_n)]]


def _st_rerank_nodes(
    nodes: List[Any], question: str, top_n: int, model_key: str = "st-mini"
) -> List[Any]:
    """Sentence-Transformers cross-encoder rerank.

    model_key: 'st-mini' -> cross-encoder/ms-marco-MiniLM-L-6-v2
               'st-bge-large' -> BAAI/bge-reranker-large
    """
    try:
        from sentence_transformers import CrossEncoder  # type: ignore
    except Exception:
        return nodes[:top_n]

    model_map = {
        "st-mini": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "st-bge-large": "BAAI/bge-reranker-large",
    }
    model_name = model_map.get(model_key, model_map["st-mini"])  # default mini
    try:
        ce = CrossEncoder(model_name)
    except Exception:
        return nodes[:top_n]

    pairs: List[tuple[str, str]] = []
    for n in nodes:
        text_getter = getattr(n.node, "get_text", None) if hasattr(n, "node") else None
        snippet = text_getter() if callable(text_getter) else getattr(n.node, "text", "")
        pairs.append((question, snippet[:1500]))
    try:
        scores = ce.predict(pairs)
    except Exception:
        return nodes[:top_n]

    ranked = sorted(zip(scores, nodes), key=lambda t: float(t[0]), reverse=True)
    return [n for _, n in ranked[:max(1, top_n)]]


def _bm25_rebuild_from_jsonl(*_args, **_kwargs):
    return None


def _expand_negative_index_expr(expr: str) -> List[str]:
    """
    Support negative selection syntax:
      - "" or "everything": returns all indexes
      - "-name": all except 'name'
      - "name1,name2": the explicit list
      - "-name1,-name2": all except those
    """
    all_idxs = set(_list_existing_indexes())
    s = (expr or "").strip()
    if not s or s.lower() in {"all", "everything", "*"}:
        return sorted(all_idxs)
    parts = [p.strip() for p in s.split(",") if p.strip()]
    negatives = {p[1:] for p in parts if p.startswith("-")}
    positives = {p for p in parts if not p.startswith("-")}
    if positives:
        return sorted(positives)
    if negatives:
        return sorted(all_idxs - negatives)
    return sorted(all_idxs)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    llm_provider: Optional[str] = typer.Option(
        None, "--llm-provider", help="LLM provider override"
    ),
    llm_model: Optional[str] = typer.Option(None, "--llm-model", help="LLM model override"),
    embed_provider: Optional[str] = typer.Option(
        None, "--embed-provider", help="Embedding provider override"
    ),
) -> None:
    _setup_logging()
    _setup_environment()
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        logger.debug("Verbose logging enabled")
    if llm_provider:
        logger.info("Received --llm-provider flag: {}", llm_provider)
    if llm_model:
        logger.info("Received --llm-model flag: {}", llm_model)
    if embed_provider:
        logger.info("Received --embed-provider flag (placeholder): {}", embed_provider)
    # Apply LLM provider configuration early
    try:
        prov, model, src = _resolve_llm_from_flags_or_settings(llm_provider, llm_model)
        if prov or model:
            _apply_llm_provider(prov, model)
            logger.info("Applied LLM provider [{}]: provider={}, model={}", src, prov, model)
    except Exception as exc:
        logger.warning("LLM provider application failed: {}", exc)
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def retrieval_audit(
    context_file: str = typer.Argument(..., help="Path to retrieval JSON from 'retrieve'"),
    output_format: str = typer.Option("md", "--format", help="md|json"),
) -> None:
    """Critique a retrieval JSON and emit a compact improvement plan and cleaned context pack."""
    import json as _json
    p = Path(context_file).resolve()
    if not p.exists():
        typer.secho(f"Context file not found: {p}", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    try:
        data = _json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        typer.secho(f"Failed to parse JSON: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    try:
        from llama_index.core import Settings as _Settings  # type: ignore
        llm = getattr(_Settings, "llm", None)
        if llm is None:
            raise RuntimeError("LLM not configured")
    except Exception as exc:
        typer.secho(f"LLM not available for audit: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    # Compact auditor prompt
    audit_prompt = (
        "You are the Retrieval Auditor. Given a retrieval_session JSON, produce:\n"
        "1) critique_summary (bullets),\n2) improvement_plan (queries, filters, scope, params),\n"
        "3) keep_set_with_spores (<=12 items with compact spores),\n4) context_pack (outline, kept ids, spores map, gaps, followups).\n"
        "Keep spores ~30-60 tokens each. Return markdown unless JSON requested.\n\n"
        f"retrieval_session_json := { _json.dumps(data) }\n"
    )
    try:
        resp = llm.complete(audit_prompt)
        text = getattr(resp, "text", str(resp))
    except Exception as exc:
        typer.secho(f"Audit failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if output_format.lower() == "json":
        typer.echo(_json.dumps({"audit": text}, indent=2))
    else:
        typer.secho(text, fg=typer.colors.CYAN)

def providers() -> None:
    typer.secho("Known LLM provider options:", fg=typer.colors.GREEN, bold=True)
    for p in _provider_choices():
        typer.secho(f"- {p}", fg=typer.colors.CYAN)


@app.command()
def info() -> None:
    try:
        cfg = {
            "provider": getattr(settings, "provider", None),
            "use_weaviate": getattr(settings, "use_weaviate", None),
            "db_path": str(getattr(settings, "db_path", "")),
            "output_dir": str(getattr(settings, "output_dir", "")),
        }
    except Exception as exc:
        logger.warning("Could not load settings: {}", exc)
        cfg = {}
    typer.echo("Caliper v2 runtime")
    typer.echo(f"Settings: {cfg}")


@app.command()
def doctor() -> None:
    """
    Environment and runtime diagnostic (cloud-only).
    - Checks critical API keys
    - Shows provider resolution
    - Reminds about required LlamaCloud index IDs per logical index
    """
    _setup_environment()

    # Keys
    keys = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "COHERE_API_KEY": bool(os.getenv("COHERE_API_KEY")),
        "LLAMA_CLOUD_API_KEY": bool(os.getenv("LLAMA_CLOUD_API_KEY")),
        "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    }
    typer.secho("API keys detected:", fg=typer.colors.GREEN, bold=True)
    for k, present in keys.items():
        color = typer.colors.GREEN if present else typer.colors.RED
        typer.secho(f"- {k}: {'OK' if present else 'MISSING'}", fg=color)

    # Provider resolution
    p, m, src = _resolve_llm_from_flags_or_settings(None, None)
    typer.secho(f"\nLLM provider resolution [{src}]: provider={p}, model={m}", fg=typer.colors.CYAN)

    # Cloud readiness reminder
    typer.secho("\nCloud readiness:", fg=typer.colors.GREEN, bold=True)
    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        typer.secho("- LLAMA_CLOUD_API_KEY: MISSING", fg=typer.colors.RED)
    else:
        typer.secho("- LLAMA_CLOUD_API_KEY: OK", fg=typer.colors.GREEN)
    typer.echo("- For each logical index you plan to use, set <NAME>_BASE_ID and <NAME>_SUMMARY_ID")

    # Check index IDs for common names if present
    common = ["federal", "state", "design", "design_standards"]
    missing: list[str] = []
    for name in common:
        b, s = _cloud_ids_for_index(name)
        if b or s:
            status = "OK" if (b and s) else "MISSING"
            color = typer.colors.GREEN if status == "OK" else typer.colors.RED
            typer.secho(f"- IDs for {name}: base={'set' if b else 'unset'}, summary={'set' if s else 'unset'}", fg=color)
        else:
            continue

    typer.secho("\nDoctor check complete.", fg=typer.colors.GREEN, bold=True)


def _embedding_preflight(embed_provider: Optional[str]) -> None:
    """Strict embedding preflight that fails fast with helpful guidance."""
    if embed_provider and embed_provider.lower() == "local":
        return
    if not os.getenv("OPENAI_API_KEY"):
        typer.secho(
            "No OPENAI_API_KEY found. Default embeddings require it and will fail.\n"
            "Fix by setting OPENAI_API_KEY or rerun with --embed-provider local (for offline smoke tests).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)


@app.command()
def ingest() -> None:
    """Removed: Local ingest has been eliminated in cloud-only Caliper."""
    typer.secho("This command is no longer available in cloud-only Caliper.", fg=typer.colors.RED)
    raise typer.Exit(code=2)
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex  # type: ignore
        from llama_index.core.node_parser import (
            SimpleNodeParser,
            SentenceSplitter,
        )  # type: ignore
        try:
            # Prefer section-aware parsing when available
            from llama_index.core.node_parser import MarkdownNodeParser  # type: ignore
        except Exception:  # pragma: no cover - optional dependency across versions
            MarkdownNodeParser = None  # type: ignore
    except Exception as exc:
        typer.secho(
            "LlamaIndex dependencies not installed. Install with one of:\n"
            "  pip install -r requirements.heavy.txt\n"
            "  or on Windows: .\\caliper.bat (auto installs)\n"
            "  or on WSL: scripts/caliper_wsl.sh (auto installs)\n",
            fg=typer.colors.RED,
        )
        logger.error("Import error for LlamaIndex: {}", exc)
        raise typer.Exit(code=1)

    _setup_environment()
    _embedding_preflight(embed_provider)

    # Configure embeddings
    if embed_provider and embed_provider.lower() == "local":

        class _LocalTinyEmbed:
            def _get_query_embedding(self, query: str):
                return [float((sum(bytearray(query.encode("utf-8"))) % 100) / 100.0)] * 8

            def _get_text_embedding(self, text: str):
                return [float((sum(bytearray(text.encode("utf-8"))) % 100) / 100.0)] * 8

            def get_text_embedding_batch(self, texts, **kwargs):
                return [self._get_text_embedding(t) for t in texts]

            def get_query_embedding(self, query):
                return self._get_query_embedding(query)

            def get_agg_embedding_from_queries(self, queries, **kwargs):
                if not queries:
                    return self._get_query_embedding("")
                embs = [self._get_query_embedding(q) for q in queries]
                dim = len(embs[0])
                agg = [0.0] * dim
                for e in embs:
                    for i in range(dim):
                        agg[i] += e[i]
                return [v / len(embs) for v in agg]

        _Settings.embed_model = _LocalTinyEmbed()
    else:
        try:
            from llama_index.embeddings.openai import OpenAIEmbedding  # type: ignore

            _Settings.embed_model = OpenAIEmbedding(
                model="text-embedding-3-small", embed_batch_size=100
            )
        except Exception as exc:
            typer.secho(f"Failed to initialize OpenAI embeddings: {exc}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    # Read documents
    try:
        if use_llama_parse and os.getenv("LLAMA_CLOUD_API_KEY"):
            from llama_index.core import SimpleDirectoryReader as SDR  # type: ignore
            from llama_parse import LlamaParse  # type: ignore

            # Prefer new parameters; fall back for older llama-parse versions
            try:
                parser = LlamaParse(
                    result_type="markdown",
                    verbose=True,
                    content_guideline_instruction="Extract tables and keep section numbers",
                )
            except TypeError:
                try:
                    parser = LlamaParse(
                        result_type="markdown",
                        verbose=True,
                        complemental_formatting_instruction="Extract tables and keep section numbers",
                    )
                except TypeError:
                    parser = LlamaParse(
                        result_type="markdown",
                        verbose=True,
                        parsing_instruction="Extract tables and keep section numbers",
                    )
            docs = SDR(input_dir=path, recursive=True, file_extractor={".pdf": parser}).load_data()
        else:
            docs = SimpleDirectoryReader(input_dir=path, recursive=True).load_data()
    except Exception as exc:
        logger.exception("Failed loading documents: {}", exc)
        typer.secho(f"Failed loading documents from {path}: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Chunk: prefer section-aware MarkdownNodeParser (when LlamaParse used),
    # otherwise sentence/heading splitter for ~300 tokens, ~15% overlap
    use_markdown_parser = bool('MarkdownNodeParser' in locals() and MarkdownNodeParser)
    parser = None
    if use_llama_parse and use_markdown_parser:
        try:
            parser = MarkdownNodeParser.from_defaults(include_metadata=True)  # type: ignore[attr-defined]
        except Exception:
            parser = None
    if parser is None:
        try:
            target_chars = int((300 * 4))  # approx char len per token
            overlap_chars = int(target_chars * 0.15)
            parser = SentenceSplitter.from_defaults(
                chunk_size=target_chars,
                chunk_overlap=overlap_chars,
                include_metadata=True,
            )
        except Exception:
            chunk_size = getattr(settings, "chunk_size", 1000) if settings else 1000
            chunk_overlap = getattr(settings, "chunk_overlap", 200) if settings else 200
            parser = SimpleNodeParser.from_defaults(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap, include_metadata=True
            )
    nodes = parser.get_nodes_from_documents(docs)

    # Metadata enrichment: basic breadcrumbs + section heading + file_name fallback
    import re as _re
    heading_regex = _re.compile(r"^(#{1,6})\s+(.+)$", _re.MULTILINE)
    for n in nodes:
        md = getattr(n, "metadata", {}) or {}
        # Section from last heading in chunk text
        try:
            text_getter = getattr(n, "get_text", None)
            ntext = text_getter() if callable(text_getter) else getattr(n, "text", "")
            headings = heading_regex.findall(ntext or "")
            if headings:
                # take the last heading's title
                md["section"] = headings[-1][1].strip()
        except Exception:
            pass
        # Ensure file_name present
        if not md.get("file_name") and md.get("file_path"):
            try:
                md["file_name"] = Path(str(md["file_path"])) .name
            except Exception:
                pass
        # Breadcrumbs from file path
        src = md.get("file_path") or md.get("file_name") or ""
        if src:
            parts = str(src).split("/")
            md["breadcrumbs"] = " > ".join(parts[-4:])
        n.metadata = md

    # Build vector index
    idx = VectorStoreIndex(nodes)

    # Persist if requested (vector + BM25)
    if persist:
        persist_dir = Path("data_v2/indexes") / index
        persist_dir.mkdir(parents=True, exist_ok=True)
        try:
            idx.storage_context.persist(persist_dir=str(persist_dir))
            typer.secho(f"Persisted vector index to {persist_dir}", fg=typer.colors.GREEN)
        except Exception as exc:
            logger.exception("Failed to persist index: {}", exc)
            typer.secho("Failed to persist index; index remains in-memory", fg=typer.colors.YELLOW)

        # BM25 corpus persistence (JSON/JSONL only; no pickles)
        try:
            import json as _json

            # Stable corpus dump to allow deterministic rebuilds without pickle
            corpus_meta = {"version": 1, "node_count": len(nodes)}
            (persist_dir / "bm25_corpus.json").write_text(
                _json.dumps(corpus_meta, indent=2), encoding="utf-8"
            )
            # JSONL with minimal per-node text
            jsonl = persist_dir / "bm25_corpus.jsonl"
            with jsonl.open("w", encoding="utf-8") as f:
                for n in nodes:
                    node_id = getattr(n, "node_id", None) or getattr(n, "id_", None)
                    get_text = getattr(n, "get_text", None)
                    text = get_text() if callable(get_text) else getattr(n, "text", "")
                    _json.dump({"node_id": node_id, "text": text}, f, ensure_ascii=False)
                    f.write("\n")
            typer.secho("Persisted BM25 corpus (JSONL)", fg=typer.colors.GREEN)
        except Exception as exc:
            logger.warning("BM25 corpus persistence skipped: {}", exc)
            typer.secho(
                "BM25 JSONL corpus not written; BM25 will be rebuilt in-memory at query time.",
                fg=typer.colors.YELLOW,
            )

        # Summary-layer index (document/section summaries) for HRAG routing
        try:
            from llama_index.core import SummaryIndex  # type: ignore
            from llama_index.core.node_parser import SentenceSplitter  # type: ignore
            from llama_index.core import Settings as _Settings  # type: ignore

            # Generate compact summaries per document by re-chunking larger and summarizing
            # Fallback to original nodes if needed
            larger_chunks = []
            try:
                large_parser = SentenceSplitter.from_defaults(
                    chunk_size=int(1600), chunk_overlap=int(160), include_metadata=True
                )
                # We need original documents; if not available, synthesize from nodes' text
                # Here we just reuse nodes as pseudo-docs
                doc_like_nodes = nodes
                larger_chunks = doc_like_nodes
            except Exception:
                larger_chunks = nodes

            s_index = SummaryIndex(larger_chunks)
            summary_dir = persist_dir / "summary"
            summary_dir.mkdir(parents=True, exist_ok=True)
            s_index.storage_context.persist(persist_dir=str(summary_dir))

            # Build a minimal mapping from summary nodes to child nodes by file/section
            import json as _json
            map_path = summary_dir / "summary_map.json"
            mapping = {}
            try:
                # Group children by (file, section)
                groups: Dict[str, List[str]] = {}
                for n in nodes:
                    md = getattr(n, "metadata", {}) or {}
                    file = md.get("file_name") or md.get("file_path") or "Unknown"
                    section = md.get("section") or md.get("header") or md.get("heading") or ""
                    key = f"{file}||{section}"
                    nid = getattr(n, "node_id", None) or getattr(n, "id_", None)
                    if nid:
                        groups.setdefault(key, []).append(nid)
                mapping = {"group_to_child_node_ids": groups}
            except Exception:
                mapping = {}
            map_path.write_text(_json.dumps(mapping, indent=2), encoding="utf-8")
            typer.secho(f"Persisted summary layer at {summary_dir}", fg=typer.colors.GREEN)
        except Exception as exc:
            logger.warning("Summary index creation skipped: {}", exc)
    else:
        typer.secho(f"Ingest complete for index '{index}' (in-memory)", fg=typer.colors.GREEN)


def _load_persisted_vector_index(*_args, **_kwargs):
    raise RuntimeError("Local vector indexes are not supported in cloud-only Caliper")


def _load_summary_index(index_dir: Path):
    """Load summary index and mapping if present.

    Returns (summary_index, summary_map_dict) or (None, None) if missing.
    """
    try:
        from llama_index.core import StorageContext, load_index_from_storage  # type: ignore
        import json as _json
    except Exception:
        return None, None

    summary_dir = index_dir / "summary"
    if not summary_dir.exists() or not any(summary_dir.iterdir()):
        return None, None
    try:
        storage = StorageContext.from_defaults(persist_dir=str(summary_dir))
        s_index = load_index_from_storage(storage)
    except Exception:
        return None, None

    mapping_path = summary_dir / "summary_map.json"
    mapping = None
    if mapping_path.exists():
        try:
            mapping = _json.loads(mapping_path.read_text(encoding="utf-8"))
        except Exception:
            mapping = None
    return s_index, mapping


def _expand_and_retrieve(
    question: str,
    vs_index,
    storage,
    persist_dir: Path,
    *,
    search_mode: str = "hybrid",
    top_k: int = 60,
    reranker: Optional[str] = None,
    reranker_top_n: int = 16,
    summary_first: bool = True,
) -> List[Any]:
    """Run hybrid retrieval with query expansion + optional reranking. Returns NodeWithScore list."""
    # Build expanded queries
    expanded_queries: list[str] = [question]
    try:
        from llama_index.core.query_transform.multi_para import MultiParagraphQueryTransform  # type: ignore
        mq = MultiParagraphQueryTransform(num_queries=4)
        expanded = mq.run(query_str=question)
        if isinstance(expanded, list):
            expanded_queries.extend([q for q in expanded if isinstance(q, str)])
    except Exception:
        pass
    try:
        from llama_index.core.query_transform.hyde import HyDEQueryTransform  # type: ignore
        hyde = HyDEQueryTransform()
        hypothetical = hyde.run(query_str=question)
        if isinstance(hypothetical, str):
            expanded_queries.append(hypothetical)
    except Exception:
        pass

    vector_nodes: list[Any] = []
    bm25_nodes: list[Any] = []

    # Summary-first routing to gather high-context child nodes
    if summary_first:
        try:
            s_index, s_map = _load_summary_index(persist_dir)
        except Exception:
            s_index, s_map = None, None
        if s_index is not None and isinstance(s_map, dict):
            try:
                sret = s_index.as_retriever(similarity_top_k=min(12, top_k))
                s_hits = sret.retrieve(question)

                # Helper to fetch a node by ID from docstore
                def _get_node_by_id(nid: str):
                    try:
                        # Preferred API
                        return storage.docstore.get(nid)  # type: ignore
                    except Exception:
                        ds = getattr(storage, "docstore", None)
                        if ds is not None:
                            data = getattr(ds, "_data", None) or getattr(ds, "docs", None)
                            if isinstance(data, dict):
                                return data.get(nid)
                    return None

                # Build child candidates from summary groups
                group_map: Dict[str, List[str]] = s_map.get("group_to_child_node_ids", {}) if isinstance(s_map, dict) else {}
                collected: List[Any] = []
                for sh in s_hits:
                    try:
                        md = getattr(sh.node, "metadata", {}) or {}
                        file = md.get("file_name") or md.get("file_path") or "Unknown"
                        section = md.get("section") or md.get("header") or md.get("heading") or ""
                        key = f"{file}||{section}"
                        child_ids = group_map.get(key, [])
                        if not child_ids:
                            continue
                        # Take a few children per group to preserve adjacency
                        for cid in child_ids[: max(2, min(6, top_k // 3))]:
                            node_obj = _get_node_by_id(cid)
                            if node_obj is None:
                                continue
                            collected.append(type("_NWS", (), {"node": node_obj, "score": getattr(sh, "score", None)}))
                    except Exception:
                        continue
                if collected:
                    vector_nodes = collected
            except Exception:
                pass

    # Vector retrieval union across expanded queries
    # If summary-first did not provide nodes, fall back to standard vector retrieval union
    if not vector_nodes:
        try:
            vret = vs_index.as_retriever(similarity_top_k=top_k)
            seen: Dict[str, Any] = {}
            for q in expanded_queries[:8]:
                try:
                    res = vret.retrieve(q)
                except Exception:
                    continue
                for nws in res:
                    nid = getattr(nws.node, "node_id", None) or getattr(nws.node, "id_", None)
                    if nid and nid not in seen:
                        seen[nid] = nws
            vector_nodes = list(seen.values())
        except Exception as exc:
            logger.warning("Vector retrieval failed: {}", exc)

    # BM25
    bm25_built = False
    # Always prefer deterministic rebuild from JSONL corpus
    rebuilt = _bm25_rebuild_from_jsonl(persist_dir)
    if rebuilt is not None:
        try:
            tmp = rebuilt.retrieve(question)
            bm25_nodes = tmp[: max(1, min(10, len(tmp)))]
            bm25_built = True
        except Exception as exc2:
            logger.warning("BM25 rebuilt object retrieval failed: {}", exc2)

    if not bm25_built and search_mode.lower() in {"bm25", "hybrid"}:
        try:
            from llama_index.retrievers.bm25 import BM25Retriever  # type: ignore

            all_nodes = []
            try:
                all_nodes = list(storage.docstore.get_all().values())  # type: ignore
            except Exception:
                ds = getattr(storage, "docstore", None)
                if ds is not None:
                    maybe_data = getattr(ds, "_data", None) or getattr(ds, "docs", None)
                    if isinstance(maybe_data, dict):
                        all_nodes = list(maybe_data.values())
            if all_nodes:
                bm25 = BM25Retriever.from_defaults(nodes=all_nodes)
                # Retrieve then slice locally (more compatible across versions)
                try:
                    bm25_nodes = bm25.retrieve(question)
                except Exception:
                    bm25_nodes = []
                safe_top_k = max(1, min(len(bm25_nodes), 10))
                bm25_nodes = bm25_nodes[:safe_top_k]
                bm25_built = True
                # Ensure JSONL corpus is written for future deterministic rebuilds
                try:
                    import json as _json
                    jsonl = persist_dir / "bm25_corpus.jsonl"
                    with jsonl.open("w", encoding="utf-8") as f:
                        for n in all_nodes:
                            node_id = getattr(n, "node_id", None) or getattr(n, "id_", None)
                            get_text = getattr(n, "get_text", None)
                            text = get_text() if callable(get_text) else getattr(n, "text", "")
                            _json.dump({"node_id": node_id, "text": text}, f, ensure_ascii=False)
                            f.write("\n")
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("BM25 in-memory rebuild failed: {}", exc)

    # Fuse
    mode = search_mode.lower()
    fused_nodes: list[Any] = []
    if mode == "vector" or (mode in {"bm25", "hybrid"} and not bm25_nodes):
        fused_nodes = vector_nodes
    elif mode == "bm25":
        fused_nodes = bm25_nodes
    elif mode == "hybrid":
        def rrf(rank: int, k: int = 60) -> float:
            return 1.0 / (k + rank)

        scores: Dict[str, float] = {}
        order: Dict[str, Any] = {}
        for i, nws in enumerate(vector_nodes):
            nid = getattr(nws.node, "node_id", None) or getattr(nws.node, "id_", None) or str(i)
            scores[nid] = scores.get(nid, 0.0) + rrf(i + 1)
            order.setdefault(nid, nws)
        for i, nws in enumerate(bm25_nodes):
            nid = getattr(nws.node, "node_id", None) or getattr(nws.node, "id_", None) or f"b{i}"
            scores[nid] = scores.get(nid, 0.0) + rrf(i + 1)
            order.setdefault(nid, nws)
        fused_nodes = [
            order[nid]
            for nid, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[: top_k * 2]
        ]
    else:
        fused_nodes = vector_nodes

    # Group-aware rerank prep: build groups by parent/section so adjacency is preserved
    def _group_key(nws: Any) -> Tuple[str, str, str]:
        try:
            node = nws.node
            md = getattr(node, "metadata", {}) or {}
            parent_rel = getattr(getattr(node, "relationships", {}), "get", lambda *_: None)("PARENT") if hasattr(node, "relationships") else None
            parent_id = parent_rel or md.get("parent_id") or ""
            file_name = md.get("file_name") or md.get("file_path") or ""
            section = md.get("section") or md.get("header") or md.get("heading") or ""
            return (str(parent_id), str(file_name), str(section))
        except Exception:
            return ("", "", "")

    def _group_nodes(nodes: List[Any]) -> List[Tuple[Tuple[str, str, str], List[Any]]]:
        groups: Dict[Tuple[str, str, str], List[Any]] = {}
        for n in nodes:
            k = _group_key(n)
            groups.setdefault(k, []).append(n)
        # Preserve original group order by first appearance
        seen_keys: List[Tuple[str, str, str]] = []
        for n in nodes:
            k = _group_key(n)
            if k not in seen_keys:
                seen_keys.append(k)
        return [(k, groups[k]) for k in seen_keys]

    def _group_repr_text(group_nodes: List[Any], max_chars: int = 2000) -> str:
        parts: List[str] = []
        total = 0
        for n in group_nodes:
            text_getter = getattr(n.node, "get_text", None) if hasattr(n, "node") else None
            snippet = text_getter() if callable(text_getter) else getattr(n.node, "text", "")
            if not snippet:
                continue
            take = max_chars - total
            if take <= 0:
                break
            s = snippet[:take]
            parts.append(s)
            total += len(s)
        return "\n\n".join(parts)

    # Optional rerank (group-aware). Apply on groups and then flatten preserving within-group order
    if not reranker and os.getenv("COHERE_API_KEY"):
        # Default chain for single-user quality: cohere,st-mini
        reranker = "cohere,st-mini"
    if reranker:
        # Build groups
        grouped = _group_nodes(fused_nodes)
        # Representative texts per group for reranking
        group_texts = [(_group_repr_text(nodes), nodes) for _, nodes in grouped]

        # Apply each reranker to groups, updating group order each time
        def _apply_chain_to_groups(chain: List[str], items: List[Tuple[str, List[Any]]]) -> List[Tuple[str, List[Any]]]:
            ordered = items
            for rr in chain:
                rr = rr.strip().lower()
                if not rr:
                    continue
                texts = [t for t, _ in ordered]
                nodes_lists = [ns for _, ns in ordered]
                if rr == "cohere":
                    try:
                        from llama_index.postprocessor.cohere_rerank import CohereRerank  # type: ignore
                        if os.getenv("COHERE_API_KEY"):
                            # Build minimal NodeWithScore-like dicts acceptable by adapter
                            group_nodes = [
                                {"node": {"text": t}, "score": None} for t in texts
                            ]
                            pp = CohereRerank(top_n=min(reranker_top_n, len(group_nodes)))
                            rescored = pp.postprocess_nodes(group_nodes, query_str=question)  # type: ignore
                            # Map back based on text identity
                            text_to_idx = {t: i for i, t in enumerate(texts)}
                            new_order: List[Tuple[str, List[Any]]] = []
                            for gn in rescored:
                                # Support both dict and object outputs
                                t = None
                                try:
                                    if isinstance(gn, dict):
                                        t = ((gn.get("node") or {}).get("text"))
                                    else:
                                        t = getattr(getattr(gn, "node", None), "text", None)
                                except Exception:
                                    t = None
                                i = text_to_idx.get(t)
                                if i is not None:
                                    new_order.append((texts[i], nodes_lists[i]))
                            # If any dropped, append remaining
                            used = {id(v) for _, v in new_order}
                            for i, v in enumerate(nodes_lists):
                                if id(v) not in used:
                                    new_order.append((texts[i], v))
                            ordered = new_order
                    except Exception as exc:
                        logger.warning("Failed Cohere group rerank: {}", exc)
                elif rr.startswith("st-"):
                    try:
                        # Score groups with ST and reorder
                        scores_order = _st_rerank_nodes(
                            # reuse function by creating node-like wrappers
                            [type("_NW", (), {"node": type("_N", (), {"text": t})}) for t in texts],
                            question,
                            top_n=len(texts),
                            model_key=rr,
                        )
                        # Build mapping from text to rank
                        ranks: Dict[str, int] = {}
                        for rank, w in enumerate(scores_order):
                            t = getattr(w.node, "text", "")
                            ranks[t] = rank
                        ordered = sorted(ordered, key=lambda pair: ranks.get(pair[0], 1_000_000))
                    except Exception as exc:
                        logger.warning("Failed ST group rerank '{}': {}", rr, exc)
                elif rr == "llm":
                    try:
                        # Use internal LLM reranker on group texts
                        scores_order = _llm_rerank_nodes(
                            [type("_NW", (), {"node": type("_N", (), {"text": t})}) for t in texts],
                            question,
                            top_n=len(texts),
                        )
                        ranks: Dict[str, int] = {}
                        for rank, w in enumerate(scores_order):
                            t = getattr(w.node, "text", "")
                            ranks[t] = rank
                        ordered = sorted(ordered, key=lambda pair: ranks.get(pair[0], 1_000_000))
                    except Exception as exc:
                        logger.warning("Failed LLM group rerank: {}", exc)
            return ordered

        chain_list = [r for r in str(reranker).split(",") if r.strip()]
        ordered_groups = _apply_chain_to_groups(chain_list, group_texts)
        # Flatten groups back to nodes, preserving within-group order
        fused_nodes = [n for _, ns in ordered_groups for n in ns]

    # MMR diversity
    try:
        from llama_index.core.postprocessor import MMREngine  # type: ignore

        mmr = MMREngine(diversity=0.3)
        fused_nodes = mmr.postprocess_nodes(fused_nodes, query_str=question)  # type: ignore
    except Exception:
        pass

    return fused_nodes[:top_k]


def _node_payload(nws: Any, index_name: Optional[str] = None) -> Dict[str, Any]:
    # Resolve underlying node/document and metadata across providers
    node_obj = getattr(nws, "node", None) or getattr(nws, "document", None) or nws
    md: Dict[str, Any] = {}
    try:
        md = getattr(node_obj, "metadata", {}) or getattr(nws, "metadata", {}) or {}
    except Exception:
        md = {}

    # Resolve text with multiple fallbacks
    snippet = ""
    try:
        get_text = getattr(node_obj, "get_text", None)
        if callable(get_text):
            snippet = get_text() or ""
    except Exception:
        pass
    if not snippet:
        snippet = getattr(node_obj, "text", None) or getattr(nws, "text", None) or ""

    # Score and identifiers
    score_val = getattr(nws, "score", None)
    node_id = (
        getattr(node_obj, "node_id", None)
        or getattr(node_obj, "id_", None)
        or getattr(nws, "id", None)
    )
    parent_rel = getattr(node_obj, "relationships", None)
    parent_id = None
    try:
        if parent_rel and hasattr(parent_rel, "get"):
            parent_id = parent_rel.get("PARENT")
    except Exception:
        parent_id = None

    # Enrich section if missing by scanning headings in the snippet
    if not (md.get("section") or md.get("header") or md.get("heading")) and snippet:
        try:
            import re as _re
            _hdr = _re.findall(r"^(#{1,6})\s+(.+)$", snippet, flags=_re.MULTILINE)
            if _hdr:
                md["section"] = _hdr[-1][1].strip()
        except Exception:
            pass

    # Include source index name if provided
    if index_name:
        try:
            md["index"] = index_name
        except Exception:
            pass

    # Derive document title, author, publisher/agency when possible
    def _derive_title(md_in: Dict[str, Any]) -> Optional[str]:
        for k in ("document_title", "title", "doc_title"):
            v = md_in.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        fn = md_in.get("file_name") or md_in.get("file_path")
        if isinstance(fn, str) and fn:
            base = fn.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
            base = base.rsplit(".", 1)[0]
            return base.replace("_", " ").strip()
        return None

    def _derive_author(md_in: Dict[str, Any]) -> Optional[str]:
        for k in ("author", "authors", "doc_author"):
            v = md_in.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
            if isinstance(v, list) and v:
                return ", ".join([str(x) for x in v if str(x).strip()])
        return None

    def _derive_publisher(md_in: Dict[str, Any], title_in: Optional[str]) -> Optional[str]:
        for k in ("publisher", "publishing_agency", "agency", "organization", "source_organization"):
            v = md_in.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        # Heuristic from file name/title
        txt = (md_in.get("file_name") or md_in.get("file_path") or title_in or "").upper()
        if "EPA" in txt:
            return "U.S. Environmental Protection Agency"
        if "DOE" in txt or "ECOLOGY" in txt:
            return "Washington State Department of Ecology"
        if "WEF" in txt or "MOP" in txt:
            return "Water Environment Federation"
        return None

    doc_title = _derive_title(md)
    doc_author = _derive_author(md)
    doc_publisher = _derive_publisher(md, doc_title)

    return {
        "node_id": node_id,
        "parent_id": parent_id,
        "score": float(score_val) if isinstance(score_val, (int, float)) else None,
        "text": snippet or "",
        "metadata": {
            "file_name": md.get("file_name"),
            "file_path": md.get("file_path"),
            "page": md.get("page_label", md.get("page")),
            "section": md.get("section") or md.get("header") or md.get("heading"),
            "breadcrumbs": md.get("breadcrumbs"),
            "index": md.get("index"),
            "document_title": doc_title,
            "author": doc_author,
            "publisher": doc_publisher,
        },
    }


def _heuristic_node_spore(md: Dict[str, Any], text: str, question: str) -> Dict[str, Any]:
    """Generate heuristic node spore based on metadata and text analysis."""
    import re as _re
    txt = (text or "")[:1200]
    regs: list[str] = []
    try:
        regs += _re.findall(r"\b(?:40|33)\s+CFR\s+[\d.]+", txt, _re.IGNORECASE)[:2]
        regs += _re.findall(r"\bWAC\s+[\d-]+", txt, _re.IGNORECASE)[:2]
        regs += _re.findall(r"\bRCW\s+[\d.]+", txt, _re.IGNORECASE)[:2]
    except Exception:
        pass
    parts: list[str] = []
    if regs:
        parts.append("Cites " + ", ".join(regs))
    sec = (md or {}).get("section") or (md or {}).get("header") or (md or {}).get("heading")
    if sec:
        parts.append(f"Section: {sec}")
    pg = (md or {}).get("page_label", (md or {}).get("page"))
    if pg is not None:
        parts.append(f"p.{pg}")
    # topical
    tl = txt.lower()
    if "wastewater" in tl or "wwtp" in tl:
        parts.append("WWTP guidance")
    if "effluent" in tl:
        parts.append("effluent limits")
    if "permit" in tl:
        parts.append("permitting")
    if not parts:
        q = txt.strip().split(". ")[:1]
        if q and q[0]:
            parts.append("Quote: \"" + q[0][:120].strip().rstrip(",;") + "\"")
    reason = "; ".join(parts) or "Matches key terms and definitions related to the question."
    conf = 0.6 + (0.1 if regs else 0.0) + (0.05 if sec else 0.0)
    return {"reason": reason, "confidence": round(min(0.95, conf), 2)}


def _generate_spore(nodes: List[Any], question: str) -> Dict[str, Any]:
    """Call the configured LLM once to generate a 'context spore' explanation and confidence."""
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        _Settings = None  # type: ignore

    top_labels = []
    for i, nws in enumerate(nodes[:12], 1):
        md = getattr(nws.node, "metadata", {}) if hasattr(nws, "node") else {}
        file = (md or {}).get("file_name") or (md or {}).get("file_path") or "Unknown"
        page = (md or {}).get("page_label", (md or {}).get("page"))
        section = (md or {}).get("section") or (md or {}).get("header")
        parts = [str(file)]
        if page is not None:
            parts.append(f"p.{page}")
        if section:
            parts.append(str(section))
        top_labels.append(f"[{i}] " + " - ".join([parts[0]] + (["; ".join(parts[1:])] if len(parts) > 1 else [])))

    prompt = (
        "You are creating a retrieval justification for a RAG pipeline which will give context to the document chunks and metadata retrieved by LlamaCloud in response to a user query.\n"
        "Question: "
        + question
        + "\n"
        "You are given a list of top retrieved sources (filenames/pages/sections).\n"
        "Explain in 2-5 concise sentences WHY these sources were selected and how they\n"
        "together provide upstream/downstream context. Then provide a single confidence\n"
        "score in [0.0,1.0] for the overall relevance.\n\n"
        "Sources:\n"
        + "\n".join(top_labels)
    )

    default_spore = {
        "summary": "Top sources selected based on hybrid similarity and coverage of relevant sections.",
        "rationale_bullets": [
            "Covers primary regulatory sections referenced by the question",
            "Includes adjacent sections providing upstream/downstream context",
            "Combines lexical and semantic matches to reduce out-of-context risk",
        ],
        "confidence": 0.7,
    }

    if _Settings and getattr(_Settings, "llm", None) is not None:
        import json as _json
        llm = _Settings.llm
        # Try JSON mode if supported, else extract JSON block
        try:
            if hasattr(llm, "complete_json"):
                resp = llm.complete_json(prompt)  # type: ignore[attr-defined]
                raw = getattr(resp, "text", getattr(resp, "json", "{}"))
            else:
                resp = llm.complete(prompt)
                raw = getattr(resp, "text", str(resp))
                try:
                    start = raw.index("{")
                    end = raw.rfind("}") + 1
                    raw = raw[start:end]
                except Exception:
                    pass

            data = _json.loads(raw)
            if not isinstance(data, dict):
                return default_spore
            conf = data.get("confidence", 0.7)
            try:
                data["confidence"] = max(0.0, min(1.0, float(conf)))
            except Exception:
                data["confidence"] = 0.7
            if "summary" not in data or not isinstance(data.get("summary"), str):
                data["summary"] = default_spore["summary"]
            if "rationale_bullets" not in data or not isinstance(data.get("rationale_bullets"), list):
                data["rationale_bullets"] = default_spore["rationale_bullets"]
            return data
        except Exception:
            # One minimal retry requesting only JSON
            try:
                mini = "Return only JSON with keys summary (string), rationale_bullets (array of strings), confidence (number)."
                resp2 = llm.complete(mini)
                raw2 = getattr(resp2, "text", str(resp2))
                data2 = _json.loads(raw2)
                if isinstance(data2, dict):
                    data2.setdefault("summary", default_spore["summary"])
                    data2.setdefault("rationale_bullets", default_spore["rationale_bullets"])
                    c2 = data2.get("confidence", 0.7)
                    try:
                        data2["confidence"] = max(0.0, min(1.0, float(c2)))
                    except Exception:
                        data2["confidence"] = 0.7
                    return data2
            except Exception:
                pass
            return default_spore
    return default_spore


@app.command()
def retrieve(
    question: Optional[str] = typer.Argument(None, help="Natural language question (omit if using --question-file)"),
    question_file: Optional[str] = typer.Option(None, "--question-file", "-Q", help="Path to a .md/.txt file containing the question/prompt"),
    indexes: str = typer.Option(
        "federal,state,design_standards",
        "--indexes",
        help="Comma-separated index names to route across",
    ),
    top_k: int = typer.Option(16, "--top-k", help="Retriever pre-rank top_k (cloud: before rerank)"),
    reranker: Optional[str] = typer.Option(
        "cohere",
        "--reranker",
        help="cohere|none (default: cohere when COHERE_API_KEY present; else MMR)",
    ),
    reranker_top_n: int = typer.Option(16, "--reranker-top-n", help="Keep N after rerank"),
    out: Optional[str] = typer.Option(None, "--out", help="Output JSON path (default: data_v2/context/*.json)"),
    no_spore: bool = typer.Option(False, "--no-spore", help="Skip spore generation (no extra LLM call)"),
    node_spore: bool = typer.Option(True, "--node-spore/--no-node-spore", help="Also attach a brief per-node justification+confidence (auto-capped)"),
    include_terms: Optional[str] = typer.Option(None, "--include-terms", help="Comma-separated lexical must-have terms to boost (cloud)"),
    exclude_sections: Optional[str] = typer.Option(None, "--exclude-sections", help="Comma-separated section keywords to drop (e.g., toc,glossary,references,figures)"),
    retrieval_mode: str = typer.Option("chunks", "--retrieval-mode", help="chunks|files_via_content|files_via_metadata|auto_routed (cloud)"),
    dense_k: int = typer.Option(8, "--dense-k", help="Cloud dense_similarity_top_k"),
    sparse_k: int = typer.Option(8, "--sparse-k", help="Cloud sparse_similarity_top_k"),
    alpha: float = typer.Option(0.5, "--alpha", help="Cloud hybrid alpha (0..1)"),
    rerank_top_n: int = typer.Option(8, "--rerank-top-n", help="Cloud rerank top N"),
    filters: Optional[str] = typer.Option(None, "--filters", help='JSON object of metadata filters, e.g., {"jurisdiction":"WA","chapter":"G1"}'),
    infer_filters: bool = typer.Option(False, "--infer-filters/--no-infer-filters", help="Enable schema-driven filter inference when supported (cloud)"),
    expand_queries: int = typer.Option(4, "--expand-queries", help="Number of query expansions (0 disables)"),
    hyde: bool = typer.Option(True, "--hyde/--no-hyde", help="Enable HyDE query expansion"),
    cloud: bool = typer.Option(False, "--cloud", help="Use LlamaCloud for retrieval"),
) -> None:
    """Phase 1: Retrieval + Context Spore. Writes a persistent JSON file and prints its path."""
    # Setup environment and decide routing mode first
    _setup_environment()

    # Resolve question from file if provided (takes precedence)
    if question_file:
        p = Path(question_file)
        if not p.exists() or not p.is_file():
            typer.secho(f"Question file not found: {question_file}", fg=typer.colors.RED)
            raise typer.Exit(code=2)
        try:
            question = _extract_question_from_file(p)
        except Exception as exc:
            typer.secho(str(exc), fg=typer.colors.RED)
            raise typer.Exit(code=2)

    if not question:
        typer.secho("No question provided. Supply a question argument or --question-file.", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    # Router over multiple indexes: retrieve per-index then fuse across indexes
    index_list = [s.strip() for s in (indexes or "").split(",") if s.strip()]
    if not index_list:
        typer.secho("No indexes provided.", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    # ===== BUGGY SIMPLE PATH - COMMENTED OUT BY fix_retrieval.py =====
    # This path was preventing sophisticated retrieval logic from running.
    # Issues: ignores --indexes, no spore generation, no query expansion.
    # The sophisticated path below handles all these correctly.
    #     # Cloud-only: require API key and IDs
    #     if cloud:
    #         api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    #         if not api_key:
    #             typer.secho("LLAMA_CLOUD_API_KEY environment variable not set.", fg=typer.colors.RED)
    #             raise typer.Exit(code=1)
    # 
    #         project_name = os.getenv("LLAMA_CLOUD_PROJECT_NAME", "Default")
    # 
    #         # 1) Retrieve from LlamaCloud (simple path for now)
    #         retriever = LlamaCloudRetriever(project_name=project_name, api_key=api_key)
    #         fused: list[Any] = []
    #         try:
    #             fused = list(retriever.retrieve(question, limit=top_k) or [])
    #         except Exception as exc:
    #             logger.warning("Cloud retrieval failed: {}", exc)
    #             fused = []
    # 
    #         # 2) Optional rerank via Cohere if requested and available
    #         chain = [r.strip() for r in str(reranker or "").split(",") if r.strip()]
    #         try:
    #             if chain and "cohere" in chain and fused:
    #                 if not os.getenv("COHERE_API_KEY"):
    #                     typer.secho(
    #                         "COHERE_API_KEY missing and --reranker cohere requested. Install and set key or use --reranker none.",
    #                         fg=typer.colors.RED,
    #                     )
    #                     raise typer.Exit(code=2)
    #                 try:
    #                     from llama_index.postprocessor.cohere_rerank import CohereRerank  # type: ignore
    #                 except Exception as exc:
    #                     typer.secho(
    #                         f"Cohere rerank module not available: {exc}. Install 'llama-index-postprocessor-cohere-rerank' and retry.",
    #                         fg=typer.colors.RED,
    #                     )
    #                     raise typer.Exit(code=2)
    #                 rr = CohereRerank(top_n=min(top_k, reranker_top_n))
    #                 fused = rr.postprocess_nodes(fused, query_str=question)
    #         except Exception:
    #             fused = fused[:top_k]
    #         fused = fused[:top_k]
    # 
    #         # 3) Build payload and write to file
    #         spore = {} if no_spore else _generate_spore(fused, question)
    #         payload: Dict[str, Any] = {
    #             "type": "retrieval_session",
    #             "version": 1,
    #             "created_at": _utc_now_iso(),
    #             "question": question,
    #             "indexes": index_list,
    #             "search_mode": "cloud",
    #             "requested_top_k": top_k,
    #             "final_kept": len(fused),
    #             "reranker": ",".join(chain) if chain else None,
    #             "retrieval": {
    #                 "nodes": [_node_payload(n) for n in fused],
    #                 "spore": spore,
    #             },
    #         }
    # 
    #         # Add citations list for convenience
    #         citations: List[Dict[str, Any]] = []
    #         for n in fused:
    #             try:
    #                 md = getattr(n.node, "metadata", {}) or {}
    #                 citations.append(
    #                     {
    #                         "file": md.get("file_name") or md.get("file_path"),
    #                         "page": md.get("page_label", md.get("page")),
    #                         "section": md.get("section") or md.get("header") or md.get("heading"),
    #                     }
    #                 )
    #             except Exception:
    #                 continue
    #         payload["retrieval"]["citations"] = citations  # type: ignore[index]
    # 
    #         # Optional per-node spore generation (cloud path)
    #         if node_spore and not no_spore and payload["retrieval"]["nodes"]:
    #             try:
    #                 from llama_index.core import Settings as _Settings  # type: ignore
    #                 llm = getattr(_Settings, "llm", None)
    #             except Exception:
    #                 llm = None
    #             if llm is not None:
    #                 import json as _json
    #                 for nd in payload["retrieval"]["nodes"][:top_k]:
    #                     text = (nd.get("text") or "")[:600]
    #                     label = nd.get("metadata", {}).get("file_name") or nd.get("metadata", {}).get("file_path") or "Unknown"
    #                     prompt_ns = (
    #                         "Explain in 1-2 sentences why this node helps answer the question, then give confidence [0.0,1.0] as JSON.\n"
    #                         f"Question: {question}\n"
    #                         f"Source: {label}\n"
    #                         f"Text: {text}\n"
    #                         "Return only JSON: {\"reason\": string, \"confidence\": number}."
    #                     )
    #                     try:
    #                         respn = llm.complete(prompt_ns)
    #                         rawn = getattr(respn, "text", str(respn))
    #                         try:
    #                             start = rawn.index("{"); end = rawn.rfind("}") + 1; rawn = rawn[start:end]
    #                         except Exception:
    #                             pass
    #                         jd = _json.loads(rawn)
    #                         nd["spore"] = {
    #                             "reason": jd.get("reason", "Relevant to the query scope."),
    #                             "confidence": float(jd.get("confidence", 0.7) or 0.7),
    #                         }
    #                     except Exception:
    #                         nd["spore"] = {"reason": "Relevant to the query scope.", "confidence": 0.7}
    # 
    #         import json as _json
    #         if out:
    #             out_path = Path(out).resolve(); out_path.parent.mkdir(parents=True, exist_ok=True)
    #         else:
    #             slug = _slugify(question)
    #             out_path = CONTEXT_ROOT / f"{_utc_now_iso().replace(':','').replace('-','')}_{slug}.json"
    #         out_path.write_text(_json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    #         typer.secho(f"Wrote retrieval context to: {out_path}", fg=typer.colors.GREEN)
    #         typer.echo(str(out_path))
    #         return
    # ===== END COMMENTED OUT BUGGY PATH =====

    # Cloud retrieval: use sophisticated path with multi-index support
    if cloud:
        def _sfirst_retrieve(q: str, base_idx: Any, sum_idx: Any, s_top: int = 36, b_top: int = 180, per_group: int = 18):
            # Strict cloud retrieval: surface errors instead of swallowing them
            retriever_kwargs = {
                "similarity_top_k": min(100, int(s_top)),
                "retrieval_mode": retrieval_mode,
                "dense_similarity_top_k": max(1, int(dense_k)),
                "sparse_similarity_top_k": max(0, int(sparse_k)),
                "alpha": max(0.0, min(1.0, float(alpha))),
                "enable_reranking": True,
                "rerank_top_n": max(1, int(rerank_top_n)),
            }
            # Attach filters if provided
            import json as _json
            filter_obj = None
            if filters:
                try:
                    filter_obj = _json.loads(filters)
                except Exception:
                    filter_obj = None
            if filter_obj:
                retriever_kwargs["filters"] = filter_obj
            if infer_filters:
                retriever_kwargs["enable_filter_inference"] = True
            try:
                s_ret = sum_idx.as_retriever(**retriever_kwargs)
            except TypeError:
                s_ret = sum_idx.as_retriever(similarity_top_k=min(100, int(s_top)))
            s_hits = s_ret.retrieve(q)
            boosts: List[str] = []
            for h in s_hits:
                try:
                    md = getattr(h.node, "metadata", {}) or {}
                    file_hint = md.get("file_name") or md.get("file_path") or ""
                    section_hint = md.get("section") or md.get("header") or md.get("heading") or ""
                    if file_hint or section_hint:
                        boosts.append((" ".join([q, file_hint, section_hint])).strip())
                except Exception:
                    continue
            seen: Dict[str, Any] = {}
            try:
                bret = base_idx.as_retriever(**{**retriever_kwargs, "similarity_top_k": min(100, int(b_top))})
            except TypeError:
                bret = base_idx.as_retriever(similarity_top_k=min(100, int(b_top)))
            for q2 in boosts[:24]:
                for nw in bret.retrieve(q2)[:per_group]:
                    nid = getattr(nw.node, "node_id", None) or getattr(nw.node, "id_", None)
                    if nid and nid not in seen:
                        seen[nid] = nw
            if len(seen) < max(24, b_top // 3):
                for nw in bret.retrieve(q)[:per_group]:
                    nid = getattr(nw.node, "node_id", None) or getattr(nw.node, "id_", None)
                    if nid and nid not in seen:
                        seen[nid] = nw
            return list(seen.values())

        # Respect user-specified indexes strictly (no auto scoping)
        scoped_indexes = list(index_list)
        buckets: List[Any] = []
        # Build expansions (Multi-Query + HyDE) client-side
        expanded_queries: List[str] = []
        expanded_queries.append(question)
        try:
            if expand_queries and expand_queries > 0:
                from llama_index.core.query_transform.multi_para import MultiParagraphQueryTransform  # type: ignore
                mq = MultiParagraphQueryTransform(num_queries=int(expand_queries))
                expanded = mq.run(query_str=question)
                if isinstance(expanded, list):
                    expanded_queries.extend([q for q in expanded if isinstance(q, str)])
        except Exception:
            pass
        try:
            if hyde:
                from llama_index.core.query_transform.hyde import HyDEQueryTransform  # type: ignore
                hy = HyDEQueryTransform()
                hyp = hy.run(query_str=question)
                if isinstance(hyp, str):
                    expanded_queries.append(hyp)
        except Exception:
            pass

        for name in scoped_indexes:
            b_id, s_id = _cloud_ids_for_index(name)
            if not (b_id and s_id):
                typer.secho(
                    f"Missing cloud IDs for '{name}'. Set {name.upper()}_BASE_ID and {name.upper()}_SUMMARY_ID in your .env.",
                    fg=typer.colors.RED,
                )
                raise typer.Exit(code=2)
            base = LlamaCloudIndex(index_id=b_id)
            summ = LlamaCloudIndex(index_id=s_id)
            try:
                # Build per-expansion retrieval with modest caps per expansion
                per_s_top = min(24, max(8, top_k * 2))
                per_b_top = min(80, max(24, top_k * 4))
                per_group = max(6, min(20, top_k))

                # Compose a boosted question with optional domain terms
                domain_terms = [
                    "G1", "General Sewer Plan", "Engineering Report", "Plans and Specifications",
                    "WAC 173-240-050", "WAC 173-240-060", "WAC 173-240-070", "SEPA", "NEPA", "SERP",
                ]
                base_question = question
                if include_terms:
                    extra = [t.strip() for t in include_terms.split(",") if t.strip()]
                    if extra:
                        base_question = base_question + " " + " ".join(extra)
                base_question = base_question + " " + " ".join(domain_terms)

                for qx in expanded_queries:
                    q_use = (qx + " " + " ".join(domain_terms)).strip()
                    res = _sfirst_retrieve(q_use, base, summ, s_top=per_s_top, b_top=per_b_top, per_group=per_group)
                    for _n in res:
                        try:
                            setattr(_n, "_caliper_index_name", name)
                        except Exception:
                            pass
                    buckets += res
            except Exception as exc:
                typer.secho(f"Cloud retrieval failed for '{name}': {exc}", fg=typer.colors.RED)
                raise typer.Exit(code=1)

        # Dedup and cap
        seen_ids: set[str] = set()
        fused: List[Any] = []
        for nw in buckets:
            try:
                nid = getattr(nw.node, "node_id", None) or getattr(nw.node, "id_", None)
                if nid and nid not in seen_ids:
                    seen_ids.add(nid)
                    fused.append(nw)
                if len(fused) >= max(10, min(200, top_k*8)):
                    break
            except Exception:
                continue

        # Exclude unwanted sections (TOC, references, glossary, figures/exhibits)
        drop_keys = ["table of contents", "references", "glossary", "figures", "exhibits"]
        if exclude_sections:
            drop_keys += [s.strip().lower() for s in exclude_sections.split(",") if s.strip()]
        def _is_dropped(n: Any) -> bool:
            try:
                md = getattr(n.node, "metadata", {}) or {}
                sec = (md.get("section") or "").lower()
                return any(k in sec for k in drop_keys)
            except Exception:
                return False
        fused = [n for n in fused if not _is_dropped(n)]

        # Rerank (Cohere-only)
        chain = [r.strip() for r in str(reranker or "").split(",") if r.strip()]
        try:
            if chain and "cohere" in chain:
                if not os.getenv("COHERE_API_KEY"):
                    typer.secho(
                        "COHERE_API_KEY missing and --reranker cohere requested. Install and set key or use --reranker none.",
                        fg=typer.colors.RED,
                    )
                    raise typer.Exit(code=2)
                try:
                    from llama_index.postprocessor.cohere_rerank import CohereRerank  # type: ignore
                except Exception as exc:
                    typer.secho(
                        f"Cohere rerank module not available: {exc}. Install 'llama-index-postprocessor-cohere-rerank' and retry.",
                        fg=typer.colors.RED,
                    )
                    raise typer.Exit(code=2)
                rr = CohereRerank(top_n=top_k)
                fused = rr.postprocess_nodes(fused, query_str=question)
        except Exception:
            # If rerank fails, just trim
            fused = fused[:top_k]
        fused = fused[:top_k]
        if not fused:
            typer.secho(
                "No nodes retrieved after rerank; check cloud IDs, hybrid params, and query specificity.",
                fg=typer.colors.YELLOW,
            )

        spore = {} if no_spore else _generate_spore(fused, question)
        payload: Dict[str, Any] = {
            "type": "retrieval_session",
            "version": 1,
            "created_at": _utc_now_iso(),
            "question": question,
            "indexes": scoped_indexes,
            "search_mode": "cloud",
            "requested_top_k": top_k,
            "final_kept": len(fused),
            "reranker": ",".join(chain) if chain else None,
            "retrieval": {
                "nodes": [_node_payload(n, index_name=getattr(n, "_caliper_index_name", None)) for n in fused],
                "spore": spore,
            },
        }
        # Add citations list for convenience
        citations: List[Dict[str, Any]] = []
        for n in fused:
            try:
                md = getattr(n.node, "metadata", {}) or {}
                citations.append(
                    {
                        "file": md.get("file_name") or md.get("file_path"),
                        "page": md.get("page_label", md.get("page")),
                        "section": md.get("section") or md.get("header") or md.get("heading"),
                    }
                )
            except Exception:
                continue
        payload["retrieval"]["citations"] = citations  # type: ignore[index]
        # Optional per-node spore generation (cloud path)
        if node_spore and not no_spore and payload["retrieval"]["nodes"]:
            try:
                from llama_index.core import Settings as _Settings  # type: ignore
                llm = getattr(_Settings, "llm", None)
            except Exception:
                llm = None
            if llm is not None:
                import json as _json, re as _re
                for nd in payload["retrieval"]["nodes"][:top_k]:
                    text = (nd.get("text") or "")[:800]
                    label = nd.get("metadata", {}).get("file_name") or nd.get("metadata", {}).get("file_path") or "Unknown"
                    prompt_ns = (
                        "Explain in 1-2 sentences why this node helps answer the question, then give confidence [0.0,1.0] as JSON.\n"
                        f"Question: {question}\n"
                        f"Source: {label}\n"
                        f"Text: {text}\n"
                        "Return only JSON: {\"reason\": string, \"confidence\": number}."
                    )
                    try:
                        respn = llm.complete(prompt_ns)
                        rawn = getattr(respn, "text", str(respn))
                        try:
                            start = rawn.index("{"); end = rawn.rfind("}") + 1; rawn = rawn[start:end]
                        except Exception:
                            pass
                        jd = _json.loads(rawn)
                        nd["spore"] = {
                            "reason": jd.get("reason", "Relevant to the query scope."),
                            "confidence": float(jd.get("confidence", 0.7) or 0.7),
                        }
                    except Exception:
                        # Heuristic fallback
                        md = nd.get("metadata", {}) or {}
                        regs = []
                        try:
                            regs += _re.findall(r"\b(?:40|33)\s+CFR\s+[\d.]+", text, _re.IGNORECASE)[:2]
                            regs += _re.findall(r"\bWAC\s+[\d-]+", text, _re.IGNORECASE)[:2]
                            regs += _re.findall(r"\bRCW\s+[\d.]+", text, _re.IGNORECASE)[:2]
                        except Exception:
                            pass
                        parts = []
                        if regs:
                            parts.append("Cites " + ", ".join(regs))
                        sec = md.get("section") or md.get("header") or md.get("heading")
                        if sec:
                            parts.append(f"Section: {sec}")
                        pg = md.get("page_label", md.get("page"))
                        if pg is not None:
                            parts.append(f"p.{pg}")
                        txt_low = text.lower()
                        if "wastewater" in txt_low or "wwtp" in txt_low:
                            parts.append("WWTP guidance")
                        if "effluent" in txt_low:
                            parts.append("effluent limits")
                        if "permit" in txt_low:
                            parts.append("permitting")
                        reason = "; ".join(parts) or "Matches query terms in retrieved content."
                        conf = 0.6 + (0.1 if regs else 0.0) + (0.05 if sec else 0.0)
                        nd["spore"] = {"reason": reason, "confidence": round(min(0.95, conf), 2)}
            else:
                # No LLM bound: heuristic spore for each node
                import re as _re
                for nd in payload["retrieval"]["nodes"][:top_k]:
                    text = (nd.get("text") or "")[:800]
                    md = nd.get("metadata", {}) or {}
                    regs = []
                    try:
                        regs += _re.findall(r"\b(?:40|33)\s+CFR\s+[\d.]+", text, _re.IGNORECASE)[:2]
                        regs += _re.findall(r"\bWAC\s+[\d-]+", text, _re.IGNORECASE)[:2]
                        regs += _re.findall(r"\bRCW\s+[\d.]+", text, _re.IGNORECASE)[:2]
                    except Exception:
                        pass
                    parts = []
                    if regs:
                        parts.append("Cites " + ", ".join(regs))
                    sec = md.get("section") or md.get("header") or md.get("heading")
                    if sec:
                        parts.append(f"Section: {sec}")
                    pg = md.get("page_label", md.get("page"))
                    if pg is not None:
                        parts.append(f"p.{pg}")
                    txt_low = text.lower()
                    if "wastewater" in txt_low or "wwtp" in txt_low:
                        parts.append("WWTP guidance")
                    if "effluent" in txt_low:
                        parts.append("effluent limits")
                    if "permit" in txt_low:
                        parts.append("permitting")
                    reason = "; ".join(parts) or "Matches query terms in retrieved content."
                    conf = 0.6 + (0.1 if regs else 0.0) + (0.05 if sec else 0.0)
                    nd["spore"] = {"reason": reason, "confidence": round(min(0.95, conf), 2)}
        import json as _json
        if out:
            out_path = Path(out).resolve(); out_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            slug = _slugify(question)
            out_path = CONTEXT_ROOT / f"{_utc_now_iso().replace(':','').replace('-','')}_{slug}.json"
        out_path.write_text(_json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        typer.secho(f"Wrote retrieval context to: {out_path}", fg=typer.colors.GREEN)
        typer.echo(str(out_path))
        return

    # If no API key: fail fast (cloud-only build)
    typer.secho("LLAMA_CLOUD_API_KEY not set; cloud retrieval is required.", fg=typer.colors.RED)
    raise typer.Exit(code=2)


def _synthesize_with_style(
    question_text: str,
    nodes: list,
    style: str = "strict-citation",
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> str:
    """
    Minimal synthesizer: builds a context block from nodes and calls the configured LLM once.
    Optionally binds a provider/model for this call.
    """
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"LlamaIndex Settings unavailable: {exc}")

    # Optionally bind provider/model for this generation
    try:
        if llm_provider or llm_model:
            _apply_llm_provider(llm_provider, llm_model)
    except Exception as exc:
        logger.warning("Could not apply LLM provider override in generate: {}", exc)

    if getattr(_Settings, "llm", None) is None:
        raise RuntimeError("LLM not configured; pass --llm-provider/--llm-model or set API keys in .env")

    # Build a compact context block with numbered items
    labels: List[str] = []
    lines: List[str] = ["Context below (numbered for citation):", "---------------------"]
    max_items = max(10, min(40, len(nodes)))
    for i, node in enumerate(nodes[:max_items], 1):
        md = node.get("metadata", {}) if isinstance(node, dict) else {}
        file = md.get("file_name") or md.get("file_path") or "Unknown"
        page = md.get("page")
        section = md.get("section")
        parts = [str(file)]
        if page is not None:
            parts.append(f"p.{page}")
        if section:
            parts.append(str(section))
        label = " - ".join([parts[0]] + (["; ".join(parts[1:])] if len(parts) > 1 else []))
        labels.append(label)
        text = node.get("text", "") if isinstance(node, dict) else ""
        lines.append(f"[{i}] {label}\n{text}\n")
    context_block = "\n".join(lines)

    if style == "compare":
        extra = "Structure as: Key points (bullets), Side-by-side comparison bullets, short conclusion.\n"
    elif style == "outline":
        extra = "Return a concise outline with nested bullets, focusing on headings/sections.\n"
    elif style == "quote-heavy":
        extra = "Include short, high-signal quotes (5–25 words) with page/section labels.\n"
    else:
        extra = "Be concise and precise. Always include exact section/page labels when available.\n"

    prompt = (
        f"{context_block}\n"
        "---------------------\n"
        "Using ONLY the numbered context above, answer the question with inline [n] citations.\n"
        f"{extra}"
        f"Question: {question_text}\n"
        "Answer: "
    )

    try:
        resp = _Settings.llm.complete(prompt)
        return getattr(resp, "text", str(resp))
    except Exception as exc:
        raise RuntimeError(f"Generation failed: {exc}")

@app.command(rich_help_panel="Core Commands")
def generate(
    context_file: str = typer.Argument(..., help="Path to a context JSON file from 'retrieve'"),
    style: str = typer.Option("strict-citation", "--style", help="strict-citation|compare|outline|quote-heavy"),
    llm_provider: str = typer.Option("cohere", "--llm-provider", help="LLM provider (cohere|openai)"),
) -> None:
    """Phase 2: Generation. Reads a context JSON and synthesizes a response."""
    import json as _json
    p = Path(context_file).resolve()
    if not p.exists():
        typer.secho(f"Context file not found: {p}", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    try:
        data = _json.loads(p.read_text(encoding="utf-8"))
        question_text = data.get("question", "")
        nodes = (data.get("retrieval") or {}).get("nodes", [])
        if not question_text or not nodes:
            raise ValueError("Missing question or nodes in context file")
    except Exception as exc:
        typer.secho(f"Failed to parse context file: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    response = _synthesize_with_style(question_text, nodes, style, llm_provider=llm_provider)
    typer.echo(response)



@app.command()
def enhance(
    in_path: str = typer.Option(..., "--in", help="Input retrieval_session JSON path"),
    out_path: str = typer.Option(..., "--out", help="Output enhanced_retrieval JSON path"),
    write_outline: bool = typer.Option(True, "--write-outline/--no-write-outline", help="Generate response outline"),
    rewrite_spore: bool = typer.Option(True, "--rewrite-spore/--no-rewrite-spore", help="Rewrite spore to align with outline"),
    suggest_retrieve: bool = typer.Option(True, "--suggest-retrieve/--no-suggest-retrieve", help="Emit follow-up retrieve commands"),
    topic_profile: Optional[str] = typer.Option(None, "--topic-profile", help="Named topic profile to guide outline"),
    max_per_source: Optional[int] = typer.Option(None, "--max-per-source", help="Soft cap per source (normalization hint)"),
    include_terms: Optional[str] = typer.Option(None, "--include-terms", help="Terms to consider when composing suggestions"),
    filters: Optional[str] = typer.Option(None, "--filters", help="JSON filters to reflect in suggestions"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run without writing output"),
) -> None:
    """Phase 1.5: Enhance retrieval context for better generation (outline, gaps, suggestions, spore rewrite)."""
    try:
        from caliper_v2.commands.enhance import main as enhance_main  # lazy import
    except Exception as exc:
        typer.secho(f"Enhance module unavailable: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    try:
        outp = enhance_main(
            in_path=in_path,
            out_path=out_path,
            write_outline=write_outline,
            rewrite_spore=rewrite_spore,
            suggest_retrieve=suggest_retrieve,
            topic_profile=topic_profile,
            max_per_source=max_per_source,
            include_terms=include_terms,
            filters=filters,
            dry_run=dry_run,
        )
        typer.secho(f"Enhanced retrieval written to: {outp}", fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"Enhance failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def judge(
    context: str = typer.Option(..., "--context", help="Path to enhanced_retrieval or retrieval_session JSON"),
    generation: str = typer.Option(..., "--generation", help="Path to generated draft (Markdown/text)"),
    out: str = typer.Option(..., "--out", help="Output judgment_report JSON path"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Require stronger evidence to mark claims supported"),
    max_evidence_per_claim: int = typer.Option(3, "--max-evidence-per-claim", help="Max evidence snippets per claim"),
    claims_json: Optional[str] = typer.Option(None, "--claims-json", help="Optional JSON list of claims to judge"),
    bm25_k: int = typer.Option(200, "--bm25-k", help="BM25 top-K for candidate selection"),
    embed_strategy: str = typer.Option("auto", "--embed-strategy", help="auto|none (skip embeddings)"),
    per_source_cap: int = typer.Option(3, "--per-source-cap", help="Cap candidate snippets per source before adjudication"),
) -> None:
    """Phase 3: Judge generated output against retrieved evidence (claim-level report)."""
    try:
        from caliper_v2.commands.judge import main as judge_main  # lazy import
    except Exception as exc:
        typer.secho(f"Judge module unavailable: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    try:
        outp = judge_main(
            context_path=context,
            generation_path=generation,
            out_path=out,
            strict=strict,
            max_evidence_per_claim=max_evidence_per_claim,
            claims_json=claims_json,
            bm25_k=bm25_k,
            embed_strategy=embed_strategy,
            per_source_cap=per_source_cap,
        )
        typer.secho(f"Judgment report written to: {outp}", fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"Judge failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def review(
    context: str = typer.Option(..., "--context", help="Path to enhanced_retrieval or retrieval_session JSON"),
    draft: str = typer.Option(..., "--draft", help="Path to draft section Markdown/text"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Optional topic profile json for lints"),
    criteria: Optional[str] = typer.Option(None, "--criteria", help="Path to review criteria file (JSON or Markdown)"),
    outline: Optional[str] = typer.Option(None, "--outline", help="Path to outline file for additional guidance"),
    out_json: str = typer.Option(..., "--out-json", help="Output review_report JSON path"),
    out_md: str = typer.Option(..., "--out-md", help="Output Markdown report path"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Pass-through to judge strictness"),
    max_evidence_per_claim: int = typer.Option(5, "--max-evidence-per-claim", help="Judge evidence cap per claim"),
    use_llm: bool = typer.Option(True, "--use-llm/--no-llm", help="Use LLM for additional review analysis"),
) -> None:
    """Review a draft document against context and custom criteria.
    
    This command performs a comprehensive review of a draft document by:
    1. Checking claims against the provided context (using judge)
    2. Running deterministic lints for issues like acronyms and units
    3. Analyzing the document against custom review criteria
    4. Using LLM to provide in-depth analysis based on the criteria
    
    The --criteria parameter is key for domain-specific reviews. For example:
    
    For wastewater facility plans: --criteria data_v2/criteria/wastewater_facility_plan.md
    
    You can also provide an --outline parameter with a document outline to use as additional guidance:
    
    Example command:
      caliper_v2 review --context facility_requirements.json --draft facility_plan.md --criteria data_v2/criteria/wastewater_facility_plan.md --outline outputs/outline/q01_outline.md --out-json review.json --out-md review.md
    """
    try:
        from caliper_v2.commands.review import main as review_main  # lazy import
    except Exception as exc:
        typer.secho(f"Review module unavailable: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    try:
        res = review_main(
            context_path=context,
            draft_path=draft,
            out_json=out_json,
            out_md=out_md,
            profile=profile,
            criteria_path=criteria,
            outline_path=outline,
            strict=strict,
            max_evidence_per_claim=max_evidence_per_claim,
            use_llm_review=use_llm,
        )
        typer.secho(f"Review report written to: {res['json']} and {res['md']}", fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"Review failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
