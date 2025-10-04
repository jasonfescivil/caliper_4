# Caliper v2 — “Best‑of” State Summary and Forward Plan (2025‑09‑23)

Purpose
- Critically synthesize the strongest ideas from existing reviews and proposals into a single, pragmatic plan for Junie to execute.
- Keep changes low‑risk, Windows‑friendly, and aligned with Caliper’s CLI‑first architecture while adding real value for engineering report work.

Primary inputs assessed
- docs/reviews/code-review-2025-09-23.md (current capabilities and gaps)
- docs/dash_ui_functional_plan.md (feature roadmap with 1–100 ratings)
- warp_review.md and warp_proposal.md (sprint framing, high‑ROI focus)
- augment_review_proposal.md (long‑report review/rewrite pipeline)
- AGENTS.md (roles and naming used across the CLI)
- Additional composite plans provided in the issue text (Dash UI phases; Augmented Review sessions)

Note on external user files
- C:\Users\JasonFroelich\review_augment.md and proposal_augment.md are referenced but not available in‑repo. This plan integrates their described goals via the composite content included in the issue and aligns with existing repo artifacts.


Current state (best‑of synthesis)
- Architecture: CLI‑first workflow (retrieve → enhance → generate → judge → review); UIs are thin wrappers. Windows ergonomics are prioritized.
- Retrieval:
  - Cloud: LlamaCloud hybrid dense+sparse with server‑side rerank.
  - Local GraphRAG: KnowledgeGraphIndex persisted from Markdown/CSV/XLSX with per‑sheet metadata; optional union with cloud + local LLM rerank.
- Post‑retrieval:
  - Enhance: outline, diagnostics, spore rewrites, suggestions.
  - Generate: synthesis from context; style presets supported in UIs.
  - Judge v2: claim‑level adjudication with evidence and follow‑ups.
  - Review: merges judge metrics with lints; emits JSON and readable MD.
- Strengths: clean separation UI↔logic; reproducible artifacts (contexts, manifests); practical tabular ingestion; hybrid retrieval.
- Gaps:
  - Dash/Plotly UI entrypoint missing (src\caliper_v2\ui_dash\app.py referenced in docs, not present).
  - Long‑report workflows (structure, completeness vs. standards, throughline) not first‑class yet.
  - Graph relations and entity detection are heuristic‑only; acceptable for MVP but limits analytics.


Best‑of forward plan (two tracks + shared foundations)
- Track A — Dash/Plotly UI parity + UX upgrades (pure wrapper)
- Track B — Augmented Review & Rewrite for long engineering reports (file‑based, idempotent)
- Shared foundations — Windows‑safe adapters, diagnostics, reproducibility, and light tests.

Strategic rationale
- Prioritize fast, low‑risk wins that immediately improve day‑to‑day workflows (P0 UI parity, diagnostics) while laying the groundwork for transformative features (augmented review/rewrite).
- Keep UIs as wrappers to avoid logic duplication; reuse CLI/services in‑process where possible for speed and reliability.


Phased plan — Track A: Dash/Plotly UI
Time: ~3–5 weeks across P0→P1. Ratings are averaged from the functional plan.

Phase 0 (1 week) — Scaffolding & Diagnostics
- Reintroduce minimal Dash app skeleton with tabs (Retrieval, Enhance, Draft, Generate, Review, Graph, Settings).
- Environment Doctor: check keys, resolved provider/model, quick connectivity tests.  R/G 30 | Risk 10 | Time 10 | Report 40
- Provider/Model Switchboard with safe fallbacks and dry‑run checks.  R/G 35 | Risk 15 | Time 20 | Report 35
- Session state via dcc.Store (paths/presets); path sanitization.  R/G 55 | Risk 20 | Time 25 | Report 65

Phase 1 (1–2 weeks) — CLI Parity (P0)
- Retrieval (cloud) wrapper via Windows‑safe argv helper.  R/G 70 | Risk 20 | Time 20 | Report 75
- Retrieval (graph) wrapper (hops/limit/mix/rerank).  R/G 78 | Risk 25 | Time 25 | Report 80
- Graph build + stats/export controls.  R/G 45–65 | Risk 25–35 | Time 25–30 | Report 55–70
- Enhance & Generate in‑process wrappers; outline presets.  R/G 70–75 | Risk 20–25 | Time 20–25 | Report 80–85
- Judge & Review wrappers; render Markdown.  R/G 82 | Risk 25 | Time 25 | Report 90

Phase 2 (2 weeks) — UX/Quality (P1)
- Evidence viewer/inspector (filters: file/index/sheet/units).  R/G 76 | Risk 30 | Time 30 | Report 92
- Claim‑level retry & revision loop from Review.  R/G 75 | Risk 35 | Time 30 | Report 75
- Rerank introspection & tuning; hybrid fusion controls.  R/G 65 | Risk 30 | Time 35 | Report 60
- Inline citation checker & evidence pane.  R/G 60 | Risk 35 | Time 35 | Report 80
- Text lint profile editor (presence/prohibited/unit checks).  R/G 40 | Risk 15 | Time 25 | Report 70

Phase 3 (2–3 weeks) — Productivity & Analytics (P2)
- GraphRAG viz (Plotly) with snippet drilldown.  R/G 60 | Risk 40 | Time 45 | Report 60
- Scenario/batch runner and A/B dashboard.  R/G 65 | Risk 50 | Time 50 | Report 85
- Per‑node annotations/exclusions + filters.  R/G 70 | Risk 35 | Time 35 | Report 65
- Cost/token estimator & local telemetry (opt‑in).  R/G 30 | Risk 30 | Time 25 | Report 30
- Exporters & report assembly (MD/DOCX templates).  R/G 45 | Risk 20 | Time 25 | Report 80
- Optional: Tekoa I&I vertical vizzes (rainfall vs. influent, events).  R/G 50–55 | Risk 30–35 | Time 30–35 | Report 80–88

