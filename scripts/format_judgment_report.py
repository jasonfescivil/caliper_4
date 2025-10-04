#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format a Caliper judgment_report JSON into a readable Markdown or plain text file.
- Deterministic, mechanical: formatting only (no LLMs, no content changes).
- Supports v1/v2 schemas; tolerant of minor field differences.
- Groups claims by supported/partial/false, prints evidence + rationale.
"""

from __future__ import annotations
import argparse, json, sys, os, textwrap
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

WRAP = 100
IND = "  "

def _read_json(path: str) -> Dict[str, Any]:
    with (sys.stdin if path == "-" else open(path, "r", encoding="utf-8")) as f:
        return json.load(f)

def _basename(p: Optional[str]) -> str:
    if not p:
        return ""
    return os.path.basename(p)

def _wrap(s: Optional[str], width: int = WRAP, indent: str = "") -> str:
    if not s:
        return ""
    return textwrap.fill(s, width=width, initial_indent=indent, subsequent_indent=indent)

def _val(d: Dict[str, Any], key: str, default=None):
    v = d.get(key, default)
    return default if v in (None, "") else v

def _as_str(v: Any) -> Optional[str]:
    if v is None or v == "":
        return None
    try:
        # keep integers like "55" as strings
        return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
    except Exception:
        return str(v)

def _norm_supported(v: Any) -> str:
    """Normalize supported field to one of 'supported','partial','false',''.
    Accepts booleans, strings, or None.
    """
    if isinstance(v, bool):
        return "supported" if v else "false"
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"supported", "partial", "false"}:
            return s
        # common aliases
        if s in {"true", "yes", "y"}:
            return "supported"
        if s in {"no", "n"}:
            return "false"
    return ""

def _fmt_evidence(ev: Dict[str, Any]) -> str:
    file_   = _val(ev, "file")
    page    = _as_str(_val(ev, "page"))
    section = _val(ev, "section")
    quote   = _val(ev, "quote", _val(ev, "snippet"))
    head = []
    if file_:
        head.append(_basename(file_))
    if page:
        head.append(f"p.{page}")
    if section:
        head.append(section)
    head_str = " — ".join(head) if head else "(source unknown)"
    q = quote or "(no quote provided)"
    # Precompute multiline formatting to avoid backslashes inside f-string expression (which can trip parser)
    formatted_q = q.replace("\n", "\n" + IND + "> ")
    return f"- **{head_str}**\n{IND}> {formatted_q}"

def _status_badge(supported: str) -> str:
    s = (supported or "").lower()
    return {
        "supported": "✅ supported",
        "partial":   "⚠️ partial",
        "false":     "❌ false",
    }.get(s, s or "unknown")

def _risk_badge(risk: str) -> str:
    r = (risk or "").lower()
    return {
        "low": "🟢 low",
        "medium": "🟡 medium",
        "high": "🔴 high",
    }.get(r, r or "unknown")

def render_markdown(report: Dict[str, Any], max_evidence: int = 3) -> str:
    t = report.get("type", "")
    ver = report.get("version", "")
    created = report.get("created_at") or ""
    try:
        created_disp = datetime.fromisoformat(created.replace("Z","+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        created_disp = created

    ctx = report.get("context_path")
    doc = report.get("doc_path")
    metrics = report.get("metrics", {})
    claims: List[Dict[str, Any]] = report.get("claims", [])
    followups: List[str] = report.get("follow_up_retrieves", [])

    by_status = defaultdict(list)
    for c in claims:
        supp = _norm_supported(c.get("supported"))
        by_status[supp].append(c)

    total = metrics.get("total_claims", len(claims))
    counts = {k: len(v) for k, v in by_status.items()}
    order = ["false", "partial", "supported", ""]  # unknown last

    md = []
    md.append(f"# Judgment Report — formatted\n")
    md.append(f"**Type:** `{t}` v{ver}   |   **Created:** {created_disp}")
    md.append(f"\n**Context:** `{ctx}`\n**Draft:** `{doc}`\n")

    # Metrics section
    md.append("## Metrics\n")
    mlines = [
        f"- Total claims: **{total}**",
        f"- Support rate: **{metrics.get('support_rate', '—')}**",
        f"- Strict precision: **{metrics.get('strict_precision', '—')}**",
        f"- Citation coverage: **{metrics.get('citation_coverage', '—')}**",
        f"- Unique sources cited: **{metrics.get('unique_sources_cited', '—')}**",
        f"- Avg evidence/claim: **{metrics.get('avg_evidence_per_claim', '—')}**",
        f"- Counts: supported={counts.get('supported',0)}, partial={counts.get('partial',0)}, false={counts.get('false',0)}",
    ]
    md.extend(mlines)
    md.append("")

    # Claims grouped by status
    for status in order:
        clist = by_status.get(status, [])
        if not clist:
            continue
        status_hdr = {
            "supported": "Supported",
            "partial": "Partially Supported",
            "false": "Unsupported",
            "": "Unclassified"
        }[status]
        md.append(f"## {status_hdr} ({len(clist)})\n")
        for c in clist:
            cid   = c.get("id") or ""
            text  = c.get("text") or ""
            badge = _status_badge(_norm_supported(c.get("supported")))
            risk  = _risk_badge(c.get("risk") or "")
            evs = c.get("evidence") or []
            citok = c.get("citations_valid")
            derived_cit = citok if (citok is True or citok is False) else (True if evs else None)
            cit_s = (
                "✅ citations valid" if derived_cit is True else (
                "⚠️ no citations" if derived_cit is None else "❌ citations invalid")
            )
            md.append(f"### {cid} — {badge}  ·  risk: {risk}  ·  {cit_s}\n")
            md.append(_wrap(text, width=WRAP))
            # Evidence
            if evs:
                md.append("\n**Evidence**")
                for ev in evs[:max_evidence]:
                    md.append(_fmt_evidence(ev))
            else:
                md.append("\n**Evidence**\n- *(none provided)*")
            # Rationale
            rationale = c.get("rationale")
            if rationale:
                md.append("\n**Rationale**")
                md.append(_wrap(rationale, width=WRAP))
            md.append("")  # spacer

    # Follow-ups
    md.append("## Follow-up retrieve commands\n")
    if followups:
        for cmd in followups:
            md.append(f"- `{cmd}`")
    else:
        md.append("- *(none)*")

    return "\n".join(md).rstrip() + "\n"

def render_text(report: Dict[str, Any], max_evidence: int = 3) -> str:
    """Plain text version (no Markdown), same content."""
    md = render_markdown(report, max_evidence=max_evidence)
    # Basic conversion: strip bold/headers/inline code markers
    txt = md
    for ch in ["**", "`"]:
        txt = txt.replace(ch, "")
    # Remove markdown headers (#) but keep readable spacing
    lines = []
    for line in txt.splitlines():
        if line.startswith("#"):
            line = line.lstrip("# ").strip()
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"

def main():
    ap = argparse.ArgumentParser(description="Format a Caliper judgment_report JSON to Markdown or text.")
    ap.add_argument("--in", dest="inp", required=True, help="Path to judgment_report JSON (or '-' for STDIN).")
    ap.add_argument("--out", dest="out", default="-", help="Output path (default: '-' for STDOUT).")
    ap.add_argument("--format", dest="fmt", choices=["markdown", "md", "text", "txt"], default="markdown",
                    help="Output format (markdown|text). Default: markdown")
    ap.add_argument("--max-evidence", type=int, default=3, help="Max evidence items per claim (default: 3).")
    args = ap.parse_args()

    try:
        report = _read_json(args.inp)
        if (report.get("type") or "").startswith("judgment_report") is False:
            print("[warn] Input doesn't look like a judgment_report; formatting anyway.", file=sys.stderr)
        if args.fmt in ("markdown", "md"):
            out_str = render_markdown(report, max_evidence=args.max_evidence)
        else:
            out_str = render_text(report, max_evidence=args.max_evidence)
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(1)

    if args.out == "-":
        sys.stdout.write(out_str)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out_str)

if __name__ == "__main__":
    main()
