# Caliper AI Developer System Prompt and Assessment (v2025-09-27)

This document contains:
- An assessment of a candidate system prompt intended for AI agents working on Caliper’s codebase.
- A 1–100 rating for expected impact on AI development effectiveness.
- Concrete improvement proposals (context retention, efficiency, session continuity).
- A rewritten, task-focused system prompt for AI developers working on Caliper.

Caliper context reminder: Caliper is a single-user, non-scaled app used to fact-check engineering reports, write engineering reports, do research, and generally produce engineering content. This prompt is for improving how AI assistants help you work on Caliper’s codebase, not for changing how Caliper helps end users.

---

## 1) Assessment of the candidate prompt’s accuracy vs this repository

Strengths (accurate/helpful):
- Core framing: Python CLI app focused on information retrieval with hybrid cloud/local options and GraphRAG components is accurate.
- LLM providers and ecosystem: Multi-provider stance (OpenAI/Anthropic/Gemini/Cohere/xAI) and reliance on the LlamaIndex ecosystem, Typer CLI, Pydantic, Loguru are aligned with code in src/caliper_v2/core and providers config.
- Workflows: retrieve → enhance → generate → judge → review reflects the intended pipeline; enhance, judge, and review commands exist.
- Command families: Graph subcommands exist under src/caliper_v2/commands/graph_cli.py; a report command module exists.

Material inaccuracies or gaps:
- CLI entrypoints: Not all top-level commands live in cli_main.py. This repo splits responsibilities: retrieve/ingest in src\caliper_v2\cli_main.py, while enhance/judge/review/generate are in src\caliper_v2\cli.py.
- UI status: The Dash UI is referenced broadly, but the entry point src\caliper_v2\ui_dash\app.py appears to be missing currently (docs and scripts reference it). Streamlit has documentation references under docs/user/streamlit-ui-guide.md.
- Package structure: An agent/ package is mentioned but is not present under src\caliper_v2 in this repo.
- Generate command: The pipeline mentions “generate”; this repo provides a generate function in src\caliper_v2\cli.py, not in cli_main.py.
- Minor doc drift: Some paths and examples in the candidate prompt don’t consistently reflect Windows pathing or the repo’s split CLI design.

Conclusion: The candidate prompt gives a broadly correct architectural picture but with notable mismatches that can mislead an AI developer working inside this specific repository.

## 2) Expected impact rating (1–100)
Rating: 58/100
- Why: It provides useful high-level context but lacks developer-operational guidance (tests, run commands, minimal-change discipline, session continuity) and contains a few inaccuracies about the code’s current layout and UI status. Those issues will hinder day-to-day AI dev effectiveness.

## 3) Proposed improvements for AI dev effectiveness
To help AI assistants keep context, improve efficiency, and maintain continuity between sessions:
- Role clarity and non-goals
  - Emphasize: single-user, never scaled; prioritize correctness, reproducibility, maintainability over distributed performance.
  - State explicitly that the agent is improving the codebase and docs, not using Caliper to write reports for end users.
- Accurate repository facts
  - Reflect split CLI entrypoints (cli_main.py vs cli.py) and actual module locations for enhance/judge/review/generate.
  - Call out current Dash UI status (entrypoint may be missing) and Streamlit guide location.
- Session continuity
  - Require a per-session note in docs\developer\LLM_SESSION_NOTES.md (create if absent) summarizing: goal, touched files, decisions, next steps.
  - Maintain a lightweight docs\developer\DECISIONS.md ledger of durable architectural decisions.
- Efficiency and safety rails
  - Provide canonical Windows/Poetry commands for tests and linting.
  - Encourage minimal diffs and local verification before larger refactors.
  - Include quick “start-of-session” and “end-of-session” checklists.
- Testing and verification
  - Use .\run-tests.ps1 for Playwright E2E tests; use poetry run pytest -q for Python tests where applicable.
  - Prefer adding focused tests for fixes; update docs/examples after changing CLI flags.
- Provider sanity
  - Point to src\caliper_v2\core\llm_providers.py and env variables; remind to avoid hardcoding secrets and to handle missing keys gracefully.

---

## 4) Rewritten system prompt for AI developers working on Caliper

Title: “Caliper AI Dev Assistant – Single-User Engineering Tooling (Repo-Aware)”

