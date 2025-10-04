# CLAUDE.md

<system_context>
Caliper: RAG regulatory compliance system. LlamaIndex 0.12.52, Poetry, Python 3.11+.
</system_context>

<paved_path>
## THE CANONICAL WAY
- Commands: Always use `poetry run caliper_v2`
- Dependencies: Only modify via Poetry, never pip
- Paths: Use pathlib, not strings
- Errors: Catch specific exceptions, no bare except
</paved_path>

<verified_commands>
## TESTED & WORKING
```bash
poetry run caliper_v2 info
poetry run caliper_v2 ingest test_docs/federal --index federal --persist
poetry run caliper_v2 query "What are BOD limits?" --index federal
poetry run caliper_v2 agent "Compare requirements" --indexes federal,state --verbose
```
</verified_commands>

<critical_notes>
## MUST-KNOW INFORMATION

### NO IMPROVISED WORKAROUNDS
**NEVER** create "simpler approaches" or workarounds when something is missing or not available.

When you encounter:
- "X isn't available"
- "Y is missing"
- "Z doesn't exist"
- Import errors
- Missing features

YOU MUST:
1. STOP immediately
2. Report EXACTLY what's missing
3. Provide 2-3 solution options with:
   - Time estimate to implement
   - Risk assessment
   - Benefits/drawbacks
   - Your recommendation
4. ASK the user how to proceed
5. WAIT for explicit permission before making ANY changes

FORBIDDEN PHRASES:
- "Let me fix this by using a simpler approach"
- "Let me work around this"
- "I'll implement a basic version"
- "Let me create a minimal implementation"

### OTHER CRITICAL RULES
- **Type hints mandatory**: Every function needs types
- **Test before claiming**: Run actual commands
- **Embedding consistency**: Same provider for ingest/query (default: OpenAI)
</critical_notes>

<file_map>
src/caliper_v2/cli.py - Main CLI entry point (1204 lines)
src/caliper_v2/core/llm_providers.py - Multi-provider configuration
src/caliper_v2/services/ - Service layer implementation
pyproject.toml - LlamaIndex 0.12.52 + all providers
.env - API keys (OPENAI_API_KEY required)
data_v2/indexes/ - Persisted indexes with manifests
</file_map>

<api_setup>
## API KEY CHECKLIST
Required in .env:
- OPENAI_API_KEY - Always needed
- LLAMA_CLOUD_API_KEY - For --llama-parse
- COHERE_API_KEY - For reranking (optional)
Verify: `poetry run caliper_v2 info`
</api_setup>

<dependency_protocol>
## BEFORE ANY DEPENDENCY CHANGES
1. Search: "[package] [version] breaking changes"
2. Check compatibility matrix
3. Run: `poetry check`
4. Create compatibility report BEFORE updating
5. Update incrementally (core first, then related)

NEVER update multiple packages at once without explicit permission.
</dependency_protocol>

<patterns>
## COMMON PATTERNS

Dependency check:
```bash
poetry show --tree | grep [package]
poetry lock --no-update  # Test without installing
```

Debug embeddings:
```python
# Check dimensions
print(f"Expected: 1536, Got: {len(embedding)}")
```

Error handling:
```python
# BAD
try:
    risky_operation()
except:
    pass

# GOOD
try:
    risky_operation()
except FileNotFoundError as e:
    logger.error(f"Config not found: {e}")
    raise
```
</patterns>

<examples>
Working single-index query - src/caliper_v2/cli.py, search:`query_command`
Embedding setup - src/caliper_v2/cli.py, search:`embed_provider`
Index persistence - src/caliper_v2/services/persistence.py
</examples>

<testing_standards>
## BEFORE CLAIMING SUCCESS
1. Run the actual command
2. Check for side effects
3. If code change: `poetry run pytest`
4. Document working example
</testing_standards>

<workflow>
## THINKING TRIGGERS
- Basic analysis: "think about this"
- Complex problems: "think hard" or "ultrathink"
- Multi-step: Break into subtasks with parallel agents
</workflow>

<decision_protocol>
## "HOW TO PROCEED" RESPONSES

When asked for next steps or how to proceed, provide:

### STATUS + OPTIONS FORMAT
```
CURRENT STATE:
✅ Working: [what's functioning]
⚠️ Partial: [what's incomplete]
❌ Broken: [what needs fixing]

OPTION 1: [Quick Win - 30 min]
- What: Fix immediate blocker
- Why: Unblocks other work
- Risk: Low | Dependencies: None
- Outcome: Immediate productivity

OPTION 2: [Strategic - 2-4 hours]
- What: Implement core feature
- Why: Enables planned workflows
- Risk: Medium | Dependencies: [list any]
- Outcome: Long-term efficiency

OPTION 3: [Optimal - 1-2 days]
- What: Best practice implementation
- Why: Technical debt reduction
- Risk: Higher | Dependencies: [list any]
- Outcome: Maximum maintainability

MY RECOMMENDATION: Option [X] if [condition]
- Choose Option 1 if: Blocking current work
- Choose Option 2 if: Have dedicated focus time
- Choose Option 3 if: Starting fresh or major refactor

UNCLEAR? Need to know: [time budget / priority / constraints]
```

### RULES
- ALWAYS give 3+ options (quick/strategic/optimal)
- ALWAYS include time, risk, dependencies
- ALWAYS state recommendation with reasoning
- ASK if missing: time budget, blocking issues, learning goals
</decision_protocol>

<common_tasks>
## Switch LLM Provider
   ```bash
# OpenAI (default)
poetry run caliper_v2 query "test" --llm-provider openai

# Anthropic Claude
poetry run caliper_v2 query "test" --llm-provider anthropic --llm-model claude-3-opus-20240229

# Google Gemini
poetry run caliper_v2 query "test" --llm-provider gemini --llm-model gemini-pro
```

## Debug Embeddings
1. Check manifest: `cat data_v2/indexes/[name]/manifest.json`
2. Verify consistency between ingest/query
3. Re-ingest if needed (without --embed-provider local)
</common_tasks>

<gotchas>
## KNOWN ISSUES
- BM25 persistence: Pickling error but doesn't affect functionality
- ReActAgent deprecated: Use workflow-based implementation (v0.13 breaking)
- xAI Grok: Needs OpenAI-like adapter configuration
</gotchas>

<context_management>
## KEEP CONTEXT CLEAN
- Use `/clear` between unrelated tasks
- Use `/compact` at 20-30% usage
- Press `#` to save learnings to CLAUDE.md
</context_management>
