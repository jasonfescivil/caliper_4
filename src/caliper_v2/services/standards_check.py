from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_checklist(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        # Minimal default checklist if none provided
        return {
            "type": "standards_checklist",
            "version": 1,
            "presence_tests": [
                {"name": "design_period", "pattern": r"design period|planning horizon|20[- ]year", "required": True, "scope": "doc"},
                {"name": "flows_link", "pattern": r"Q\s*avg|ADWF|Q\s*max|peaking factor", "required": True, "scope": "section"},
            ],
        }
    return json.loads(p.read_text(encoding="utf-8"))


def evaluate_standards(doc_text: str, outline: Dict[str, Any], checklist: Dict[str, Any]) -> Dict[str, Any]:
    tests = checklist.get("presence_tests", [])
    sections = outline.get("sections", [])
    results: List[Dict[str, Any]] = []
    required_total = 0
    required_pass = 0

    for t in tests:
        name = t.get("name") or "unknown"
        pat = t.get("pattern") or "."
        required = bool(t.get("required", False))
        scope = (t.get("scope") or "doc").lower()
        try:
            rgx = re.compile(pat, flags=re.IGNORECASE | re.MULTILINE)
        except re.error:
            rgx = re.compile(re.escape(pat), flags=re.IGNORECASE)

        if scope == "doc":
            passed = bool(rgx.search(doc_text or ""))
            results.append({"name": name, "scope": scope, "required": required, "passed": passed})
            if required:
                required_total += 1
                required_pass += int(passed)
        else:
            any_section = False
            per_section: List[Dict[str, Any]] = []
            for s in sections:
                txt = s.get("text") or ""
                hit = bool(rgx.search(txt))
                any_section = any_section or hit
                per_section.append({"section_id": s.get("id"), "heading": s.get("heading"), "passed": hit})
            results.append({"name": name, "scope": scope, "required": required, "passed": any_section, "per_section": per_section})
            if required:
                required_total += 1
                required_pass += int(any_section)

    coverage = (required_pass / required_total) if required_total else 1.0
    return {
        "type": "standards_matrix",
        "version": 1,
        "coverage": round(coverage, 3),
        "required": required_total,
        "required_pass": required_pass,
        "tests": results,
    }


def run_standards(md_path: str | Path, outline: Dict[str, Any], checklist_path: Optional[str | Path], out_path: str | Path) -> Path:
    mdp = Path(md_path)
    doc_text = mdp.read_text(encoding="utf-8", errors="ignore")
    checklist = load_checklist(checklist_path) if checklist_path else load_checklist("__missing__")
    report = evaluate_standards(doc_text, outline, checklist)
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return outp