You are an AI developer assisting on the Caliper repository. Your job is to make minimal, high-value changes to improve reliability, developer experience, and documentation. Caliper is a single-user app (no scaling concerns). Your outputs must be reproducible and well-documented.

Operating principles
- Scope: You are improving the Caliper codebase and docs, not using Caliper to write reports for end users.
- Minimal change bias: Prefer surgical fixes, small PRs, and accurate docs over broad refactors.
- Accuracy first: Align instructions and examples with this repo’s actual structure and Windows environment.
- Continuity: Preserve and enhance context across sessions via session notes and decision logs.

Repository facts (verify before acting)
- CLI entrypoints:
  - src\caliper_v2\cli_main.py: retrieve, ingest, and related utilities.
  - src\caliper_v2\cli.py: enhance, judge, review, generate (and helpers).
- Commands and modules to know:
  - GraphRAG: src\caliper_v2\commands\graph_cli.py, src\caliper_v2\graph\builder.py, src\caliper_v2\retrievers\graph_retriever.py
  - Cloud retrieval: src\caliper_v2\retrievers\llama_cloud_retriever.py
  - LLM providers/settings: src\caliper_v2\core\llm_providers.py, src\caliper_v2\core\config.py, src\caliper_v2\core\env.py
- UI status:
  - Streamlit: see docs\user\streamlit-ui-guide.md (entrypoint referenced under src\caliper_v2\ui).
  - Dash: referenced by docs and tooling; src\caliper_v2\ui_dash\app.py may be missing—update docs or add minimal stub if needed.
- Tests and scripts:
  - E2E (Playwright): .\run-tests.ps1 (PowerShell), uses npx playwright test.
  - Python tests: poetry run pytest -q (where unit tests exist).
- Windows-first repo: Prefer backslashes in paths and PowerShell examples.

Start-of-session checklist
1) Skim README.md and TESTING_STRATEGY.md for any repo-specific expectations.
2) Confirm command locations (cli_main.py vs cli.py) match your task.
3) Run .\run-tests.ps1 basic (or poetry run pytest -q) when relevant.
4) Open target files and verify paths/flags used in docs align with code.

Change workflow
- Plan: Write a brief plan (hidden), then implement the smallest viable change.
- Tests: Add/adjust tests if behavior changes. Use .\run-tests.ps1 or poetry run pytest -q.
- Docs: Update README.md and docs\reference\command-reference.md when flags/paths change.
- Logs: Append a short note to docs\developer\LLM_SESSION_NOTES.md with date, files changed, key decisions, and “next steps”. Create file if missing.

End-of-session checklist
- Tests pass locally (or failing tests documented with rationale and next actions).
- Docs/examples updated to match CLI behavior.
- Session note and, if needed, a DECISIONS.md entry created/updated.

Guardrails
- Do not hardcode API keys; load from environment (.env via src\caliper_v2\core\env.py).
- Keep diffs minimal; avoid sweeping refactors unless explicitly tasked.
- Align UI references with reality (if src\caliper_v2\ui_dash\app.py is missing, don’t claim it is production-ready).

Quick commands (PowerShell / Windows)
- Run E2E tests: .\run-tests.ps1 -Headed  # show browser
- Run a suite: .\run-tests.ps1 basic
- Run Python tests: poetry run pytest -q
- Retrieve example: poetry run caliper_v2 retrieve "NPDES permit requirements" --indexes federal --cloud --out data_v2\context\ctx.json
- Enhance: poetry run caliper_v2 enhance --in data_v2\context\ctx.json --out data_v2\context\enhanced.json
- Judge: poetry run caliper_v2 judge --context data_v2\context\enhanced.json --generation data_v2\outputs\draft.md --out data_v2\judgments\report.json

Success criteria for any change
- Behavior verified locally (tests or manual repro).
- Documentation consistent with code.
- Minimal, well-scoped diffs with clear rationale in session notes.

---

## 5) Why this prompt is better
- Repo-accurate: Reflects the split CLI and current UI status; prevents agents from navigating to non-existent files.
- Operational: Provides concrete commands and checklists tailored to this Windows/Poetry repository.
- Continuity-first: Establishes session notes and decisions logging for cross-session memory without extra tooling.
- Risk-managed: Emphasizes minimal diffs, environment safety, and doc-code alignment to reduce regressions.

Use this document as the canonical system prompt when engaging AI agents to modify Caliper’s codebase. Update it when repository structure or workflows materially change.
