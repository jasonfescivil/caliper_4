from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Section:
    id: str
    level: int
    heading: Optional[str]
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    text: str


_heading_re = re.compile(r"^(#{1,6})\s+(.+)$")


def parse_markdown_sections(md_path: Path) -> Dict[str, Any]:
    """Parse a Markdown file into sections using ATX headings (#..######).

    Returns a dict with:
      - type: outline
      - version: 1
      - doc_path: string
      - sections: List[Section as dict]
    """
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # Identify headings with their line numbers
    headings: List[tuple[int, int, str]] = []  # (line_idx, level, title)
    for i, line in enumerate(lines):
        m = _heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((i, level, title))

    sections: List[Section] = []
    # If no headings, treat whole document as one section level 1
    if not headings:
        sec_text = text
        sections.append(Section(
            id="S1",
            level=1,
            heading=None,
            start_line=0,
            end_line=len(lines) - 1,
            start_char=0,
            end_char=len(text),
            text=sec_text,
        ))
    else:
        # Define section spans between headings
        for idx, (line_no, level, title) in enumerate(headings):
            start_line = line_no + 1  # content starts after the heading line
            end_line = (headings[idx + 1][0] - 1) if idx + 1 < len(headings) else len(lines) - 1
            # Compute char spans
            # char index at start of start_line
            start_char = sum(len(l) + 1 for l in lines[:start_line])  # +1 for newline
            end_char = sum(len(l) + 1 for l in lines[: end_line + 1])
            sec_text = "\n".join(lines[start_line : end_line + 1])
            sections.append(Section(
                id=f"S{idx+1}",
                level=level,
                heading=title,
                start_line=start_line,
                end_line=end_line,
                start_char=start_char,
                end_char=end_char,
                text=sec_text,
            ))

    return {
        "type": "outline",
        "version": 1,
        "doc_path": str(md_path),
        "sections": [s.__dict__ for s in sections],
    }


def write_outline(md_path: str | Path, out_path: str | Path) -> Path:
    mdp = Path(md_path)
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    data = parse_markdown_sections(mdp)
    outp.write_text(__import__("json").dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return outp