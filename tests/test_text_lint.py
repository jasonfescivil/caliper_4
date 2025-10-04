from __future__ import annotations

from pathlib import Path

from caliper_v2.services.text_lint import run_text_lints


def test_text_lints_detect_issues(tmp_path: Path):
    # Text intentionally missing planning horizon and flows link; includes TBD and acronyms
    text = (
        "# Draft Section\n"
        "This section discusses wastewater planning. TBD placeholder remains.\n"
        "I/I should be addressed. I/I occurs multiple times without definition.\n"
        "Flow units appear as mgd in one place and gpd repeatedly gpd gpd.\n"
    )
    p = tmp_path / "draft.md"
    p.write_text(text, encoding="utf-8")

    issues = run_text_lints(p.read_text(encoding="utf-8"))
    # Expect at least one blocking (missing required presence), one prohibited (TBD), one acronym or unit issue
    kinds = {i.kind for i in issues}
    severities = {i.severity for i in issues}
    assert "missing_required" in kinds
    assert "prohibited" in kinds
    assert ("acronym" in kinds) or ("unit_inconsistency" in kinds)
    assert "blocking" in severities
