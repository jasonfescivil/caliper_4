from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import os


def resolve_llm_from_env_settings() -> Tuple[Optional[str], Optional[str], str]:
    """Lightweight provider/model resolution for UI display.

    Returns (provider, model, source) where source is one of: settings|env|none.
    This mirrors caliper_v2.cli behavior sufficiently for UI status without
    importing the CLI module (which conflicts with caliper_v2/cli/ package).
    """
    try:
        from caliper_v2.core.config import settings  # type: ignore
    except Exception:
        settings = None  # type: ignore

    # Settings first
    set_llm_provider = getattr(settings, "llm_provider", None) if settings else None
    set_llm_model = getattr(settings, "llm_model", None) if settings else None
    if set_llm_provider or set_llm_model:
        return set_llm_provider, set_llm_model, "settings"

    # Explicit env overrides
    env_override_provider = os.getenv("CALIPER_LLM_PROVIDER")
    env_override_model = os.getenv("CALIPER_LLM_MODEL")
    if env_override_provider or env_override_model:
        return env_override_provider, env_override_model, "env"

    # Auto-detect
    if os.getenv("OPENAI_API_KEY"):
        return "openai", os.getenv("CALIPER_LLM_MODEL") or None, "env"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic", os.getenv("CALIPER_LLM_MODEL") or None, "env"
    if (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    ):
        return "gemini", os.getenv("CALIPER_LLM_MODEL") or None, "env"
    if os.getenv("XAI_API_KEY"):
        return "grok", os.getenv("CALIPER_LLM_MODEL") or None, "env"
    return None, None, "none"


