from __future__ import annotations

import json
from pathlib import Path

# Smoke tests for schemas and sample payloads without external dependencies.
# Goal: ensure files exist, parse as JSON, and contain required top-level keys.

ROOT = Path(__file__).resolve().parents[1]


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def test_claims_v1_sample_shape():
    sample = ROOT / "samples" / "claims_v1.sample.json"
    assert sample.exists(), f"missing sample: {sample}"
    data = _load_json(sample)
    # Top-level keys
    assert data.get("type") == "claims"
    assert int(data.get("version", 0)) == 1
    assert isinstance(data.get("claims"), list) and data["claims"], "claims list must be non-empty"
    # Minimal claim shape
    c0 = data["claims"][0]
    assert isinstance(c0.get("id"), str) and c0.get("id")
    assert isinstance(c0.get("text"), str) and c0.get("text")
    span = c0.get("span")
    assert isinstance(span, dict) and isinstance(span.get("start"), int) and isinstance(span.get("end"), int)


def test_review_report_v1_sample_shape():
    sample = ROOT / "samples" / "review_report_v1.sample.json"
    assert sample.exists(), f"missing sample: {sample}"
    data = _load_json(sample)
    # Top-level keys
    assert data.get("type") == "review_report"
    assert int(data.get("version", 0)) == 1
    for k in ("doc_path", "context_path", "summary", "issues", "claims", "metrics", "follow_up_retrieves"):
        assert k in data, f"missing key: {k}"
    # Summary minimal shape
    s = data["summary"]
    assert {"blocking", "high_risk", "inconsistencies"}.issubset(set(s.keys()))
    # Issues minimal shape
    issues = data["issues"]
    assert isinstance(issues, list)
    if issues:
        i0 = issues[0]
        for k in ("severity", "kind", "message"):
            assert k in i0
    # Claims minimal presence
    assert isinstance(data["claims"], list)
    # Follow-up list shape
    assert isinstance(data["follow_up_retrieves"], list)
