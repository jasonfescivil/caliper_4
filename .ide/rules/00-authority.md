# Caliper IDE Authority

This repository uses a single, canonical source of truth for AI rules and workflows. Both Cursor and Cline MUST defer to the files in this directory.

Precedence order when guidance conflicts:
1) .ide/rules/*.md (this directory is canonical)
2) docs/caliper current/CALIPER_V2_QUICK_REFERENCE.md
3) docs/technical/*.md (Migration/Monitoring/Testing/Progress/Rollback)
4) PROJECT_STATE_SUMMARY.md
5) Optional rule-bank files explicitly enabled (e.g., docs-sync, release, memory-bank)

Conflict policy:
- If Cursor `.mdc` or Cline `.clinerules` content conflicts with `.ide/rules`, `.ide/rules` wins.
- If ambiguity remains:
  - Proceed with a low‑risk, reversible edit when the change is clearly aligned with intent; leave a note to sync rules/docs.
  - For medium/high‑risk or behavior‑changing edits, stop and ask for clarification.

Update policy (required triggers):
- CLI or flag behavior changes
- Ingestion/query/retrieval behavior changes
- Provider, embedding, reranking, or LlamaParse policy changes
- Index persistence or wizard behavior changes

When triggered:
1) Update CALIPER_V2_QUICK_REFERENCE.md and any relevant docs/technical/*.md
2) Update the appropriate file(s) in .ide/rules
3) Run “Sync IDE Rules” task (scripts/sync_ide_rules.py) to refresh Cursor and Cline adapters
4) If using Cline Memory Bank, run “update memory bank” to refresh memory-bank/activeContext.md and progress.md

Tool alignment:
- Cursor: .cursor/rules/*.mdc wrapper files include these canonical files via @-references
- Cline: .clinerules/ contains mirrored copies of these canonical files (auto-applied)

Do not edit .clinerules/* or .cursor/rules/*.mdc directly for content changes. Edit only .ide/rules/* and sync.
