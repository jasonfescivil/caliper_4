# Tekoa Facility Plan — Caliper workflow to finish Chapters 1–3

Audience: author/editor on Windows using PowerShell. This playbook shows two paths (CLI and Dash UI) to finish the first three chapters of the attached report “Tekoa Facility Plan draft v2 (2).docx”. It uses Caliper’s retrieve → enhance → generate → judge → review loop to produce evidence-backed drafts you can ship.

Prereqs
- Install deps (from repo root):
  - poetry install
- Configure .env with provider keys (pick one you have):
  - COHERE_API_KEY (recommended for reasoning) and set LLM_PROVIDER=cohere
  - or OPENAI_API_KEY (LLM_PROVIDER=openai)
  - LLAMA_CLOUD_API_KEY if you plan to use cloud retrieval; otherwise local retrieval works after ingest
- Verify CLI: poetry run caliper_v2 --help

Folder conventions (suggested)
- Prompts: C:\repos\caliper_3\prompts\tekoa\
  - ch1_prompt.md, ch2_prompt.md, ch3_prompt.md
- Context: C:\repos\caliper_3\data_v2\context\tekoa\
  - ch1.json, ch2.json, ch3.json (raw retrieval)
  - ch1_enh.json, ch2_enh.json, ch3_enh.json (enhanced)
- Drafts: C:\repos\caliper_3\outputs\drafts\
  - tekoa_ch1.md, tekoa_ch2.md, tekoa_ch3.md
- Reviews/Judgments: C:\repos\caliper_3\outputs\reviews\ and C:\repos\caliper_3\outputs\judgments\

Tip: You don’t have to create these folders manually; Caliper will create missing parents for output paths.

Chapter prompt templates (copy into prompts/tekoa)
- ch1_prompt.md (example)
  - Title: Chapter 1 — [Replace with actual title]
  - Goal: Finish this chapter using only the Tekoa Facility Plan draft and relevant standards already ingested. Maintain the document’s style and section numbering. Identify any gaps explicitly as TODOs.
  - Scope: Summarize the purpose, background, and scope of the facility plan for Tekoa. Include assumptions and constraints as bullets with citations.
  - Deliverable: Polished draft with inline bracketed citations [1], [2]… tied to the retrieval context.
- ch2_prompt.md + ch3_prompt.md: replicate the structure above and adapt goals/scope to the chapter.

------------------------------------------------------------------------
Path A — CLI (fastest and scriptable)

0) Ingest sources into a dedicated index (local retrieval)
- Ingest the attached Word doc directly:
  - poetry run caliper_v2 ingest "C:\repos\caliper_3\Tekoa Facility Plan draft v2 (2).docx" --index tekoa --persist
- If you have additional PDFs/refs:
  - poetry run caliper_v2 ingest "C:\repos\caliper_3\data\tekoa_sources" --index tekoa --persist --llama-parse

Notes
- Use --force to re-ingest when sources change.
- If you want to mix public standards, you can later search across multiple indexes, e.g., "tekoa,design_standards" (and optionally state,federal if configured).

1) Retrieve per chapter
- Chapter 1 example (hybrid local retrieval with rerank):
  - poetry run caliper_v2 retrieve --question-file "C:\repos\caliper_3\prompts\tekoa\ch1_prompt.md" \
    --indexes "tekoa" --search-mode hybrid --top-k 40 --reranker "cohere,st-mini" \
    --out "C:\repos\caliper_3\data_v2\context\tekoa\ch1.json"
- You can broaden evidence by adding standards:
  - --indexes "tekoa,design_standards"   (optionally add state,federal if configured)
- Repeat for ch2 and ch3, changing prompt and output path accordingly.

2) Enhance the retrieval (recommended)
- Adds outline, gap analysis, refined suggestions, and spore rewrite to guide generation.
- Chapter 1:
  - poetry run caliper_v2 enhance --in "C:\repos\caliper_3\data_v2\context\tekoa\ch1.json" \
    --out "C:\repos\caliper_3\data_v2\context\tekoa\ch1_enh.json" \
    --write-outline --rewrite-spore --suggest-retrieve

3) Generate the chapter draft
- Generate uses a single LLM call based on the retrieval context. Capture stdout to a file on Windows:
- Chapter 1 (strict-citation style, Cohere reasoning optional):
  - $ctx = "C:\repos\caliper_3\data_v2\context\tekoa\ch1.json"  # or ch1_enh.json
  - poetry run caliper_v2 generate $ctx --style strict-citation --llm-provider cohere --llm-model command-a-reasoning-08-2025 \
    | Out-File -FilePath "C:\repos\caliper_3\outputs\drafts\tekoa_ch1.md" -Encoding utf8

