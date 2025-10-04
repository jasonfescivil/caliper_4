"""Pytest configuration and fixtures for Dash UI tests."""
import pytest
from pathlib import Path
import json


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables with test API keys."""
    monkeypatch.setenv("COHERE_API_KEY", "test_cohere_key_12345")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key_12345")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key_12345")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key_12345")
    monkeypatch.setenv("XAI_API_KEY", "test_xai_key_12345")
    monkeypatch.setenv("LLAMA_CLOUD_API_KEY", "test_llama_cloud_key_12345")
    monkeypatch.setenv("FEDERAL_BASE_ID", "test-federal-base-id")
    monkeypatch.setenv("FEDERAL_SUMMARY_ID", "test-federal-summary-id")
    monkeypatch.setenv("STATE_BASE_ID", "test-state-base-id")
    monkeypatch.setenv("STATE_SUMMARY_ID", "test-state-summary-id")
    monkeypatch.setenv("DESIGN_BASE_ID", "test-design-base-id")
    monkeypatch.setenv("DESIGN_SUMMARY_ID", "test-design-summary-id")


@pytest.fixture
def sample_retrieval_result(tmp_path):
    """Create a sample retrieval result JSON."""
    result = {
        "type": "retrieval_session",
        "question": "Test question about design standards",
        "indexes": ["design"],
        "retrieval": {
            "nodes": [
                {
                    "text": "Sample node text with design guidance",
                    "score": 0.95,
                    "metadata": {
                        "file_name": "test_design_doc.pdf",
                        "page": 1,
                        "section": "Introduction"
                    }
                },
                {
                    "text": "Another relevant node about standards",
                    "score": 0.89,
                    "metadata": {
                        "file_name": "test_standards.pdf",
                        "page": 5,
                        "section": "Design Requirements"
                    }
                }
            ],
            "spore": {
                "summary": "Retrieved nodes about design standards",
                "confidence": 0.85,
                "rationale_bullets": [
                    "Found relevant design guidance",
                    "Multiple sources cited"
                ]
            }
        },
        "timestamp": "2025-09-30T20:00:00Z"
    }
    output_path = tmp_path / "sample_retrieval.json"
    output_path.write_text(json.dumps(result, indent=2))
    return output_path
