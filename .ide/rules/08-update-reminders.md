# Update Reminders (Rules & Docs)

Use this checklist whenever you change Caliper behavior or developer-facing UX.

Triggers (when to update)
- CLI flags/defaults or wizard prompts change
- Ingestion (LlamaParse toggles, chunking) or indexing behavior changes
- Retrieval (vector/bm25/hybrid), reranking, or metadata filtering changes
- Provider/model resolution rules change
- Embedding provider defaults or failure behavior changes
- Persistence layout or index naming changes
- Any guidance in docs that becomes stale

Required steps
1) Update docs/caliper current/CALIPER_V2_QUICK_REFERENCE.md
2) Update matching .ide/rules/*.md content (source of truth)
3) Run: python scripts/sync_ide_rules.py
4) (Optional) If using Cline Memory Bank: "update memory bank" (activeContext.md, progress.md)
5) Commit with a message that references “rules-sync” (e.g., chore(rules): sync wizard flags + retrieval notes)
6) For urgent, low-risk changes, it is acceptable to land code first and sync rules/docs immediately after; leave a short TODO in the PR/commit.

Fast check (before commit)
- If you touched src/caliper_v2/cli.py or docs/caliper current/* and did NOT touch .ide/rules or docs/technical, re-check if you should update them now.

Notes
- .ide/rules is canonical; .clinerules and .cursor/rules are generated.
- Prefer adding flags over changing defaults to keep behavior low-risk for the single-user workflow.
