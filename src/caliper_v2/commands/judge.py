from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from caliper_v2.services.judge_components import (
    BM25Index,
    JudgmentMetrics,
    JudgmentReportV2,
    EvidenceItem,
    ClaimItem,
    ClaimSpan,
    ClaimsInput,
    build_bm25,
    compute_embeddings,
    embed_query,
    cosine,
    llm_adjudicate,
    windows_retrieve_command,
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    # Only create parent directory if it's not the current directory
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_nodes_from_context(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = []
    if isinstance(ctx.get("retrieval"), dict):
        nodes = (ctx["retrieval"].get("nodes") or [])
    if not nodes and ctx.get("type") == "enhanced_retrieval":
        src = ctx.get("source_file")
        try:
            if src:
                base = _read_json(Path(src))
                nodes = (base.get("retrieval") or {}).get("nodes", [])
        except Exception:
            pass
    return nodes


def _node_text(nd: Dict[str, Any]) -> str:
    return (nd.get("text") or "")


def _node_label(nd: Dict[str, Any]) -> Dict[str, Any]:
    md = (nd.get("metadata") or {})
    return {
        "file": md.get("file_name") or md.get("file_path"),
        "page": md.get("page_label", md.get("page")),
        "section": md.get("section") or md.get("header") or md.get("heading"),
    }


def _extract_claims_with_spans(draft: str, max_claims: int = 100) -> List[ClaimItem]:
    import re

    claims: List[ClaimItem] = []
    # Split paragraphs and track headings
    heading = None
    pos = 0
    for line in draft.splitlines(keepends=True):
        line_text = line.rstrip("\n")
        line_len = len(line)
        # Heading heuristic: starts with digits/letters and a dot or all-caps short line
        if re.match(r"^\s*\d+\.|^#[#\s]*[A-Za-z]", line_text) or (line_text.isupper() and 3 < len(line_text) < 80):
            heading = line_text.strip().strip("# ")
            pos += line_len
            continue
        # Skip empty or very short lines
        if len(line_text.strip()) < 2:
            pos += line_len
            continue
        # Split into sentences
        parts = re.split(r"(?<=[\.!?])\s+", line_text)
        offset = 0
        for sent in parts:
            st = sent.strip().strip("-* ")
            if len(st) < 20:
                offset += len(sent) + 1
                continue
            # Split compound sentences on ';' or ' and '
            subparts = [p.strip() for p in re.split(r";|\band\b", st) if p.strip()]
            for sub in subparts:
                if len(sub) < 15:
                    continue
                start = pos + (line_text.find(sub, offset))
                end = start + len(sub)
                ctype = _guess_claim_type(sub)
                claims.append(ClaimItem(id=f"C{len(claims)+1}", text=sub, heading=heading, span=ClaimSpan(start=start, end=end), claim_type=ctype))
                if len(claims) >= max_claims:
                    return claims
            offset += len(sent) + 1
        pos += line_len
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
    if any(k in t for k in ["parameter", "input", "variable"]):
        return "parameter"
    return None


def _normalize_citations_from_context(nodes: List[Dict[str, Any]]) -> List[Tuple[str, Optional[str], Optional[str]]]:
    seen = set()
    cites: List[Tuple[str, Optional[str], Optional[str]]] = []
    for n in nodes:
        lbl = _node_label(n)
        key = (str(lbl.get("file")), str(lbl.get("page")), str(lbl.get("section")))
        if key in seen:
            continue
        seen.add(key)
        cites.append((lbl.get("file"), lbl.get("page"), lbl.get("section")))
    return cites


def _parse_citations_in_draft(draft: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
    # Very simple heuristic: look for patterns like [file: XYZ], p.12, section 3.1
    import re
    results: List[Tuple[str, Optional[str], Optional[str]]] = []
    # Extract quoted filenames or .pdf mentions
    for m in re.finditer(r"\[([^\]]+?)\]|([A-Za-z0-9_\-]+\.pdf)", draft):
        token = (m.group(1) or m.group(2) or "").strip()
        if not token:
            continue
        results.append((token, None, None))
    # Pages like p.12
    for m in re.finditer(r"p\.?\s*(\d{1,4})", draft, flags=re.IGNORECASE):
        results.append(("", m.group(1), None))
    # Sections like 3.1 or Section 3.1
    for m in re.finditer(r"section\s+([0-9]+(?:\.[0-9]+)*)", draft, flags=re.IGNORECASE):
        results.append(("", None, m.group(1)))
    return results


def _blend_scores(bm25_scores: Dict[int, float], emb_scores: Dict[int, float]) -> Dict[int, float]:
    # Normalize each, then average
    def _norm(d: Dict[int, float]) -> Dict[int, float]:
        if not d:
            return {}
        vals = list(d.values())
        lo, hi = min(vals), max(vals)
        if abs(hi - lo) < 1e-9:
            return {k: 0.5 for k in d}
        return {k: (v - lo) / (hi - lo) for k, v in d.items()}

    nb = _norm(bm25_scores)
    ne = _norm(emb_scores)
    keys = set(nb) | set(ne)
    out: Dict[int, float] = {}
    for k in keys:
        out[k] = (nb.get(k, 0.0) + ne.get(k, 0.0)) / (2.0 if k in nb and k in ne else 1.0)
    return out


def main(
    context_path: str,
    generation_path: str,
    out_path: str,
    strict: bool = True,
    max_evidence_per_claim: int = 3,
    claims_json: Optional[str] = None,
    bm25_k: int = 200,
    embed_strategy: str = "auto",
    per_source_cap: int = 3,
) -> Path:
    ctx_file = Path(context_path)
    gen_file = Path(generation_path)
    out_file = Path(out_path)

    if not ctx_file.exists():
        raise FileNotFoundError(f"judge: context not found: {ctx_file}")
    if not gen_file.exists():
        raise FileNotFoundError(f"judge: generation not found: {gen_file}")

    context = _read_json(ctx_file)
    nodes = _load_nodes_from_context(context)
    draft = _read_text(gen_file)

    # Claims input
    claims_items: List[ClaimItem]
    if claims_json:
        try:
            parsed = ClaimsInput(**_read_json(Path(claims_json)))
            claims_items = parsed.claims
        except Exception:
            claims_items = _extract_claims_with_spans(draft)
    else:
        claims_items = _extract_claims_with_spans(draft)

    # Build retrieval matrices
    node_texts = [_node_text(n) for n in nodes]
    labels = [_node_label(n) for n in nodes]

    bm25: Optional[BM25Index] = None
    if node_texts:
        bm25 = build_bm25(node_texts)

    doc_embs: Optional[List[List[float]]] = None
    if embed_strategy != "none":
        doc_embs = compute_embeddings(node_texts) or None

    context_citations = _normalize_citations_from_context(nodes)

    verdicts = []
    supported_cnt = 0
    precision_num = 0  # supported + false with evidence
    precision_den = 0

    followup_cmds: List[str] = []
    followup_seen: set[str] = set()

    for claim in claims_items:
        # Prefilter
        bm_scores: Dict[int, float] = {}
        if bm25:
            # Using tokenizer from bm25 builder
            from caliper_v2.services.judge_components import tokenize as _tok
            q = _tok(claim.text)
            for i in range(len(node_texts)):
                bm_scores[i] = bm25.score(q, i)
        # Top-K BM25
        bm_top = sorted(bm_scores.items(), key=lambda t: t[1], reverse=True)[: max(1, bm25_k)]
        bm_set = {i for i, _ in bm_top}

        emb_scores: Dict[int, float] = {}
        if doc_embs is not None:
            qv = embed_query(claim.text) or []
            for i, dv in enumerate(doc_embs):
                emb_scores[i] = cosine(qv, dv)
        # Top-K embeddings (50 default via spec)
        emb_top = sorted(emb_scores.items(), key=lambda t: t[1], reverse=True)[:50]
        emb_set = {i for i, _ in emb_top}

        blend = _blend_scores({i: bm_scores.get(i, 0.0) for i in bm_set}, {i: emb_scores.get(i, 0.0) for i in emb_set})
        # Ensure some candidates even if embeddings missing
        if not blend:
            blend = {i: s for i, s in bm_top}

        # Per-source cap and keep top 20
        # Map index -> source counts
        scored = sorted(blend.items(), key=lambda t: t[1], reverse=True)
        per_source_count: Dict[str, int] = {}
        chosen_idx: List[int] = []
        for idx_i, _sc in scored:
            src = (labels[idx_i].get("file") or "Unknown") if idx_i < len(labels) else "Unknown"
            if per_source_count.get(src, 0) >= max(1, per_source_cap):
                continue
            per_source_count[src] = per_source_count.get(src, 0) + 1
            chosen_idx.append(idx_i)
            if len(chosen_idx) >= 20:
                break
        # Build candidate evidence items
        candidates: List[EvidenceItem] = []
        for idx_i in chosen_idx:
            txt = node_texts[idx_i]
            lbl = labels[idx_i]
            quote = txt[:500]
            candidates.append(EvidenceItem(file=lbl.get("file"), page=str(lbl.get("page")) if lbl.get("page") is not None else None, section=str(lbl.get("section")) if lbl.get("section") else None, quote=quote))

        # LLM adjudication
        adjudicated = llm_adjudicate(claim.text, candidates, max_evidence=max_evidence_per_claim)
        evidence_final: List[EvidenceItem] = []
        supported_str = "partial"
        rationale = None
        risk = None
        if adjudicated:
            # Normalize supported value
            raw_supported = str(adjudicated.get("supported", "partial")).lower()
            if raw_supported not in {"supported", "partial", "false"}:
                supported_str = "partial"
            else:
                supported_str = raw_supported

            # Normalize evidence list to tolerate strings
            raw_evidence = adjudicated.get("evidence", []) or []
            norm_evidence: List[Dict[str, Any]] = []
            for ev in raw_evidence:
                if isinstance(ev, str):
                    ev = {"quote": ev}
                if isinstance(ev, dict):
                    norm_evidence.append(ev)
                # silently skip other types

            for ev in norm_evidence[: max_evidence_per_claim]:
                evidence_final.append(
                    EvidenceItem(
                        file=ev.get("file"),
                        page=ev.get("page"),
                        section=ev.get("section"),
                        quote=ev.get("quote"),
                    )
                )
            rationale = adjudicated.get("rationale")
            risk = adjudicated.get("risk")
        else:
            # Fallback: heuristic keyword overlap
            evidence_final = candidates[: max(1, max_evidence_per_claim)]
            supported_str = "partial"
            rationale = "Heuristic fallback due to LLM adjudication unavailability."
            risk = "medium"

        # Metrics counters for strict precision (on claims with any evidence)
        if evidence_final:
            precision_den += 1
            if supported_str == "supported":
                precision_num += 1

        if supported_str == "supported":
            supported_cnt += 1

        # Citation validation per claim: if draft contains any recognizable context citation tokens, mark true; if it contains citation-like tokens but none match context, false; else null
        draft_cites = _parse_citations_in_draft(draft)
        has_any_citation_token = bool(draft_cites)
        valid = None
        if has_any_citation_token:
            # if any token matches a context file token, consider valid
            context_files = {str(f or "") for (f, p, s) in context_citations}
            valid = any((fc and fc in context_files) for (fc, p, s) in draft_cites)
        # Assemble verdict
        verdicts.append({
            "id": claim.id,
            "heading": claim.heading,
            "text": claim.text,
            "span": claim.span.model_dump(),
            "supported": supported_str,
            "citations_valid": valid,
            "evidence": [e.model_dump() for e in evidence_final],
            "rationale": rationale,
            "risk": risk,
        })

        # Follow-up suggestions for partial/false
        if supported_str in {"partial", "false"}:
            # Craft short query from claim text
            short_q = (claim.text[:120] + ("…" if len(claim.text) > 120 else ""))
            indexes = context.get("indexes", []) or ["design"]
            # Output path near context path
            outp = str(ctx_file.parent / f"retry_{claim.id}.json")
            cmd = windows_retrieve_command(short_q, indexes, outp, top_k=40, rerank_top_n=20)
            if cmd not in followup_seen:
                followup_seen.add(cmd)
                followup_cmds.append(cmd)
                if len(followup_cmds) >= 10:
                    # global cap
                    pass

    total_claims = len(claims_items)
    support_rate = round((supported_cnt / total_claims) if total_claims else 0.0, 3)
    strict_precision = round((precision_num / precision_den) if precision_den else 0.0, 3)
    unique_sources = set()
    ev_count = 0
    for v in verdicts:
        for ev in v.get("evidence", []):
            if ev.get("file"):
                unique_sources.add(ev.get("file"))
            ev_count += 1
    avg_ev = round((ev_count / total_claims) if total_claims else 0.0, 3)
    # Normalize to 0..1 by max_evidence_per_claim for reporting consistency
    avg_ev_norm = round(min(1.0, (avg_ev / max(1, max_evidence_per_claim))), 3)

    # citation coverage: count claims with >=1 valid citation OR any evidence
    cited_or_evid = 0
    for v in verdicts:
        if v.get("citations_valid") is True or (v.get("evidence") and len(v.get("evidence")) > 0):
            cited_or_evid += 1
    citation_coverage = round((cited_or_evid / total_claims) if total_claims else 0.0, 3)

    metrics = JudgmentMetrics(
        total_claims=total_claims,
        support_rate=support_rate,
        strict_precision=strict_precision,
        citation_coverage=citation_coverage,
        unique_sources_cited=len(unique_sources),
        avg_evidence_per_claim=avg_ev_norm,
    )

    report = JudgmentReportV2(
        created_at=context.get("created_at") or "",
        context_path=str(ctx_file),
        doc_path=str(gen_file),
        metrics=metrics,
        claims=[],
        follow_up_retrieves=followup_cmds[:10],
    ).model_dump()
    # Replace claims with prepared dicts (already model_dumped spans/evidence)
    report["claims"] = verdicts

    _write_json(out_file, report)
    logger.info("Judgment report written to: %s", out_file)
    return out_file
