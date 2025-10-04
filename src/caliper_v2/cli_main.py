from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import typer
from loguru import logger

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

# Register GraphRAG subcommands (export-cloud, build-cloud, retrieve, stats)
try:
    from caliper_v2.commands import graph_cli as _graph_cli_app  # type: ignore
    app.add_typer(_graph_cli_app.app, name="graph", help="GraphRAG commands (experimental, non-disruptive)")
except Exception as _graph_exc:
    logger.debug("Graph subcommands not registered: {}", _graph_exc)

# Register Report subcommands (claims extraction, etc.)
try:
    from caliper_v2.commands import report as _report_app  # type: ignore
    app.add_typer(_report_app.app, name="report", help="Report tools (sectionize, claims)")
except Exception as _rep_exc:
    logger.debug("Report subcommands not registered: {}", _rep_exc)

INDEX_ROOT = Path("data_v2/indexes").resolve()
CONTEXT_ROOT = Path("data_v2/context").resolve()
CONTEXT_ROOT.mkdir(parents=True, exist_ok=True)
CATALOG_ROOT = CONTEXT_ROOT / "catalogs"
CATALOG_ROOT.mkdir(parents=True, exist_ok=True)

# --- cohere readiness helpers ---
_WARNED_PASSAGE_ID_COMPUTE: bool = False

def _normalize_text(s: Optional[str], *, lower: bool = False) -> str:
    """General text normalization: remove control chars, collapse whitespace, optional lowercase."""
    try:
        if not s:
            return ""
        import re as _re
        # Remove control characters except tab/newline which will be collapsed anyway
        s2 = _re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", s)
        # Normalize whitespace
        s2 = _re.sub(r"\s+", " ", s2).strip()
        if lower:
            s2 = s2.lower()
        return s2
    except Exception:
        try:
            return s.strip().lower() if lower and isinstance(s, str) else (s or "").strip()
        except Exception:
            return ""

def _normalize_text_for_id(s: Optional[str]) -> str:
    """Normalize text for stable ID hashing: remove soft-hyphens and collapse whitespace."""
    try:
        if not s:
            return ""
        # remove soft hyphen and other zero-width chars
        s2 = s.replace("\u00AD", "").replace("\u200B", "").replace("\u200C", "").replace("\u200D", "")
        # collapse whitespace
        import re as _re
        s2 = _re.sub(r"\s+", " ", s2).strip()
        return s2
    except Exception:
        return (s or "").strip()

def _relpath_for_id(abs_path: Optional[str], ingest_root: Optional[Path]) -> str:
    """Lowercased forward-slash relpath for stable hashing.
    Falls back to basename when relpath cannot be computed."""
    try:
        if not abs_path:
            return ""
        p = Path(abs_path)
        if ingest_root:
            try:
                rel = p.resolve().relative_to(ingest_root.resolve())
            except Exception:
                rel = p.name  # fallback to filename only
        else:
            rel = p
        relstr = str(rel).replace("\\", "/").lower()
        return relstr
    except Exception:
        return (abs_path or "").replace("\\", "/").lower()

def _sha256_hex(s: str) -> str:
    import hashlib as _hashlib
    h = _hashlib.sha256()
    h.update(s.encode("utf-8", errors="ignore"))
    return h.hexdigest()

def _sha256_file(file_path: Path) -> str:
    """Compute SHA256 of a file in chunks to avoid memory spikes."""
    import hashlib as _hashlib
    h = _hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def _infer_routing(relpath: str, filename: str) -> Dict[str, Optional[str]]:
    """Heuristic routing metadata from path/name.
    Returns keys: jurisdiction, agency, doc_type, date
    """
    import re as _re
    rp = (relpath or "").lower()
    fn = (filename or "").lower()
    # Jurisdiction
    jurisdiction = None
    if any(key in rp for key in ["federal", "usc", "cfr", "epa"]):
        jurisdiction = "federal"
    elif _re.search(r"\\b(ak|al|ar|az|ca|co|ct|dc|de|fl|ga|hi|ia|id|il|in|ks|ky|la|ma|md|me|mi|mn|mo|ms|mt|nc|nd|ne|nh|nj|nm|nv|ny|oh|ok|or|pa|ri|sc|sd|tn|tx|ut|va|vt|wa|wi|wv)\\b", rp):
        jurisdiction = "state"
    elif any(key in rp for key in ["city", "county", "municipal", "local"]):
        jurisdiction = "local"
    # Agency (simple signals)
    agency = None
    if "epa" in rp or "us-epa" in rp or "us_epa" in rp or "environmental protection agency" in rp:
        agency = "epa"
    elif "ecology" in rp or "wa-dept-ecology" in rp or "department of ecology" in rp:
        agency = "ecology"
    elif "usace" in rp or "army corps" in rp:
        agency = "usace"
    # Doc type from filename
    doc_type = None
    if _re.search(r"permit|application|coverage", fn):
        doc_type = "permit"
    elif _re.search(r"guidance|guide|handbook|manual", fn):
        doc_type = "guidance"
    elif _re.search(r"rule|regulation|cfr|wac|rcw|ordinance", fn):
        doc_type = "regulation"
    elif _re.search(r"report|study|whitepaper|white-paper", fn):
        doc_type = "report"
    # Date: try YYYY-MM-DD, YYYYMMDD, YYYY
    date = None
    m = _re.search(r"(20\d{2}|19\d{2})(?:[-_]?(\d{2})(?:[-_]?(\d{2}))?)?", fn)
    if m:
        yyyy = m.group(1)
        mm = m.group(2) or "01"
        dd = m.group(3) or "01"
        try:
            date = f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}"
        except Exception:
            date = yyyy
    return {"jurisdiction": jurisdiction, "agency": agency, "doc_type": doc_type, "date": date}

def stable_document_id(file_path: Optional[str], ingest_root: Optional[Path]) -> str:
    """did_<sha256(relpath)[:16]>"""
    rel = _relpath_for_id(file_path, ingest_root)
    return f"did_{_sha256_hex(rel)[:16]}"

def stable_passage_id(
    file_path: Optional[str],
    start_char: Optional[int],
    end_char: Optional[int],
    text_for_hash: Optional[str],
    ingest_root: Optional[Path],
) -> str:
    """pid_<sha256(relpath:start:end:sha256(text_norm)[:16])[:24]>"""
    rel = _relpath_for_id(file_path, ingest_root)
    start = 0 if start_char is None else int(start_char)
    end = 0 if end_char is None else int(end_char)
    tnorm = _normalize_text_for_id(text_for_hash or "")
    inner = f"{rel}:{start}:{end}:{_sha256_hex(tnorm)[:16]}"
    return f"pid_{_sha256_hex(inner)[:24]}"

def _get_or_compute_passage_id(node_obj: Any, ingest_root: Optional[Path] = None) -> str:
    """Best-effort to return a passage_id from node metadata or compute one.
    WARNs once if computed at retrieval time for backward compatibility."""
    global _WARNED_PASSAGE_ID_COMPUTE
    try:
        md = getattr(node_obj, "metadata", {}) or {}
        pid = md.get("passage_id")
        if pid:
            return str(pid)
        # compute
        file_path = md.get("file_path") or md.get("file_name")
        # try positions from attributes or metadata
        start = getattr(node_obj, "start_char_idx", None) or md.get("start_char") or md.get("start_char_idx")
        # Prefer explicit end, else infer from text length
        text_val = None
        try:
            gt = getattr(node_obj, "get_text", None)
            if callable(gt):
                text_val = gt() or ""
        except Exception:
            text_val = None
        if text_val is None:
            text_val = getattr(node_obj, "text", "") or ""
        end = getattr(node_obj, "end_char_idx", None) or md.get("end_char") or md.get("end_char_idx")
        if end is None and isinstance(text_val, str):
            end = (0 if start is None else int(start)) + len(text_val)
        pid = stable_passage_id(file_path, start, end, text_val, ingest_root)
        if not _WARNED_PASSAGE_ID_COMPUTE:
            try:
                logger.warning("passage_id missing in node metadata; computing on-the-fly for dedup. Consider re-ingesting to persist passage_id.")
            except Exception:
                pass
            _WARNED_PASSAGE_ID_COMPUTE = True
        return pid
    except Exception:
        # last resort
        return f"pid_{_sha256_hex(str(getattr(node_obj, 'node_id', '') or getattr(node_obj, 'id_', '') or '')[:64])[:24]}"


def _count_tokens(text: Optional[str]) -> int:
    """Count tokens using tiktoken cl100k_base with whitespace fallback."""
    try:
        if not text:
            return 0
        import tiktoken  # type: ignore
        try:
            enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(text))
    except Exception:
        try:
            return len((text or "").split())
        except Exception:
            return 0

# --- table and kv extraction helpers (L1, L2) ---

def _extract_markdown_tables(text: str, max_tables: int = 1) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Very simple Markdown table detector/parser.
    Returns (tables, caption) where tables is a list of {header:[], rows:[[]]} dicts.
    Caption is a heuristic: preceding line starting with 'Table' or ending with ':'
    """
    try:
        lines = (text or "").splitlines()
        tables: List[Dict[str, Any]] = []
        caption: Optional[str] = None
        i = 0
        while i < len(lines) and len(tables) < max_tables:
            line = lines[i].strip()
            # Detect a table header line like: | col1 | col2 |
            if line.startswith("|") and "|" in line[1:]:
                # Next non-empty line that looks like a separator: |---|---|
                if i + 1 < len(lines) and set(lines[i + 1].strip().replace("|", "").replace(":", "").replace("-", "").strip()) == set():
                    # Parse header
                    header = [c.strip() for c in line.strip().strip("|").split("|")]
                    j = i + 2
                    rows: List[List[str]] = []
                    while j < len(lines):
                        l2 = lines[j].strip()
                        if not l2.startswith("|"):
                            break
                        row = [c.strip() for c in l2.strip().strip("|").split("|")]
                        # Pad/truncate to header length
                        if len(row) < len(header):
                            row += [""] * (len(header) - len(row))
                        if len(row) > len(header):
                            row = row[: len(header)]
                        rows.append(row)
                        j += 1
                    tables.append({"header": header, "rows": rows})
                    # Caption heuristic: look at previous non-empty line
                    k = i - 1
                    while k >= 0 and not (lines[k].strip()):
                        k -= 1
                    if k >= 0:
                        prev = lines[k].strip()
                        if prev.lower().startswith("table") or prev.endswith(":"):
                            caption = prev
                    i = j
                    continue
            i += 1
        return tables, caption
    except Exception:
        return [], None

def _extract_kv_pairs(text: str, max_pairs: int = 20) -> List[Dict[str, str]]:
    """Extract simple Key: Value pairs from the first ~100 lines of text."""
    try:
        import re as _re
        pairs: List[Dict[str, str]] = []
        for line in (text or "").splitlines()[:100]:
            m = _re.match(r"\s*([A-Za-z0-9_\-/ ]{2,64})\s*:\s*(.+)\s*$", line)
            if m:
                k = _normalize_text(m.group(1))
                v = _normalize_text(m.group(2))
                if k and v:
                    pairs.append({"key": k, "value": v})
                    if len(pairs) >= max_pairs:
                        break
        return pairs
    except Exception:
        return []

# Minimal stub to avoid unresolved reference in optional tooling paths
def _synthesize_with_style(question_text: Any, nodes: Any, style_local: Any) -> str:  # pragma: no cover
    try:
        return "synthesis-unavailable"
    except Exception:
        return "synthesis-unavailable"


def _extract_question_from_file(path: Path, max_chars: int = 16000) -> str:
    """Read question/instructions from a text/markdown file.

    Heuristics:
    - If YAML front matter exists and contains a 'question:' key, use its value.
    - Otherwise return the whole file (trimmed to max_chars).
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover
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


