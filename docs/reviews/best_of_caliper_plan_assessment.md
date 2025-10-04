# Caliper v2 — Plan Assessment and Revised Plan (2025-09-23)

This document provides:
- A critical assessment of the proposed Phase 1–3 plan for Caliper’s long‑report review/rewriting pipeline and Dash UI wrapper.
- A revised, narrower plan emphasizing low‑risk, Windows‑friendly execution with measurable acceptance checks and light tests.


Part 1 — Critical assessment

Overall verdict
- Quality: High. The plan is concrete, repo‑aware, and aligned with Caliper’s CLI‑first architecture and Windows ergonomics.
- Realism: Moderate‑High with scope discipline. Phase 2 (coherence/standards) is feasible. Phase 3 (rewrite + re‑judge + Dash orchestration) is the heaviest and benefits from a conservative MVP.
- Risk posture: Acceptable if JSON schemas, deterministic tests, and a stubbed embeddings fallback are included early.

Strengths
- Preserves UI↔logic separation: Dash is a thin wrapper over services/commands.
- File‑based, single‑user artifacts; no DB/servers.
- Clear acceptance artifacts for each phase (JSON+MD outputs).
- Emphasizes Windows path hygiene and lazy imports for fast startup.
- Already includes scaffolding for section parsing, claims extraction, and report CLI wiring.

Gaps and watch‑outs
- JSON schema/versioning: Schemas are referenced but not standardized. Without minimal schemas and smoke validators, regressions are likely.
- Embeddings dependency: Coherence depends on llama_index Settings.embed_model. Tests and offline runs need a deterministic stub when the model is missing.
- Standards checklist availability: Needs a default, minimal checklist to avoid a broken first run.
- Rewrite safety: “Conservative apply” must be explicit (idempotent patch format, boundary checks, and automatic backups) to prevent document corruption.
- Performance: Similarity over many sections can be slow. Add early caps and progress logging; cache by file hash.
- UI scope: A new “Report QA” tab that orchestrates end‑to‑end review is valuable, but it’s easy to over‑pack. Start with Run Review → List Tasks; defer Apply Rewrite until the CLI paths are stable.
- Acceptance tests: The plan mentions tests but should specify the minimum set and their determinism constraints.

Feasibility by phase
- Phase 1 polish: Already done per repo notes (HyDE defaults off, advanced flags pass‑through, warn‑only for gpt‑5 model, lazy provider config). Looks consistent with current code references.
- Phase 2 (review foundations): Very feasible. Section parser and claims extractor exist; adding standards/coherence/per‑section judge rollups is straightforward if schemas and deterministic tests are in place.
- Phase 3 (aggregate + rewrite): Feasible with a narrowed MVP: aggregation + report_review.md + rewrite plan JSONL first; section writer as a separate small step; Dash orchestration last.

Acceptance criteria coverage
- Phase 1 acceptance reads clear and is likely already satisfied.
- Phase 2–3 acceptance is solid but would benefit from minimal schema keys enumerated and a one‑command smoke run to produce all artifacts into data_v2/reviews/<slug>/.

Recommended adjustments (high‑impact, low risk)
- Define minimal JSON schemas in schemas/ for: outline.json, claims_v1.json, standards_matrix.json, coherence.json, partial_review.json, report_review_v1.json, rewrite_plan.jsonl. Keep them permissive but versioned.
- Provide a deterministic embeddings stub for tests and offline runs when no embed model is configured.
- Ship a tiny default checklist file (knowledge_base/standards_checklists/generic.json) with a handful of presence tests.
- Add a single CLI entrypoint caliper_v2 report review that orchestrates Phase 2 artifacts end‑to‑end, with flags to toggle standards/coherence.
- For Phase 3, split into: (a) aggregator+renderer, (b) rewrite planner JSONL, (c) section rewriter with backup+patch+rejudge, and (d) Dash tab wiring. Gate each with its own smoke test.


