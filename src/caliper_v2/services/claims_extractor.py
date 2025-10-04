from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Claim:
    id: str
    text: str
    heading: Optional[str]
    span_start: int
    span_end: int
    claim_type: Optional[str]


_sentence_re = re.compile(r"(?<=[\.!?])\s+")


def extract_claims_from_text(text: str, *, heading: Optional[str] = None, max_claims: int = 10) -> List[Claim]:
    """Heuristic claim extraction: split sentences; keep moderately long ones; split on ';' and ' and '."""
    claims: List[Claim] = []
    if not text:
        return claims
    # Normalize newlines for span tracking
    base = text
    pos = 0
    for sent in _sentence_re.split(base):
        s = sent.strip().strip("-* ")
        if len(s) < 50:
            pos += len(sent) + 1
            continue
        subs = [p.strip() for p in re.split(r";|\band\b", s) if p.strip()]
        for sub in subs:
            if len(sub) < 30:
                continue
            start = base.find(sub, pos)
            if start == -1:
                start = pos
            end = start + len(sub)
            ctype = _guess_claim_type(sub)
            claims.append(Claim(id=f"C{len(claims)+1}", text=sub, heading=heading, span_start=start, span_end=end, claim_type=ctype))
            if len(claims) >= max_claims:
                return claims
        pos += len(sent) + 1
    return claims


def _guess_claim_type(text: str) -> Optional[str]:
    t = text.lower()
    if any(k in t for k in ["shall", "must", "required", "requirement"]):
        return "requirement"
    if any(k in t for k in ["method", "approach", "procedure"]):
        return "method"
    if any(k in t for k in ["per capita", "factor", "rate", "%", "gpd", "mgd"]):
        return "numeric"
    if any(k in t for k in ["define", "definition", "means"]):
        return "definition"
    if any(k in t for k in ["caution", "risk", "uncertainty", "assumption"]):
        return "caution"
    return None


def claims_to_json(doc_path: str, claims: List[Claim]) -> Dict[str, Any]:
    return {
        "type": "claims",
        "version": 1,
        "doc_path": doc_path,
        "claims": [
            {
                "id": c.id,
                "text": c.text,
                "heading": c.heading,
                "span": {"start": c.span_start, "end": c.span_end},
                "claim_type": c.claim_type,
            }
            for c in claims
        ],
    }