from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LintIssue:
    id: str
    severity: str  # blocking|high|medium|low
    kind: str      # missing_required|prohibited|acronym|unit_inconsistency|placeholder
    message: str
    suggestion: Optional[str]
    where: Optional[Dict[str, Any]]


def _load_profile(profile_path: Optional[Path]) -> Dict[str, Any]:
    if not profile_path or not profile_path.exists():
        # Default minimal profile
        return {
            "presence_tests": [
                {"name": "design_period", "pattern": r"design period|planning horizon|20[- ]year", "required": True},
                {"name": "flows_link", "pattern": r"Q\s*avg|ADWF|Q\s*max|peaking factor|Q\s*min", "required": True},
            ],
            "prohibited_patterns": [
                {"name": "tbd_placeholder", "pattern": r"\b(TBD|XX|YYY|FIXME)\b"},
            ],
            "expected_sections": [
                "Purpose", "Authorities", "Design Period", "Forecasting Method", "Design Flows",
            ],
        }
    import json
    return json.loads(profile_path.read_text(encoding="utf-8"))


def _compile(regex: str) -> re.Pattern:
    return re.compile(regex, flags=re.IGNORECASE | re.MULTILINE)


def run_text_lints(draft_text: str, profile_path: Optional[Path] = None) -> List[LintIssue]:
    profile = _load_profile(profile_path)
    issues: List[LintIssue] = []

    # Presence tests
    for i, test in enumerate(profile.get("presence_tests", []), 1):
        pat = _compile(test.get("pattern", "."))
        required = bool(test.get("required", False))
        if required and not pat.search(draft_text or ""):
            issues.append(
                LintIssue(
                    id=f"B{i}",
                    severity="blocking",
                    kind="missing_required",
                    message=f"Required content missing: {test.get('name')}",
                    suggestion=f"Add material satisfying: {test.get('pattern')}",
                    where=None,
                )
            )

    # Prohibited patterns
    for j, test in enumerate(profile.get("prohibited_patterns", []), 1):
        pat = _compile(test.get("pattern", ""))
        for m in pat.finditer(draft_text or ""):
            issues.append(
                LintIssue(
                    id=f"P{j}-{m.start()}",
                    severity="high",
                    kind="prohibited",
                    message=f"Prohibited pattern '{test.get('name')}' detected",
                    suggestion="Remove or rewrite to comply with guidance.",
                    where={"start": m.start(), "end": m.end()},
                )
            )

    # Acronyms: collect and check first-use definition (improved heuristic)
    # Common words that are all caps but not acronyms
    common_caps_words = {
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",  # Roman numerals
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",  # Section labels
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "INTRODUCTION", "BACKGROUND", "SUMMARY", "APPENDIX", "TABLE",  # Common headings
        "FIGURE", "SECTION", "CHAPTER", "PART", "TITLE", "EXHIBIT",
        "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY",  # Months
        "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
        "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY",  # Days
        "AM", "PM", "VS", "NA", "ID", "OK", "NO", "YES", "MAX", "MIN",  # Common abbreviations
    }
    
    # Common engineering/wastewater acronyms that don't need definition
    common_engineering_acronyms = {
        "EPA", "DOE", "NPDES", "BOD", "TSS", "MGD", "GPD", "GPM", "CFS",
        "WA", "US", "USA", "WAC", "CFR", "RCW", "SEPA", "NEPA", "EIS", "EA",
        "CWA", "WWTP", "STP", "I/I", "O&M", "UV", "MBR", "SBR", "RBC", "TF",
        "POTW", "WWTF", "TMDL", "WLA", "LA", "MOS", "WQS", "WQC", "BMP",
        "AKART", "ERU", "EDU", "PE", "SWPPP", "SPCC", "SCADA", "PLC", "HMI",
        "USGS", "FEMA", "USDA", "NRCS", "USFWS", "NMFS", "SHPO", "THPO",
    }
    
    acr_pat = re.compile(r"\b([A-Z][A-Z0-9]{1,})\b")
    seen_defs: set[str] = set()
    seen_acr: Dict[str, int] = {}
    
    # First pass: find defined acronyms
    # Look for patterns like "Biochemical Oxygen Demand (BOD)" or "BOD (Biochemical Oxygen Demand)"
    definition_patterns = [
        re.compile(r'([A-Z][a-z][\w\s]+)\s+\(([A-Z][A-Z0-9]{1,})\)'),  # Term (ACRONYM)
        re.compile(r'\(([A-Z][A-Z0-9]{1,})\)\s+([A-Z][a-z][\w\s]+)'),  # (ACRONYM) Term
    ]
    
    for pattern in definition_patterns:
        for match in pattern.finditer(draft_text):
            if len(match.groups()) >= 2:
                # One of the groups will be the acronym
                for group in match.groups():
                    if re.match(r'^[A-Z][A-Z0-9]{1,}$', group):
                        seen_defs.add(group)
    
    # Also consider defined if "(ACR)" occurs anywhere
    for m in acr_pat.finditer(draft_text or ""):
        acr = m.group(1)
        if re.search(rf"\b\({re.escape(acr)}\)\b", draft_text) or re.search(rf"\b{re.escape(acr)}\s+\(", draft_text):
            seen_defs.add(acr)
    
    # Second pass: count occurrences
    for m in acr_pat.finditer(draft_text or ""):
        acr = m.group(1)
        seen_acr[acr] = seen_acr.get(acr, 0) + 1
    
    # Third pass: report undefined acronyms
    for acr, count in seen_acr.items():
        # Skip if:
        # 1. Already defined
        # 2. Common word that's not an acronym
        # 3. Common engineering acronym
        # 4. Only appears once (might be a proper name)
        # 5. Less than 3 characters (likely not an acronym)
        if (acr in seen_defs or 
            acr in common_caps_words or 
            acr in common_engineering_acronyms or
            count < 2 or
            len(acr) < 3):
            continue
            
        issues.append(
            LintIssue(
                id=f"A-{acr}",
                severity="medium",
                kind="acronym",
                message=f"Acronym '{acr}' appears {count} times without definition.",
                suggestion=f"Define '{acr}' on first use.",
                where=None,
            )
        )

    # Units/number consistency (very conservative)
    # Warn if both mgd and gpd appear heavily; may indicate inconsistency
    mgd = len(re.findall(r"\bmgd\b", draft_text, flags=re.IGNORECASE))
    gpd = len(re.findall(r"\bgpd\b", draft_text, flags=re.IGNORECASE))
    if mgd > 0 and gpd > 0 and abs(mgd - gpd) >= 2:
        issues.append(
            LintIssue(
                id="U1",
                severity="medium",
                kind="unit_inconsistency",
                message="Both 'mgd' and 'gpd' used; ensure consistent units and conversions.",
                suggestion="Consider standardizing on one unit and providing conversions where needed.",
                where=None,
            )
        )

    # Placeholders like TBD/XX
    placeholder_hits = list(re.finditer(r"\b(TBD|XX|YYY|FIXME)\b", draft_text or "", flags=re.IGNORECASE))
    for ph in placeholder_hits:
        issues.append(
            LintIssue(
                id=f"PL-{ph.start()}",
                severity="high",
                kind="placeholder",
                message="Placeholder text found (e.g., TBD/XX).",
                suggestion="Replace placeholders with actual content and citations.",
                where={"start": ph.start(), "end": ph.end()},
            )
        )

    return issues
