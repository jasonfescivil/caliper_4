from __future__ import annotations

import json
from pathlib import Path

from caliper_v2.commands.judge import main as judge_main


def write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def make_context(tmp: Path) -> Path:
    # Minimal context unlikely to fully support all claims -> triggers follow-ups
    ctx = {
        "type": "retrieval_session",
        "version": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "question": "Test Q",
        "indexes": ["state", "design"],
        "retrieval": {
            "nodes": [
                {"text": "Guidance mentions planning horizon.", "metadata": {"file_name": "g1.pdf", "page_label": "1", "section": "Intro"}},
            ]
        },
    }
    p = tmp / "ctx.json"
    write_json(p, ctx)
    return p


def make_draft(tmp: Path) -> Path:
    # Several claims; at least one should be partial/false -> follow-up commands
    txt = (
        "# Draft\n"
        "The planning horizon shall be 20 years.\n"
        "Per capita flow values for schools are 12 gpcd (example).\n"
        "A claim about an unrelated policy that is not in context.\n"
    )
    p = tmp / "draft.md"
    p.write_text(txt, encoding="utf-8")
    return p


def test_recommendations_present_and_windows_safe(tmp_path: Path):
    ctx = make_context(tmp_path)
    draft = make_draft(tmp_path)
    out = tmp_path / "judgment_recs.json"

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
    cmds = data.get("follow_up_retrieves", [])
    assert cmds, "Expected at least one follow-up retrieve command"
    # Windows-safe quoting: use double quotes around query, indexes and out path should appear quoted
    sample = cmds[0]
    assert sample.startswith("poetry run caliper_v2 retrieve \"")
    assert " --indexes " in sample
    assert " --out \"" in sample and sample.endswith("\"")
