<!-- AUTO-GENERATED FROM .ide/rules/07-docs-sync.md | Do not edit here. -->
<!-- Edit .ide/rules/*.md and run scripts/sync_ide_rules.py -->

# Docs & Rules Synchronization

When to update
- CLI behavior changes (flags, defaults)
- Ingestion, retrieval, reranking, embedding, LlamaParse behavior changes
- Persistence paths or index structure changes
- Wizard prompts or defaults changes

Process
1) Update docs/caliper current/CALIPER_V2_QUICK_REFERENCE.md
2) Update the matching .ide/rules/*.md file(s)
3) Run: python scripts/sync_ide_rules.py
4) Commit both docs and rules with a descriptive message
5) If time-critical, reversible edits may land before docs/rules sync; add a TODO note and complete sync within the work session.

Cline Memory Bank (optional but recommended)
- memory-bank/activeContext.md: current focus, recent changes, next steps
- memory-bank/progress.md: features working, remaining work, known issues
- Trigger "update memory bank" after significant changes