def _load_bm25_index_safe(bm25_path: Path, persist_dir: Path):
    """Safely load BM25 index with path + checksum verification."""
    import hashlib as _hashlib
    import pickle as _pickle

    p = bm25_path.resolve()
    if not p.name.endswith(".pkl"):
        raise ValueError("Refusing to load non-.pkl BM25 file")
    allowed_root = INDEX_ROOT
    if allowed_root not in p.parents:
        raise ValueError("BM25 path outside allowed index dir")
    sha_file = persist_dir / "bm25_index.sha256"
    if sha_file.exists():
        expected = sha_file.read_text(encoding="utf-8").strip()
        h = _hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        if h.hexdigest() != expected:
            raise ValueError("BM25 SHA256 mismatch")
    with p.open("rb") as f:
        return _pickle.load(f)


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
        return "openai", "gpt-5"
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
        # Avoid reusing a stale LLM when explicit provider binding fails
        try:
            from llama_index.core import Settings as _Settings  # type: ignore
            if llm_provider:  # explicit request
                _Settings.llm = None  # force later checks to fail fast
        except Exception:
            pass
        # Re-raise when user explicitly requested a provider so callers can decide to abort
        if llm_provider:
            raise


def _provider_choices() -> List[str]:
    return ["openai", "anthropic", "gemini", "cohere", "grok"]


def _list_existing_indexes() -> List[str]:
    if not INDEX_ROOT.exists():
        return []
    return sorted([p.name for p in INDEX_ROOT.iterdir() if p.is_dir()])


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