Acceptance for Track A
- P0 runs end‑to‑end on Windows with only .env configured; parity with CLI flags; persistent UI state across tabs; saved outputs under data_v2/ and outputs/.


Phased plan — Track B: Augmented Review & Rewrite (long reports)
Time: ~4–6 weeks (8–12 short sessions); safe for a single user; file‑based artifacts.

Session 1–3 — Structure and claims (foundations)
- Sectionizer for MD (Docx→MD first via existing script) → section_map.json.
- Claim extraction per section (cap N/section) → claims_v1.json.
- Per‑claim judge at scale; metrics rollup → partial review JSON.

Session 4–6 — Completeness, coherence, standards
- Standards checklist loader (JSON under knowledge_base/standards_checklists/); coverage scoring → standards_matrix.
- Coherence/throughline via embeddings; drift map; optional LLM rubric.
- Clause crosswalk aligning claims to standards with evidence.

Session 7–8 — Unified review pack and summary
- report_review_v1.json aggregating outline, claims, metrics, completeness, coherence, standards, follow‑ups.
- Render report_review.md (engineer‑readable).
- CLI: caliper_v2 report review —doc <path> —out <dir>.

Session 9–10 — Rewrite planning and safe apply
- rewrite_plan.jsonL (prioritized actions per section with prompts/citations requirements).
- Section rewriter producing replacement blocks with [n] citations from evidence pack; patch spec; conservative apply.
- Quick re‑judge per rewritten section; delta metrics.

Session 11–12 — Optional export and hardening
- DOCX export from MD (pandoc path) or python‑docx (later, off by default).
- Windows path hygiene; idempotent reruns; 3–5 unit tests; troubleshooting doc.

Deliverables (new modules/CLI — minimal surface)
- New services: report_review.py, rewrite_planner.py, section_rewriter.py (file‑based IO; reuse judge and ui_api).
- CLI: caliper_v2 report review|rewrite|apply (thin glue over services; defaults to safe conservative actions).
- Dash UI: add a “Report QA” tab later (P1/P2), reusing the above services.

Acceptance for Track B
- Deterministic file artifacts per run; no changes to existing flows unless augment/report commands are used.
- Clear metrics: support_rate ↑, blocking issues ↓, standards coverage ↑; review.md usable by engineers.


Shared foundations and adjustments (applies to both tracks)
- Windows‑safe argv builder centralization; sanitize inputs (strip quotes, absolute paths).
- Environment Doctor and provider fallbacks to reduce setup friction and 403/model_not_found traps.
- Reproducibility: file‑based manifests and idempotent outputs; cache by file hash.
- Light tests: smoke tests for wrappers; JSON schema spot checks for review packs; PowerShell scripts for CLI smoke runs.
- Schema alignment: ensure review/report JSON keys are versioned and consistent with judge v2; document schemas.


Risks and mitigations (best‑of)
- Provider/model drift or access errors (Medium): surface actionable UI errors; provide provider/model fallbacks and a local test call.
- Large corpora performance (High in GraphRAG): conservative defaults (head/tail previews), progress indicators, resumable builds.
- LlamaIndex drift (Low–Medium): feature‑detect methods; minimize direct dependency on unstable APIs.
- Novice workflow safety (Low): conservative defaults, [VERIFY] markers on generated numbers/citations, never overwrite originals by default.


What Junie should implement first (concrete next steps)
1) Write the minimal Dash app scaffold (P0 tabs + dcc.Store + adapters) and commit under src\\caliper_v2\\ui_dash\\app.py.
2) Add Environment Doctor and Provider/Model Switchboard.
3) Implement Retrieval (cloud + graph) wrappers and Enhance in‑process; confirm outputs.
4) Implement Generate and Review wrappers; confirm end‑to‑end.
5) Start Track B Session 1: sectionizer + tests + CLI glue for report review (behind a new command namespace).

Each step should land with:
- Deterministic outputs in data_v2/ and outputs/.
- Short acceptance checks or a smoke test script.
- Documentation snippets in docs/dash_ui.md and a new docs/report_review_runbook.md (later).


Appendix A — Mapping of high‑value features to impact
- P0 UI parity items (Retrieval, Generate, Review) deliver the largest day‑to‑day report impact (75–95) at low–medium risk/time (15–30).
- Evidence inspector and Judge‑guided revision loops (P1) provide the biggest quality gains short of the augmented review pipeline.
- Augmented review’s standards matrix and throughline checks (Sessions 4–6) most improve completeness/coherence for long reports; start with a small checklist for low risk.

Appendix B — File layout for augmented review artifacts
- data_v2\\reviews\\<slug>\\report_review_v1.json
- data_v2\\reviews\\<slug>\\report_review.md
- data_v2\\reviews\\<slug>\\claims_v1.json
- data_v2\\reviews\\<slug>\\standards_matrix.json
- data_v2\\reviews\\<slug>\\rewrite_plan.jsonl
- .caliper\\augment_sessions\\<slug>.json (manifest with hashes/provider/config)


This “best‑of” plan balances immediate parity and diagnostics with the deeper, structured review/rewrite system that most directly improves engineering report outcomes. It preserves Caliper’s strengths (CLI‑first, reproducible artifacts, Windows ergonomics) while charting a practical path to higher quality and productivity. 