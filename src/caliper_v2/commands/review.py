from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from caliper_v2.commands.judge import main as judge_main
from caliper_v2.services.text_lint import run_text_lints
from caliper_v2.services.review_render import render_markdown
from caliper_v2.services.review_criteria import ReviewCriteria, analyze_with_criteria, llm_review_with_criteria


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    # Only create parent directory if it's not the current directory
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    # Only create parent directory if it's not the current directory
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(
    context_path: str,
    draft_path: str,
    out_json: str,
    out_md: str,
    profile: Optional[str] = None,
    criteria_path: Optional[str] = None,
    outline_path: Optional[str] = None,
    strict: bool = True,
    max_evidence_per_claim: int = 5,
    use_llm_review: bool = True,
) -> Dict[str, Path]:
    """
    Review a draft document against context and custom criteria.
    
    Args:
        context_path: Path to the context JSON file
        draft_path: Path to the draft document to review
        out_json: Path to write the JSON output
        out_md: Path to write the Markdown output
        profile: Optional path to a profile JSON for linting
        criteria_path: Optional path to a criteria file (JSON or Markdown)
        outline_path: Optional path to an outline file to use as additional guidance
        strict: Whether to use strict mode for claim verification
        max_evidence_per_claim: Maximum evidence items per claim
        use_llm_review: Whether to use LLM for additional review
        
    Returns:
        Dictionary with paths to the output files
    """
    ctx_file = Path(context_path)
    drf_file = Path(draft_path)
    outj = Path(out_json)
    outm = Path(out_md)
    criteria_file = Path(criteria_path) if criteria_path else None
    outline_file = Path(outline_path) if outline_path else None

    if not ctx_file.exists():
        raise FileNotFoundError(f"review: context not found: {ctx_file}")
    if not drf_file.exists():
        raise FileNotFoundError(f"review: draft not found: {drf_file}")

    # 1) Run judge (in-process) with deterministic settings
    tmp_judge = outj.parent / (outj.stem + "_judge.json")
    judge_main(
        context_path=str(ctx_file),
        generation_path=str(drf_file),
        out_path=str(tmp_judge),
        strict=strict,
        max_evidence_per_claim=max_evidence_per_claim,
        claims_json=None,
        bm25_k=200,
        embed_strategy="none",
        per_source_cap=3,
    )
    judgment = _read_json(tmp_judge)

    # 2) Run deterministic lints
    profile_path = Path(profile) if profile else None
    issues = [i.__dict__ for i in run_text_lints(_read_text(drf_file), profile_path)]

    # 3) Load review criteria and perform additional analysis
    draft_text = _read_text(drf_file)
    
    # Load criteria from file - try JSON first, then markdown if that fails
    criteria = None
    if criteria_file and criteria_file.exists():
        if criteria_file.suffix.lower() in ['.json']:
            criteria = ReviewCriteria.from_file(criteria_file)
        else:
            criteria = ReviewCriteria.from_markdown(criteria_file)
    else:
        # If no criteria file is provided but an outline file is, try to extract criteria from it
        if outline_file and outline_file.exists():
            logger.info(f"No criteria file provided, attempting to extract criteria from outline: {outline_file}")
            # Create a temporary criteria file from the outline
            criteria = ReviewCriteria.from_markdown(outline_file)
            # If the outline doesn't have the expected sections, supplement with defaults
            if not criteria.required_sections:
                logger.info("Outline doesn't contain required sections, using defaults plus outline content")
                default_criteria = ReviewCriteria.from_file(None)
                criteria.focus_areas = default_criteria.focus_areas
                # Extract potential section names from the outline
                outline_text = _read_text(outline_file)
                # Look for numbered sections like "1. Executive summary"
                section_matches = re.findall(r'^\d+\.\s+([^-\n]+)', outline_text, re.MULTILINE)
                if section_matches:
                    criteria.required_sections.extend([s.strip() for s in section_matches])
        else:
            criteria = ReviewCriteria.from_file(None)  # Use default criteria
    
    # Run criteria-based analysis
    criteria_issues = analyze_with_criteria(draft_text, criteria)
    issues.extend(criteria_issues)
    
    # 4) Run LLM-based review if enabled
    llm_review_results = None
    if use_llm_review:
        # If we have an outline file, include it in the LLM review context
        outline_text = None
        if outline_file and outline_file.exists():
            outline_text = _read_text(outline_file)
            
        llm_review_results = llm_review_with_criteria(draft_text, criteria, outline_text)
        
        # Add LLM-identified issues if available
        if llm_review_results and "issues" in llm_review_results:
            llm_issues = llm_review_results.get("issues", [])
            if isinstance(llm_issues, list):
                for i, issue in enumerate(llm_issues):
                    if isinstance(issue, dict):
                        # Ensure the issue has an ID
                        if "id" not in issue:
                            issue["id"] = f"LLM-{i+1}"
                        issues.append(issue)

    # 5) Merge results into review_report v2
    blocking = sum(1 for it in issues if it.get("severity") == "blocking")
    high = sum(1 for it in issues if it.get("severity") == "high")
    medium = sum(1 for it in issues if it.get("severity") == "medium")
    inconsistencies = sum(1 for it in issues if it.get("kind") in {"unit_inconsistency", "acronym"})
    missing_sections = sum(1 for it in issues if it.get("kind") == "missing_section")
    missing_topics = sum(1 for it in issues if it.get("kind") == "missing_topic")

    summary = {
        "blocking": blocking,
        "high_risk": high,
        "medium_risk": medium,
        "inconsistencies": inconsistencies,
        "missing_sections": missing_sections,
        "missing_topics": missing_topics,
        "coverage_score": judgment.get("metrics", {}).get("citation_coverage", 0.0),
    }
    
    # Add LLM overall assessment if available
    if llm_review_results and "summary" in llm_review_results:
        llm_summary = llm_review_results.get("summary", {})
        if isinstance(llm_summary, dict) and "overall_assessment" in llm_summary:
            summary["llm_assessment"] = llm_summary.get("overall_assessment")

    review_report: Dict[str, Any] = {
        "type": "review_report",
        "version": 2,
        "doc_path": str(drf_file),
        "context_path": judgment.get("context_path") or str(ctx_file),
        "criteria_path": str(criteria_file) if criteria_file else None,
        "summary": summary,
        "issues": issues,
        "claims": judgment.get("claims", []),
        "metrics": judgment.get("metrics", {}),
        "follow_up_retrieves": judgment.get("follow_up_retrieves", []),
    }
    
    # Add LLM review text if available
    if llm_review_results and "review" in llm_review_results:
        review_report["llm_review"] = llm_review_results.get("review")

    # 6) Write JSON and Markdown
    _write_json(outj, review_report)
    _write_text(outm, render_markdown(review_report))

    logger.info("Review report written to: %s, %s", outj, outm)
    return {"json": outj, "md": outm}