def _bm25_rebuild_from_jsonl(persist_dir: Path):
    """Rebuild BM25 retriever deterministically from bm25_corpus.jsonl if present."""
    try:
        from llama_index.retrievers.bm25 import BM25Retriever  # type: ignore
        from llama_index.core.schema import TextNode  # type: ignore
        import json as _json
    except Exception as exc:
        logger.warning("BM25 rebuild prerequisites missing: {}", exc)
        return None

    jsonl = persist_dir / "bm25_corpus.jsonl"
    if not jsonl.exists():
        return None
    nodes: List[Any] = []
    try:
        with jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = _json.loads(line)
                    pid = obj.get("passage_id") or obj.get("node_id")
                    text = obj.get("text_clean") or obj.get("text", "")
                    if text:
                        nodes.append(TextNode(text=text, id_=pid) if pid else TextNode(text=text))
                except Exception:
                    continue
        if not nodes:
            return None
        return BM25Retriever.from_defaults(nodes=nodes)
    except Exception as exc:
        logger.warning("BM25 rebuild from JSONL failed: {}", exc)
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
        # Make global flags visible to subcommands without eagerly binding
        os.environ["CALIPER_LLM_PROVIDER"] = llm_provider
    if llm_model:
        logger.info("Received --llm-model flag: {}", llm_model)
        os.environ["CALIPER_LLM_MODEL"] = llm_model
    if embed_provider:
        logger.info("Received --embed-provider flag (placeholder): {}", embed_provider)
    # Do NOT configure an LLM at startup; just record intended overrides via env
    try:
        prov, model, src = _resolve_llm_from_flags_or_settings(llm_provider, llm_model)
        if prov or model:
            logger.info("Startup provider resolution [{}]: provider={}, model={} (not applied)", src, prov, model)
        else:
            logger.debug("Startup provider resolution: none (not applied)")
    except Exception as exc:
        logger.warning("LLM provider resolution failed (ignored): {}", exc)
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
    Environment and runtime diagnostic.
    - Checks critical API keys and warns about embedding readiness
    - Shows provider resolution
    - Lists available indexes and missing ones
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

    # Embedding readiness (OpenAI as default)
    if not os.getenv("OPENAI_API_KEY"):
        typer.secho(
            "\nEmbedding preflight: No OPENAI_API_KEY found. Default OpenAI embeddings will fail.",
            fg=typer.colors.RED,
        )
        typer.secho("Options:", fg=typer.colors.YELLOW)
        typer.echo("- Set OPENAI_API_KEY in your .env or environment")
        typer.echo("- Or run with --embed-provider local (smoke testing only)")
    else:
        typer.secho("\nEmbedding preflight: OK (OPENAI_API_KEY present).", fg=typer.colors.GREEN)

    # Indexes
    typer.secho("\nIndexes under data_v2/indexes:", fg=typer.colors.GREEN, bold=True)
    idxs = _list_existing_indexes()
    if not idxs:
        typer.secho(
            "- None found. Ingest first with: python run_caliper_v2.py ingest knowledge_base --index all_docs_enhanced --persist",
            fg=typer.colors.YELLOW,
        )
    else:
        for n in idxs:
            path = INDEX_ROOT / n
            persisted = "yes" if path.exists() and any(path.iterdir()) else "no"
            bm25_ok = (path / "bm25_index.pkl").exists() or (path / "bm25_corpus.json").exists()
            typer.echo(
                f"- {n} (persisted artifacts present: {persisted}; bm25: {'yes' if bm25_ok else 'no'})"
            )

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
def ingest(
    path: str = typer.Argument(..., help="Path to file or directory to ingest"),
    index: str = typer.Option("default", "--index", help="Index name"),
    persist: bool = typer.Option(
        False, "--persist/--no-persist", help="Persist index artifacts to disk"
    ),
    embed_provider: Optional[str] = typer.Option(
        None,
        "--embed-provider",
        help="Embedding provider (default uses OpenAI; use 'local' for offline smoke)",
    ),
    use_llama_parse: bool = typer.Option(
        False, "--llama-parse", help="Use LlamaParse for PDFs (requires LLAMA_CLOUD_API_KEY)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Re-ingest even if unchanged"),
    bm25_pickle: bool = typer.Option(False, "--bm25-pickle/--no-bm25-pickle", help="Also persist BM25 pickle for speed"),
) -> None:
    """Minimal ingest using LlamaIndex with optional persistence.

    Also writes a summary-layer index (document/section summaries) when an LLM is configured,
    enabling hierarchical retrieval routing.
    """
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
            from llama_index.embeddings.cohere import CohereEmbedding  # type: ignore
            # Ensure the Cohere API key is available and pass it explicitly
            from dotenv import load_dotenv as _load_dotenv  # type: ignore
            _load_dotenv()  # best-effort reload (safe if already loaded)
            cohere_key = (os.getenv("COHERE_API_KEY") or "").strip()
            if not cohere_key:
                typer.secho(
                    "COHERE_API_KEY is not set. Add it to your .env or environment to use Cohere embeddings.",
                    fg=typer.colors.RED,
                )
                raise typer.Exit(code=2)

            _Settings.embed_model = CohereEmbedding(
                model="embed-v4.0",
                input_type="search_document",
                api_key=cohere_key,  # pass explicitly to avoid env resolution issues
            )
            try:
                if hasattr(_Settings, "embed_batch_size"):
                    _Settings.embed_batch_size = int(os.getenv("CALIPER_EMBED_BATCH", "64"))
                logger.info(
                    "Index embeddings configured: provider=cohere, model=embed-v4.0, input_type=search_document, batch_size={}",
                    getattr(_Settings, "embed_batch_size", "default"),
                )
            except Exception:
                pass
        except Exception as exc:
            typer.secho(f"Failed to initialize Cohere embeddings: {exc}", fg=typer.colors.RED)
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

    # Precompute file hashes for idempotent ingest (M2)
    file_hash_map: Dict[str, str] = {}
    try:
        ingest_root_path = Path(path).resolve()
        if ingest_root_path.is_file():
            ingest_root_path = ingest_root_path.parent
        for d in docs:
            md = getattr(d, "metadata", {}) or {}
            fp = md.get("file_path") or md.get("file_name")
            if not fp:
                continue
            abs_fp = Path(fp)
            if not abs_fp.is_absolute():
                abs_fp = (ingest_root_path / fp)
            relp = _relpath_for_id(str(abs_fp), ingest_root_path)
            h = _sha256_file(abs_fp)
            if h:
                file_hash_map[relp] = h
    except Exception as exc:
        logger.debug("File hashing skipped: {}", exc)
        file_hash_map = {}

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

    # Determine ingest root for stable ID relpaths
    try:
        _ingest_root = Path(path).resolve()
        if _ingest_root.is_file():
            _ingest_root = _ingest_root.parent
    except Exception:
        _ingest_root = None  # type: ignore

    # Idempotent ingest filtering: decide which relpaths to process (M2)
    import json as _json
    prev_manifest: Dict[str, str] = {}
    changed_relpaths: set[str] = set()
    unchanged_relpaths: set[str] = set()
    manifest_path = (INDEX_ROOT / index / "file_hashes.json")
    if persist and not force and manifest_path.exists():
        try:
            prev_manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
            for relp, h in (file_hash_map or {}).items():
                if prev_manifest.get(relp) == h:
                    unchanged_relpaths.add(relp)
                else:
                    changed_relpaths.add(relp)
        except Exception as exc:
            logger.warning("Failed reading file_hashes.json: {}", exc)
            prev_manifest = {}
            changed_relpaths = set(file_hash_map.keys()) if file_hash_map else set()
    else:
        changed_relpaths = set(file_hash_map.keys()) if file_hash_map else set()

    # If nothing changed and manifest exists, short-circuit
    if persist and not force and prev_manifest and not changed_relpaths:
        typer.secho(f"No changes detected for index '{index}'. SKIP unchanged files. Use --force to re-ingest.", fg=typer.colors.GREEN)
        return

    # Metadata enrichment: basic breadcrumbs + section heading + file_name fallback + stable IDs
    import re as _re
    heading_regex = _re.compile(r"^(#{1,6})\s+(.+)$", _re.MULTILINE)
    new_nodes = []
    _skip_logged: set[str] = set()
    for n in nodes:
        md = getattr(n, "metadata", {}) or {}
        # Filter out nodes from unchanged files when applicable
        try:
            file_hint0 = md.get("file_path") or md.get("file_name")
            relp0 = _relpath_for_id(file_hint0, _ingest_root) if file_hint0 else None
            if persist and not force and prev_manifest and relp0 and unchanged_relpaths and relp0 in unchanged_relpaths:
                if relp0 not in _skip_logged:
                    logger.info("SKIP unchanged: {}", relp0)
                    _skip_logged.add(relp0)
                continue
        except Exception:
            pass
        # Section from last heading in chunk text
        try:
            text_getter = getattr(n, "get_text", None)
            ntext = text_getter() if callable(text_getter) else getattr(n, "text", "")
            headings = heading_regex.findall(ntext or "")
            if headings:
                # take the last heading's title
                md["section"] = headings[-1][1].strip()
                md["section_heading"] = md["section"]
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
        # Propagate page numbers consistently
        if md.get("page_label") and not md.get("page"):
            md["page"] = md.get("page_label")
        # Stable IDs + text fields
        try:
            file_hint = md.get("file_path") or md.get("file_name")
            did = stable_document_id(file_hint, _ingest_root)
            # character span if available
            start = getattr(n, "start_char_idx", None) or md.get("start_char") or md.get("start_char_idx")
            # prefer explicit end else infer length from text
            ntext2 = None
            try:
                gt2 = getattr(n, "get_text", None)
                if callable(gt2):
                    ntext2 = gt2() or ""
            except Exception:
                ntext2 = None
            if ntext2 is None:
                ntext2 = getattr(n, "text", "") or ""
            # Set dual text fields and counts
            try:
                md["text_raw"] = ntext2
                _clean = _normalize_text(ntext2)
                md["text_clean"] = _clean
                md["char_count"] = len(_clean)
                md["token_count"] = _count_tokens(_clean)
                # L1: table extraction (first table only)
                if not md.get("table_json"):
                    tables, caption = _extract_markdown_tables(ntext2 or "")
                    if tables:
                        md["table_json"] = tables[0]
                        if caption:
                            md["table_caption"] = caption
                # L2: key-value pairs
                if not md.get("kv_pairs"):
                    kvs = _extract_kv_pairs(ntext2 or "")
                    if kvs:
                        md["kv_pairs"] = kvs
            except Exception:
                pass
            end = getattr(n, "end_char_idx", None) or md.get("end_char") or md.get("end_char_idx")
            if end is None and isinstance(ntext2, str):
                end = (0 if start is None else int(start)) + len(ntext2)
            pid = stable_passage_id(file_hint, start, end, ntext2, _ingest_root)
            md["document_id"] = did
            md["passage_id"] = pid
            # Routing metadata (M1)
            try:
                relp = _relpath_for_id(file_hint, _ingest_root)
                fname = Path(str(file_hint)).name if file_hint else (md.get("file_name") or "")
                r = _infer_routing(relp, str(fname))
                for k in ("jurisdiction", "agency", "doc_type", "date"):
                    if r.get(k) and not md.get(k):
                        md[k] = r[k]
            except Exception:
                pass
        except Exception:
            pass
        n.metadata = md
        new_nodes.append(n)

    # Build vector index
    nodes = new_nodes
    idx = VectorStoreIndex(nodes)

    # Persist if requested (vector + BM25)
    if persist:
        persist_dir = INDEX_ROOT / index
        persist_dir.mkdir(parents=True, exist_ok=True)
        try:
            idx.storage_context.persist(persist_dir=str(persist_dir))
            typer.secho(f"Persisted vector index to {persist_dir}", fg=typer.colors.GREEN)
            # Write embedding_config.json for retrieval-time validation
            try:
                import json as _json
                from datetime import datetime as _dt
                provider = "cohere"
                model = None
                dim = None
                similarity = "cosine"
                index_input_type = "search_document"
                try:
                    from llama_index.core import Settings as _Settings  # type: ignore
                    em = getattr(_Settings, "embed_model", None)
                    model = getattr(em, "model_name", None) or getattr(em, "model", None)
                    try:
                        # Best-effort dimension inference
                        vec = None
                        get_emb = getattr(em, "get_text_embedding", None)
                        if callable(get_emb):
                            vec = get_emb("caliper-dim-probe")
                        if isinstance(vec, list):
                            dim = len(vec)
                    except Exception:
                        dim = None
                except Exception:
                    pass
                cfg = {
                    "provider": provider,
                    "model": model or "unknown",
                    "dimension": int(dim) if isinstance(dim, int) else (dim or None),
                    "similarity": similarity,
                    "index_input_type": index_input_type,
                    "created_at": _dt.utcnow().isoformat() + "Z",
                }
                (persist_dir / "embedding_config.json").write_text(_json.dumps(cfg, indent=2), encoding="utf-8")
            except Exception as _exc:
                logger.warning("Failed to write embedding_config.json: {}", _exc)
        except Exception as exc:
            logger.exception("Failed to persist index: {}", exc)
            typer.secho("Failed to persist index; index remains in-memory", fg=typer.colors.YELLOW)

        # Update idempotent ingest manifest (M2)
        try:
            import json as _json
            if file_hash_map:
                (persist_dir / "file_hashes.json").write_text(_json.dumps(file_hash_map, indent=2), encoding="utf-8")
                typer.secho("Updated file_hashes.json (idempotent ingest manifest)", fg=typer.colors.GREEN)
        except Exception as exc:
            logger.warning("Failed to write file_hashes.json: {}", exc)

        # BM25 corpus persistence (JSON/JSONL); optional pickle for speed
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
                    mdn = getattr(n, "metadata", {}) or {}
                    get_text = getattr(n, "get_text", None)
                    text_raw = (get_text() if callable(get_text) else getattr(n, "text", "")) or ""
                    text_clean = mdn.get("text_clean") or _normalize_text(text_raw)
                    relp = _relpath_for_id(mdn.get("file_path") or mdn.get("file_name"), _ingest_root)
                    obj = {
                        "node_id": node_id,
                        "passage_id": mdn.get("passage_id"),
                        "text": text_clean,
                        "char_count": mdn.get("char_count") or len(text_clean),
                        "token_count": mdn.get("token_count") or _count_tokens(text_clean),
                        "file_name": mdn.get("file_name"),
                        "relative_path": relp,
                        "section_heading": mdn.get("section_heading") or mdn.get("section") or mdn.get("header") or mdn.get("heading"),
                        "page": mdn.get("page") or mdn.get("page_label"),
                        "jurisdiction": mdn.get("jurisdiction"),
                        "agency": mdn.get("agency"),
                        "doc_type": mdn.get("doc_type"),
                        "date": mdn.get("date"),
                        "table_json": mdn.get("table_json"),
                        "table_caption": mdn.get("table_caption"),
                        "kv_pairs": mdn.get("kv_pairs"),
                    }
                    _json.dump(obj, f, ensure_ascii=False)
                    f.write("\n")
            typer.secho("Persisted BM25 corpus (JSONL)", fg=typer.colors.GREEN)

            # Optional pickle build for speed (M3)
            if bm25_pickle:
                try:
                    from llama_index.retrievers.bm25 import BM25Retriever  # type: ignore
                    from llama_index.core.schema import TextNode  # type: ignore
                    import pickle as _pickle, hashlib as _hashlib

                    tnodes = []
                    for n in nodes:
                        mdn = getattr(n, "metadata", {}) or {}
                        txt = mdn.get("text_clean")
                        if not txt:
                            gt = getattr(n, "get_text", None)
                            raw = gt() if callable(gt) else getattr(n, "text", "") or ""
                            txt = _normalize_text(raw)
                        pid = mdn.get("passage_id")
                        tnodes.append(TextNode(text=txt, id_=pid) if pid else TextNode(text=txt))
                    bm25obj = BM25Retriever.from_defaults(nodes=tnodes)
                    pkl_path = persist_dir / "bm25_index.pkl"
                    with pkl_path.open("wb") as pf:
                        _pickle.dump(bm25obj, pf)
                    # Write checksum
                    h = _hashlib.sha256()
                    with pkl_path.open("rb") as pf2:
                        for chunk in iter(lambda: pf2.read(8192), b""):
                            h.update(chunk)
                    (persist_dir / "bm25_index.sha256").write_text(h.hexdigest(), encoding="utf-8")
                    typer.secho("Persisted BM25 pickle with checksum", fg=typer.colors.GREEN)
                except Exception as _exc:
                    logger.warning("BM25 pickle build failed: {}", _exc)
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


