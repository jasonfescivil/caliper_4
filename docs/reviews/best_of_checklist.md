# Caliper v2 — Best‑of Implementation Checklist (Seed)

Legend: [ ] not started, [*] in progress, [x] done

Track A — Dash/Plotly UI (Parity and UX)

Phase 0 — Scaffolding & Diagnostics
- [ ] Create src\caliper_v2\ui_dash\app.py minimal skeleton (tabs + dcc.Store)
- [ ] Add Environment Doctor panel (keys, indexes, provider/model resolution, quick test)
- [ ] Add Provider/Model Switchboard (apply + dry‑run test)
- [ ] Implement session persistence (paths/presets) via dcc.Store; sanitize Windows paths

Phase 1 — CLI Parity (P0)
- [ ] Retrieval (cloud) wrapper using Windows‑safe argv helper; write context.json
- [ ] Retrieval (graph) wrapper (hops/limit/mix/rerank); write context.json
- [ ] Graph build UI (corpus/out/provider/relation_mode/k_hop/rebuild/table controls)
- [ ] Enhance wrapper (in‑process) writing enhanced context
- [ ] Generate wrapper (in‑process) with style presets; write draft.md
- [ ] Judge & Review wrapper (in‑process) writing review JSON/MD; render Markdown

Phase 2 — UX/Quality (P1)
- [ ] Evidence viewer/inspector (filters by file/index/sheet/units)
- [ ] Claim‑level retry & revision loop from Review tab
- [ ] Rerank introspection (pre/post lists; thresholds/top‑N; re‑run)
- [ ] Inline citation checker + evidence pane
- [ ] Text lint profile editor; persist profile.json

Phase 3 — Productivity & Analytics (P2)
- [ ] GraphRAG mini‑viz (Plotly) of entities/sections with snippet drilldown
- [ ] Scenario/batch runner with A/B comparison dashboard
- [ ] Per‑node annotations/exclusions + advanced filters
- [ ] Cost/token estimator and local telemetry (opt‑in)
- [ ] Exporters and report assembly (MD/DOCX templates)
- [ ] Optional Tekoa I&I viz (rainfall vs. influent + event tagging)

Acceptance (Track A)
- [ ] Full P0 smoke test on Windows succeeds with only .env configured
- [ ] Parity with CLI flags for Retrieval/Graph/Review
- [ ] Persistent state across tabs; discover last outputs under data_v2/ and outputs/


Track B — Augmented Review & Rewrite (Long Reports)

Session 1–3 — Structure and claims
- [ ] MD sectionizer (Docx→MD first) → section_map.json + numbering_map.json
- [ ] Claim extraction per section (cap N) → claims_v1.json
- [ ] Per‑claim judge pass; metrics rollup → partial review JSON

Session 4–6 — Completeness, coherence, standards
- [ ] Standards checklist loader; initial templates under knowledge_base/standards_checklists/
- [ ] Coverage scoring → standards_matrix.json
- [ ] Coherence/throughline analysis (embeddings + rubric) → coherence.json
- [ ] Clause crosswalk aligning claims↔standards with evidence

Session 7–8 — Unified review pack and summary
- [ ] Aggregate report_review_v1.json (outline, claims, metrics, completeness, coherence, standards, follow‑ups)
- [ ] Render report_review.md summary
- [ ] CLI: caliper_v2 report review —doc <path> —out <dir>

Session 9–10 — Rewrite plan and conservative apply
- [ ] rewrite_planner → rewrite_plan.jsonl (prioritized actions)
- [ ] section_rewriter → replacement blocks with [n] citations + patch spec
- [ ] Apply conservative changes to MD; re‑judge changed sections; record delta metrics

Session 11–12 — Optional export and hardening
- [ ] DOCX export from MD (pandoc path) or python‑docx (off by default)
- [ ] Windows path hygiene; idempotent reruns; add 3–5 unit tests and troubleshooting doc

Acceptance (Track B)
- [ ] Deterministic artifacts per run; no impact to existing flows by default
- [ ] Metrics improvements visible after rewrites (support_rate↑, blocking issues↓)


Shared foundations
- [ ] Centralize Windows‑safe argv builder and path sanitization helpers
- [ ] Environment Doctor checks and provider fallback logic
- [ ] Reproducibility: hash‑based caching; avoid overwriting originals unless --force
- [ ] Smoke tests for wrappers; JSON schema checks for review packs
- [ ] Document schemas and update runbooks (docs/dash_ui.md; add docs/report_review_runbook.md)
