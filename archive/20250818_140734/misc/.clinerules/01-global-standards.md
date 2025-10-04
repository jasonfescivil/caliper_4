<!-- AUTO-GENERATED FROM .ide/rules/01-global-standards.md | Do not edit here. -->
<!-- Edit .ide/rules/*.md and run scripts/sync_ide_rules.py -->

# Global Engineering Standards (Caliper)

This rule applies to all AI-assisted changes in this repo.

Core principles
- Single-user reliability, low-risk iteration, no breaking changes without explicit confirmation.
- Prefer minimal, reversible changes (add new flags over changing defaults).
- Preserve existing workflows: Windows PowerShell first; WSL optional; Docker not required.

Workflow
- Small PR-sized changes. Update docs and rules when behavior changes.
- If uncertainty is minor and the edit is reversible, proceed and leave a note to sync rules/docs; stop and ask only for medium/high-risk changes.
- Always show the exact CLI command equivalents for any operation.

Change policy
- Questions-only → no changes: Do not modify code or docs unless the user explicitly requests changes.

Logging & errors
- Use loguru via existing logger; do not duplicate logger config.
- Fail loudly and helpfully: include fix-it steps in user-facing errors.
- Never swallow exceptions; log context and re-raise or exit via Typer with code.

Docs & rules sync (required)
- When CLI behavior, ingestion, retrieval, providers, persistence, or wizard UX changes:
  1) Update docs/caliper current/CALIPER_V2_QUICK_REFERENCE.md
  2) Update matching .ide/rules file(s)
  3) Run: python scripts/sync_ide_rules.py

Planning hygiene
- Keep OPERATIONS truth in CALIPER_V2_QUICK_REFERENCE.md; keep technical truth in docs/technical/*.
- When adding features, propose flags and defaults first; implement after approval.
