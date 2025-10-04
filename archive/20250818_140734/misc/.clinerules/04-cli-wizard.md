<!-- AUTO-GENERATED FROM .ide/rules/04-cli-wizard.md | Do not edit here. -->
<!-- Edit .ide/rules/*.md and run scripts/sync_ide_rules.py -->

# CLI & Wizard Behavior

Entrypoint
- python run_caliper_v2.py <command>
- Commands: info, providers, ingest, query, agent, wizard

Wizard goals
- Guided prompts for ingest/query/agent
- Prints the exact CLI command to be executed for reproducibility
- Remembers prior selections in .caliper_v2_profile.json

Provider resolution
- Flags (--llm-provider/--llm-model) > settings > environment heuristic
- Known providers: openai, anthropic, gemini, grok

Query UX flags (current)
- --index supports comma-separated names and negatives (e.g., -tekoa); "Everything" selects all
- --search-mode vector|bm25|hybrid
- --top-k <int>
- --reranker cohere --reranker-top-n <int>
- --format md|json

Agent UX flags (current)
- --tools fs,calc (safe defaults; fs lists/reads under knowledge_base)
- --max-steps <int>

Planned small upgrades (non-breaking)
- Prompt-from-file selection for structured tasks.
- Output-template selection (YAML front-matter + Jinja2) for formatted responses.
