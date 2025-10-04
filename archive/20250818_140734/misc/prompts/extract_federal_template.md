---
title: "Federal Regulations Extraction"
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
          federal_references:
            type: "array"
            items:
              type: "object"
              properties:
                citation:
                  type: "string"
                type:
                  type: "string"
                  enum: ["CFR", "USC", "EPA_Guidance", "Federal_Law", "Other"]
                full_title:
                  type: "string"
                description:
                  type: "string"
                context:
                  type: "string"
                page_reference:
                  type: "string"
---

# Extract Federal Regulations

Analyze the provided document and extract all federal regulations, CFR citations, EPA guidance documents, and federal laws.

**Instructions:**
1. Go through each chapter systematically
2. Identify all federal references including:
   - CFR citations (format: ## CFR ###)
   - USC citations (format: ## USC ###)
   - EPA guidance documents
   - Federal acts and laws
   - Federal technical standards
3. For each reference found, provide:
   - Exact citation as written
   - Type of reference (CFR, USC, EPA_Guidance, etc.)
   - Full official title if available
   - Brief description
   - Context of how it's referenced
   - Page or section where found

**Output the results as a JSON object following the schema above.**

{{ llm_analysis }}
