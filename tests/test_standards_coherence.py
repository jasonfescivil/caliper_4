from __future__ import annotations

from pathlib import Path
import sys

# Ensure src on path for imports
ROOT = Path(__file__).resolve().parents[1]
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from caliper_v2.services.standards_check import evaluate_standards
from caliper_v2.services.coherence import compute_coherence


def test_standards_and_coherence_minimal(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text(
        """# Purpose
This report provides the planning horizon of 20-year for design.

## Methods
We document the procedure and peaking factor.

## Results
Numbers appear here.
""",
        encoding="utf-8",
    )
    # Minimal outline
    lines = md.read_text(encoding="utf-8").splitlines()
    outline = {
        "type": "outline",
        "version": 1,
        "doc_path": str(md),
        "sections": [
            {"id": "S1", "heading": "Purpose", "text": "\n".join(lines[1:3])},
            {"id": "S2", "heading": "Methods", "text": "\n".join(lines[4:6])},
            {"id": "S3", "heading": "Results", "text": "\n".join(lines[7:])},
        ],
    }
    checklist = {
        "type": "standards_checklist",
        "version": 1,
        "presence_tests": [
            {"name": "design_period", "pattern": r"design|planning horizon", "required": True, "scope": "doc"},
            {"name": "peaking", "pattern": r"peaking factor", "required": True, "scope": "section"},
        ],
    }

    # Standards
    report = evaluate_standards(md.read_text(encoding="utf-8"), outline, checklist)
    assert 0.0 <= float(report.get("coverage", 0.0)) <= 1.0
    assert report.get("required") >= report.get("required_pass")

    # Coherence
    coh = compute_coherence(outline)
    assert "coherence_score" in coh and 0.0 <= float(coh["coherence_score"]) <= 1.0
    assert isinstance(coh.get("sections"), list)
