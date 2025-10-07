from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

from loguru import logger

from caliper_v2.services.standards_check import load_checklist


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    # Only create parent directory if it's not the current directory
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _safe_get_metadata(node_obj: Dict[str, Any]) -> Dict[str, Any]:
    md = node_obj.get("metadata") or {}
    # Normalize common keys
    if "section" not in md:
        for k in ("header", "heading"):
            if k in md and md[k]:
                md["section"] = md[k]
                break
    return md


def _diagnostics(nodes: List[Dict[str, Any]]) -> Tuple[Dict[str, int], Dict[str, int], float]:
    per_source: Dict[str, int] = {}
    per_index: Dict[str, int] = {}
    for n in nodes:
        md = _safe_get_metadata(n)
        src = md.get("file_name") or md.get("file_path") or "Unknown"
        idx = (n.get("index") or n.get("index_name") or (n.get("metadata") or {}).get("_caliper_index_name") or "unknown").lower()
        per_source[src] = per_source.get(src, 0) + 1
        per_index[idx] = per_index.get(idx, 0) + 1
    total = max(1, len(nodes))
    dominance = 0.0
    if per_source:
        max_count = max(per_source.values())
        dominance = round(max_count / total, 3)
    return per_index, per_source, dominance


def _collect_citations(nodes: List[Dict[str, Any]], max_items: int = 30) -> List[Dict[str, Any]]:
    """Collect unique citations (file, page, section) up to max_items."""
    cites: List[Dict[str, Any]] = []
    seen: set[tuple] = set()
    for nd in nodes:
        md = _safe_get_metadata(nd)
        file = md.get("file_name") or md.get("file_path")
        page = md.get("page_label", md.get("page"))
        section = md.get("section")
        key = (file, str(page) if page is not None else None, section)
        if key in seen:
            continue
        seen.add(key)
        cites.append({"file": file, "page": page, "section": section})
        if len(cites) >= max_items:
            break
    return cites


