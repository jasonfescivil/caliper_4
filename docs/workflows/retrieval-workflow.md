# Caliper v2 Retrieval Workflow

This document outlines the complete retrieval workflow in Caliper v2, from initial question to final output.

## Overview

The Caliper v2 workflow consists of five main stages:

1. **Retrieve**: Get relevant information from indexes
2. **Enhance**: Improve the retrieved context
3. **Generate**: Create a response based on the context
4. **Judge**: Evaluate the generated content
5. **Review**: Analyze and improve the final output

## Detailed Workflow

### 1. Retrieve

The first step is to retrieve relevant information from indexes based on a question or prompt.

#### Using Cloud Retrieval

```powershell
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state,design_standards" --cloud --dense-k 12 --sparse-k 12 --alpha 0.5 --rerank-top-n 12 --out data_v2/context/g1_cloud.json
```

This command:
- Searches for information about G1 requirements for engineering reports
- Uses three indexes: federal, state, and design_standards
- Retrieves using a hybrid approach (dense and sparse retrieval)
- Reranks the top 12 results
- Saves the retrieval session to a JSON file

#### Using a Question File

For more complex questions, you can use a Markdown file:

```powershell
poetry run caliper_v2 retrieve --question-file prompts/my_query.md --indexes "federal,state,design_standards" --cloud --top-k 30 --out data_v2/context/my_query_results.json
```

Or use the shorthand:

```powershell
poetry run caliper_v2 retrieve @prompts/my_query.md --indexes federal --out data_v2/context/my_query_results.json
```

### 2. Enhance

After retrieving information, you can enhance the context to improve the quality of the generated response.

```powershell
poetry run caliper_v2 enhance --in data_v2/context/my_query_results.json --out data_v2/context/my_query_enhanced.json --write-outline --rewrite-spore --review-spores --suggest-retrieve
```

This command:
- Takes the retrieval session JSON as input
- Adds an outline of the retrieved information
- Rewrites the global "spore" (summary of why the retrieval set is coherent and relevant)
- Reviews and rewrites per-node spores
- Suggests follow-up retrievals for missing information
- Saves the enhanced context to a new JSON file

### 3. Generate

Next, generate a response based on the enhanced context:

```powershell
poetry run caliper_v2 generate data_v2/context/my_query_enhanced.json --style strict-citation --out data_v2/outputs/my_query_draft.md
```

This command:
- Uses the enhanced context as input
- Generates a response with strict citation style
- Saves the generated content to a Markdown file

### 4. Judge

After generating the response, you can judge its quality:

```powershell
poetry run caliper_v2 judge --context data_v2/context/my_query_enhanced.json --generation data_v2/outputs/my_query_draft.md --out data_v2/judgments/my_query_judgment.json --strict
```

This command:
- Assesses the generated draft against the retrieved context
- Uses strict criteria for evaluating support
- Emits a claim-level judgment report with evidence snippets
- Saves the judgment report to a JSON file

### 5. Review

Finally, review the generated content and judgment:

```powershell
poetry run caliper_v2 review --context data_v2/context/my_query_enhanced.json --draft data_v2/outputs/my_query_draft.md --out-json data_v2/reviews/my_query_review.json --out-md data_v2/reviews/my_query_review.md --strict --max-evidence-per-claim 5
```

This command:
- Runs a lightweight review on the draft
- Combines judge metrics and deterministic text lints
- Generates both JSON and Markdown reports
- Uses strict criteria and caps evidence at 5 snippets per claim

## Complete Example

Here's a complete example workflow for answering a question about G1 requirements:

```powershell
# 1. Retrieve
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --indexes "federal,state,design_standards" --cloud --dense-k 12 --sparse-k 12 --alpha 0.5 --rerank-top-n 12 --out data_v2/context/g1_cloud.json

# 2. Enhance
poetry run caliper_v2 enhance --in data_v2/context/g1_cloud.json --out data_v2/context/g1_enhanced.json --write-outline --rewrite-spore --review-spores --suggest-retrieve

# 3. Generate
poetry run caliper_v2 generate data_v2/context/g1_enhanced.json --style strict-citation --out data_v2/outputs/g1_draft.md

# 4. Judge
poetry run caliper_v2 judge --context data_v2/context/g1_enhanced.json --generation data_v2/outputs/g1_draft.md --out data_v2/judgments/g1_judgment.json --strict

# 5. Review
poetry run caliper_v2 review --context data_v2/context/g1_enhanced.json --draft data_v2/outputs/g1_draft.md --out-json data_v2/reviews/g1_review.json --out-md data_v2/reviews/g1_review.md --strict --max-evidence-per-claim 5
```

## Output Files

The workflow generates several output files:

- **Retrieval Session**: `data_v2/context/g1_cloud.json`
- **Enhanced Context**: `data_v2/context/g1_enhanced.json`
- **Generated Draft**: `data_v2/outputs/g1_draft.md`
- **Judgment Report**: `data_v2/judgments/g1_judgment.json`
- **Review Report (JSON)**: `data_v2/reviews/g1_review.json`
- **Review Report (Markdown)**: `data_v2/reviews/g1_review.md`

These files provide a complete record of the workflow and can be used for further analysis or refinement.