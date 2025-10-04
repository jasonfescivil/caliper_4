from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


def _overlap_score(a: str, b: str) -> float:
    a_tokens = set(re.findall(r"[A-Za-z0-9]{3,}", (a or "").lower()))
    b_tokens = set(re.findall(r"[A-Za-z0-9]{3,}", (b or "").lower()))
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def judge_per_section(outline: Dict[str, Any], claims_json: Dict[str, Any], threshold: float = 0.15) -> Dict[str, Any]:
    sections = {s.get("id"): s for s in (outline.get("sections") or [])}
    claims = claims_json.get("claims") or []
    if not claims:
        return {"type": "partial_review", "version": 1, "sections": [], "metrics": {"support_rate": 0.0, "total_claims": 0}}

    per_section: Dict[str, Dict[str, Any]] = {}
    supported_cnt = 0
    for c in claims:
        # find best matching section by heading if present else first
        heading = (c.get("heading") or "").lower()
        target_id = None
        if heading:
            for sid, s in sections.items():
                h = (s.get("heading") or "").lower()
                if heading == h:
                    target_id = sid; break
        if target_id is None:
            # fallback to first section
            target_id = next(iter(sections.keys()), None)
        sec = sections.get(target_id) or {}
        txt = sec.get("text") or ""
        score = _overlap_score(c.get("text") or "", txt)
        supported = score >= threshold
        if supported:
            supported_cnt += 1
        info = per_section.setdefault(target_id or "unknown", {"claims": 0, "supported": 0, "heading": sec.get("heading")})
        info["claims"] += 1
        info["supported"] += int(supported)

    # Build list
    per_list = []
    for sid, agg in per_section.items():
        rate = (agg["supported"] / agg["claims"]) if agg["claims"] else 0.0
        per_list.append({"section_id": sid, "heading": agg.get("heading"), "claims": agg["claims"], "support_rate": round(rate, 3)})

    support_rate = supported_cnt / len(claims) if claims else 0.0
    return {
        "type": "partial_review",
        "version": 1,
        "sections": per_list,
        "metrics": {"support_rate": round(support_rate, 3), "total_claims": len(claims)},
        "follow_up_retrieves": [],
    }


def run_per_section_judge(outline: Dict[str, Any], claims_json: Dict[str, Any], out_path: str | Path) -> Path:
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    data = judge_per_section(outline, claims_json)
    outp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return outp