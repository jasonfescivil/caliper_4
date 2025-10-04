# References and Precedence Extractor

GOAL
- Read all relevant state and federal law and the two Orange Book documents (primary book and lagoon chapter).
- Extract:
  - All “References” at the end of each chapter
  - All “Recommended reading” sources
  - All “Guidance documents” suggested as alternates to the Orange Book
- Build a precedence schema to guide future searches and design reviews.

SCOPE (tailored)
- Jurisdictions: Washington State; Federal
- Indexes: federal, state, design_standards
- Orange Book PDFs (Washington Ecology):
  - Primary: knowledge_base/02_state_regulations/washington/DOE_Orange_Book_Design_Standards.pdf
  - Lagoon/Liners chapter: knowledge_base/02_state_regulations/washington/DOE_T6_Criteria_Liners_Lagoons.pdf
- Timebox: 2 hours (soft)

TOOLS POLICY
- Use tools proactively and iterate:
  1) search_across('federal', <query>, <top_k>)
  2) fetch_node(<index>, <node_id>) for full text as needed
  3) get_pdf_pages(<orange_book_path>, "page ranges") for end-of-chapter reference pages
  4) cite_and_summarize for structured, citation-rich outputs
- Self-report tools used (names + key args) at the end under a "Tools used" section.
- If a tool fails, retry with smaller top_k or narrower scope.

SEARCH QUERIES (run multiple)
- "References" OR "Bibliography" OR "Incorporation by Reference" OR "Recommended reading"
- "Guidance" OR "EPA guidance" OR "Ecology guidance" OR "DOE guidance" OR "WEF manual"
- "Alternate guidance" OR "Alternative to Orange Book"
- For Orange Book PDFs: use get_pdf_pages for the last 2–6 pages of each chapter (end-of-chapter references)

EXTRACTION SPEC
- Normalize each source to this JSON shape:
```json
{
  "title": "",
  "year": null,
  "issuing_body": "EPA|Ecology|WEF|ASCE|AWWA|CFR|RCW|WAC|Other",
  "document_type": "Statute|Regulation|Permit|Guidance|Manual|Standard|Technical Report|Book|Paper|Other",
  "jurisdiction": "Federal|State|Local|Org",
  "where_cited": {
    "index": "federal|state|design_standards",
    "file": "",
    "section_or_chapter": null,
    "page": null
  },
  "is_alternate_to_orange_book": false,
  "is_recommended_reading": false,
  "is_reference_list_item": false,
  "url_or_identifier": null,
  "snippets": [""],
  "confidence": 0.7
}
```

PRECEDENCE SCHEMA (authoritativeness rank)
- Base ranking (highest to lowest):
  1) Statutes (e.g., RCW), then Regulations (CFR/WAC), then Permits/Orders
  2) Official agency guidance (EPA/State)
  3) Consensus standards (WEF/ASCE/AWWA)
  4) Manuals/books and peer-reviewed papers
  5) Technical reports/whitepapers
- Ties: prefer newest; prefer more specific to the subject/jurisdiction; prefer documents explicitly incorporated by reference.
- Output format:
```json
{
  "rank_rules": [
    {"rule": "Statute > Regulation > Permit/Order > Guidance > Standard > Manual/Book > Paper > Technical Report"},
    {"rule": "If tied, prefer newer"},
    {"rule": "If tied, prefer jurisdiction-specific over general"},
    {"rule": "If incorporated by reference, elevate one level"}
  ],
  "authority_levels": [
    {"level": 1, "kinds": ["Statute"]},
    {"level": 2, "kinds": ["Regulation"]},
    {"level": 3, "kinds": ["Permit", "Order"]},
    {"level": 4, "kinds": ["Guidance"]},
    {"level": 5, "kinds": ["Standard"]},
    {"level": 6, "kinds": ["Manual", "Book"]},
    {"level": 7, "kinds": ["Paper"]},
    {"level": 8, "kinds": ["Technical Report"]}
  ]
}
```

OUTPUTS
- Part A: References catalog (JSON in a fenced block)
```json
{ "references": [ ... normalized items ... ] }
```
- Part B: Precedence schema (JSON in a fenced block)
```json
{ "rank_rules": [ ... ], "authority_levels": [ ... ] }
```
- Part C: Top gaps/missing sources and next steps (bullets)
- Part D: Tools used (bulleted list with key args)

PROCESS (step-by-step)
1) Broad retrieval:
   - Run search_across('federal', queries above, top_k=40).
2) Focus on Orange Book references:
   - For each chapter you identify, use get_pdf_pages with the last few pages to capture "References".
3) Normalize:
   - Convert found citations to the JSON schema; fill missing year/issuer if inferable from context.
4) De-duplicate:
   - Merge duplicate sources by title+issuer+year; union where_cited and snippets.
5) Precedence mapping:
   - Assign each source an authority level using the schema; note elevations via incorporation by reference.
6) Validate:
   - cite_and_summarize a short justification for the precedence rules and any non-obvious mappings.
7) Return outputs exactly as specified above.

QUALITY BAR
- Every catalog entry must have at least one supporting snippet and a where_cited pointer.
- Prefer page/section labels in snippets.
- Mark low-confidence entries clearly (confidence < 0.6).

CONSTRAINTS
- Use only the available tools and the specified indexes/paths.
- If a source is implied but not extractable, list as a gap.