def _load_persisted_vector_index(index_name: str):
    try:
        from llama_index.core import StorageContext, load_index_from_storage  # type: ignore
    except Exception as exc:
        typer.secho(
            "LlamaIndex dependencies not installed. Install with one of:\n"
            "  pip install -r requirements.heavy.txt\n"
            "  or on Windows: .\\caliper.bat (auto installs)\n"
            "  or on WSL: scripts/caliper_wsl.sh (auto installs)\n",
            fg=typer.colors.RED,
        )
        logger.error("Import error for LlamaIndex: {}", exc)
        raise

    persist_dir = INDEX_ROOT / index_name
    if not persist_dir.exists() or not any(persist_dir.iterdir()):
        raise FileNotFoundError(
            f"Persisted index '{index_name}' not found at {persist_dir}. Ingest first with --persist."
        )
    storage = StorageContext.from_defaults(persist_dir=str(persist_dir))
    idx = load_index_from_storage(storage)
    return idx, storage, persist_dir


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
    rerank_min_score: float = 0.5,
    summary_first: bool = True,
    dense_top_k: Optional[int] = None,
    sparse_top_k: Optional[int] = None,
    alpha_blend: Optional[float] = None,
) -> List[Any]:
    """Run hybrid retrieval with query expansion + optional reranking. Returns NodeWithScore list."""
    # Validate embedding config if present
    try:
        import json as _json
        cfg_path = persist_dir / "embedding_config.json"
        if not cfg_path.exists():
            logger.warning("embedding_config.json missing in {} (proceeding)", persist_dir)
        else:
            cfg = _json.loads(cfg_path.read_text(encoding="utf-8"))
            model = cfg.get("model")
            provider = cfg.get("provider")
            if str(provider).lower() != "cohere":
                logger.warning("Index provider mismatch: expected cohere, found {} in {}", provider, persist_dir)
    except Exception as _exc:
        logger.debug("embedding_config.json read failed: {}", _exc)
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
                    try:
                        pid = _get_or_compute_passage_id(getattr(nws, "node", nws), ingest_root=None)
                    except Exception:
                        pid = getattr(nws.node, "node_id", None) or getattr(nws.node, "id_", None)
                    if pid and pid not in seen:
                        seen[str(pid)] = nws
            vector_nodes = list(seen.values())
        except Exception as exc:
            logger.warning("Vector retrieval failed: {}", exc)

    # BM25
    bm25_built = False
    # Prefer prebuilt pickle when available
    try:
        bm25_path = persist_dir / "bm25_index.pkl"
        if bm25_path.exists():
            bm25_obj = _load_bm25_index_safe(bm25_path, persist_dir)
            tmp = bm25_obj.retrieve(question)
            bm25_nodes = tmp[: max(1, min(10, len(tmp)))]
            bm25_built = True
    except Exception as exc1:
        logger.warning("BM25 pickle load failed: {}", exc1)
    # Otherwise prefer deterministic rebuild from JSONL corpus
    if not bm25_built:
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
    # Optional slicing for alpha blending
    if alpha_blend is not None:
        if isinstance(dense_top_k, int) and dense_top_k > 0:
            vector_nodes = vector_nodes[:dense_top_k]
        if isinstance(sparse_top_k, int) and sparse_top_k > 0:
            bm25_nodes = bm25_nodes[:sparse_top_k]
    fused_nodes: list[Any] = []
    if mode == "vector" or (mode in {"bm25", "hybrid"} and not bm25_nodes and alpha_blend is None):
        fused_nodes = vector_nodes
    elif mode == "bm25":
        fused_nodes = bm25_nodes
    elif mode == "hybrid":
        if alpha_blend is not None:
            # Alpha-blended score fusion
            alpha_v = max(0.0, min(1.0, float(alpha_blend)))
            # Build normalized score maps keyed by passage_id
            def _norm_map(ns: List[Any]) -> Dict[str, float]:
                vals: List[float] = []
                ids: List[str] = []
                for i, nws in enumerate(ns):
                    try:
                        pid = _get_or_compute_passage_id(getattr(nws, "node", nws), ingest_root=None)
                    except Exception:
                        pid = f"x{i}"
                    sc = getattr(nws, "score", None)
                    if sc is None:
                        sc = 1.0 - (i / max(1.0, len(ns)))  # rank proxy
                    ids.append(str(pid))
                    vals.append(float(sc))
                if not vals:
                    return {}
                lo, hi = min(vals), max(vals)
                if hi - lo < 1e-9:
                    return {ids[i]: 0.5 for i in range(len(ids))}
                return {ids[i]: (vals[i] - lo) / (hi - lo) for i in range(len(ids))}

            dmap = _norm_map(vector_nodes)
            smap = _norm_map(bm25_nodes)
            keys = set(dmap.keys()) | set(smap.keys())
            combined: List[Tuple[str, float]] = []
            for k in keys:
                dv = dmap.get(k, 0.0)
                sv = smap.get(k, 0.0)
                combined.append((k, alpha_v * dv + (1.0 - alpha_v) * sv))
            combined.sort(key=lambda t: t[1], reverse=True)
            # Map back to actual objects; prefer vector node object, else bm25
            by_id: Dict[str, Any] = {}
            for nws in vector_nodes:
                try:
                    pid = _get_or_compute_passage_id(getattr(nws, "node", nws), ingest_root=None)
                    by_id.setdefault(str(pid), nws)
                except Exception:
                    pass
            for nws in bm25_nodes:
                try:
                    pid = _get_or_compute_passage_id(getattr(nws, "node", nws), ingest_root=None)
                    by_id.setdefault(str(pid), nws)
                except Exception:
                    pass
            fused_nodes = [by_id[k] for k, _ in combined[: max(1, top_k * 2)]]
        else:
            # Reciprocal Rank Fusion
            def rrf(rank: int, k: int = 60) -> float:
                return 1.0 / (k + rank)

            scores: Dict[str, float] = {}
            order: Dict[str, Any] = {}
            for i, nws in enumerate(vector_nodes):
                try:
                    key_id = _get_or_compute_passage_id(getattr(nws, "node", nws), ingest_root=None)
                except Exception:
                    key_id = f"v{i}"
                scores[key_id] = scores.get(key_id, 0.0) + rrf(i + 1)
                order.setdefault(key_id, nws)
            for i, nws in enumerate(bm25_nodes):
                try:
                    key_id = _get_or_compute_passage_id(getattr(nws, "node", nws), ingest_root=None)
                except Exception:
                    key_id = f"b{i}"
                scores[key_id] = scores.get(key_id, 0.0) + rrf(i + 1)
                order.setdefault(key_id, nws)
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
            # Prefer text_clean from metadata if available
            try:
                md0 = getattr(getattr(n, "node", n), "metadata", {}) or {}
                clean = md0.get("text_clean")
            except Exception:
                clean = None
            if isinstance(clean, str) and clean.strip():
                snippet = clean
            else:
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
        # Default: try Cohere first; ST fallback triggers only if Cohere fails
        reranker = "cohere"
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
                        from llama_index.core.schema import TextNode, NodeWithScore  # type: ignore
                        if os.getenv("COHERE_API_KEY"):
                            # Build NodeWithScore objects for reranker
                            nws_list = [NodeWithScore(node=TextNode(text=t), score=None) for t in texts]
                            # Use latest rerank model with return_documents for confidence scores
                            rerank_model = os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.5")
                            pp = CohereRerank(
                                top_n=min(reranker_top_n, len(nws_list)),
                                model=rerank_model
                            )
                            rescored = pp.postprocess_nodes(nws_list, query_str=question)  # type: ignore
                            # Apply threshold filtering and remap to original groups by text
                            text_to_idx = {t: i for i, t in enumerate(texts)}
                            new_order: List[Tuple[str, List[Any]]] = []
                            seen_idx: set[int] = set()
                            for gn in rescored:
                                # Drop groups below threshold
                                try:
                                    gn_score = float(getattr(gn, 'score', 0.0) or 0.0)
                                except Exception:
                                    gn_score = 0.0
                                if gn_score < float(rerank_min_score):
                                    continue
                                t = getattr(getattr(gn, "node", None), "text", None)
                                i = text_to_idx.get(t)
                                if i is not None and i not in seen_idx:
                                    # Add rerank confidence to metadata of all nodes in this group
                                    enhanced_nodes = []
                                    for node in nodes_lists[i]:
                                        if hasattr(node, 'metadata'):
                                            if not getattr(node, 'metadata', None):
                                                node.metadata = {}
                                            node.metadata["rerank_confidence"] = gn_score
                                        enhanced_nodes.append(node)
                                    new_order.append((texts[i], enhanced_nodes))
                                    seen_idx.add(i)
                            # Append remaining groups in original order
                            for i, v in enumerate(nodes_lists):
                                if i not in seen_idx:
                                    new_order.append((texts[i], v))
                            ordered = new_order
                            if os.getenv("CALIPER_DEBUG_RERANK"):
                                logger.debug("Applied Cohere rerank to {} groups; kept {}", len(texts), len(ordered))
                    except Exception as exc:
                        logger.warning("Failed Cohere group rerank: {}", exc)
                        # Fallback to ST-mini when Cohere rerank fails
                        try:
                            scores_order = _st_rerank_nodes(
                                [type("_NW", (), {"node": type("_N", (), {"text": t})}) for t in texts],
                                question,
                                top_n=len(texts),
                                model_key="st-mini",
                            )
                            # Build mapping from text to rank
                            ranks: Dict[str, int] = {}
                            for rank, w in enumerate(scores_order):
                                tt = getattr(w.node, "text", "")
                                ranks[tt] = rank
                            ordered = sorted(ordered, key=lambda pair: ranks.get(pair[0], 1_000_000))
                        except Exception as _st_fallback_exc:
                            logger.warning("ST-mini fallback rerank failed: {}", _st_fallback_exc)
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
                        if os.getenv("CALIPER_DEBUG_RERANK"):
                            logger.debug("Applied ST rerank '{}' to {} groups", rr, len(texts))
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
                        if os.getenv("CALIPER_DEBUG_RERANK"):
                            logger.debug("Applied LLM rerank to {} groups", len(texts))
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

    # Add citation anchoring information for Cohere-style citations
    citation_anchor = {
        "start_char": 0,
        "end_char": len(snippet) if snippet else 0,
        "source_file": md.get("file_name"),
        "page": md.get("page_label", md.get("page")),
        "section": md.get("section") or md.get("header") or md.get("heading"),
        "document_title": doc_title,
        "confidence": md.get("rerank_confidence")  # From enhanced reranking
    }
    
    # Ensure document_id/passsage_id present (compute if missing)
    try:
        did = md.get("document_id")
        if not did:
            file_hint = md.get("file_path") or md.get("file_name")
            did = stable_document_id(file_hint, None)
    except Exception:
        did = None
    try:
        pid = md.get("passage_id")
        if not pid:
            pid = _get_or_compute_passage_id(node_obj, ingest_root=None)
    except Exception:
        pid = None

    return {
        "node_id": node_id,
        "document_id": did,
        "passage_id": pid,
        "parent_id": parent_id,
        "score": float(score_val) if isinstance(score_val, (int, float)) else None,
        "text": snippet or "",
        "text_raw": (md.get("text_raw") or (snippet or "")),
        "text_clean": (md.get("text_clean") or _normalize_text(snippet or "")),
        "char_count": (md.get("char_count") or len(md.get("text_clean") or _normalize_text(snippet or ""))),
        "token_count": (md.get("token_count") or _count_tokens(md.get("text_clean") or _normalize_text(snippet or ""))),
        "citation_anchor": citation_anchor,  # NEW: Enable exact text span citations
            "metadata": {
            "file_name": md.get("file_name"),
            "file_path": md.get("file_path"),
            # Back-compat: keep 'page', but also emit normalized 'page_label' and raw 'page_raw'
            "page": md.get("page_label", md.get("page")),
            "page_label": (str(md.get("page_label", md.get("page"))) if (md.get("page_label") is not None or md.get("page") is not None) else None),
            "page_raw": (str(md.get("page")) if md.get("page") is not None else None),
            "section": md.get("section") or md.get("header") or md.get("heading"),
            "breadcrumbs": md.get("breadcrumbs"),
            "index": md.get("index"),
            "jurisdiction": md.get("jurisdiction"),
            "agency": md.get("agency"),
            "doc_type": md.get("doc_type"),
            "date": md.get("date"),
            "table_json": md.get("table_json"),
            "table_caption": md.get("table_caption"),
            "kv_pairs": md.get("kv_pairs"),
            "document_title": doc_title,
            "author": doc_author,
            "publisher": doc_publisher,
            "rerank_confidence": md.get("rerank_confidence"),  # Include confidence score
            "retrieval_strategy": "cohere_optimized" if md.get("rerank_confidence") else "standard"
        },
    }


