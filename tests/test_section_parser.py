from __future__ import annotations

from pathlib import Path

from pathlib import Path as _P
import sys as _sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
src_path = ROOT / "src"
if str(src_path) not in _sys.path:
    _sys.path.insert(0, str(src_path))

from caliper_v2.services.section_parser import parse_markdown_sections
from caliper_v2.services.claims_extractor import extract_claims_from_text


def test_section_parser_splits_headings(tmp_path: Path):
    md = tmp_path / "sample.md"
    md.write_text(
        """# Title\n\nIntro text.\n\n## Methods\nWe must document the procedure and factors.\nThis sentence adds more context.\n\n## Results\nPer capita flow factor may be 100 gpd.\n""",
        encoding="utf-8",
    )
    outline = parse_markdown_sections(md)
    secs = outline["sections"]
    assert len(secs) == 3  # Title content + Methods + Results
    # Ensure section metadata exists
    assert secs[1]["heading"].lower() == "methods"
    assert isinstance(secs[1]["start_char"], int)


def test_claims_extractor_basic():
    text = (
        "We must document the procedure and factors. Another short. "
        "The facility shall be sized for a 20-year horizon; and provide references."
    )
    claims = extract_claims_from_text(text, heading="Methods", max_claims=5)
    assert claims, "should extract at least one claim"
    # Ensure spans and headings populated
    c = claims[0]
    assert c.heading == "Methods"
    assert isinstance(c.span_start, int) and isinstance(c.span_end, int)