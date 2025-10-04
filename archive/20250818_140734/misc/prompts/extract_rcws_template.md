---
title: "RCW References Extraction"
output_format: "json"
schema:
  type: "object"
  properties:
    document_title:
      type: "string"
    extraction_date:
      type: "string"
    total_chapters:
      type: "integer"
    chapters:
      type: "array"
      items:
        type: "object"
        properties:
          chapter_number:
            type: "string"
          chapter_title:
            type: "string"
          rcw_references:
            type: "array"
            items:
              type: "object"
              properties:
                rcw_citation:
                  type: "string"
                full_title:
                  type: "string"
                description:
                  type: "string"
                context:
                  type: "string"
                page_reference:
                  type: "string"
---

# Extract RCW References

Analyze the provided document and extract all Revised Code of Washington (RCW) references.

**Instructions:**
1. Go through each chapter systematically
2. Identify all RCW citations (format: RCW ##.##.###)
3. For each RCW found, provide:
   - Exact citation as written
   - Full official title if available
   - Brief description of what it covers
   - Context of how it's referenced
   - Page or section where found

**Output the results as a JSON object following the schema above.**

{{ llm_analysis }}