def _generate_spore(nodes: List[Any], question: str) -> Dict[str, Any]:
    """Call the configured LLM once to generate a 'context spore' explanation and confidence."""
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        _Settings = None  # type: ignore

    # First, do a quick content analysis to inform the LLM
    import re
    regulations_found = set()
    standards_found = set()
    topics_mentioned = set()
    jurisdictions = set()
    
    top_labels = []
    content_snippets = []
    
    for i, nws in enumerate(nodes[:12], 1):
        md = getattr(nws.node, "metadata", {}) if hasattr(nws, "node") else {}
        text = getattr(nws.node, "text", "") if hasattr(nws, "node") else nws.get("text", "")
        
        # Build label for this node
        file = (md or {}).get("file_name") or (md or {}).get("file_path") or "Unknown"
        page = (md or {}).get("page_label", (md or {}).get("page"))
        section = (md or {}).get("section") or (md or {}).get("header")
        jurisdiction = (md or {}).get("jurisdiction", "")
        
        parts = [str(file)]
        if page is not None:
            parts.append(f"p.{page}")
        if section:
            parts.append(str(section))
        if jurisdiction:
            jurisdictions.add(jurisdiction)
            
        top_labels.append(f"[{i}] " + " - ".join([parts[0]] + (["; ".join(parts[1:])] if len(parts) > 1 else [])))
        
        # Extract key content for analysis
        text_preview = text[:200] if text else ""
        content_snippets.append(f"[{i}] {text_preview}...")
        
        # Quick regex to find regulations and standards
        cfr_matches = re.findall(r"\b(?:40|33)\s+CFR\s+[\d.]+", text[:500], re.IGNORECASE)
        regulations_found.update(cfr_matches[:2])  # Limit per node
        
        wac_matches = re.findall(r"\bWAC\s+[\d-]+", text[:500], re.IGNORECASE)
        regulations_found.update(wac_matches[:2])
        
        # Check for standards
        text_upper = text[:500].upper()
        if "AASHTO" in text_upper:
            standards_found.add("AASHTO")
        if "WEF" in text_upper or "WATER ENVIRONMENT" in text_upper:
            standards_found.add("WEF")
        if "ASCE" in text_upper:
            standards_found.add("ASCE")
        if "AWWA" in text_upper:
            standards_found.add("AWWA")
        
        # Topic detection
        text_lower = text[:500].lower()
        if "wwtp" in text_lower or "wastewater" in text_lower:
            topics_mentioned.add("wastewater treatment")
        if "bridge" in text_lower and "foundation" in text_lower:
            topics_mentioned.add("bridge foundations")
        if "effluent" in text_lower:
            topics_mentioned.add("effluent requirements")
        if "permit" in text_lower:
            topics_mentioned.add("permitting")

    # Build enhanced prompt with actual content analysis
    analysis_context = ""
    if regulations_found:
        analysis_context += f"\nRegulations detected: {', '.join(list(regulations_found)[:5])}"
    if standards_found:
        analysis_context += f"\nStandards detected: {', '.join(sorted(standards_found))}"
    if topics_mentioned:
        analysis_context += f"\nTopics covered: {', '.join(list(topics_mentioned)[:4])}"
    if jurisdictions:
        analysis_context += f"\nJurisdictions: {', '.join(sorted(jurisdictions))}"

    prompt = (
        "Analyze why these retrieved documents are relevant for answering the question.\n"
        "Be SPECIFIC about regulations, standards, and technical content found.\n\n"
        "Question: " + question + "\n"
        "\nContent Analysis:" + (analysis_context or "\nGeneral technical content") + "\n"
        "\nTop Sources:\n" + "\n".join(top_labels[:8]) + "\n"
        "\nSample Content (first 200 chars from top nodes):\n" + "\n".join(content_snippets[:4]) + "\n"
        "\nProvide a detailed analysis in JSON format with:\n"
        "- summary: 1-2 sentences explaining coverage and relevance (mention specific regulations/standards found)\n"
        "- rationale_bullets: array of 3-5 SPECIFIC observations (e.g., 'Covers 40 CFR 133 effluent limits', not generic statements)\n"
        "- confidence: float 0.0-1.0 based on actual coverage\n"
        "\nReturn ONLY valid JSON. Be specific, not generic.\n"
    )

    # Build a better default spore based on the actual content analysis
    default_bullets = []
    if regulations_found:
        default_bullets.append(
            f"Retrieved {len(regulations_found)} regulatory citations including {', '.join(list(regulations_found)[:3])}"
        )
    if standards_found:
        default_bullets.append(f"Found technical standards from {', '.join(sorted(standards_found))}")
    if topics_mentioned:
        default_bullets.append(
            f"Covers {len(topics_mentioned)} relevant topics: {', '.join(list(topics_mentioned)[:3])}"
        )
    if jurisdictions:
        default_bullets.append(f"Includes content from jurisdictions: {', '.join(sorted(jurisdictions))}")
    
    # Add generic bullet if we have few specific ones
    if len(default_bullets) < 3:
        default_bullets.append("Sources selected based on semantic and lexical relevance to query")
        default_bullets.append("Includes upstream/downstream context for comprehensive coverage")
    
    # Calculate default confidence based on what we found
    default_confidence = 0.5
    if regulations_found:
        default_confidence += 0.2
    if standards_found:
        default_confidence += 0.15
    if len(topics_mentioned) >= 2:
        default_confidence += 0.15
    default_confidence = min(0.95, default_confidence)
    
    default_spore = {
        "summary": (
            f"Retrieved {len(nodes[:12])} nodes covering {len(regulations_found)} regulations, "
            f"{len(standards_found)} standards, addressing '{question[:80]}...'"
        ),
        "rationale_bullets": default_bullets[:5],
        "confidence": round(default_confidence, 2),
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
                mini = (
                    "Return only JSON with keys summary (string), rationale_bullets (array of strings), "
                    "confidence (number)."
                )
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
    search_mode: str = typer.Option(
        "hybrid", "--search-mode", help="vector|bm25|hybrid (bm25/hybrid require persistence)"
    ),
    top_k: int = typer.Option(16, "--top-k", help="Retriever pre-rank top_k (cloud: before rerank)"),
    reranker: Optional[str] = typer.Option("cohere", "--reranker", help="cohere,llm (ST fallback auto if Cohere fails)"),
    reranker_top_n: int = typer.Option(16, "--reranker-top-n", help="Keep N after rerank"),
    rerank_min_score: float = typer.Option(0.5, "--rerank-min-score", help="Drop results with rerank score below this (when available)"),
    embed_provider: Optional[str] = typer.Option(
        None, "--embed-provider", help="Embedding provider (use 'local' to avoid OpenAI)"
    ),
    out: Optional[str] = typer.Option(None, "--out", help="Output JSON path (default: data_v2/context/*.json)"),
    cloud: Optional[bool] = typer.Option(
        None,
        "--cloud/--local",
        help="Force cloud (LlamaCloud) or local retrieval. Default: auto (env-driven).",
    ),
    cloud_rerank: bool = typer.Option(True, "--cloud-rerank/--no-cloud-rerank", help="Enable server-side reranking when using LlamaCloud"),
    no_spore: bool = typer.Option(False, "--no-spore", help="Skip spore generation (no extra LLM call)"),
    node_spore: bool = typer.Option(True, "--node-spore/--no-node-spore", help="Also attach a brief per-node justification+confidence (auto-capped)"),
    include_terms: Optional[str] = typer.Option(None, "--include-terms", help="Comma-separated lexical must-have terms to boost (cloud)"),
    exclude_sections: Optional[str] = typer.Option(None, "--exclude-sections", help="Comma-separated section keywords to drop (e.g., toc,glossary,references,figures)"),
    retrieval_mode: str = typer.Option("chunks", "--retrieval-mode", help="chunks|files_via_content|files_via_metadata|auto_routed (cloud)"),
    dense_k: int = typer.Option(8, "--dense-k", help="Cloud dense_similarity_top_k (also used locally if --use-alpha)"),
    sparse_k: int = typer.Option(8, "--sparse-k", help="Cloud sparse_similarity_top_k (also used locally if --use-alpha)"),
    alpha: float = typer.Option(0.5, "--alpha", help="Cloud hybrid alpha (0..1); for local, requires --use-alpha"),
    use_alpha: bool = typer.Option(False, "--use-alpha/--rrf", help="Use alpha blending locally instead of RRF (default RRF)"),
    rerank_top_n: int = typer.Option(8, "--rerank-top-n", help="Cloud rerank top N"),
    filters: Optional[str] = typer.Option(None, "--filters", help='JSON object of metadata filters, e.g., {"jurisdiction":"WA","chapter":"G1"}'),
    infer_filters: bool = typer.Option(True, "--infer-filters/--no-infer-filters", help="Enable schema-driven filter inference when supported (cloud)"),
    cloud_reranker_chain: Optional[str] = typer.Option(None, "--cloud-reranker-chain", help="Group-aware reranker chain for cloud: comma-separated cohere,st-mini,llm; fallback to CALIPER_CLOUD_RERANKER_CHAIN"),
    cloud_bm25_lite: bool = typer.Option(False, "--cloud-bm25-lite/--no-cloud-bm25-lite", help="Apply BM25-lite over cloud candidates before MMR"),
    bm25_lite_min_score: float = typer.Option(0.05, "--bm25-lite-min-score", help="BM25-lite min score threshold to keep a candidate"),
    hyde: bool = typer.Option(True, "--hyde/--no-hyde", help="Enable HyDE query expansion (cloud/local)"),
    trace: bool = typer.Option(False, "--trace", help="Write a .trace.json next to the output with basic timings and counts"),
) -> None:
    """Phase 1: Retrieval + Context Spore. Writes a persistent JSON file and prints its path."""
    # Setup environment and decide routing mode first
    _setup_environment()
    import time as _time
    _t0 = _time.perf_counter()

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

    # Decide routing mode: cloud if explicitly requested, or if env IDs exist
    def _should_use_cloud() -> bool:
        if cloud is not None:
            return bool(cloud)
        if not os.getenv("LLAMA_CLOUD_API_KEY"):
            return False
        # Use cloud only if at least one requested index has both IDs
        for name in index_list:
            b_id, s_id = _cloud_ids_for_index(name)
            if b_id and s_id:
                return True
        return False

    if _should_use_cloud():
        try:
            from caliper_v2.services.llama_cloud_index import LlamaCloudIndex  # type: ignore
        except Exception as exc:
            typer.secho(f"Cloud routing requested but unavailable: {exc}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        def _sfirst_retrieve(q: str, base_idx: Any, sum_idx: Any, s_top: int = 36, b_top: int = 180, per_group: int = 18):
            # Strict cloud retrieval: surface errors instead of swallowing them
            retriever_kwargs = {
                "similarity_top_k": min(100, int(s_top)),
                "retrieval_mode": retrieval_mode,
                "dense_similarity_top_k": max(1, int(dense_k)),
                "sparse_similarity_top_k": max(0, int(sparse_k)),
                "alpha": max(0.0, min(1.0, float(alpha))),
                "enable_reranking": bool(cloud_rerank),
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

            # Build query expansions (multi-query + HyDE) with safe fallbacks
            expansions: List[str] = [q]
            try:
                use_multi = str(os.getenv("CALIPER_CLOUD_USE_MULTI", "1")).lower() not in {"0", "false", "no"}
            except Exception:
                use_multi = True
            try:
                if use_multi:
                    from llama_index.core.query_transform.multi_para import MultiParagraphQueryTransform  # type: ignore
                    try:
                        mq = MultiParagraphQueryTransform(num_queries=4)
                        expanded = mq.run(query_str=q)
                        if isinstance(expanded, list):
                            expansions.extend([e for e in expanded if isinstance(e, str)])
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                use_hyde = str(os.getenv("CALIPER_CLOUD_USE_HYDE", "1")).lower() not in {"0", "false", "no"}
            except Exception:
                use_hyde = True
            try:
                if use_hyde:
                    from llama_index.core.query_transform.hyde import HyDEQueryTransform  # type: ignore
                    try:
                        hyde = HyDEQueryTransform()
                        hypothetical = hyde.run(query_str=q)
                        if isinstance(hypothetical, str):
                            expansions.append(hypothetical)
                    except Exception:
                        pass
            except Exception:
                pass
            # De-duplicate and cap number of expansions
            _seen_exp: set[str] = set()
            _dedup_exp: List[str] = []
            for e in expansions:
                es = (e or "").strip()
                if es and es not in _seen_exp:
                    _dedup_exp.append(es)
                    _seen_exp.add(es)
                if len(_dedup_exp) >= 6:
                    break
            expansions = _dedup_exp or [q]

            # Summary hits for boosting
            try:
                s_ret = sum_idx.as_retriever(**retriever_kwargs)
            except TypeError:
                s_ret = sum_idx.as_retriever(similarity_top_k=min(100, int(s_top)))
            s_hits = s_ret.retrieve(q)

            # Construct boosted query list: start with raw expansions, then expansions combined with (file, section) hints
            boosted_queries: List[str] = []
            _seen_q: set[str] = set()

            def _push(items: List[str]) -> None:
                for it in items:
                    val = " ".join((it or "").split()).strip()
                    if not val:
                        continue
                    if val in _seen_q:
                        continue
                    boosted_queries.append(val)
                    _seen_q.add(val)

            _push(expansions)
            for h in s_hits:
                try:
                    md = getattr(h.node, "metadata", {}) or {}
                    file_hint = md.get("file_name") or md.get("file_path") or ""
                    section_hint = md.get("section") or md.get("header") or md.get("heading") or ""
                    if file_hint or section_hint:
                        combos = [(" ".join([e, file_hint, section_hint])).strip() for e in expansions]
                        _push([c for c in combos if c])
                except Exception:
                    continue

            # Retrieve from base with a capped set of boosted queries
            seen: Dict[str, Any] = {}
            try:
                bret = base_idx.as_retriever(**{**retriever_kwargs, "similarity_top_k": min(100, int(b_top))})
            except TypeError:
                bret = base_idx.as_retriever(similarity_top_k=min(100, int(b_top)))
            for q2 in boosted_queries[:24]:
                try:
                    for nw in bret.retrieve(q2)[:per_group]:
                        nid = getattr(nw.node, "node_id", None) or getattr(nw.node, "id_", None)
                        if nid and nid not in seen:
                            seen[nid] = nw
                except Exception:
                    continue

            # Fallback: try raw expansions and original q if coverage is thin
            if len(seen) < max(24, b_top // 3):
                for e in expansions[:3]:
                    try:
                        for nw in bret.retrieve(e)[:per_group]:
                            nid = getattr(nw.node, "node_id", None) or getattr(nw.node, "id_", None)
                            if nid and nid not in seen:
                                seen[nid] = nw
                    except Exception:
                        continue
            if len(seen) < max(24, b_top // 3):
                try:
                    for nw in bret.retrieve(q)[:per_group]:
                        nid = getattr(nw.node, "node_id", None) or getattr(nw.node, "id_", None)
                        if nid and nid not in seen:
                            seen[nid] = nw
                except Exception:
                    pass
            return list(seen.values())

        # Respect user-specified indexes strictly (no auto scoping)
        scoped_indexes = list(index_list)
        buckets: List[Any] = []
        per_index_results: Dict[str, List[Any]] = {}
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
                # Build a boosted query per-index without mutating the original question
                orig_q = question
                boosted_q = orig_q
                if include_terms:
                    extra = [t.strip() for t in include_terms.split(",") if t.strip()]
                    if extra:
                        boosted_q = boosted_q + " " + " ".join(extra)
                # Default lexical boosts for this domain
                default_terms = [
                    "G1", "General Sewer Plan", "Engineering Report", "Plans and Specifications",
                    "WAC 173-240-050", "WAC 173-240-060", "WAC 173-240-070", "SEPA", "NEPA", "SERP",
                ]
                boosted_q = boosted_q + " " + " ".join(default_terms)
                res = _sfirst_retrieve(boosted_q, base, summ, s_top=min(36, top_k), b_top=min( max(24, top_k*6), 100), per_group=max(8, min(24, top_k)))
                # Tag each node with its logical index for metadata enrichment
                for _n in res:
                    try:
                        setattr(_n, "_caliper_index_name", name)
                    except Exception:
                        pass
                per_index_results[name] = list(res)
                buckets += res
            except Exception as exc:
                typer.secho(f"Cloud retrieval failed for '{name}': {exc}", fg=typer.colors.RED)
                raise typer.Exit(code=1)

        # Cross-index normalization + round-robin interleave, then dedup by passage_id
        fused: List[Any] = []
        def _normalize_cloud(ns: List[Any]) -> List[Tuple[float, Any]]:
            vals: List[float] = [float(getattr(n, "score", 0.0) or 0.0) for n in ns]
            if not vals:
                return [(0.0, n) for n in ns]
            lo, hi = min(vals), max(vals)
            if hi - lo < 1e-6:
                return [(0.5, n) for n in ns]
            return [(((float(getattr(n, "score", 0.0) or 0.0) - lo) / (hi - lo)), n) for n in ns]
        buckets_norm: List[List[Tuple[float, Any]]] = [
            _normalize_cloud(per_index_results[k]) for k in per_index_results.keys()
        ]
        budget_cap = max(10, min(200, top_k * 8))
        while any(buckets_norm) and len(fused) < budget_cap:
            for b in list(buckets_norm):
                if not b:
                    continue
                b.sort(key=lambda t: t[0], reverse=True)
                _, item = b.pop(0)
                fused.append(item)
                if len(fused) >= budget_cap:
                    buckets_norm = []
                    break
        # Deduplicate by stable passage_id
        try:
            seen_pids: set[str] = set()
            uniq: List[Any] = []
            for item in fused:
                try:
                    pid = _get_or_compute_passage_id(getattr(item, "node", item), ingest_root=None)
                except Exception:
                    pid = getattr(getattr(item, "node", item), "node_id", None) or getattr(getattr(item, "node", item), "id_", None)
                key = str(pid) if pid else None
                if key and key not in seen_pids:
                    seen_pids.add(key)
                    uniq.append(item)
            fused = uniq
        except Exception:
            pass

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

        # Rerank and diversity
        final_keep = max(1, min(200, top_k))
        chain = [r.strip() for r in str(reranker or "").split(",") if r.strip()]
        try:
            # 1) Basic Cohere rerank (node-level), if requested via --reranker
            if chain:
                if "cohere" in chain:
                    try:
                        from llama_index.postprocessor.cohere_rerank import CohereRerank  # type: ignore
                        rerank_model = os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.5")
                        rr = CohereRerank(top_n=final_keep, model=rerank_model)
                        rescored = rr.postprocess_nodes(fused, query_str=question)  # type: ignore
                        if any(getattr(n, 'score', None) is not None for n in rescored):
                            fused = [n for n in rescored if float(getattr(n, 'score', 0.0) or 0.0) >= float(rerank_min_score)] or list(rescored)[:final_keep]
                        else:
                            fused = list(rescored)
                    except Exception as exc:
                        logger.warning("Cohere node-level rerank failed: {}", exc)
                        # Fallback to ST-mini
                        try:
                            fused = _st_rerank_nodes(fused, question, top_n=final_keep, model_key="st-mini")
                        except Exception as _st_exc:
                            logger.warning("ST-mini fallback failed: {}", _st_exc)
            # 2) Optional group-aware reranker chain for cloud
            cloud_chain_str = cloud_reranker_chain or os.getenv("CALIPER_CLOUD_RERANKER_CHAIN")
            if cloud_chain_str:
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
                def _group_nodes(nodes_in: List[Any]) -> List[Tuple[Tuple[str, str, str], List[Any]]]:
                    groups: Dict[Tuple[str, str, str], List[Any]] = {}
                    for n in nodes_in:
                        k = _group_key(n)
                        groups.setdefault(k, []).append(n)
                    seen_keys: List[Tuple[str, str, str]] = []
                    for n in nodes_in:
                        k = _group_key(n)
                        if k not in seen_keys:
                            seen_keys.append(k)
                    return [(k, groups[k]) for k in seen_keys]
                def _group_repr_text(group_nodes: List[Any], max_chars: int = 2000) -> str:
                    parts: List[str] = []
                    total = 0
                    for n in group_nodes:
                        try:
                            md0 = getattr(getattr(n, "node", n), "metadata", {}) or {}
                            clean = md0.get("text_clean")
                        except Exception:
                            clean = None
                        if isinstance(clean, str) and clean.strip():
                            snippet = clean
                        else:
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
                grouped = _group_nodes(fused)
                group_texts = [(_group_repr_text(nodes), nodes) for _, nodes in grouped]
                def _apply_chain_to_groups(chain_list: List[str], items: List[Tuple[str, List[Any]]]) -> List[Tuple[str, List[Any]]]:
                    ordered = items
                    for rr in chain_list:
                        rr = rr.strip().lower()
                        if not rr:
                            continue
                        texts = [t for t, _ in ordered]
                        nodes_lists = [ns for _, ns in ordered]
                        if rr == "cohere":
                            try:
                                from llama_index.postprocessor.cohere_rerank import CohereRerank  # type: ignore
                                from llama_index.core.schema import TextNode, NodeWithScore  # type: ignore
                                if os.getenv("COHERE_API_KEY"):
                                    nws_list = [NodeWithScore(node=TextNode(text=t), score=None) for t in texts]
                                    rerank_model = os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.5")
                                    pp = CohereRerank(top_n=min(reranker_top_n, len(nws_list)), model=rerank_model)
                                    rescored = pp.postprocess_nodes(nws_list, query_str=question)  # type: ignore
                                    text_to_idx = {t: i for i, t in enumerate(texts)}
                                    new_order: List[Tuple[str, List[Any]]] = []
                                    seen_idx: set[int] = set()
                                    for gn in rescored:
                                        try:
                                            gn_score = float(getattr(gn, 'score', 0.0) or 0.0)
                                        except Exception:
                                            gn_score = 0.0
                                        if gn_score < float(rerank_min_score):
                                            continue
                                        t = getattr(getattr(gn, "node", None), "text", None)
                                        i = text_to_idx.get(t)
                                        if i is not None and i not in seen_idx:
                                            enhanced_nodes = []
                                            for node in nodes_lists[i]:
                                                if hasattr(node, 'metadata'):
                                                    if not getattr(node, 'metadata', None):
                                                        node.metadata = {}
                                                    node.metadata["rerank_confidence"] = gn_score
                                                enhanced_nodes.append(node)
                                            new_order.append((texts[i], enhanced_nodes))
                                            seen_idx.add(i)
                                    for i, v in enumerate(nodes_lists):
                                        if i not in seen_idx:
                                            new_order.append((texts[i], v))
                                    ordered = new_order
                            except Exception as exc:
                                logger.warning("Failed Cohere group rerank: {}", exc)
                                # Fallback to ST-mini when Cohere rerank fails
                                try:
                                    scores_order = _st_rerank_nodes(
                                        [type("_NW", (), {"node": type("_N", (), {"text": t})}) for t in texts],
                                        question,
                                        top_n=len(texts),
                                        model_key="st-mini",
                                    )
                                    ranks: Dict[str, int] = {}
                                    for rank, w in enumerate(scores_order):
                                        tt = getattr(w.node, "text", "")
                                        ranks[tt] = rank
                                    ordered = sorted(ordered, key=lambda pair: ranks.get(pair[0], 1_000_000))
                                except Exception as _st_fallback_exc:
                                    logger.warning("ST-mini fallback rerank failed: {}", _st_fallback_exc)
                        elif rr.startswith("st-"):
                            try:
                                scores_order = _st_rerank_nodes(
                                    [type("_NW", (), {"node": type("_N", (), {"text": t})}) for t in texts],
                                    question,
                                    top_n=len(texts),
                                    model_key=rr,
                                )
                                ranks: Dict[str, int] = {}
                                for rank, w in enumerate(scores_order):
                                    t = getattr(w.node, "text", "")
                                    ranks[t] = rank
                                ordered = sorted(ordered, key=lambda pair: ranks.get(pair[0], 1_000_000))
                            except Exception as exc:
                                logger.warning("Failed ST group rerank '{}': {}", rr, exc)
                        elif rr == "llm":
                            try:
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
                chain_list = [r for r in str(cloud_chain_str).split(",") if r.strip()]
                ordered_groups = _apply_chain_to_groups(chain_list, group_texts)
                fused = [n for _, ns in ordered_groups for n in ns]

            # 3) Optional BM25-lite over cloud candidates
            if cloud_bm25_lite and fused:
                try:
                    from caliper_v2.services.judge_components import build_bm25, tokenize  # type: ignore
                    docs: List[str] = []
                    for n in fused:
                        try:
                            md0 = getattr(getattr(n, "node", n), "metadata", {}) or {}
                            txt = md0.get("text_clean")
                            if not isinstance(txt, str) or not txt.strip():
                                gt = getattr(getattr(n, "node", n), "get_text", None)
                                txt = gt() if callable(gt) else getattr(getattr(n, "node", n), "text", "")
                            docs.append((txt or "")[:1600])
                        except Exception:
                            docs.append("")
                    bm25 = build_bm25(docs)
                    q_tokens = tokenize(question or "")
                    scored = []
                    for i, d in enumerate(docs):
                        try:
                            s = bm25.score(q_tokens, i)
                        except Exception:
                            s = 0.0
                        scored.append((s, fused[i]))
                    # Filter by threshold and sort
                    keep = [(s, n) for s, n in scored if float(s) >= float(bm25_lite_min_score)] or scored
                    keep.sort(key=lambda t: float(t[0]), reverse=True)
                    fused = [n for _, n in keep[:max(1, final_keep * 2)]]
                except Exception as exc:
                    logger.warning("BM25-lite step failed (skipped): {}", exc)

            # 4) MMR diversity and final cap
            from llama_index.core.postprocessor import MMREngine  # type: ignore
            mmr = MMREngine(diversity=0.3)
            fused = mmr.postprocess_nodes(fused, query_str=question)  # type: ignore
        except Exception as _exc:
            # If rerank fails, just trim
            fused = fused[:final_keep]
        fused = fused[:final_keep]
        if not fused:
            typer.secho(
                "No nodes retrieved after rerank/diversity; check cloud IDs, hybrid params, and query specificity.",
                fg=typer.colors.YELLOW,
            )

        spore = {} if no_spore else _generate_spore(fused, question)
        payload: Dict[str, Any] = {
            "type": "retrieval_session",
            "version": 1,
            "created_at": _utc_now_iso(),
            "question": question,
            "indexes": scoped_indexes,
            "search_mode": search_mode,
            "requested_top_k": top_k,
            "final_kept": len(fused),
            "top_k": len(fused),
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
        
        # Define heuristic spore function locally to avoid circular imports
        def _heuristic_node_spore(md: Dict[str, Any], text: str, question: str) -> Dict[str, Any]:
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
        
        # Optional per-node spore generation (cloud path)
        if node_spore and not no_spore and payload["retrieval"]["nodes"]:
            try:
                from llama_index.core import Settings as _Settings  # type: ignore
                llm = getattr(_Settings, "llm", None)
            except Exception:
                llm = None
            if llm is not None:
                import json as _json, re as _re
                for nd in payload["retrieval"]["nodes"][:final_keep]:
                    text = (nd.get("text") or "")[:1000]
                    md = nd.get("metadata", {}) or {}
                    label = md.get("file_name") or md.get("file_path") or "Unknown"
                    prompt_ns = (
                        "Return ONLY JSON with keys reason (1-2 sentences) and confidence (0.0-1.0).\n"
                        "Explain concretely how this snippet helps answer the question; mention section/page if present.\n"
                        f"Question: {question}\n"
                        f"Source: {label}\n"
                        f"Text: {text}\n"
                        'JSON: {"reason": "...", "confidence": 0.0}'
                    )
                    try:
                        respn = llm.complete(prompt_ns)
                        rawn = getattr(respn, "text", str(respn))
                        try:
                            start = rawn.index("{"); end = rawn.rfind("}") + 1; rawn = rawn[start:end]
                        except Exception:
                            pass
                        jd = _json.loads(rawn) if rawn else {}
                    except Exception:
                        jd = {}

                    # Robust extraction and de-genericization
                    reason = None
                    if isinstance(jd, dict):
                        for k in ("reason", "rationale", "explanation", "why", "justification"):
                            v = jd.get(k)
                            if isinstance(v, str) and v.strip():
                                reason = v.strip()
                                break
                    conf_val = None
                    try:
                        conf_val = float(jd.get("confidence")) if isinstance(jd, dict) and jd.get("confidence") is not None else None
                    except Exception:
                        conf_val = None

                    heur = _heuristic_node_spore(md, text, question)
                    generic_phrases = {
                        "relevant to the query",
                        "relevant to the question",
                        "relevant to the query scope",
                        "related to the query",
                    }
                    if not reason or reason.strip().lower().strip(".") in generic_phrases:
                        reason = heur["reason"]
                    confidence = conf_val if isinstance(conf_val, (int, float)) and 0.0 <= conf_val <= 1.0 else heur["confidence"]
                    nd["spore"] = {"reason": reason, "confidence": float(confidence)}
            else:
                # No LLM bound: apply heuristic spore for each node
                for nd in payload["retrieval"]["nodes"][:final_keep]:
                    text = (nd.get("text") or "")[:800]
                    md = nd.get("metadata", {}) or {}
                    nd["spore"] = _heuristic_node_spore(md, text, question)
        import json as _json
        if out:
            out_path = Path(out).resolve(); out_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            slug = _slugify(question)
            out_path = CONTEXT_ROOT / f"{_utc_now_iso().replace(':','').replace('-','')}_{slug}.json"
        out_path.write_text(_json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        typer.secho(f"Wrote retrieval context to: {out_path}", fg=typer.colors.GREEN)
        typer.echo(str(out_path))
        if trace:
            trace_path = out_path.with_suffix(".trace.json")
            trace_data = {"elapsed": round(_time.perf_counter() - _t0, 3)}
            trace_path.write_text(_json.dumps(trace_data, indent=2), encoding="utf-8")
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
) -> Tuple[str, List[str]]:
    """
    Minimal synthesizer: builds a context block from nodes and calls the configured LLM once.
    Optionally binds a provider/model for this call.
    Uses provider-specific RAG profiles for optimal parameters.
    Returns: (response_text, list_of_reference_labels)
    """
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
        from caliper_v2.core.generation_profiles import get_rag_profile
    except Exception as exc:
        raise RuntimeError(f"Dependencies unavailable: {exc}")

    # Optionally bind provider/model for this generation
    try:
        if llm_provider or llm_model:
            _apply_llm_provider(llm_provider, llm_model)
    except Exception as exc:
        logger.warning("Could not apply LLM provider override in generate: {}", exc)

    if getattr(_Settings, "llm", None) is None:
        raise RuntimeError("LLM not configured; pass --llm-provider/--llm-model or set API keys in .env")

    # Get current provider and model to fetch optimal RAG profile
    current_provider = llm_provider or os.getenv("LLM_PROVIDER") or "openai"
    current_model = llm_model or os.getenv("LLM_MODEL") or "gpt-5"

    # Get optimized profile for this model
    profile = get_rag_profile(current_provider, current_model)

    logger.info(
        f"RAG generation with {current_provider}/{current_model}: "
        f"max_nodes={profile.max_context_nodes}, temp={profile.temperature}, "
        f"max_tokens={profile.max_tokens}, format={profile.prompt_format}"
    )

    # Build a compact context block with numbered items
    # Use profile's max_context_nodes instead of hardcoded 40
    labels: List[str] = []
    lines: List[str] = ["Context below (numbered for citation):", "---------------------"]
    max_items = max(10, min(profile.max_context_nodes, len(nodes)))
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

    # Style-specific instructions
    if style == "compare":
        extra = "Structure as: Key points (bullets), Side-by-side comparison bullets, short conclusion.\n"
    elif style == "outline":
        extra = "Return a concise outline with nested bullets, focusing on headings/sections.\n"
    elif style == "quote-heavy":
        extra = "Include short, high-signal quotes (5–25 words) with page/section labels.\n"
    else:
        extra = "Be concise and precise. Always include exact section/page labels when available.\n"

    # Format prompt based on profile's preferred format
    prompt = _format_prompt_for_profile(context_block, question_text, extra, profile, max_items)

    try:
        resp = _Settings.llm.complete(prompt)
        response_text = getattr(resp, "text", str(resp))
        return response_text, labels
    except Exception as exc:
        raise RuntimeError(f"Generation failed: {exc}")


def _format_prompt_for_profile(
    context_block: str,
    question: str,
    extra: str,
    profile,
    num_sources: int
) -> str:
    """Format prompt optimally for each provider based on their RAG profile."""

    if profile.prompt_format == "reasoning-structured":
        # Grok-4-fast-reasoning optimized format
        return f"""You are a comprehensive knowledge synthesis engine with access to extensive source material.

KNOWLEDGE BASE ({num_sources} sources, numbered for citation):
{context_block}

SYNTHESIS TASK:
Using ONLY the knowledge base above, provide thorough, well-reasoned analysis.

Requirements:
- Cite ALL sources using [n] notation
- Synthesize information across multiple sources
- Identify patterns, connections, and insights
- {extra}

QUESTION: {question}

COMPREHENSIVE ANSWER WITH REASONING:"""

    elif profile.prompt_format == "xml":
        # Claude-optimized XML format
        return f"""<context>
{context_block}
</context>

<instructions>
Using ONLY the numbered context above, answer the question with inline [n] citations.
{extra}
</instructions>

<question>{question}</question>

<answer>"""

    elif profile.prompt_format == "command-a-reasoning":
        # Command-A-Reasoning optimized format
        # Cohere models benefit from: preamble, explicit reasoning instructions, structured guidance
        return f"""You are a comprehensive technical knowledge analyst with access to {num_sources} carefully retrieved source documents.

ROLE AND CONTEXT:
Your task is to synthesize information from multiple authoritative sources to provide thorough, well-reasoned answers to complex technical and regulatory questions. You excel at identifying patterns, cross-referencing requirements, and producing detailed, citation-rich responses.

SOURCE MATERIALS ({num_sources} documents):
{context_block}

ANALYSIS TASK:
Question: {question}

INSTRUCTIONS:
1. **Comprehensive Coverage**: Address all relevant aspects of the question using information from the provided sources
2. **Thorough Citation**: Use [n] notation for EVERY factual claim (e.g., "Reports must be sealed [4,9]")
3. **Multi-Source Synthesis**: Connect information across documents to provide complete answers
4. **Structured Response**: Organize your answer with clear sections or bullet points for readability
5. **Detail Level**: Provide specific details (section numbers, requirements, procedures, exceptions) rather than high-level summaries
6. **Reasoning**: When synthesizing complex information, briefly explain your reasoning process
7. **Completeness**: {extra}

CONSTRAINTS:
- Use ONLY information from the numbered sources above
- Cite sources for every factual statement
- If sources conflict, note the discrepancy and cite both [n,m]
- If information is missing, state what's not covered in the provided sources

COMPREHENSIVE ANSWER:"""

    elif profile.prompt_format == "claude-sonnet-4-5":
        # Claude Sonnet 4.5 optimized format
        # Research shows: data first, instructions last = 30% improvement
        # Sonnet 4.5 tends toward brevity - needs explicit thoroughness guidance
        # Use nested XML tags for hierarchical structure
        return f"""<document>
<source_materials count="{num_sources}">
{context_block}
</source_materials>

<question>
{question}
</question>
</document>

<instructions>
<task_description>
You are analyzing {num_sources} source documents to provide a comprehensive, detailed answer to the question above. Your response should be thorough and well-structured, going beyond basic summaries to provide actionable insights.
</task_description>

<response_requirements>
<requirement priority="critical">Use inline [n] citations for EVERY factual statement (e.g., "Reports must include X [4,9,15]")</requirement>
<requirement priority="high">Provide comprehensive coverage - address all relevant aspects found in the sources</requirement>
<requirement priority="high">Include specific details: section numbers, procedures, requirements, exceptions, and edge cases</requirement>
<requirement priority="high">Organize with clear hierarchical structure (main sections, subsections, bullet points where appropriate)</requirement>
<requirement priority="medium">Synthesize across sources - connect related information from different documents</requirement>
<requirement priority="medium">Note any conflicts between sources, citing both [n,m]</requirement>
<requirement>Additional guidance: {extra}</requirement>
</response_requirements>

<constraints>
<constraint>Use ONLY information from the numbered sources above - do not add external knowledge</constraint>
<constraint>Every factual claim must have at least one citation</constraint>
<constraint>If information is not in sources, explicitly state what is missing</constraint>
</constraints>

<output_style>
Be thorough and detailed rather than concise. Provide the depth of analysis and specificity that would be needed for professional technical or regulatory work. Your natural efficiency is valuable, but in this case, comprehensive coverage takes priority over brevity.
</output_style>
</instructions>

<answer>"""

    elif profile.prompt_format == "claude-opus-4.1":
        # Claude Opus 4.1 optimized format
        # Opus 4.1 excels at extended reasoning and autonomous operation
        # Use <thinking> tags to encourage step-by-step analysis
        # Data first, instructions last structure
        return f"""<document>
<source_materials count="{num_sources}">
{context_block}
</source_materials>

<question>
{question}
</question>
</document>

<instructions>
<task_description>
You are conducting an in-depth analysis of {num_sources} source documents to synthesize a comprehensive answer. Leverage your extended reasoning capabilities to identify patterns, cross-reference requirements, and provide thorough coverage of the topic.
</task_description>

<analysis_approach>
<step>First, review the question and identify all aspects that need to be addressed</step>
<step>Scan through the source materials to locate relevant information for each aspect</step>
<step>Synthesize findings across sources, noting connections and patterns</step>
<step>Structure your response hierarchically with clear sections</step>
<step>Ensure every factual statement is supported by source citations</step>
</analysis_approach>

<response_requirements>
<requirement type="citation">Use inline [n] citations for ALL factual claims (e.g., "X is required [4,9,15]")</requirement>
<requirement type="coverage">Address all relevant aspects comprehensively, not just highlights</requirement>
<requirement type="detail">Include specific details: section numbers, procedures, requirements, exceptions</requirement>
<requirement type="structure">Organize with clear hierarchy: main sections → subsections → details</requirement>
<requirement type="synthesis">Connect related information across multiple sources</requirement>
<requirement type="conflicts">When sources differ, note discrepancies and cite both [n,m]</requirement>
<requirement type="guidance">{extra}</requirement>
</response_requirements>

<constraints>
<constraint>Source-only: Use exclusively information from the numbered sources above</constraint>
<constraint>Citation-required: Every statement must be citeable to at least one source</constraint>
<constraint>Completeness: State explicitly if needed information is not available in sources</constraint>
</constraints>
</instructions>

<thinking>
[Use this space to reason through your analysis step-by-step before formulating your answer. Consider: What are the key aspects? How do sources relate? What structure would best present this information?]
</thinking>

<answer>"""

    elif profile.prompt_format == "gemini-2.5-pro":
        # Gemini 2.5 Pro optimized format
        # Research shows: markdown structure, clear delimiters, role definition, step-by-step guidance
        # Gemini excels with delimiter-based structure (###, ---) and explicit process instructions
        return f"""### ROLE
You are an expert technical knowledge analyst specializing in comprehensive document synthesis and regulatory analysis. Your responses are thorough, well-structured, and citation-rich.

---

### SOURCE MATERIALS ({num_sources} documents)
{context_block}

---

### ANALYSIS TASK
**Question:** {question}

---

### INSTRUCTIONS

**Your Approach:**
1. Review the question and identify all aspects that need coverage
2. Scan source materials systematically to locate relevant information
3. Synthesize findings across multiple sources
4. Structure your response with clear hierarchical organization
5. Support every factual statement with source citations

**Response Requirements:**
- ✅ **Comprehensive Coverage**: Address all relevant aspects found in sources, not just highlights
- ✅ **Dense Citations**: Use inline [n] notation for EVERY factual claim (e.g., "X is required [4,9,15]")
- ✅ **Specific Details**: Include section numbers, procedures, requirements, exceptions, edge cases
- ✅ **Clear Structure**: Organize with markdown headings (##, ###) and bullet points
- ✅ **Multi-Source Synthesis**: Connect related information across different documents
- ✅ **Conflict Handling**: Note discrepancies between sources, citing both [n,m]
- ✅ **Completeness**: {extra}

**Constraints:**
- Use ONLY information from the numbered sources above
- Every statement must have at least one citation [n]
- If information is missing, explicitly state what's not in the sources
- Provide detailed, professional-level analysis suitable for technical/regulatory work

---

### COMPREHENSIVE ANSWER
"""

    else:
        # Standard format (GPT-5, Gemini base, Command-A base)
        return f"""{context_block}
---------------------
Using ONLY the numbered context above, answer the question with inline [n] citations.
{extra}
Question: {question}
Answer: """


@app.command()
def generate(
    context_file: str = typer.Argument(..., help="Path to a context JSON file from 'retrieve'"),
    style: str = typer.Option("strict-citation", "--style", help="strict-citation|compare|outline|quote-heavy"),
    llm_provider: Optional[str] = typer.Option(None, "--llm-provider", help="LLM provider (openai|anthropic|cohere)"),
    llm_model: Optional[str] = typer.Option(None, "--llm-model", help="LLM model name"),
    out: Optional[str] = typer.Option(None, "--out", help="Output markdown path (default: stdout)"),
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

    response, labels = _synthesize_with_style(question_text, nodes, style, llm_provider=llm_provider, llm_model=llm_model)
    
    # Append references section
    references_section = "\n\n---\n\n## References\n\n"
    for i, label in enumerate(labels, 1):
        references_section += f"[{i}] {label}\n"
    
    full_output = response + references_section
    
    if out:
        out_path = Path(out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(full_output, encoding="utf-8")
        typer.secho(f"Wrote generation to: {out_path}", fg=typer.colors.GREEN)
    else:
        typer.echo(full_output)
