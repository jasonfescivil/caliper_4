from __future__ import annotations

import json
from pathlib import Path

from caliper_v2.commands.review import main as review_main


def write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


essential_ctx = {
    "type": "retrieval_session",
    "version": 1,
    "created_at": "2025-01-01T00:00:00Z",
    "question": "Test Q",
    "indexes": ["state"],
    "retrieval": {
        "nodes": [
            {
                "text": "Planning horizon of 20 years and peaking factor guidance mentioned.",
                "metadata": {"file_name": "guide.pdf", "page_label": "12", "section": "3.1"},
            }
        ]
    },
}


def make_context(tmp: Path) -> Path:
    p = tmp / "ctx.json"
    write_json(p, essential_ctx)
    return p


def make_draft(tmp: Path) -> Path:
    txt = (
        "# Section\n"
        "The planning horizon is 20-year and we must consider peaking factor.\n"
        "However, ensure no TBD placeholders remain.\n"
    )
    p = tmp / "draft.md"
    p.write_text(txt, encoding="utf-8")
    return p


def test_review_end_to_end(tmp_path: Path):
    ctx = make_context(tmp_path)
    draft = make_draft(tmp_path)
    out_json = tmp_path / "review.json"
    out_md = tmp_path / "review.md"

    res = review_main(
        context_path=str(ctx),
        draft_path=str(draft),
        out_json=str(out_json),
        out_md=str(out_md),
        profile=None,
        strict=True,
        max_evidence_per_claim=3,
    )

    assert out_json.exists() and out_md.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))

    assert data["type"] == "review_report"
    assert data["version"] == 1
    # Must include summary, issues, claims, metrics and follow-ups
    for key in ["summary", "issues", "claims", "metrics", "follow_up_retrieves"]:
        assert key in data

    md_text = out_md.read_text(encoding="utf-8")
    assert "# Review Report" in md_text
    assert "## Summary" in md_text