Part 2 — Revised plan (pragmatic, low‑risk)

Guiding constraints
- Windows + Poetry + PowerShell 7.5.
- Dash is a wrapper; logic lives in src/caliper_v2/services and src/caliper_v2/commands.
- Keys loaded via caliper_v2.core.env.load_env(); no secrets in logs.
- Never remap user‑entered models (e.g., "gpt-5"); warn‑only if unavailable.
- Deterministic, file‑based artifacts; no DB or servers.

Phase A — Confirm Phase 1 polish (status: DONE per repo notes)
- Ensure UI passes advanced flags; HyDE unchecked by default; no gpt‑5 remap; lazy provider config.
- Quick smoke: Start Dash, run a retrieval and review with small inputs; confirm no remapping and HyDE defaults.

Phase B — Review foundations (outline/claims/standards/coherence/rollup)
1) Schemas and helpers
- Add minimal JSON schemas (versioned) under schemas/ and a tiny schema_checker helper for smoke validation.
- Define required top‑level keys for each artifact type; allow additionalProperties for flexibility.

2) Standards checks (new services/standards_check.py)
- Load JSON checklist at knowledge_base/standards_checklists/<report_type>.json; fallback to generic.json.
- Compute presence per section and doc‑level; coverage = passed/required.
- Output standards_matrix.json with type: standards_matrix, version: 1, doc_path, report_type, per_section[], doc_summary.

3) Coherence (new services/coherence.py)
- Use llama_index Settings.embed_model when available; else a deterministic stub.
- Compute cosine similarity for: Purpose ↔ each section, and parent ↔ child.
- Optional one‑line LLM summaries gated by a flag; default off for tests.
- Output coherence.json with type: coherence, version: 1, vectors_meta, similarities[], drifts[].

4) Per‑section adjudication rollup (new services/per_section_judge.py)
- Reuse judge components to compute per‑section: support_rate, strict_precision, citation_coverage, and follow‑ups.
- Output partial_review.json with type: partial_review, version: 1, sections[].

5) CLI wiring (extend commands/report.py or add a thin commands/report_review.py)
- caliper_v2 report claims (exists).
- caliper_v2 report standards --doc <md> --out <dir> --report-type <name>.
- caliper_v2 report coherence --doc <md> --out <dir> [--summarize].
- caliper_v2 report partial --doc <md> --out <dir> [--strict] [--max-ev N].
- caliper_v2 report review --doc <md> --out <dir> to orchestrate the three above and emit all artifacts in one go.

6) Tests (light, deterministic)
- tests/test_standards_check.py: presence scoring and coverage on a toy doc.
- tests/test_coherence_stub.py: verify signature and shape using the stub embedder.
- Optional smoke: create temp dir, run report review on a tiny MD, assert files exist and load with schema_checker.

Acceptance for Phase B
- Given a small sample MD, the following files are produced under data_v2/reviews/<slug>/ and pass schema checks:
  - outline.json, claims_v1.json, standards_matrix.json, coherence.json, partial_review.json.

Phase C — Aggregation and rewrite (MVP first)
1) Aggregator + renderer (new services/report_review.py)
- Aggregate outline, claims, standards, coherence, partial_review into report_review_v1.json.
- Render human‑readable report_review.md using existing review_render styling.

2) Rewrite planner (new services/rewrite_planner.py)
- Convert issues into prioritized actions per section; include rationale, evidence_refs, clause_refs, target_length.
- Output rewrite_plan.jsonl (one JSON object per line).

3) Section rewriter (new services/section_rewriter.py) — conservative MVP
- Build evidence pack from adjudicated evidence.
- Prompt LLM to produce a replacement block with inline [n] citations.
- Emit a patch spec (offset/length/text) and write a .bak of the original.
- Apply patch safely; re‑run per‑section judge; produce delta metrics.

