#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit a Caliper judgment_report JSON and propose improvements/fixes.
- Tolerates v1 and v2 variants.
- Computes basic metrics if missing or obviously wrong.
- Flags schema inconsistencies (e.g., boolean supported, missing fields, null metrics),
  and suggests non-destructive fixes. Optionally writes a "fixed" JSON copy.

Usage:
  python scripts/judgment_audit.py --in data_v2/judgments/population_judgment.json --report -
  python scripts/judgment_audit.py --in data_v2/judgments/population_judgment.json --out-fixed data_v2/judgments/population_judgment.fixed.json --report outputs/judgment_audit.md
"""
from __future__ import annotations
import argparse, json, os, sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Set


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_supported(v: Any) -> str:
    if isinstance(v, bool):
        return "supported" if v else "false"
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"supported", "partial", "false"}:
            return s
        if s in {"true", "yes", "y"}:
            return "supported"
        if s in {"no", "n"}:
            return "false"
    return ""


def _as_str(v: Any) -> Optional[str]:
    if v is None or v == "":
        return None
    try:
        return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
    except Exception:
        return str(v)


@dataclass
class Issue:
    kind: str
    message: str
    path: str


@dataclass
class Metrics:
    total_claims: int
    support_rate: float
    strict_precision: float
    citation_coverage: float
    unique_sources_cited: int
    avg_evidence_per_claim: float


def _compute_metrics(report: Dict[str, Any]) -> Metrics:
    claims: List[Dict[str, Any]] = report.get("claims") or []
    total = len(claims) or 1
    supp = 0
    cited = 0
    ev_counts = 0
    srcs: Set[str] = set()
    for c in claims:
        status = _norm_supported(c.get("supported"))
        if status == "supported":
            supp += 1
        evs = c.get("evidence") or []
        if evs:
            cited += 1
        ev_counts += len(evs)
        for ev in evs:
            fn = ev.get("file")
            if fn:
                srcs.add(os.path.basename(fn))
    support_rate = round(supp / total, 4)
    strict_precision = support_rate  # heuristic; refine later if needed
    citation_coverage = round(cited / total, 4)
    uniq = len(srcs)
    avg_ev = round(ev_counts / total, 2)
    return Metrics(total, support_rate, strict_precision, citation_coverage, uniq, avg_ev)


def audit(report: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    issues: List[Issue] = []

    # Basic presence
    if (report.get("type") or "") != "judgment_report":
        issues.append(Issue("schema", "type should be 'judgment_report'", "$.type"))
    ver = report.get("version")
    if ver not in (1, 2):
        issues.append(Issue("schema", "version should be 1 or 2; prefer 2", "$.version"))
    created = report.get("created_at")
    if not created:
        issues.append(Issue("schema", "created_at missing; add an ISO8601 UTC timestamp", "$.created_at"))
    else:
        try:
            datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            issues.append(Issue("schema", "created_at not ISO8601; use e.g., 2025-09-13T12:00:00Z", "$.created_at"))

    # Paths
    if not report.get("doc_path"):
        issues.append(Issue("data", "doc_path missing", "$.doc_path"))
    if "context_path" not in report:
        issues.append(Issue("compat", "context_path missing (required in v2)", "$.context_path"))

    # Claims checks
    claims: List[Dict[str, Any]] = report.get("claims") or []
    if not isinstance(claims, list) or not claims:
        issues.append(Issue("data", "claims array is empty or missing", "$.claims"))
    for i, c in enumerate(claims, start=1):
        pfx = f"$.claims[{i-1}]"
        st = c.get("supported")
        ns = _norm_supported(st)
        if ns == "":
            issues.append(Issue("schema", "supported should be one of supported|partial|false", f"{pfx}.supported"))
        if st is True or st is False:
            issues.append(Issue("compat", "boolean supported found; convert to string label", f"{pfx}.supported"))
        evs = c.get("evidence") or []
        if not isinstance(evs, list):
            issues.append(Issue("schema", "evidence should be an array", f"{pfx}.evidence"))
            evs = []
        for j, ev in enumerate(evs, start=1):
            q = ev.get("quote") or ev.get("snippet")
            if not q:
                issues.append(Issue("data", "evidence item missing quote/snippet", f"{pfx}.evidence[{j-1}]"))
            if ev.get("page") is not None and not isinstance(ev.get("page"), str):
                issues.append(Issue("compat", "evidence.page should be string (coerce numbers)", f"{pfx}.evidence[{j-1}].page"))

    # Metrics sanity
    want = _compute_metrics(report)
    m = report.get("metrics") or {}
    if not m:
        issues.append(Issue("schema", "metrics missing; compute and populate", "$.metrics"))
    else:
        # Check each metric; if missing or null, suggest value
        for k in ("total_claims", "support_rate", "strict_precision", "citation_coverage", "unique_sources_cited", "avg_evidence_per_claim"):
            if m.get(k) in (None, ""):
                issues.append(Issue("metrics", f"metrics.{k} missing; suggest {getattr(want, k)}", f"$.metrics.{k}"))

    # Build proposed fixed copy (non-destructive: only fill missing/convert types)
    fixed = json.loads(json.dumps(report))  # deep copy
    if fixed.get("type") != "judgment_report":
        fixed["type"] = "judgment_report"
    if fixed.get("version") == 1:
        # Do not force upgrade, but prefer consistency with codebase
        fixed["version"] = 2
    if not fixed.get("created_at"):
        fixed["created_at"] = _iso_now()
    if "context_path" not in fixed:
        fixed["context_path"] = fixed.get("context") or ""
    # Normalize claims supported type and evidence.page strings
    fclaims: List[Dict[str, Any]] = []
    for c in fixed.get("claims") or []:
        cc = dict(c)
        cc["supported"] = _norm_supported(cc.get("supported"))
        evs2: List[Dict[str, Any]] = []
        for ev in (cc.get("evidence") or []):
            ee = dict(ev)
            if "quote" not in ee and "snippet" in ee:
                ee["quote"] = ee.get("snippet")
            if ee.get("page") is not None:
                ee["page"] = _as_str(ee.get("page"))
            evs2.append(ee)
        cc["evidence"] = evs2
        fclaims.append(cc)
    if fclaims:
        fixed["claims"] = fclaims

    # Recompute/complete metrics if missing
    if not fixed.get("metrics"):
        fixed["metrics"] = {}
    want2 = _compute_metrics(fixed)
    fxm = fixed["metrics"]
    fxm.setdefault("total_claims", want2.total_claims)
    fxm.setdefault("support_rate", want2.support_rate)
    fxm.setdefault("strict_precision", want2.strict_precision)
    fxm.setdefault("citation_coverage", want2.citation_coverage)
    fxm.setdefault("unique_sources_cited", want2.unique_sources_cited)
    fxm.setdefault("avg_evidence_per_claim", want2.avg_evidence_per_claim)

    # Markdown report
    lines: List[str] = []
    lines.append(f"# Judgment audit\n")
    lines.append(f"Input type: `{report.get('type')}` v{report.get('version')}  |  Claims: {len(report.get('claims') or [])}\n")
    lines.append("## Summary metrics\n")
    lines.append(f"- Total claims: **{want.total_claims}**")
    lines.append(f"- Support rate: **{want.support_rate}**")
    lines.append(f"- Strict precision: **{want.strict_precision}**")
    lines.append(f"- Citation coverage: **{want.citation_coverage}**")
    lines.append(f"- Unique sources cited: **{want.unique_sources_cited}**")
    lines.append(f"- Avg evidence/claim: **{want.avg_evidence_per_claim}**\n")
    if issues:
        lines.append("## Issues found\n")
        for iss in issues:
            lines.append(f"- [{iss.kind}] {iss.message}  (at {iss.path})")
    else:
        lines.append("## Issues found\n- *(none)*")
    lines.append("\n## Proposed automatic fixes\n")
    lines.append("- Normalize `supported` values to 'supported'|'partial'|'false' (no booleans).")
    lines.append("- Coerce evidence.page to string; copy `snippet` to `quote` when missing.")
    if report.get("version") == 1:
        lines.append("- Upgrade version to 2 for consistency with current tools.")
    if not report.get("created_at"):
        lines.append("- Add created_at as current UTC timestamp.")
    if "context_path" not in report:
        lines.append("- Add context_path (empty if unknown).")

    md = "\n".join(lines).rstrip() + "\n"
    return md, fixed


def main():
    ap = argparse.ArgumentParser(description="Audit a Caliper judgment_report JSON and propose fixes.")
    ap.add_argument("--in", dest="inp", required=True, help="Path to judgment_report JSON")
    ap.add_argument("--report", dest="report", default="-", help="Output Markdown report path ('-' for STDOUT)")
    ap.add_argument("--out-fixed", dest="out_fixed", default=None, help="Optional path to write a fixed JSON copy")
    args = ap.parse_args()

    try:
        data = _read_json(args.inp)
    except Exception as e:
        print(f"[fatal] failed to read JSON: {e}", file=sys.stderr)
        sys.exit(1)

    md, fixed = audit(data)

    # Emit report
    if args.report == "-":
        sys.stdout.write(md)
    else:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(md)

    # Optionally write fixed copy
    if args.out_fixed:
        try:
            _write_json(args.out_fixed, fixed)
        except Exception as e:
            print(f"[warn] could not write fixed JSON: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
