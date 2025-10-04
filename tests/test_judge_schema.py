from __future__ import annotations

import json
from pathlib import Path

from caliper_v2.commands.judge import main as judge_main


def _write(p: Path, data: dict) -> None:
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
                {
                    "text": "Planning horizon of 20 years is commonly used per guidance.",
                    "metadata": {"file_name": "guide.pdf", "page_label": "12", "section": "3.1"},
                }
            ]
        },
    }
    p = tmp / "ctx.json"
    _write(p, ctx)
    return p


def make_draft(tmp: Path) -> Path:
    txt = "# 1. Scope\nPopulation projections should consider a 20-year planning horizon. See [guide.pdf] p.12.\n"
    p = tmp / "draft.md"
    p.write_text(txt, encoding="utf-8")
    return p


def test_schema_and_determinism(tmp_path: Path):
    ctx = make_context(tmp_path)
    draft = make_draft(tmp_path)
    out1 = tmp_path / "judgment1.json"
    out2 = tmp_path / "judgment2.json"

    judge_main(
        context_path=str(ctx),
        generation_path=str(draft),
        out_path=str(out1),
        strict=True,
        max_evidence_per_claim=2,
        claims_json=None,
        bm25_k=50,
        embed_strategy="none",
        per_source_cap=2,
    )
    judge_main(
        context_path=str(ctx),
        generation_path=str(draft),
        out_path=str(out2),
        strict=True,
        max_evidence_per_claim=2,
        claims_json=None,
        bm25_k=50,
        embed_strategy="none",
        per_source_cap=2,
    )

    d1 = json.loads(out1.read_text(encoding="utf-8"))
    d2 = json.loads(out2.read_text(encoding="utf-8"))

    assert d1["type"] == "judgment_report"
    assert d1["version"] == 2
    assert "metrics" in d1 and isinstance(d1["metrics"], dict)
    # determinism ignoring created_at; compare core fields
    for k in ["type", "version", "context_path", "doc_path", "claims", "follow_up_retrieves"]:
        assert d1.get(k) == d2.get(k)

    # claims structure
    assert d1["claims"]
    c = d1["claims"][0]
    assert set(["id", "text", "span", "supported", "evidence"]).issubset(c.keys())
