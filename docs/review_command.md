# Enhanced Review Command

The `review` command in Caliper v2 has been enhanced to provide more comprehensive and useful document reviews. This command now supports custom review criteria and LLM-powered analysis to give you more detailed feedback on your documents.

## Basic Usage

```bash
poetry run caliper_v2 review \
  --context data_v2/context/your_context.json \
  --draft your_draft_document.md \
  --out-json data_v2/outputs/reviews/review_output.json \
  --out-md data_v2/outputs/reviews/review_output.md
```

## Enhanced Features

### Custom Review Criteria

You can now provide a custom criteria file to guide the review process:

```bash
poetry run caliper_v2 review \
  --context data_v2/context/your_context.json \
  --draft your_draft_document.md \
  --criteria data_v2/criteria/your_criteria.md \
  --out-json data_v2/outputs/reviews/review_output.json \
  --out-md data_v2/outputs/reviews/review_output.md
```

The criteria file can be in either JSON or Markdown format:

#### Markdown Format

```markdown
# Review Criteria

## Focus Areas
- Area 1
- Area 2

## Required Sections
- Section 1
- Section 2

## Required Topics
- Topic 1
- Topic 2

## Citation Requirements
- Requirement 1
- Requirement 2

## Technical Requirements
- Requirement 1
- Requirement 2

## Style Requirements
- Requirement 1
- Requirement 2

## Custom Patterns
- pattern_name: regex_pattern
- another_pattern: another_regex
```

#### JSON Format

```json
{
  "focus_areas": ["Area 1", "Area 2"],
  "required_sections": ["Section 1", "Section 2"],
  "required_topics": ["Topic 1", "Topic 2"],
  "citation_requirements": ["Requirement 1", "Requirement 2"],
  "technical_requirements": ["Requirement 1", "Requirement 2"],
  "style_requirements": ["Requirement 1", "Requirement 2"],
  "custom_patterns": [
    {
      "name": "pattern_name",
      "pattern": "regex_pattern",
      "required": true,
      "severity": "high"
    }
  ]
}
```

### LLM-Powered Review

The review command now uses LLM to provide additional analysis based on the criteria. This can be disabled if needed:

```bash
poetry run caliper_v2 review \
  --context data_v2/context/your_context.json \
  --draft your_draft_document.md \
  --criteria data_v2/criteria/your_criteria.md \
  --no-llm \
  --out-json data_v2/outputs/reviews/review_output.json \
  --out-md data_v2/outputs/reviews/review_output.md
```

## Output

The review command produces two output files:

1. A JSON file containing the full review data
2. A Markdown file with a human-readable report

The report includes:

- Summary statistics
- LLM-generated review (if enabled)
- Issues grouped by type
- Claims assessment from the judge command
- Follow-up retrieval suggestions

## Example Criteria Files

Example criteria files are provided in the `data_v2/criteria/` directory:

- `wastewater_facility_plan.md` - Criteria for reviewing wastewater facility plans
- `wastewater_facility_plan.json` - Same criteria in JSON format

## Integration with Judge Command

The review command builds on the judge command, which analyzes claims in the document against the provided context. The review command adds:

1. Deterministic linting (acronyms, units, etc.)
2. Criteria-based analysis (sections, topics, patterns)
3. LLM-powered review

This provides a more comprehensive assessment of your document than the judge command alone.