def synthesize_from_context(
    context_path: str,
    *,
    style: str = "strict-citation",
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> str:
    """Read a retrieval/enhanced context JSON and synthesize a response.

    Robust to small schema variants and enhanced files by:
    - Accepting multiple keys for the question (question|query|task|prompt|question_text)
    - Loading nodes from retrieval.retrieval.nodes or top-level nodes/results
    - If given an enhanced_retrieval JSON, loading its source_file for question/nodes
    """
    import json as _json

    def _read_json(p: Path) -> Dict[str, Any]:
        return _json.loads(p.read_text(encoding="utf-8"))

    def _find_question(d: Dict[str, Any]) -> str:
        for k in ["question", "query", "task", "prompt", "question_text"]:
            v = d.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""

    def _find_nodes(d: Dict[str, Any]) -> List[Dict[str, Any]]:
        cand = (d.get("retrieval") or {}).get("nodes")
        if isinstance(cand, list) and cand:
            return cand  # type: ignore[return-value]
        for k in ["nodes", "results"]:
            v = d.get(k)
            if isinstance(v, list) and v:
                return v  # type: ignore[return-value]
        return []

    p = Path(context_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Context file not found: {p}")

    data = _read_json(p)

    # If this is an enhanced file, prefer its source_file for nodes/question when missing
    data_type = str(data.get("type") or "").lower()
    question_text = _find_question(data)
    nodes = _find_nodes(data)

    if data_type == "enhanced_retrieval" and (not question_text or not nodes):
        src = data.get("source_file")
        try:
            if src and Path(src).exists():
                original = _read_json(Path(src))
                if not question_text:
                    question_text = _find_question(original)
                if not nodes:
                    nodes = _find_nodes(original)
        except Exception:
            pass

    # Final guardrails with helpful diagnostics
    if not question_text or not nodes:
        keys = ", ".join(sorted(list(data.keys())))
        raise ValueError(
            "Context file missing required fields for generation. "
            f"Found top-level keys: [{keys}]. Expected a 'question' (or synonyms) and retrieval nodes."
        )

    # Apply provider override if requested
    if llm_provider or llm_model:
        try:
            from caliper_v2.core.llm_providers import configure_llm_provider

            configure_llm_provider(llm_provider or "openai", model=llm_model)
        except Exception as exc:
            # If configuration fails but an LLM is already configured globally, continue;
            # otherwise surface a clear error to the UI.
            try:
                from llama_index.core import Settings as _Settings  # type: ignore
                if getattr(_Settings, "llm", None) is None:
                    raise RuntimeError(
                        "Could not configure LLM provider and no default LLM is set. "
                        f"Details: {exc}"
                    )
            except Exception:
                raise RuntimeError(f"Could not configure LLM provider: {exc}")

    # Use LlamaIndex Settings LLM
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"LlamaIndex Settings unavailable: {exc}")

    if getattr(_Settings, "llm", None) is None:
        raise RuntimeError("LLM not configured; set API keys or configure provider in sidebar")

    # Build compact context
    labels: List[str] = []
    lines: List[str] = ["Context below (numbered for citation):", "---------------------"]
    max_items = max(10, min(40, len(nodes)))
    for i, node in enumerate(nodes[:max_items], 1):
        md = node.get("metadata", {}) if isinstance(node, dict) else {}
        file = md.get("file_name") or md.get("file_path") or "Unknown"
        page = md.get("page") or md.get("page_label")
        section = md.get("section") or md.get("header") or md.get("heading")
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

    # Prefer chat() for providers that are chat-only or work better with chat API
    provider_lower = (llm_provider or "").lower()
    last_exc: Optional[Exception] = None
    if provider_lower in {"cohere", "xai", "grok", "gemini", "google"}:
        try:
            try:
                from llama_index.core.llms import ChatMessage, MessageRole  # type: ignore
            except Exception:
                from llama_index.core.llms.types import ChatMessage, MessageRole  # type: ignore
            msgs = [ChatMessage(role=MessageRole.USER, content=prompt)]
            resp = _Settings.llm.chat(msgs)
            # Handle different response formats from chat()
            if hasattr(resp, "message") and hasattr(resp.message, "content"):
                return resp.message.content
            elif hasattr(resp, "text"):
                return resp.text
            else:
                return str(resp)
        except Exception as exc:
            last_exc = exc
            # Log the chat() error for debugging
            print(f"DEBUG: chat() failed for {provider_lower}: {exc}")
            # Fall through to complete() as a best-effort fallback
    try:
        resp = _Settings.llm.complete(prompt)
        return getattr(resp, "text", str(resp))
    except Exception as exc:
        print(f"DEBUG: complete() failed for {provider_lower}: {exc}")
        # Final fallback: try chat() for non-cohere providers too
        try:
            try:
                from llama_index.core.llms import ChatMessage, MessageRole  # type: ignore
            except Exception:
                from llama_index.core.llms.types import ChatMessage, MessageRole  # type: ignore
            msgs = [ChatMessage(role=MessageRole.USER, content=prompt)]
            resp2 = _Settings.llm.chat(msgs)
            # Handle different response formats from chat()
            if hasattr(resp2, "message") and hasattr(resp2.message, "content"):
                return resp2.message.content
            elif hasattr(resp2, "text"):
                return resp2.text
            else:
                return str(resp2)
        except Exception:
            pass
        msg = str(exc)
        # Improve guidance for common provider issues
        if "Unknown model" in msg or "model_not_found" in msg or "does not exist" in msg:
            hint = (
                "Hint: choose a supported model (e.g., gpt-4o or gpt-4o-mini) or leave the Model field blank "
                "to use the provider default. You can also switch providers if your project lacks access."
            )
            raise RuntimeError(f"Generation failed: {msg}\n{hint}")
        # Cohere Generate-deprecation guidance
        if "Generate API is deprecated" in msg or "invalid request: generate API is not supported" in msg:
            raise RuntimeError(
                "Generation failed: Cohere Generate API is deprecated or unsupported for the selected model. "
                "Try again with Cohere using the Chat API (this UI now prefers chat automatically). If the error persists, "
                "update llama-index-llms-cohere to a recent version."
            )
        # Otherwise surface the original error with any earlier chat error for context
        extra = f"; prior chat error: {last_exc}" if last_exc else ""
        raise RuntimeError(f"Generation failed: {msg}{extra}")
