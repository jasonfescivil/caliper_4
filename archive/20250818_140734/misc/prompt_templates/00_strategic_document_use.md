TITLE
Corpus-Aware Strategic & Tactical Document Use (with alternative recommendation)

ROLE
You are a senior process engineer AND technical librarian. Be citation-aware and jurisdiction-sensitive. Use only provided snippets/metadata.

INPUTS
TOPIC: {topic}
PRIMARY_DOC: {primary_doc_title_or_id}
JURISDICTION: {jurisdiction_or_unknown}
DESIGN_CONTEXT (optional): {project/site/constraints}
MODE (optional): {auto|stage_a_only|stage_b_only}  # auto = do Stage A then proceed to Stage B using retrieved context as candidates
GRAPH_FEATURES (optional): {
  "edges": ["cites","supersedes","clarifies","same_topic","jurisdiction_of"],
  "max_hops": 2
}
PARAMS (editable): {
  "K_INIT": 12,
  "K_COMPARE": 8,
  "SNIPPET_BUDGET_PER_DOC_CHARS": 800,
  "OUTPUT_TOKEN_CAP": 650,
  "RUBRIC_WEIGHTS": {
    "topical_fit": 4,
    "authority": 4,
    "recency": 2,
    "citations_dependency": 3,
    "practicality": 3,
    "jurisdiction": 4
  }
}
CANDIDATES (optional; provide to run Stage B): [
  {
    "id":"...",
    "title":"...",
    "year":20XX,
    "jurisdiction":"...",
    "doc_type":"regulation|standard|manual|guidance|textbook",
    "authority":"EPA|State|Professional Std|Textbook",
    "links_to":["doc_ids it cites"],
    "cited_by":["doc_ids that cite it"],
    "snippets":["short excerpt 1 (5–25 words, with page/section)", "..."]
  },
  ...
]

TASK
Stage A — Candidate Discovery (always run)
1) Propose 5–7 precise retrieval queries to identify documents that are better primaries or key complements for TOPIC and JURISDICTION.
2) Provide a short screening rubric (with the weights above) and acceptance criteria to select top K_INIT for review.
3) Return JSON ONLY:
{
  "queries": [...],
  "screening_rubric": {"topical_fit":..., "authority":..., "recency":..., "citations_dependency":..., "practicality":..., "jurisdiction":...},
  "acceptance_criteria": "How to pick top K_INIT",
  "notes": "Any graph expansions (≤2 hops) to apply around PRIMARY_DOC"
}
If MODE == stage_a_only, stop here. Otherwise continue to Stage B.

Stage B — Comparative Judgment & Synthesis
If CANDIDATES not provided: use the retrieved context to construct CANDIDATES automatically by grouping snippets by document. Infer basic metadata (title, year if visible, jurisdiction, doc_type, authority) from filenames/headers. Include 1–3 short snippets per document with page/section markers.
1) Score each candidate with the rubric (0–4 unless noted) and show a compact score table with totals.
2) Select the best PRIMARY for this TOPIC and JURISDICTION. If it is NOT {PRIMARY_DOC}, explain why; then state how {PRIMARY_DOC} should be used (complement/exception/legacy).
3) Map relationships among documents (who supersedes/implements/clarifies whom; note conflicts + resolution order).
4) Produce two practitioner-focused sections:
   • Strategic Use — when/why each doc governs; where it sits in the design basis; jurisdictional caveats.
   • Tactical Use — specific sections/tables/procedures/parameters to apply; cross-checks with complements; pitfalls.
5) If evidence is insufficient for any critical point, list up to 5 “Targeted Pulls Needed” (doc_id + section/page hint).

OUTPUT FORMAT (Stage B)
Preferred for Caliper/Cursor (markdown):
- Return concise markdown sections in this order: Primary Choice, Scores (compact table), Doc Map (bullets), Strategic, Tactical, Targeted Pulls Needed, Sources.
- Inline citations use [1], [2], etc., where numbers map to Sources.

Alternative (JSON, if tool requires it; ≤ OUTPUT_TOKEN_CAP):
{
  "primary_choice": {"doc_id":"...", "why":"(2–4 sentences with citations [1], [2])"},
  "scores": [
    {"doc_id":"...","topical_fit":..,"authority":..,"recency":..,"citations":..,"practicality":..,"jurisdiction":..,"total":..},
    ...
  ],
  "doc_map": [
    {"doc_id":"...","role":"primary|complement|superseded",
     "relationships":[{"type":"cites|supersedes|clarifies","target":"..."}]}
  ],
  "strategic": "Concise, actionable paragraph(s) with inline markers [1], [2].",
  "tactical": "Concrete steps/sections/parameters with inline markers [1], [2].",
  "targeted_pulls_needed": [{"doc_id":"...","hint":"..."}],
  "sources": [
    {"id":"[1]","file":"...","page_or_section":"...", "quote":"5–25 words"},
    {"id":"[2]","file":"...","page_or_section":"...", "quote":"5–25 words"}
  ]
}

CONSTRAINTS
- Use only provided snippets/metadata; no speculation.
- Quotes must be brief (5–25 words) with page/section labels.
- Prefer higher authority within JURISDICTION; break ties by recency → practicality.
- Keep language concise and decision-oriented. Obey OUTPUT_TOKEN_CAP.