def _default_outline(question: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Heuristic outline with top-level sections relevant to engineering guidance
    titles = [
        "Purpose and Scope",
        "Regulatory Framework and Citations",
        "Methodologies for Population Projection",
        "Design Years and Planning Horizon",
        "Per Capita Flow and Peaking Factors",
        "Special Considerations (Seasonal, Institutions, Inflow)",
        "Sensitivity and Uncertainty",
        "Documentation, Assumptions, and Citations",
    ]
    cites = _collect_citations(nodes, max_items=15)
    sections = []
    for i, t in enumerate(titles, 1):
        sections.append(
            {
                "id": f"S{i}",
                "title": t,
                "description": f"Section on {t.lower()} tailored to: {question[:120]}",
                "expected_content": "Summarize retrieved guidance; include numbered citations.",
                "citations": cites[max(0, (i - 1) * 2): i * 2] if cites else [],
                "priority": 0.5 if i > 2 else 0.9,
            }
        )
    return {"sections": sections}


def _rewrite_spore(original_spore: Dict[str, Any], outline: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(original_spore, dict):
        original_spore = {}
    summary = original_spore.get("summary") or "Context prepared for grounded generation using hybrid retrieval."
    bullets = original_spore.get("rationale_bullets") or []
    # Include outline section titles into bullets to align generation focus
    titles = [s.get("title") for s in outline.get("sections", [])][:5]
    merged_bullets = bullets[:3] + [f"Covers: {', '.join([t for t in titles if t])}"]
    conf = original_spore.get("confidence", 0.7)
    try:
        conf = float(conf)
        if not (0.0 <= conf <= 1.0):
            conf = 0.7
    except Exception:
        conf = 0.7
    return {
        "summary": summary,
        "rationale_bullets": merged_bullets,
        "confidence": conf,
    }


def _suggest_followup_commands(question: str, indexes: List[str], base_out: Path) -> List[str]:
    """Build targeted follow-up retrieve commands using the natural-language question only."""
    idx_primary = indexes[0] if indexes else "design"
    base_dir = base_out.parent

    def _escape_quotes(s: str) -> str:
        return (s or "").replace('"', "'").strip()

    qbase = _escape_quotes(question)
    topics = [
        "planning horizon and design year definitions",
        "per capita flows and peaking factors guidance",
        "methodology: cohort vs trend vs land-use comparison",
    ]
    suggestions: List[str] = []
    for j, topic in enumerate(topics, 1):
        query = f"{qbase} — {topic}" if qbase else topic
        outf = base_dir / f"followup_{j}.json"
        top_k = 50 if "methodology" in topic else 40
        cmd = (
            f"poetry run caliper_v2 retrieve \"{query}\" --indexes {idx_primary} --cloud "
            f"--search-mode hybrid --dense-k 12 --sparse-k 12 --alpha 0.5 "
            f"--top-k {top_k} --rerank-top-n 24 --out {outf}"
        )
        suggestions.append(cmd)
    return suggestions


def _check_for_missing_sections(outline: Dict[str, Any], checklist_path: str | Path) -> List[str]:
    """
    Checks the generated outline against a checklist for missing mandatory sections.
    Returns a list of warnings for any missing sections.
    """
    checklist = load_checklist(checklist_path)
    presence_tests = checklist.get("presence_tests", [])

    outline_titles = [s.get("title", "").lower() for s in outline.get("sections", [])]

    missing_warnings = []

    for test in presence_tests:
        if test.get("required"):
            name = test.get("name", "Unnamed Test")
            pattern = test.get("pattern", "")

            found = any(re.search(pattern, title, re.IGNORECASE) for title in outline_titles)

            if not found:
                missing_warnings.append(f"Gap Alert: Missing mandatory section '{name}'. Expected content matching pattern: '{pattern}'")

    return missing_warnings


def main(
    in_path: str,
    out_path: str,
    write_outline: bool = True,
    rewrite_spore: bool = True,
    suggest_retrieve: bool = True,
    topic_profile: Optional[str] = None,
    max_per_source: Optional[int] = None,
    include_terms: Optional[str] = None,
    filters: Optional[str] = None,
    review_spores: bool = True,
    dry_run: bool = False,
    checklist_path: Optional[str | Path] = None,
) -> Path:
    in_file = Path(in_path)
    out_file = Path(out_path)
    if not in_file.exists():
        raise FileNotFoundError(f"enhance: input not found: {in_file}")

    session = _read_json(in_file)
    if session.get("type") != "retrieval_session":
        logger.warning("enhance: input JSON type is %s (expected retrieval_session)", session.get("type"))

    q_norm = _normalize_question(session.get("question", ""))
    nodes: List[Dict[str, Any]] = (session.get("retrieval") or {}).get("nodes", [])
    per_index, per_source, dominance = _diagnostics(nodes)

    # Simple diversity normalization hint (no mutation of nodes in this minimal version)
    diversity = {"unique_files": len(per_source), "dominance_ratio": dominance}

    outline: Dict[str, Any] = {"sections": []}
    if write_outline:
        outline = _default_outline(q_norm, nodes)

    # Check for missing sections and print warnings
    if checklist_path:
        missing_warnings = _check_for_missing_sections(outline, checklist_path)
        if missing_warnings:
            logger.warning("--- Gap Alerts: Missing Mandatory Sections ---")
            for warning in missing_warnings:
                logger.warning(warning)
            logger.warning("--------------------------------------------")

    followups: List[str] = []
    if suggest_retrieve:
        followups = _suggest_followup_commands(q_norm, session.get("indexes", []), out_file)

    original_spore = (session.get("retrieval") or {}).get("spore") or {}
    new_spore = _rewrite_spore(original_spore, outline) if rewrite_spore else original_spore

    # Review and rewrite per-node spores (does not mutate source file)
    spores_review: Dict[str, Any] = {"total": len(nodes), "changed": 0, "rewritten": []}
    if review_spores and nodes:
        generic = {"relevant to the query", "relevant to the question", "relevant to the query scope", "related to the query"}
        limit = min(60, len(nodes))  # safety cap
        q = q_norm
        for nd in nodes[:limit]:
            md = _safe_get_metadata(nd)
            old = (nd.get("spore") or {}) if isinstance(nd.get("spore"), dict) else {}
            new = _rewrite_node_spore(q, nd)
            old_reason = (old.get("reason") or "").strip()
            is_generic = old_reason.lower().strip(".") in generic or not old_reason
            if is_generic or new.get("reason") != old_reason:
                spores_review["rewritten"].append({
                    "node_id": nd.get("node_id") or nd.get("id"),
                    "file": md.get("file_name") or md.get("file_path"),
                    "old": old,
                    "new": new,
                })
        spores_review["changed"] = len(spores_review["rewritten"]) 

    # Build a simple before/after comparison block
    def _extract_session_citations(sess: Dict[str, Any]) -> List[Dict[str, Any]]:
        cites = []
        try:
            raw = (sess.get("retrieval") or {}).get("citations") or []
            for c in raw:
                if not isinstance(c, dict):
                    continue
                cites.append({
                    "file": c.get("file"),
                    "page": c.get("page"),
                    "section": c.get("section"),
                })
        except Exception:
            pass
        return cites

    def _unique_citation_keys(cites: List[Dict[str, Any]]) -> List[tuple]:
        seen = []
        seen_set = set()
        for c in cites:
            key = (c.get("file"), str(c.get("page")) if c.get("page") is not None else None, c.get("section"))
            if key not in seen_set:
                seen_set.add(key)
                seen.append(key)
        return seen

    def _suggestions_ok(cmds: List[str]) -> bool:
        import re as _re
        for s in cmds:
            # Ensure we have exactly one retrieve command and the quoted query has no nested CLI
            if s.count("retrieve") < 1:
                return False
            m = _re.search(r'"([^"]+)"', s)
            if not m:
                return False
            qstr = m.group(1)
            if " caliper_v2 " in qstr or qstr.lower().startswith("poetry run"):
                return False
        return True

    before_cites = _extract_session_citations(session)
    after_cites = _collect_citations(nodes, max_items=30)
    before_keys = _unique_citation_keys(before_cites)
    after_keys = _unique_citation_keys(after_cites)

    comparison: Dict[str, Any] = {
        "question": {
            "before": session.get("question", ""),
            "after": q_norm,
            "changed": (session.get("question", "") or "").strip() != q_norm.strip(),
        },
        "citations": {
            "before_total": len(before_cites),
            "before_unique": len(before_keys),
            "after_total": len(after_cites),
            "after_unique": len(after_keys),
            "before_examples": before_cites[:3],
            "after_examples": after_cites[:3],
        },
        "suggestions": {
            "count": len(followups),
            "ok": _suggestions_ok(followups),
            "examples": followups[:2],
        },
        "spore": {
            "original_has_bullets": bool((original_spore or {}).get("rationale_bullets")),
            "rewritten_has_outline_alignment": any(isinstance(b, str) and b.startswith("Covers:") for b in (new_spore or {}).get("rationale_bullets", [])),
        },
        "notes": [
            "Index names missing in nodes; per_index_counts may show 'unknown' if upstream data lacks index metadata." if per_index.keys() == {"unknown"} else None
        ],
    }
    # Remove None notes
    comparison["notes"] = [n for n in comparison["notes"] if n]

    enhanced: Dict[str, Any] = {
        "type": "enhanced_retrieval",
        "version": 1,
        "created_at": session.get("created_at"),
        "source_file": str(in_file),
        "question": q_norm,
        "indexes": session.get("indexes", []),
        "search_mode": session.get("search_mode"),
        "requested_top_k": session.get("requested_top_k", session.get("top_k")),
        "final_kept": session.get("final_kept", len(nodes)),
        "diagnostics": {
            "per_index_counts": per_index,
            "per_source_counts": per_source,
            "diversity": diversity,
        },
        "retrieval": session.get("retrieval", {}),
        "outline": outline,
        "gap_analysis": {
            "topics_missing": [],
            "coverage_score": 1.0 - diversity.get("dominance_ratio", 0.0),
        },
        "suggestions": {"follow_up_retrieves": followups},
        "spore": {"original": original_spore, "rewritten": new_spore},
        "spores_review": spores_review,
        "comparison": comparison,
    }

    if dry_run:
        logger.info("enhance: dry-run complete (not writing file): %s", out_file)
        return out_file

    _write_json(out_file, enhanced)
    logger.info("Enhanced retrieval written to: %s", out_file)
    return out_file


# --- Spores rewrite helpers ---

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


from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception),
)
def _rewrite_node_spore(question: str, nd: Dict[str, Any]) -> Dict[str, Any]:
    """Use configured LLM to rewrite node spore; fallback to heuristics."""
    md = (nd.get("metadata") or {})
    text = (nd.get("text") or "")[:1000]
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
        llm = getattr(_Settings, "llm", None)
    except Exception:
        llm = None
    if llm is None:
        return _heuristic_node_spore(md, text, question)
    label = md.get("file_name") or md.get("file_path") or "Unknown"
    prompt = (
        "Return ONLY JSON with keys reason (1-2 sentences) and confidence (0.0-1.0).\n"
        "Explain specifically how this snippet helps answer the question; reference section/page when present.\n"
        f"Question: {question}\nSource: {label}\nText: {text}\n"
        'JSON: {"reason": "...", "confidence": 0.0}'
    )
    import json as _json
    try:
        resp = llm.complete(prompt)
        raw = getattr(resp, "text", str(resp))
        try:
            start = raw.index("{"); end = raw.rfind("}") + 1; raw = raw[start:end]
        except Exception:
            pass
        jd = _json.loads(raw) if raw else {}
    except Exception:
        jd = {}
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
    generic_phrases = {"relevant to the query", "relevant to the question", "relevant to the query scope", "related to the query"}
    if not reason or reason.strip().lower().strip(".") in generic_phrases:
        reason = heur["reason"]
    confidence = conf_val if isinstance(conf_val, (int, float)) and 0.0 <= conf_val <= 1.0 else heur["confidence"]
    return {"reason": reason, "confidence": float(confidence)}



def _normalize_question(q: str) -> str:
    """Normalize question text.
    - If q looks like a CLI command (contains 'caliper_v2 retrieve' or leading 'poetry run'),
      attempt to extract the content inside the first quoted string.
    - Collapse whitespace and trim to a reasonable length.
    """
    if not isinstance(q, str):
        return ""
    s = q.strip()
    import re as _re
    # Heuristic: extract quoted segment after retrieve command
    if "caliper_v2 retrieve" in s or s.lower().startswith("poetry run"):
        m = _re.search(r"retrieve\s+\"([^\"]+)\"", s)
        if m:
            s = m.group(1).strip()
        else:
            # fallback: take first non-flag line that doesn't start with '--'
            lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
            for ln in lines:
                if not ln.startswith("--") and " caliper_v2 " not in ln:
                    s = ln
                    break
    # Normalize whitespace and clamp
    s = _re.sub(r"\s+", " ", s).strip()
    return s[:500]
