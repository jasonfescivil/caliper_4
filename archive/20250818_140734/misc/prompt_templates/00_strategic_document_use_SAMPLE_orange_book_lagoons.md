TITLE
Corpus-Aware Strategic & Tactical Document Use (with alternative recommendation)

ROLE
You are a senior process engineer AND technical librarian. Be citation-aware and jurisdiction-sensitive. Use only provided snippets/metadata.

INPUTS
TOPIC: Lagoon design basis and parameter selection (Washington State)
PRIMARY_DOC: Washington DOE Orange Book (Design Standards for Domestic Wastewater Facilities), latest edition available in corpus
JURISDICTION: Washington State (state standards must align with federal Clean Water Act + NPDES but state standards govern local design submissions)
DESIGN_CONTEXT (optional): Small municipal lagoon upgrade; average flow 0.4–0.8 MGD; cold climate; potential infiltration/inflow; reclaimed water not in scope.
MODE (optional): auto
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
    "id":"orange_book",
    "title":"DOE Orange Book — Design Standards for Domestic Wastewater Facilities (Lagoon sections)",
    "year": 2019,
    "jurisdiction":"Washington State",
    "doc_type":"standard",
    "authority":"State",
    "links_to":["wac_173_240","wef_fd_16","wef_mop8_ch3"],
    "cited_by":[],
    "snippets":[
      "Lagoon design criteria including detention time and loading [Ch. Lagoons, p. XX]",
      "Cold weather performance and ice cover considerations [Ch. Lagoons, p. XX]",
      "Submittal requirements for engineering reports/plans [Ch. Admin, p. XX]"
    ]
  },
  {
    "id":"wac_173_240",
    "title":"WAC 173-240: Submission of Plans and Reports for Construction of Wastewater Facilities",
    "year": 2019,
    "jurisdiction":"Washington State",
    "doc_type":"regulation",
    "authority":"State",
    "links_to":["orange_book"],
    "cited_by":["engineering_reports"],
    "snippets":[
      "Engineering report content requirements; basis of design must reference state standards [173-240-050]",
      "Design criteria adherence and variances [173-240-030]"
    ]
  },
  {
    "id":"wef_fd_16",
    "title":"WEF FD-16 Facilities Design: Lagoons (relevant chapters)",
    "year": 2018,
    "jurisdiction":"Professional standard (national)",
    "doc_type":"professional standard",
    "authority":"Professional Std",
    "links_to":[],
    "cited_by":["orange_book"],
    "snippets":[
      "Hydraulic loading and wind effects on mixing [Ch. Lagoons, p. XX]",
      "Recommended ranges for detention time vs. temperature [Table, p. XX]"
    ]
  },
  {
    "id":"wef_mop8_ch3",
    "title":"WEF MOP 8, Chapter 3 — Design of Wastewater Treatment Processes (lagoon-related references)",
    "year": 2017,
    "jurisdiction":"Professional standard (national)",
    "doc_type":"professional standard",
    "authority":"Professional Std",
    "links_to":[],
    "cited_by":["orange_book"],
    "snippets":[
      "Temperature correction factors and cold climate design [Ch. 3, p. XX]",
      "Typical effluent quality expectations for facultative lagoons [Table, p. XX]"
    ]
  },
  {
    "id":"npdes_permits_wa",
    "title":"Example WA NPDES permits — lagoon effluent limits and monitoring",
    "year": 2020,
    "jurisdiction":"Washington State",
    "doc_type":"permit",
    "authority":"State",
    "links_to":[],
    "cited_by":[],
    "snippets":[
      "Seasonal BOD/TSS limits and ammonia conditions [Permit WA0023141, p. XX]",
      "Winter performance allowances and compliance schedule language [Permit, p. XX]"
    ]
  }
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
Return JSON ONLY (≤ OUTPUT_TOKEN_CAP):
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
