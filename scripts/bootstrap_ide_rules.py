#!/usr/bin/env python3
"""
Bootstrap unified IDE rules scaffolding for Caliper.

This creates canonical rule files under .ide/rules/ (if missing) and a sensible .clineignore.
After creation, run:
  python scripts/sync_ide_rules.py
to mirror rules to Cline (.clinerules) and generate Cursor wrappers (.cursor/rules).

Safe to re-run; existing files are left untouched.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / ".ide" / "rules"
CLINEIGNORE = ROOT / ".clineignore"

FILES: dict[str, str] = {
    "01-global-standards.md": """# Global Engineering Standards (Caliper)

This rule applies to all AI-assisted changes in this repo.

Core principles
- Single-user reliability, low-risk iteration, no breaking changes without explicit confirmation.
- Prefer minimal, reversible changes (add new flags over changing defaults).
- Preserve existing workflows: Windows PowerShell first; WSL optional; Docker not required.

Workflow
- Small PR-sized changes. Update docs and rules when behavior changes.
- If uncertainty > 20%, stop and ask before proceeding.
- Always show the exact CLI command equivalents for any operation.

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
""",
    "02-python-standards.md": """# Python Standards

Formatting & style
- PEP 8 with black formatting awareness (target line length ~100; do not hard-wrap docstrings unnecessarily).
- Type hints mandatory for all public functions. Use typing and collections.abc.
- Google-style docstrings for non-trivial modules/classes/functions with Args/Returns/Raises.
- Imports: stdlib, third-party, local; no unused imports.

Error handling & logging
- Use explicit exceptions (FileNotFoundError, ValueError, etc.) and log with context.
- For CLI commands, surface user-facing hints via typer.secho; log stack traces with logger.exception.

I/O & paths
- Use pathlib.Path exclusively for filesystem paths.
- No hardcoded absolute paths. Use settings and environment variables.
- Respect Windows paths and case sensitivity; avoid POSIX-only assumptions.

Env & secrets
- Never hardcode API keys; rely on .env loader and settings.
- Read-only access to .env values; never print secret values.

Testing & reliability
- Design functions to be testable; avoid singletons where possible.
- Prefer pure functions for transformations and side-effect isolation for I/O.

Performance
- Avoid O(n^2) on large collections; stream or batch where feasible.
- Chunk sizes configurable via settings; no magic constants.

Concurrency
- Prefer simple synchronous code unless there is a clear benefit to async.
""",
    "03-rag-architecture.md": """# Caliper RAG Architecture

Service boundaries (conceptual)
- Provider config: caliper_v2/core/llm_providers.py
- CLI & UX: caliper_v2/cli.py (Typer-based)
- Persistence helpers: caliper_v2/services/persistence (IndexPathResolver, HashCache)
- Index artifacts: data_v2/indexes/<name> (FAISS storage + optional BM25 pickle)

Indexing & nodes
- Reader: LlamaIndex SimpleDirectoryReader; optional LlamaParse for PDFs (LLAMA_CLOUD_API_KEY required).
- Chunking: SimpleNodeParser.from_defaults(chunk_size, chunk_overlap).
- Embeddings: default OpenAI text-embedding-3-small; allow 'local' stub for offline smoke tests.
- Vector index: VectorStoreIndex.
- BM25: optional, built from same nodes; persisted as pickle.

Retrieval
- Modes: vector (default), bm25, hybrid (QueryFusionRetriever with reciprocal rank fusion).
- Reranking: optional Cohere Rerank if API key present.
- Metadata filters: source file, regulation, document type.

Persistence
- Vector index persisted to FAISS dir; BM25 retriever pickled separately.
- HashCache used to skip unchanged files during re-ingest.

Failure policy
- Missing OpenAI key: fail fast with clear instruction and offer explicit user choice to proceed with --embed-provider local when triggered interactively (future enhancement).
""",
    "04-cli-wizard.md": """# CLI & Wizard Behavior

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

Query UX flags
- --search-mode vector|bm25|hybrid
- --expand-query, --hyde, -i/--interactive, --critique-retrieval, --self-reflect
- --format md|json
- Filters: --source-filter, --regulation-filter, --doc-type

Planned small upgrades (non-breaking)
- Negative index selection (e.g., "-tekoa" meaning all except tekoa) via wizard helper.
- Prompt-from-file selection for structured tasks.
- Output-template selection (YAML front-matter + Jinja2) for formatted responses.
""",
    "05-indexing-retrieval.md": """# Indexing & Retrieval Details