4) CLI wiring
- caliper_v2 report aggregate --doc <md> --out <dir> (or covered by report review orchestration).
- caliper_v2 report rewrite --doc <md> --out <dir> to generate rewrite_plan.jsonl.
- caliper_v2 report apply --doc <md> --plan <jsonl> --out <dir> to apply one or all rewrites with safety checks.

5) Dash UI — “Report QA” tab (thin wrapper)
- Buttons: Run Review, List Rewrite Tasks, Apply Selected Rewrite.
- Persist session_state.json under data_v2/reports/<slug>/; never store secrets.
- Start with listing and running review; add apply after CLI paths prove stable.

Acceptance for Phase C
- For a sample doc, the following files exist and pass schema checks:
  - report_review_v1.json and report_review.md.
  - rewrite_plan.jsonl.
  - After applying a selected rewrite, a patched MD exists, a .bak file is present, and partial per‑section re‑judge outputs delta metrics.
  - Dash “Report QA” can run review end‑to‑end and list rewrite tasks.

Risks and mitigations
- Provider/model availability: Warn only; provide Environment Doctor and a local test call.
- Embeddings performance: Cache vectors by section hash; cap N and show progress. Stub for tests.
- Rewrite correctness: Conservative patching with backups; diff previews; apply by explicit section ID.
- LlamaIndex API drift: Feature‑detect Settings and methods; isolate in small adapter functions.
- Windows quoting/paths: Centralize argv builder; normalize and sanitize paths.

Runbook (operator‑friendly)
- Claims extraction: poetry run caliper_v2 report claims --doc C:\path\report.md --out C:\path\claims.json
- Review orchestration: poetry run caliper_v2 report review --doc C:\path\report.md --out C:\path\out_dir
- Aggregation + rendering: emitted by review; or poetry run caliper_v2 report aggregate --doc <md> --out <dir>
- Rewrite planning: poetry run caliper_v2 report rewrite --doc <md> --out <dir>
- Apply rewrite: poetry run caliper_v2 report apply --doc <md> --plan <jsonl> --out <dir>
- Dash UI: poetry run python src\caliper_v2\ui_dash\app.py → use the “Report QA” tab.

Minimal schema keys (suggested)
- outline.json: {type: "outline", version: 1, doc_path, sections: [{id, title, level, start_line, end_line, parent_id?}]}
- claims_v1.json: {type: "claims", version: 1, doc_path, claims: [{section_id, text, confidence?}]}
- standards_matrix.json: {type: "standards_matrix", version: 1, report_type, per_section: [{section_id, tests: [{id, required, passed, notes?}]}], doc_summary: {required_total, passed_total, coverage}}
- coherence.json: {type: "coherence", version: 1, similarities: [{pair: "purpose↔section"|"parent↔child", section_id, score}], drifts: [{section_id, reason, score}]}
- partial_review.json: {type: "partial_review", version: 1, sections: [{section_id, support_rate, strict_precision, citation_coverage, follow_ups: ["cmd..."]}]}
- report_review_v1.json: {type: "report_review", version: 1, outline_ref, claims_ref, standards_ref, coherence_ref, partial_ref, summary}
- rewrite_plan.jsonl: one JSON per line: {section_id, action, rationale, evidence_refs: [ids], clause_refs: [ids], target_length}

Timeline (suggested, conservative)
- Week 1: Phase B schemas + standards_check + tests + tiny checklist.
- Week 2: Coherence with embeddings stub + tests; per‑section rollup; CLI review orchestrator.
- Week 3: Aggregator + renderer; rewrite planner JSONL; smoke E2E.
- Week 4: Section rewriter MVP with backups + re‑judge; Dash “Report QA” tab for Run Review + List Tasks; optional Apply for one section.

This revised plan keeps the footprint small, adds deterministic tests and schemas, and sequences work to deliver value early while de‑risking the rewrite path. It honors Windows ergonomics, avoids model remapping, and maintains the CLI‑first architecture with Dash as a thin wrapper.