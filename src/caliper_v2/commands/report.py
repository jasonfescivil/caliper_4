from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from caliper_v2.services.section_parser import parse_markdown_sections
from caliper_v2.services.claims_extractor import extract_claims_from_text, claims_to_json

app = typer.Typer(help="Report tooling: sectionize and extract claims")


@app.command("claims")
def extract_claims(
    doc: str = typer.Argument(..., help="Path to Markdown report"),
    out: Optional[str] = typer.Option(None, "--out", help="Output claims JSON (default next to doc)"),
    max_per_section: int = typer.Option(10, "--max-per-section", help="Cap claims per section"),
) -> None:
    """Sectionize a Markdown doc and extract heuristic claims per section.

    Emits a claims_v1 JSON file.
    """
    md_path = Path(doc).resolve()
    if not md_path.exists():
        typer.secho(f"Doc not found: {md_path}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    outline = parse_markdown_sections(md_path)
    claims_combined = []
    for s in outline.get("sections", []):
        text = s.get("text") or ""
        heading = s.get("heading")
        claims = extract_claims_from_text(text, heading=heading, max_claims=max_per_section)
        claims_combined.extend(claims)

    payload = claims_to_json(str(md_path), claims_combined)

    if out:
        out_path = Path(out)
    else:
        out_path = md_path.with_suffix(".claims.json")
    out_path.write_text(__import__("json").dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.secho(f"Wrote claims to: {out_path}", fg=typer.colors.GREEN)


@app.command("review")
def run_review(
    doc: str = typer.Argument(..., help="Path to Markdown report"),
    out_dir: str = typer.Option("outputs/reviews", "--out-dir", help="Output directory for review artifacts"),
    checklist: Optional[str] = typer.Option(None, "--checklist", help="Path to standards checklist JSON"),
) -> None:
    """Run a minimal long-report review pipeline (offline-safe).

    Produces: outline.json, claims.json, standards_matrix.json, coherence.json, partial_review.json, review.json, review.md
    """
    md_path = Path(doc).resolve()
    out_base = Path(out_dir).resolve()
    out_base.mkdir(parents=True, exist_ok=True)

    outline = parse_markdown_sections(md_path)
    # claims
    from caliper_v2.services.claims_extractor import extract_claims_from_text, claims_to_json
    claims_all = []
    for s in outline.get("sections", []):
        claims_all.extend(extract_claims_from_text(s.get("text") or "", heading=s.get("heading"), max_claims=10))
    claims_json = claims_to_json(str(md_path), claims_all)

    # standards
    from caliper_v2.services.standards_check import run_standards
    standards_path = out_base / "standards_matrix.json"
    run_standards(md_path, outline, checklist, standards_path)
    standards_json = json.loads(standards_path.read_text(encoding="utf-8"))

    # coherence
    from caliper_v2.services.coherence import run_coherence
    coherence_path = out_base / "coherence.json"
    run_coherence(outline, coherence_path)
    coherence_json = json.loads(coherence_path.read_text(encoding="utf-8"))

    # per-section judge (heuristic)
    from caliper_v2.services.per_section_judge import run_per_section_judge
    partial_path = out_base / "partial_review.json"
    run_per_section_judge(outline, claims_json, partial_path)
    partial_json = json.loads(partial_path.read_text(encoding="utf-8"))

    # aggregate
    from caliper_v2.services.report_review import aggregate_review, write_review_pack
    review = aggregate_review(
        doc_path=str(md_path), outline=outline, claims_json=claims_json,
        standards_json=standards_json, coherence_json=coherence_json, partial_review_json=partial_json,
    )
    out_json = out_base / "review.json"
    out_md = out_base / "review.md"
    write_review_pack(review, out_json, out_md)

    # Also persist outline and claims for transparency
    (out_base / "outline.json").write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_base / "claims.json").write_text(json.dumps(claims_json, ensure_ascii=False, indent=2), encoding="utf-8")

    typer.secho(f"Review pack written to: {out_base}", fg=typer.colors.GREEN)