4) Judge the draft (claim-level evidence check)
- Produces a JSON report with supported/partial/false claims, evidence, and follow-up retrieve suggestions.
- Chapter 1:
  - poetry run caliper_v2 judge \
    --context "C:\repos\caliper_3\data_v2\context\tekoa\ch1_enh.json" \
    --generation "C:\repos\caliper_3\outputs\drafts\tekoa_ch1.md" \
    --out "C:\repos\caliper_3\outputs\judgments\tekoa_ch1_judgment.json" \
    --strict --max-evidence-per-claim 5

5) Review (editor-friendly Markdown summary)
- Creates both a machine JSON and a human-readable Markdown summary with issues and the merged judge metrics.
- Chapter 1:
  - poetry run caliper_v2 review \
    --context "C:\repos\caliper_3\data_v2\context\tekoa\ch1_enh.json" \
    --draft   "C:\repos\caliper_3\outputs\drafts\tekoa_ch1.md" \
    --out-json "C:\repos\caliper_3\outputs\reviews\tekoa_ch1_review.json" \
    --out-md   "C:\repos\caliper_3\outputs\reviews\tekoa_ch1_review.md" \
    --strict --max-evidence-per-claim 5

6) Iterate quickly
- Open the review .md and address issues in your draft. For missing evidence, copy a follow_up_retrieves command from the JSON and run it to enrich context; then regenerate (step 3). Keep the loop short: retrieve → generate → judge/review → fix or enrich.
- Repeat 1–6 for chapters 2 and 3.

------------------------------------------------------------------------
Path B — Dash UI (guided, no manual commands)

Launch
- poetry run python src\caliper_v2\ui_dash\app.py

Provider
- Top panel: pick your LLM provider/model (e.g., Cohere + command-a-reasoning-08-2025), click Apply. The UI binds the provider for in-process calls and also mirrors to CLI flags it spawns.

Chapter flow per tab
- Retrieval tab
  - Paste chapter prompt (or Load from File) and set Indexes to tekoa (add design or public indexes as needed).
  - Set Top-K (e.g., 40) and Rerank Top-N (e.g., 20).
  - Set an Output Path like C:\repos\caliper_3\data_v2\context\tekoa\ch1.json.
  - Run Retrieval. Inspect the generated command and logs if needed. Preview shows top sources.
- Enhance tab
  - Input: ch1.json → Output: ch1_enh.json. Enable write-outline, rewrite spore.
  - Click Enhance to create an improved context for generation.
- Draft tab (optional scratchpad)
  - You can paste/edit text here while reviewing evidence, but final drafts will come from Generate or your editor.
- Generate tab
  - Context: ch1.json or ch1_enh.json.
  - Style: strict-citation (recommended). Provider/model inherit from top panel.
  - Click Generate; copy the output to your editor or file. For long sections, run multiple focused prompts and stitch.
- Judge & Review tab
  - Context: ch1_enh.json, Draft: tekoa_ch1.md.
  - Outputs: JSON + Markdown review paths.
  - Run Full Review to get claim-level evidence and a human-readable summary.

Notes
- All tabs are wrappers around the same CLI you can run by hand. Files live under data_v2 and outputs as shown above.
- Use the “Follow-up retrieves” in the review to enrich context, then regenerate.

------------------------------------------------------------------------
Suggested milestones and timebox (for 3 chapters)
- Day 0.5 — Setup & ingest: Env, provider test; ingest Tekoa doc + local sources into tekoa index. Quick smoke retrieve.
- Day 1 — Chapter 1: retrieve → enhance → generate → judge/review → iterate once → freeze draft v1.
- Day 1.5 — Chapter 2: repeat, 1–2 iterations.
- Day 2 — Chapter 3: repeat, 1–2 iterations. Final pass to normalize style and citations.

Quality checklist per chapter
- Draft contains inline [n] citations and a Sources block.
- Judge report shows high support_rate and strict_precision (>0.8 where feasible).
- Review Markdown has no blocking issues; any TODOs are resolved or explicitly tracked.
- All claims have at least one valid citation or are clearly marked as assumptions.

Troubleshooting
- Retrieval too thin: increase --top-k and reranker_top_n; add tekoa + standards indexes; run enhance and accept follow-up suggestions.
- Provider errors: check .env keys; try a simpler model (e.g., OpenAI gpt-4o or Cohere command).
- Windows Unicode issues: generate already guards console encoding; prefer Out-File -Encoding utf8 when saving.

Attribution
- All generation is constrained to retrieved context. Do not invent facts; mark gaps as TODO and add a follow-up retrieve.