Ingest
- Input: directory path (recursive). LlamaParse used only if LLAMA_CLOUD_API_KEY present.
- Metadata enrichment: extract basic regulatory markers (CFR/WAC/RCW), agency hints, year.
- HashCache avoids re-processing unchanged files (when available).
- Persistence: FAISS vector index + optional BM25 pickle per index.

Query
- Multi-index federation supported via comma-separated --index list.
- Retrieval budget (top_k) from settings; multiply by 3 when reranking enabled.
- Response synthesis: TreeSummarize with citation format.

Filters
- source_filter: filters by file_path substring
- regulation_filter: maps to cfr_parts/wac_sections/rcw_sections/regulation metadata
- doc_type_filter: federal | state | technical | guidance (lowercase values)

Reranking
- Cohere Rerank enabled when COHERE_API_KEY is present; model "rerank-english-v3.0".

HyDE & expansion
- HyDE requires active LLM; generated hypothetical doc used as additional query.
- Query expansion can be interactive or automatic.
""",
    "06-secrets-env.md": """# Secrets, Environment, and Keys

Loading policy
- python-dotenv is used to load .env automatically when CLI starts.
- Settings (pydantic) may supply values if available; environment variables take precedence.

Expected keys
- OPENAI_API_KEY
- COHERE_API_KEY (optional; enables reranking)
- LLAMA_CLOUD_API_KEY (optional; enables LlamaParse)
- ANTHROPIC_API_KEY (optional)
- GEMINI_API_KEY or GOOGLE_API_KEY (optional)
- XAI_API_KEY (optional)

Windows quick test
- PowerShell:
  $env:OPENAI_API_KEY="sk-..."
  python run_caliper_v2.py info
- Or put OPENAI_API_KEY=... into .env at project root and restart terminal.

Failure behavior (current)
- If no OpenAI key and embed provider not set to 'local', LlamaIndex may raise a clear error.
- If this occurs in wizard, accept the failure and show a prompt recommending:
  a) Set OPENAI_API_KEY and re-run
  b) Retry with --embed-provider local (offline smoke)
""",
    "07-docs-sync.md": """# Docs & Rules Synchronization

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

Cline Memory Bank (optional but recommended)
- memory-bank/activeContext.md: current focus, recent changes, next steps
- memory-bank/progress.md: features working, remaining work, known issues
- Trigger "update memory bank" after significant changes
""",
}

CLINEIGNORE_CONTENT = """# Cline context hygiene
# Ignore large or generated artifacts to keep context focused and fast.
# Adjust as needed.

# Python caches & envs
__pycache__/
*.pyc
.venv/
venv/

# Node/JS
node_modules/
**/node_modules/

# Build / coverage
build/
dist/
coverage/

# Editor/OS
.DS_Store
Thumbs.db

# Data artifacts (keep indexes, not source docs)
data_v2/indexes/
outputs/

# Secrets
.env
google-credentials.json

# Large binaries
*.pdf
*.docx
"""


def ensure_rules() -> None:
    CANON.mkdir(parents=True, exist_ok=True)
    created = []
    for name, content in FILES.items():
        path = CANON / name
        if not path.exists():
            path.write_text(content.strip() + "\n", encoding="utf-8")
            created.append(path)
    print(f"Canonical rules directory: {CANON}")
    if created:
        print(f"Created {len(created)} rule file(s):")
        for p in created:
            print(f" - {p.name}")
    else:
        print("All canonical rule files already exist (no changes).")


def ensure_clineignore() -> None:
    if not CLINEIGNORE.exists():
        CLINEIGNORE.write_text(CLINEIGNORE_CONTENT.strip() + "\n", encoding="utf-8")
        print(f"Created {CLINEIGNORE.relative_to(ROOT)}")
    else:
        print(f"{CLINEIGNORE.relative_to(ROOT)} exists (no changes).")


def main() -> None:
    ensure_rules()
    ensure_clineignore()
    print("\nNext steps:")
    print("  python scripts/sync_ide_rules.py")
    print("Then verify:")
    print("  - .clinerules/* mirrored for Cline")
    print("  - .cursor/rules/*.mdc wrappers generated for Cursor")


if __name__ == "__main__":
    main()
