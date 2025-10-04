from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from caliper_v2.services.review_render import render_markdown


def aggregate_review(
    *,
    doc_path: str,
    outline: Dict[str, Any],
    claims_json: Dict[str, Any],
    standards_json: Dict[str, Any],
    coherence_json: Dict[str, Any],
    partial_review_json: Dict[str, Any],
) -> Dict[str, Any]:
    total_claims = int(partial_review_json.get("metrics", {}).get("total_claims", 0))
    support_rate = float(partial_review_json.get("metrics", {}).get("support_rate", 0.0))

    # Simple summary mapping
    missing_required = max(0, int(standards_json.get("required", 0)) - int(standards_json.get("required_pass", 0)))
    drifts = coherence_json.get("drifts", [])

    summary = {
        "blocking": missing_required,  # treat missing required as blocking
        "high_risk": len(drifts),
        "inconsistencies": 0,
        "coverage_score": float(standards_json.get("coverage", 0.0)),
    }

    # Build issues list from standards + coherence drifts
    issues: List[Dict[str, Any]] = []
    for t in standards_json.get("tests", []):
        if t.get("required") and not t.get("passed"):
            issues.append({
                "severity": "blocking",
                "kind": "missing_required",
                "message": f"Required content missing: {t.get('name')}",
                "suggestion": "Add the required material and citations.",
                "where": None,
            })
    for d in drifts:
        issues.append({
            "severity": "high",
            "kind": "coherence_drift",
            "message": f"Section '{d.get('heading')}' is off-topic (sim {d.get('sim_to_purpose')}).",
            "suggestion": "Rewrite to align with purpose/scope.",
            "where": {"section_id": d.get("section_id")},
        })

    metrics = {
        "total_claims": total_claims,
        "support_rate": support_rate,
        "strict_precision": support_rate,  # heuristic placeholder
        "citation_coverage": 0.0,
        "unique_sources_cited": 0,
        "avg_evidence_per_claim": 0.0,
    }

    report = {
        "type": "review_report",
        "version": 1,
        "doc_path": doc_path,
        "context_path": "",
        "summary": summary,
        "issues": issues,
        "claims": claims_json.get("claims", []),
        "metrics": metrics,
        "follow_up_retrieves": partial_review_json.get("follow_up_retrieves", []),
    }
    return report


def write_review_pack(report: Dict[str, Any], out_json: str | Path, out_md: str | Path) -> None:
    outj = Path(out_json); outm = Path(out_md)
    outj.parent.mkdir(parents=True, exist_ok=True)
    outm.parent.mkdir(parents=True, exist_ok=True)
    outj.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    outm.write_text(render_markdown(report), encoding="utf-8")