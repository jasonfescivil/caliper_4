# Caliper v2 Architecture Overview

## Project Overview

Caliper v2 is a command-line tool for information retrieval built with Python and the Typer framework. The core functionality revolves around retrieving information from various sources, with a strong emphasis on a hybrid cloud retrieval system powered by LlamaCloud and LlamaIndex.

The tool allows users to ask natural language questions and retrieve relevant information from specified indexes. It supports advanced features like reranking, filtering, and query expansion. The retrieved information can then be used to generate a synthesized response.

## Key Technologies

- **Python:** The primary programming language
- **Typer:** Used for creating the command-line interface
- **Poetry:** For dependency management
- **LlamaIndex:** A data framework for building LLM applications
- **LlamaCloud:** A managed service for indexing and retrieval
- **Cohere:** Used for reranking search results
- **Google Generative AI:** Integrated as a potential backend
- **Pydantic:** For data validation and settings management
- **Loguru:** For logging

## Architecture

The project is structured as a Python package with a clear separation of concerns:

### Core Components

- **`src/caliper_v2/cli.py`:** The main entry point of the application, defining the CLI commands and their logic
- **`src/caliper_v2/core/`:** Contains core functionality like configuration management (`config.py`) and environment variable loading (`env.py`)
- **`src/caliper_v2/retrievers/`:** Handles the logic for retrieving information from different sources, with a specific implementation for LlamaCloud (`llama_cloud_retriever.py`)
- **`src/caliper_v2/commands/`:** Contains subcommands for different functionalities
- **`src/caliper_v2/graph/`:** Implements GraphRAG functionality
- **`src/caliper_v2/services/`:** Provides service integrations
- **`src/caliper_v2/ui_dash/`:** Contains the Dash UI implementation
- **`pyproject.toml`:** Defines the project's dependencies and scripts
- **`.env`:** Used for storing API keys and other secrets

### Workflow Components

1. **Retrieve**: Get relevant information from indexes
   - Cloud text retrieval via LlamaCloud
   - Local GraphRAG over a persisted KnowledgeGraphIndex
   - Hybrid retrieval combining both approaches

2. **Enhance**: Improve the retrieved context
   - Add outline, diagnostics, and follow-up suggestions
   - Rewrite global spore and per-node spores

3. **Generate**: Create a response based on the context
   - Consume retrieval_session or enhanced_retrieval JSON
   - Support different generation styles

4. **Judge**: Evaluate the generated content
   - Claim-level adjudication with evidence
   - Configurable caps, embedding strategy, strictness

5. **Review**: Analyze and improve the final output
   - Combine judge metrics and deterministic text lints
   - Generate readable Markdown report

## GraphRAG Implementation

The GraphRAG functionality is implemented as a set of subcommands:

- **graph build**: Ingest Markdown, CSV, and XLSX from a corpus directory
- **graph retrieve**: Load the persisted graph and find candidate entities from query
- **export-cloud**: Export documents from LlamaCloud to a local Markdown corpus
- **build-cloud**: Build a KG from exported cloud documents

## UI Implementation

- **Dash UI**: Primary user interface built with Dash/Plotly (src/caliper_v2/ui_dash/app.py), providing tabbed workflows for retrieval, enhancement, generation, and review.

## Development Conventions

- **Dependency Management:** The project uses Poetry to manage dependencies
- **CLI:** The command-line interface is built using the Typer library
- **Configuration:** Configuration is managed through a combination of a `.env` file and Pydantic settings
- **Logging:** The Loguru library is used for logging
- **Code Style:** The code follows standard Python conventions (PEP 8)
