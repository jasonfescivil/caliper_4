from __future__ import annotations

from typing import Any, Dict, List


def _h(title: str, level: int = 2) -> str:
    return f"{'#' * level} {title}\n\n"


def _group_issues_by_kind(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group issues by their kind for better organization in the report."""
    grouped = {}
    for issue in issues:
        kind = issue.get("kind", "other")
        if kind not in grouped:
            grouped[kind] = []
        grouped[kind].append(issue)
    return grouped


def _format_issue_group(kind: str, issues: List[Dict[str, Any]]) -> List[str]:
    """Format a group of issues of the same kind."""
    lines = []
    lines.append(f"### {kind.replace('_', ' ').title()}\n")
    
    # Sort issues by severity (blocking > high > medium > low)
    severity_order = {"blocking": 0, "high": 1, "medium": 2, "low": 3}
    sorted_issues = sorted(
        issues, 
        key=lambda x: severity_order.get(x.get("severity", "low"), 4)
    )
    
    for it in sorted_issues:
        lines.append(f"- [{it.get('severity','low')}] {it.get('message')}")
        if it.get("suggestion"):
            lines.append(f"  - Suggestion: {it.get('suggestion')}")
    
    lines.append("")
    return lines


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Review Report\n\n")
    doc = report.get("doc_path") or "(unknown)"
    ctx = report.get("context_path") or "(unknown)"
    criteria = report.get("criteria_path")

    lines.append(f"Document: `{doc}`  \nContext: `{ctx}`")
    if criteria:
        lines.append(f"Criteria: `{criteria}`")
    lines.append("\n")

    # --- Evidence Gap Analysis ---
    all_evidence_files = []
    claims = report.get("claims") or []
    for claim in claims:
        for evidence in claim.get("evidence", []):
            if evidence.get("file"):
                all_evidence_files.append(evidence.get("file").lower())

    required_categories = {
        "Ecology Design Manual": ["ecology design manual", "orange book"],
        "WAC/DOE Regulations": ["wac", "rcw", "washington administrative code"],
        "DOE Permit Manuals": ["doe permit manual", "ecology permit writer's manual"],
        "I/I Monitoring Attachments": ["i-i analysis", "i/i monitoring", "inflow and infiltration"],
    }

    missing_references = []
    for category, keywords in required_categories.items():
        found = False
        for f_path in all_evidence_files:
            if any(keyword in f_path for keyword in keywords):
                found = True
                break
        if not found:
            missing_references.append(category)

    # Summary
    summary = report.get("summary") or {}
    lines.append(_h("Executive Summary"))

    # Add LLM assessment first if available for immediate visibility
    if "llm_assessment" in summary:
        lines.append(f"**Overall Assessment**: {summary.get('llm_assessment')}\n")

    # Add compliance status if available
    llm_review = report.get("llm_review", {})
    if isinstance(llm_review, dict) and "summary" in llm_review:
        llm_summary = llm_review.get("summary", {})
        if isinstance(llm_summary, dict) and "compliance_status" in llm_summary:
            lines.append(f"**Regulatory Compliance**: {llm_summary.get('compliance_status')}\n")

    # Add strengths and weaknesses if available from LLM review
    if isinstance(llm_review, dict) and "summary" in llm_review:
        llm_summary = llm_review.get("summary", {})
        if isinstance(llm_summary, dict):
            if "strengths" in llm_summary and isinstance(llm_summary["strengths"], list) and llm_summary["strengths"]:
                lines.append("**Strengths**:")
                for strength in llm_summary["strengths"]:
                    lines.append(f"- {strength}")
                lines.append("")

            if "key_weaknesses" in llm_summary and isinstance(llm_summary["key_weaknesses"], list) and llm_summary["key_weaknesses"]:
                lines.append("**Key Weaknesses**:")
                for weakness in llm_summary["key_weaknesses"]:
                    lines.append(f"- {weakness}")
                lines.append("")

    # Issue counts with more descriptive labels
    lines.append("**Issue Summary**:")

    # Prioritize regulatory and structural issues in the summary
    if "missing_sections" in summary and summary.get("missing_sections", 0) > 0:
        lines.append(f"- **Missing Required Sections**: {summary.get('missing_sections', 0)} (High Priority)")

    if "missing_topics" in summary and summary.get("missing_topics", 0) > 0:
        lines.append(f"- **Missing Required Topics**: {summary.get('missing_topics', 0)} (High Priority)")

    if missing_references:
        lines.append(f"- **Evidence Gaps Detected**: {len(missing_references)}")

    # Add severity counts
    if summary.get("blocking", 0) > 0:
        lines.append(f"- **Critical Issues**: {summary.get('blocking', 0)}")

    if summary.get("high_risk", 0) > 0:
        lines.append(f"- **High Risk Issues**: {summary.get('high_risk', 0)}")

    if summary.get("medium_risk", 0) > 0:
        lines.append(f"- **Medium Risk Issues**: {summary.get('medium_risk', 0)}")

    # Add other metrics
    if "inconsistencies" in summary and summary.get("inconsistencies", 0) > 0:
        lines.append(f"- **Terminology/Unit Inconsistencies**: {summary.get('inconsistencies', 0)}")

    if "coverage_score" in summary:
        score = float(summary.get("coverage_score", 0))
        quality = "Excellent" if score > 0.9 else "Good" if score > 0.7 else "Fair" if score > 0.5 else "Poor"
        lines.append(f"- **Citation Coverage Score**: {score:.2f} ({quality})")

    lines.append("")

    # Evidence Gaps Section
    if missing_references:
        lines.append(_h("Evidence Coverage Gaps", 2))
        lines.append("The review identified potential gaps in evidence coverage. The draft may be missing citations from these key sources, which are often required for regulatory submissions:")
        for ref in missing_references:
            lines.append(f"- **Missing**: Citations from **{ref}**")
        lines.append("\n*Suggestion: Consider running a targeted retrieval (`poetry run caliper_v2 retrieve`) with queries focused on these topics to strengthen the evidence base.*")
        lines.append("")

    # Critical Issues Section - Show high priority issues first
    issues = report.get("issues") or []
    critical_issues = [i for i in issues if i.get("severity") in ["blocking", "high"]]
    if critical_issues:
        lines.append(_h("Critical Issues", 2))
        # Group critical issues by kind
        grouped_critical = _group_issues_by_kind(critical_issues)
        for kind, kind_issues in grouped_critical.items():
            lines.extend(_format_issue_group(kind, kind_issues))

    # LLM Review (if available)
    if "llm_review" in report and report["llm_review"]:
        if isinstance(report["llm_review"], str):
            lines.append(_h("Detailed Review Analysis", 2))
            lines.append(report["llm_review"])
            lines.append("")
        elif isinstance(report["llm_review"], dict) and "review" in report["llm_review"]:
            lines.append(_h("Detailed Review Analysis", 2))
            lines.append(report["llm_review"]["review"])
            lines.append("")

    # Other Issues - grouped by kind for better organization
    other_issues = [i for i in issues if i.get("severity") not in ["blocking", "high"]]
    if other_issues:
        lines.append(_h("Other Issues", 2))

        # Group issues by kind
        grouped_issues = _group_issues_by_kind(other_issues)

        # Process important issue types first
        priority_kinds = [
            "missing_section",
            "missing_topic",
            "missing_required",
            "missing_pattern",
            "technical_issue",
            "regulatory_compliance",
            "prohibited",
            "placeholder"
        ]

        # Add priority issue groups first
        for kind in priority_kinds:
            if kind in grouped_issues:
                lines.extend(_format_issue_group(kind, grouped_issues[kind]))
                del grouped_issues[kind]

        # Add remaining issue groups
        for kind, kind_issues in grouped_issues.items():
            # Skip acronym issues if there are too many (more than 10)
            if kind == "acronym" and len(kind_issues) > 10:
                lines.append(f"### Acronym Issues\n")
                lines.append(f"Found {len(kind_issues)} undefined acronyms. Top 10 shown below:")
                for it in kind_issues[:10]:
                    lines.append(f"- {it.get('message')}")
                lines.append(f"\n*Note: {len(kind_issues) - 10} more acronym issues not shown. Define all acronyms on first use.*")
                lines.append("")
            else:
                lines.extend(_format_issue_group(kind, kind_issues))

    # Claims (from judge)
    claims = report.get("claims") or []
    if claims:
        lines.append(_h("Claims Assessment", 2))

        # Group claims by support status
        supported = []
        partial = []
        unsupported = []

        for c in claims:
            status = c.get("supported", "")
            if status == "supported":
                supported.append(c)
            elif status == "partial":
                partial.append(c)
            else:
                unsupported.append(c)

        # Show unsupported claims first
        if unsupported:
            lines.append("### Unsupported Claims\n")
            for c in unsupported:
                lines.append(f"- {c.get('id')}: **{c.get('supported')}** — {c.get('text')[:140]}")
                if c.get("rationale"):
                    lines.append(f"  - Rationale: {c.get('rationale')}")
            lines.append("")

        # Show partially supported claims
        if partial:
            lines.append("### Partially Supported Claims\n")
            for c in partial:
                lines.append(f"- {c.get('id')}: **{c.get('supported')}** — {c.get('text')[:140]}")
                if c.get("rationale"):
                    lines.append(f"  - Rationale: {c.get('rationale')}")
            lines.append("")

        # Show fully supported claims (limit to 10 if there are many)
        if supported:
            lines.append("### Supported Claims\n")
            show_count = min(10, len(supported))
            for c in supported[:show_count]:
                lines.append(f"- {c.get('id')}: **{c.get('supported')}** — {c.get('text')[:140]}")

            if len(supported) > show_count:
                lines.append(f"\n*Note: {len(supported) - show_count} more supported claims not shown.*")
            lines.append("")

    # Follow-ups
    cmds = report.get("follow_up_retrieves") or []
    if cmds:
        lines.append(_h("Follow-up Retrieve Suggestions", 2))
        for cmd in cmds:
            lines.append(f"```")
            lines.append(cmd)
            lines.append(f"```")
        lines.append("")

    # Add usage instructions
    lines.append(_h("How to Use This Report", 2))
    lines.append("1. Address all **Critical Issues** first")
    lines.append("2. Review the **Detailed Analysis** for comprehensive feedback")
    lines.append("3. Fix **Other Issues** based on priority")
    lines.append("4. Check **Claims Assessment** to ensure factual accuracy")
    lines.append("5. Run the review again after making changes to verify improvements")

    if criteria:
        lines.append("\nThis review was conducted using custom criteria from: `" + criteria + "`")
    else:
        lines.append("\nTip: For more targeted reviews, use the `--criteria` parameter with a domain-specific criteria file.")

    return "\n".join(lines).strip() + "\n"