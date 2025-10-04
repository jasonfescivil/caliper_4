from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9]{2,}", (text or "").lower())


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    num = 0.0
    da = 0.0
    db = 0.0
    for x, y in zip(a, b):
        num += x * y
        da += x * x
        db += y * y
    if da <= 0 or db <= 0:
        return 0.0
    return max(-1.0, min(1.0, num / math.sqrt(da * db)))


def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _embed_batch(texts: List[str]) -> Optional[List[List[float]]]:
    try:
        from llama_index.core import Settings  # type: ignore
    except Exception:
        return None
    em = getattr(Settings, "embed_model", None)
    if em is None:
        return None
    # Prefer batch, else per-item
    try:
        if hasattr(em, "get_text_embedding_batch"):
            return em.get_text_embedding_batch(texts)
    except Exception:
        pass
    try:
        if hasattr(em, "get_text_embedding"):
            return [em.get_text_embedding(t) for t in texts]
    except Exception:
        return None
    return None


def compute_coherence(outline: Dict[str, Any], drift_threshold: float = 0.2) -> Dict[str, Any]:
    sections = outline.get("sections", [])
    if not sections:
        return {"type": "coherence", "version": 1, "coherence_score": 1.0, "sections": [], "drifts": []}
    # Pick a purpose/scope section if present, else the first
    purpose_idx = 0
    for i, s in enumerate(sections):
        h = (s.get("heading") or "").lower()
        if any(k in h for k in ("purpose", "scope")):
            purpose_idx = i
            break
    purpose_txt = sections[purpose_idx].get("text") or ""

    # Try embeddings
    texts = [purpose_txt] + [s.get("text") or "" for s in sections]
    embeddings = None
    try:
        embeddings = _embed_batch(texts)
    except Exception:
        embeddings = None

    scores: List[Dict[str, Any]] = []
    sims: List[float] = []
    for i, s in enumerate(sections):
        if embeddings:
            sim = _cosine(embeddings[0], embeddings[i + 1])
        else:
            sim = _jaccard(_tokenize(purpose_txt), _tokenize(s.get("text") or ""))
        sims.append(sim)
        scores.append({
            "section_id": s.get("id"),
            "heading": s.get("heading"),
            "sim_to_purpose": round(float(sim), 3),
        })

    avg = sum(sims) / len(sims) if sims else 1.0
    drifts = [s for s in scores if (s.get("sim_to_purpose") or 0.0) < drift_threshold]
    return {
        "type": "coherence",
        "version": 1,
        "purpose_section_id": sections[purpose_idx].get("id"),
        "coherence_score": round(float(avg), 3),
        "sections": scores,
        "drifts": drifts,
    }


def run_coherence(outline: Dict[str, Any], out_path: str | Path) -> Path:
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    report = compute_coherence(outline)
    outp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return outp