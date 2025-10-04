from __future__ import annotations

import json
from pathlib import Path

from caliper_v2.commands.judge import main as judge_main


def write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def make_context(tmp: Path) -> Path:
    ctx = {
        "type": "retrieval_session",
        "version": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "question": "Test Q",
        "indexes": ["state", "design"],
        "retrieval": {
            "nodes": [
                {
                    "text": "Per capita flow and peaking factors shall be documented. Planning horizon typically 20 years.",
                    "metadata": {"file_name": "guide.pdf", "page_label": "10", "section": "2.1"},
                },
                {
                    "text": "Definitions and scope. Unrelated content about biosolids.",
                    "metadata": {"file_name": "other.pdf", "page_label": "5", "section": "1.0"},
                },
            ]
        },
    }
    p = tmp / "ctx.json"
    write_json(p, ctx)
    return p


def make_draft(tmp: Path) -> Path:
    txt = (
        "# Plan\n"
        "The planning horizon should be 20 years for wastewater facility sizing.\n"
        "Per capita flow and peaking factors must be clearly stated.\n"
        "This claim is unrelated to the provided context completely.\n"
    )
    p = tmp / "draft.md"
    p.write_text(txt, encoding="utf-8")
    return p


def test_metrics_present_and_reasonable(tmp_path: Path):
    ctx = make_context(tmp_path)
    draft = make_draft(tmp_path)
    out = tmp_path / "judgment_metrics.json"

    judge_main(
        context_path=str(ctx),
        generation_path=str(draft),
        out_path=str(out),
        strict=True,
        max_evidence_per_claim=2,
        claims_json=None,
        bm25_k=100,
        embed_strategy="none",
        per_source_cap=2,
    )

    data = json.loads(out.read_text(encoding="utf-8"))
    m = data["metrics"]
    assert isinstance(m["total_claims"], int) and m["total_claims"] > 0
    for key in ["support_rate", "strict_precision", "citation_coverage", "avg_evidence_per_claim"]:
        assert 0.0 <= float(m[key]) <= 1.0
    assert isinstance(m["unique_sources_cited"], int) and m["unique_sources_cited"] >= 0
