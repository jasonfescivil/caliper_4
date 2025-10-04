# Execution Plan — Caliper Long-Report QA and Dash Parity

Repository: C:\\repos\\caliper_3
Date: 2025-09-23
Owner: Single-user (Windows, Poetry)

Goals
- Make Caliper excellent at reviewing 10+ page engineering reports (evidence, completeness, coherence/throughline, standards adherence).
- Use those assessments to drive targeted rewrites with anchored citations.
- Bring Dash UI to full CLI parity with quality UX.
- Keep as a pure wrapper (no business logic in UI), file-based artifacts, novice-friendly sessions.

Sprint 0 (Foundations) — 1–2 sessions
- Create minimal JSON Schemas for core artifacts under schemas/ (claims_v1, report_review_v1).
- Add a tiny schema smoke test (no external deps) and a session_state.json template for report continuity.
- Enumerate CLI parity flags for Retrieval/Graph in docs/ui_parity_flags.md.
- Add docs/CONTRIBUTING-lite.md for quick run/test workflow.

Definition of Done (Sprint 0)
- New files exist and load without errors; minimal test passes.
- session_state.json template available at data_v2/reports/_TEMPLATE/.
- ui_parity_flags.md enumerates advanced flags.

Sprint 1 (Dash P0 Parity) — 3–4 sessions
- Retrieval (cloud) wrapper + Advanced flags (dense_k, sparse_k, alpha, rerank_top_n, retrieval_mode, include_terms, exclude_sections, filters, infer_filters, expand_queries, hyde, indexes).
- Graph retrieve wrapper (hops, limit, mix-with-text, text-indexes, top-k, rerank-top-n, provider, model).
- Enhance + Generate (in-process, robust messages w/o cloud keys).
- Judge & Review (in-process, render Markdown, card metrics, download buttons).

Sprint 2 (Long-Report Review, Part 1) — 4–5 sessions
- Section parser → outline.json with ids, headings, spans.
- Claims per section → claims_v1.json with caps.
- Per-claim adjudication + rollup → partial review JSON.
- Completeness vs. standards checklist → standards_matrix.json + coverage score.
- Coherence/throughline (embeddings + optional LLM short summaries) → coherence.json.

Sprint 3 (Unified Review + Rewrite) — 3–4 sessions
- Aggregate report_review_v1.json + report_review.md renderer.
- Rewrite planner → rewrite_plan.jsonl.
- Section rewriter with anchored [n] citations + patch spec and sub-judge.
- Dash “Report QA” tab: run review, list/apply rewrites, show metrics deltas.

Guardrails
- Caps/timeouts for runtime control; partial outputs on failure.
- No secrets in logs; .env presence only; reproducibility header in outputs.
- Keep tests minimal but helpful (schema keys, simple smoke runs).
- Persist continuity in session_state.json after each stage.

Next action (now): Execute Sprint 0.