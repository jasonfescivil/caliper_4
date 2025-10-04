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
        "indexes": ["state"],
        "retrieval": {
            "nodes": [
                {"text": "Section 3.1 defines planning horizon of 20 years.", "metadata": {"file_name": "guide.pdf", "page_label": "12", "section": "3.1"}}
            ]
        },
    }
    p = tmp / "ctx.json"
    write_json(p, ctx)
    return p


def make_draft(tmp: Path) -> Path:
    # Include one valid and one invalid citation token
    txt = (
        "Outline\n"
        "The planning horizon is typically 20 years [guide.pdf], p.12.\n"
        "Another statement cites [missing.pdf] which is not in context.\n"
    )
    p = tmp / "draft.md"
    p.write_text(txt, encoding="utf-8")
    return p


def test_citation_metrics(tmp_path: Path):
    ctx = make_context(tmp_path)
    draft = make_draft(tmp_path)
    out = tmp_path / "judgment_citations.json"

    judge_main(
        context_path=str(ctx),
        generation_path=str(draft),
        out_path=str(out),
        strict=True,
        max_evidence_per_claim=2,
        claims_json=None,
        bm25_k=50,
        embed_strategy="none",
        per_source_cap=2,
    )

    data = json.loads(out.read_text(encoding="utf-8"))
    # Ensure metrics are present and citation_coverage computed
    m = data["metrics"]
    assert "citation_coverage" in m
    assert 0.0 <= float(m["citation_coverage"]) <= 1.0
    # At least one claim should have citations_valid not null since draft had tokens
    assert any(c.get("citations_valid") is not None for c in data["claims"]) 
