---
title: "Standards and Policies Extraction"
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
          standards_references:
            type: "array"
            items:
              type: "object"
              properties:
                standard_citation:
                  type: "string"
                type:
                  type: "string"
                  enum: ["ASTM", "AWWA", "WEF", "ASCE", "Technical_Standard", "Design_Criteria", "Policy", "Other"]
                full_title:
                  type: "string"
                description:
                  type: "string"
                context:
                  type: "string"
                page_reference:
                  type: "string"
---

# Extract Standards and Policies

Analyze the provided document and extract all technical standards, design criteria, policies, and engineering standards.

**Instructions:**
1. Go through each chapter systematically
2. Identify all standards and policies including:
   - ASTM standards
   - AWWA standards
   - WEF standards
   - ASCE standards
   - Technical specifications
   - Design criteria
   - Agency policies
   - Engineering standards
3. For each reference found, provide:
   - Exact citation/standard number
   - Type of standard (ASTM, AWWA, etc.)
   - Full official title if available
   - Brief description
   - Context of how it's referenced
   - Page or section where found

**Output the results as a JSON object following the schema above.**

{{ llm_analysis }}
