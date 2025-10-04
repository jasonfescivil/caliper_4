# Caliper v2 GraphRAG Workflow

This document outlines the GraphRAG workflow in Caliper v2, which allows you to build and query a knowledge graph from local documents.

## Overview

The GraphRAG workflow consists of these main stages:

1. **Build**: Create a knowledge graph from a corpus of documents
2. **Retrieve**: Query the graph to get relevant information
3. **Mix (Optional)**: Combine graph results with cloud text retrieval
4. **Generate**: Create a response based on the retrieved context
5. **Judge/Review**: Evaluate and improve the generated content

## Detailed Workflow

### 1. Build a Knowledge Graph

The first step is to build a knowledge graph from a corpus of documents (Markdown, CSV, XLSX).

```powershell
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph
```

This command:
- Ingests all supported files from the `knowledge_base` directory
- Extracts entities and relationships
- Builds a knowledge graph
- Persists the graph to the `data_v2/graph` directory

#### Advanced Build Options

For more control over the build process:

```powershell
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph --table-max-rows 200 --excel-all-sheets
```

This adds:
- `--table-max-rows 200`: Increases the number of rows included in tabular previews
- `--excel-all-sheets`: Ingests all sheets from Excel files (not just the first sheet)

### 2. Retrieve from the Graph

Once the graph is built, you can retrieve information by querying it:

```powershell
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --out data_v2/context/graph_ctx.json
```

This command:
- Queries the graph for information about G1 requirements
- Finds relevant entities and their relationships
- Expands to neighboring nodes
- Hydrates the graph nodes back to text
- Saves the retrieval session to a JSON file

### 3. Mix with Cloud Text Retrieval (Optional)

For more comprehensive results, you can mix graph retrieval with cloud text retrieval:

```powershell
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --mix-with-text --text-indexes design --top-k 40 --rerank-top-n 20 --out data_v2/context/graphmix_ctx.json
```

This command:
- Retrieves information from the graph
- Also retrieves information from the cloud text index "design"
- Combines the results
- Reranks the top 20 results
- Saves the mixed retrieval session to a JSON file

### 4. Generate from the Context

Next, generate a response based on the retrieved context:

```powershell
poetry run caliper_v2 generate data_v2/context/graphmix_ctx.json --style strict-citation --out data_v2/outputs/graphmix_draft.md
```

This command:
- Uses the mixed retrieval context as input
- Generates a response with strict citation style
- Saves the generated content to a Markdown file

### 5. Judge and Review

Finally, judge and review the generated content:

```powershell
# Judge
poetry run caliper_v2 judge --context data_v2/context/graphmix_ctx.json --generation data_v2/outputs/graphmix_draft.md --out data_v2/judgments/graphmix_judgment.json --strict

# Review
poetry run caliper_v2 review --context data_v2/context/graphmix_ctx.json --draft data_v2/outputs/graphmix_draft.md --out-json data_v2/reviews/graphmix_review.json --out-md data_v2/reviews/graphmix_review.md --strict
```

These commands assess the quality of the generated content and provide feedback for improvement.

## Complete Example

Here's a complete example workflow for building and querying a knowledge graph:

```powershell
# 1. Build the graph
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph --table-max-rows 200 --excel-all-sheets

# 2. Retrieve from the graph with cloud mixing
poetry run caliper_v2 graph retrieve "What are the G1 requirements for engineering reports?" --graph-dir data_v2/graph --mix-with-text --text-indexes design --top-k 40 --rerank-top-n 20 --out data_v2/context/graphmix_ctx.json

# 3. Generate
poetry run caliper_v2 generate data_v2/context/graphmix_ctx.json --style strict-citation --out data_v2/outputs/graphmix_draft.md

# 4. Judge
poetry run caliper_v2 judge --context data_v2/context/graphmix_ctx.json --generation data_v2/outputs/graphmix_draft.md --out data_v2/judgments/graphmix_judgment.json --strict

# 5. Review
poetry run caliper_v2 review --context data_v2/context/graphmix_ctx.json --draft data_v2/outputs/graphmix_draft.md --out-json data_v2/reviews/graphmix_review.json --out-md data_v2/reviews/graphmix_review.md --strict
```

## Additional Graph Commands

### Export Documents from LlamaCloud

You can export documents from LlamaCloud to a local Markdown corpus:

```powershell
poetry run caliper_v2 graph export-cloud --index federal --out-dir data_v2/exported/federal
```

### Build a Graph from Exported Cloud Documents

You can build a graph from the exported documents:

```powershell
poetry run caliper_v2 graph build-cloud --export-dir data_v2/exported/federal --out data_v2/graph/federal
```

### View Graph Statistics

You can view statistics about the graph:

```powershell
poetry run caliper_v2 graph stats --graph-dir data_v2/graph
```

## Graph Structure

The graph consists of:

- **Entity Nodes**: Represent key concepts extracted from the documents
- **Section Nodes**: Represent sections of the documents
- **Edges**: Represent relationships between nodes (MENTIONS, DEFINED_IN, etc.)

The graph is persisted as:
- `manifest.json`: Contains metadata about the graph
- `docstore/`: Contains the document store
- `graph_store/`: Contains the graph store
- `hash_cache.json`: Contains file hashes for incremental builds