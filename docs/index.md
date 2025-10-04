# Caliper v2 Documentation

This is the central index for all Caliper v2 documentation.

## Documentation Structure

- **User Documentation**: Installation, setup, and usage guides for end users
  - [Installation Guide](user/installation-guide.md)
  - [Quick Start Guide](user/quick-start-guide.md)
  - [Operations Checklist](user/operations-checklist.md)
  - [Dash UI Guide](user/dash-ui-guide.md)
  - [WSL Quickstart Guide](user/wsl-quickstart-guide.md)

- **Developer Documentation**: Architecture, contributing guidelines, and development workflows
  - [Architecture Overview](developer/architecture-overview.md)
  - [AI Assistant Guidelines](developer/ai-assistant-guidelines.md)
  - [Development Onboarding Guide](developer/development-onboarding-guide.md)
  - [Contributing (Lite)](developer/contributing-lite.md)
  - [Dash UI Development](developer/dash-ui-development.md)
  - [Documentation Maintenance](developer/documentation-maintenance.md)
  - [Execution Plan](developer/execution_plan.md)
  - [UI Parity Flags](developer/ui_parity_flags.md)
  - [WARP Integration Guide](developer/warp-integration-guide.md)

- **Reference Documentation**: Detailed reference material
  - [Command Reference](reference/command-reference.md)
  - [Quick Reference](reference/quick-reference.md)

- **Workflow Examples**: Example workflows and use cases
  - [Retrieval Workflow](workflows/retrieval-workflow.md)
  - [GraphRAG Workflow](workflows/graphrag-workflow.md)
  - [Tekoa Facility Plan Workflow](workflows/tekoa_facility_plan_ch1-3_workflow.md)

- **Reviews and Assessments**: Code reviews, project assessments, and planning documents
  - [Code Review (2025-09-23)](reviews/code-review-2025-09-23.md)
  - [Best of Caliper Plan](reviews/best_of_caliper_plan.md)
  - [Best of Caliper Plan Assessment](reviews/best_of_caliper_plan_assessment.md)
  - [Best of Checklist](reviews/best_of_checklist.md)
  - [Caliper LlamaIndex Structure](reviews/caliper-llamaindex-structure.md)
  - [Caliper v2 Enhancement Roadmap](reviews/caliper-v2-enhancement-roadmap.md)
  - [Caliper v2 New Features](reviews/caliper-v2-new-features.md)

## Key Documentation Files

- [README.md](../README.md): Quick start guide and project overview
- [CONTRIBUTING.md](../CONTRIBUTING.md): How to contribute to the project
- [Operations Checklist](user/operations-checklist.md): Day-to-day operations guide

## Technical Documentation

- [Technical Implementation Details](technical/)
- [Security and Secret Scanning](../SECURITY.md)

## Project Overview

Caliper v2 is a command-line tool for information retrieval built with Python. It utilizes the Typer framework for its CLI and focuses on retrieving information from various sources, with a strong emphasis on a hybrid cloud retrieval system powered by LlamaCloud and LlamaIndex.

The tool allows users to ask natural language questions and retrieve relevant information from specified indexes. It supports advanced features like reranking, filtering, and query expansion. The retrieved information can then be used to generate a synthesized response.

### Key Technologies

- **Python:** The primary programming language
- **Typer:** Used for creating the command-line interface
- **Poetry:** For dependency management
- **LlamaIndex:** A data framework for building LLM applications
- **LlamaCloud:** A managed service for indexing and retrieval
- **Cohere:** Used for reranking search results
- **Google Generative AI:** Integrated as a potential backend
- **Pydantic:** For data validation and settings management
- **Loguru:** For logging

### Workflow

1. **Retrieve**: Get relevant information from indexes
2. **Enhance**: Improve the retrieved context
3. **Generate**: Create a response based on the context
4. **Judge**: Evaluate the generated content
5. **Review**: Analyze and improve the final output
