---
title: "Comprehensive Chapter Analysis"
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
          chapter_summary:
            type: "string"
          regulatory_references:
            type: "object"
            properties:
              wacs:
                type: "array"
                items:
                  type: "string"
              rcws:
                type: "array"
                items:
                  type: "string"
              federal_cfr:
                type: "array"
                items:
                  type: "string"
              federal_other:
                type: "array"
                items:
                  type: "string"
          technical_standards:
            type: "array"
            items:
              type: "string"
          key_guidance:
            type: "array"
            items:
              type: "string"
          topics_covered:
            type: "array"
            items:
              type: "string"
---

# Comprehensive Chapter-by-Chapter Analysis

Provide a complete structural analysis of the document organized by chapters.

**Instructions:**
1. For each chapter, provide:
   - Chapter number and title
   - Brief summary of chapter content
   - All regulatory references (WACs, RCWs, CFRs, federal laws)
   - All technical standards referenced
   - Key guidance documents mentioned
   - Main topics/subjects covered

2. Focus on creating a comprehensive inventory that can be used to:
   - Identify missing documents for the knowledge base
   - Understand the regulatory landscape
   - Map topic areas to specific chapters

**Output the results as a JSON object following the schema above.**

{{ llm_analysis }}
