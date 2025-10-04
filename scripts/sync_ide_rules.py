#!/usr/bin/env python3
"""
Sync IDE Rules

Canonical rule sources live in .ide/rules/*.md.
This script:
- Mirrors canonical rules into .clinerules/ (for Cline)
- Generates Cursor wrapper rules in .cursor/rules/*.mdc that reference the canonical files

Usage:
  python scripts/sync_ide_rules.py           # write (sync) mode
  python scripts/sync_ide_rules.py --check   # verify everything is in-sync; nonzero exit if not

Notes:
- Do not hand-edit .clinerules/* or .cursor/rules/*.mdc; edit .ide/rules/* and re-run this script.
- Safe to re-run; it overwrites generated files (write mode).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CANON_DIR = ROOT / ".ide" / "rules"
CLINE_DIR = ROOT / ".clinerules"
CURSOR_DIR = ROOT / ".cursor" / "rules"

# Wrapper generation plan per canonical file
# Keys are canonical filenames; values are metadata for Cursor rule wrappers
WRAPPER_PLAN: Dict[str, Dict[str, Any]] = {
    "00-authority.md": {
        "type": "always",
        "description": "Canonical authority and precedence for IDE rules; defer to .ide/rules/*.md",
        "globs": [],
    },
    "01-global-standards.md": {
        "type": "agent",  # Agent Requested (include when agent decides it's relevant)
        "description": "Global engineering standards for Caliper (logging, errors, I/O, testing, prompts, security).",
        "globs": [],
    },
    "02-python-standards.md": {
        "type": "auto",  # Auto Attached when globs match
        "description": "Python standards: PEP8, type hints, docstrings, imports, formatting.",
        "globs": ["**/*.py", "src/**/*.py", "scripts/**/*.py"],
    },
    "03-rag-architecture.md": {
        "type": "agent",
        "description": "Caliper service boundaries, RAG patterns, persistence, and retrieval architecture.",
        "globs": [],
    },
    "04-cli-wizard.md": {
        "type": "auto",
        "description": "CLI wizard behavior, query vs agent, provider resolution, output options.",
        "globs": ["src/caliper_v2/**/*.py", "run_caliper_v2.py"],
    },
    "05-indexing-retrieval.md": {
        "type": "auto",
        "description": "Indexing, embeddings, BM25/hybrid retrieval, reranking, metadata filters.",
        "globs": ["src/caliper_v2/**/*.py", "data_v2/indexes/**/*"],
    },
    "06-secrets-env.md": {
        "type": "agent",
        "description": "Secrets & environment: .env keys (OpenAI, Cohere, LlamaParse), fail-with-prompt policy.",
        "globs": [],
    },
    "07-docs-sync.md": {
        "type": "manual",
        "description": "Docs synchronization workflow and required updates when behavior changes.",
        "globs": [],
    },
    "08-update-reminders.md": {
        "type": "agent",
        "description": "Reminders & checklist for when rules/docs need updates; triggers and required steps.",
        "globs": [],
    },
}


def ensure_dirs() -> None:
    CLINE_DIR.mkdir(parents=True, exist_ok=True)
    CURSOR_DIR.mkdir(parents=True, exist_ok=True)


def load_canonical_files() -> List[Path]:
    if not CANON_DIR.exists():
        raise SystemExit(f"Canonical rules directory not found: {CANON_DIR}")
    files = sorted(p for p in CANON_DIR.glob("*.md") if p.is_file())
    if not files:
        raise SystemExit(f"No canonical rule files found in {CANON_DIR}")
    return files


def cline_banner(src: Path) -> str:
    return (
        f"<!-- AUTO-GENERATED FROM {src.relative_to(ROOT)} | Do not edit here. -->\n"
        f"<!-- Edit .ide/rules/*.md and run scripts/sync_ide_rules.py -->\n\n"
    )


def expected_cline_content(src: Path) -> str:
    return cline_banner(src) + src.read_text(encoding="utf-8")


def write_cline_copy(src: Path, dst: Path) -> None:
    """Copy canonical rule into .clinerules with a small header banner."""
    dst.write_text(expected_cline_content(src), encoding="utf-8")


def _cursor_frontmatter(rule_type: str, description: str, globs: List[str]) -> str:
    """
    Build MDC frontmatter for Cursor.

    rule_type:
      - 'always' => Always Apply
      - 'auto'   => Auto Attached (by glob)
      - 'agent'  => Agent Requested (must give description)
      - 'manual' => Apply Manually (@mention)
    """
    always_apply = "true" if rule_type == "always" else "false"
    lines = ["---", f"description: {description}"]
    lines.append(f"alwaysApply: {always_apply}")
    if globs:
        lines.append("globs:")
        for g in globs:
            lines.append(f'  - "{g}"')
    else:
        lines.append("globs: []")
    lines.append("---")
    return "\n".join(lines)


def expected_cursor_content(src: Path, meta: Dict[str, Any]) -> str:
    description = meta.get("description", f"Wrapper for {src.name}")
    rule_type = meta.get("type", "agent")
    globs = meta.get("globs", [])
    fm = _cursor_frontmatter(rule_type, description, globs)
    body = (
        "\n"
        "- Canonical rule source (do not edit this wrapper):\n"
        f"  @{src.relative_to(ROOT).as_posix()}\n"
        "- To modify rules, edit the canonical file and re-run scripts/sync_ide_rules.py\n"
    )
    return fm + "\n" + body


def write_cursor_wrapper(src: Path, dst: Path, meta: Dict[str, Any]) -> None:
    """Create a Cursor .mdc wrapper that references the canonical file."""
    dst.write_text(expected_cursor_content(src, meta), encoding="utf-8")


def sync_to_cline(files: List[Path]) -> None:
    for src in files:
        dst = CLINE_DIR / src.name
        write_cline_copy(src, dst)


def sync_to_cursor(files: List[Path]) -> None:
    for src in files:
        base = src.stem  # e.g., '01-global-standards'
        dst = CURSOR_DIR / f"{base}.mdc"
        meta = WRAPPER_PLAN.get(
            src.name,
            {"type": "agent", "description": f"Wrapper for {src.name}", "globs": []},
        )
        write_cursor_wrapper(src, dst, meta)


def compute_out_of_sync(files: List[Path]) -> List[str]:
    """Return list of artifact paths that differ from expected content."""
    out: List[str] = []
    for src in files:
        # Cline copy
        cline_dst = CLINE_DIR / src.name
        expected_c = expected_cline_content(src)
        if not cline_dst.exists() or cline_dst.read_text(encoding="utf-8") != expected_c:
            out.append(str(cline_dst))

        # Cursor wrapper
        cursor_dst = CURSOR_DIR / f"{src.stem}.mdc"
        meta = WRAPPER_PLAN.get(
            src.name,
            {"type": "agent", "description": f"Wrapper for {src.name}", "globs": []},
        )
        expected_w = expected_cursor_content(src, meta)
        if not cursor_dst.exists() or cursor_dst.read_text(encoding="utf-8") != expected_w:
            out.append(str(cursor_dst))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync or check IDE rules.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify .clinerules and .cursor/rules are in sync with .ide/rules.",
    )
    args = parser.parse_args()

    ensure_dirs()
    files = load_canonical_files()

    if args.check:
        diffs = compute_out_of_sync(files)
        if diffs:
            print("Out-of-sync IDE rule artifacts detected:")
            for p in diffs:
                print(f" - {p}")
            print("\nFix: python scripts/sync_ide_rules.py")
            raise SystemExit(1)
        print("IDE rules are in sync.")
        return

    # Write mode
    sync_to_cline(files)
    sync_to_cursor(files)
    print(f"Synced {len(files)} canonical rule files to:")
    print(f"- Cline:   {CLINE_DIR}")
    print(f"- Cursor:  {CURSOR_DIR}")
    print("\nNext:")
    print("- In Cursor: open Settings > Rules and verify project rules loaded from .cursor/rules")
    print(
        "- In Cline: verify .clinerules/* are present (toggle as needed via UI or leave all active)"
    )
    print(
        "- Edit .ide/rules/* as the only source of truth and re-run this script when changes are made."
    )


if __name__ == "__main__":
    main()
