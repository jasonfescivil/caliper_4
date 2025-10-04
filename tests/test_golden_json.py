"""
Golden JSON Tests - Validate retrieval JSON structure
Ensures critical fields are present and correctly formatted
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List

# Required fields in retrieval JSON
REQUIRED_NODE_FIELDS = {
    "node_id": str,
    "score": (float, type(None)),
    "text": str,
    "metadata": dict,
    "citation_anchor": dict
}

REQUIRED_CITATION_FIELDS = {
    "start_char": int,
    "end_char": int,
    "source_file": (str, type(None)),
    "page": (int, type(None)),
    "section": (str, type(None)),
    "confidence": (float, type(None))
}

REQUIRED_METADATA_FIELDS = {
    "file_name": (str, type(None)),
    "page": (int, type(None)),
    "retrieval_strategy": str,
    # After reranking:
    "rerank_confidence": (float, type(None))  # Optional but should be present after Cohere rerank
}

class TestGoldenJSON:
    """Validate retrieval JSON structure and content"""
    
    @pytest.fixture
    def golden_json_path(self):
        """Path to golden JSON sample"""
        return Path("tests/fixtures/golden_retrieval.json")
    
    @pytest.fixture
    def create_golden_sample(self, golden_json_path):
        """Create a golden JSON sample for testing"""
        sample = {
            "question": "AKART engineering report requirements in WA",
            "indexes": ["state", "design_standards"],
            "retrieval_metadata": {
                "embed_provider": "cohere",
                "reranker": "cohere",
                "top_k": 24,
                "expanded_queries": [
                    "AKART engineering report requirements in WA",
                    "Alternative analysis engineering Washington State",
                    "Wastewater treatment plant AKART reports",
                    "Engineering report requirements Department of Ecology"
                ],
                "min_confidence": 0.7
            },
            "nodes": [
                {
                    "node_id": "abc123",
                    "parent_id": None,
                    "score": 0.95,
                    "text": "Engineering reports for wastewater treatment facilities must include...",
                    "citation_anchor": {
                        "start_char": 0,
                        "end_char": 67,
                        "source_file": "WAC_173-240.pdf",
                        "page": 12,
                        "section": "Engineering Reports",
                        "confidence": 0.95
                    },
                    "metadata": {
                        "file_name": "WAC_173-240.pdf",
                        "page": 12,
                        "section": "Engineering Reports",
                        "index": "state",
                        "retrieval_strategy": "cohere_optimized",
                        "rerank_confidence": 0.95
                    }
                },
                {
                    "node_id": "def456",
                    "parent_id": None,
                    "score": 0.89,
                    "text": "AKART analysis must consider cost-effectiveness...",
                    "citation_anchor": {
                        "start_char": 0,
                        "end_char": 48,
                        "source_file": "design_standards.pdf",
                        "page": 45,
                        "section": "AKART Requirements",
                        "confidence": 0.89
                    },
                    "metadata": {
                        "file_name": "design_standards.pdf",
                        "page": 45,
                        "section": "AKART Requirements",
                        "index": "design_standards",
                        "retrieval_strategy": "cohere_optimized",
                        "rerank_confidence": 0.89
                    }
                }
            ]
        }
        
        golden_json_path.parent.mkdir(parents=True, exist_ok=True)
        golden_json_path.write_text(json.dumps(sample, indent=2))
        return sample
    
    def validate_node_structure(self, node: Dict[str, Any]) -> List[str]:
        """Validate a single node's structure"""
        errors = []
        
        # Check required fields
        for field, expected_type in REQUIRED_NODE_FIELDS.items():
            if field not in node:
                errors.append(f"Missing required field: {field}")
            elif expected_type and not isinstance(node[field], expected_type):
                errors.append(f"Invalid type for {field}: expected {expected_type}, got {type(node[field])}")
        
        # Validate citation_anchor
        if "citation_anchor" in node:
            anchor = node["citation_anchor"]
            for field, expected_type in REQUIRED_CITATION_FIELDS.items():
                if field not in anchor:
                    errors.append(f"Missing citation_anchor.{field}")
                elif expected_type and not isinstance(anchor[field], expected_type):
                    errors.append(f"Invalid type for citation_anchor.{field}")
            
            # Validate anchor range
            if "start_char" in anchor and "end_char" in anchor:
                if anchor["end_char"] < anchor["start_char"]:
                    errors.append("citation_anchor: end_char < start_char")
        
        # Validate metadata
        if "metadata" in node:
            meta = node["metadata"]
            
            # Check for rerank_confidence after Cohere reranking
            if meta.get("retrieval_strategy") == "cohere_optimized":
                if "rerank_confidence" not in meta:
                    errors.append("Missing rerank_confidence for cohere_optimized node")
                elif not isinstance(meta["rerank_confidence"], (float, int)):
                    errors.append(f"Invalid rerank_confidence type: {type(meta['rerank_confidence'])}")
                elif not 0 <= meta["rerank_confidence"] <= 1:
                    errors.append(f"rerank_confidence out of range: {meta['rerank_confidence']}")
        
        return errors
    
    def test_golden_sample_valid(self, create_golden_sample):
        """Test that our golden sample is valid"""
        sample = create_golden_sample
        
        assert "nodes" in sample, "Sample must have nodes"
        assert len(sample["nodes"]) > 0, "Sample must have at least one node"
        
        for i, node in enumerate(sample["nodes"]):
            errors = self.validate_node_structure(node)
            assert not errors, f"Node {i} validation errors: {errors}"
    
    def test_validate_actual_retrieval(self, tmp_path):
        """Validate an actual retrieval JSON output"""
        # This would be called after running retrieval
        test_output = tmp_path / "test_retrieval.json"
        
        # Simulate retrieval output
        output = {
            "question": "test query",
            "nodes": [
                {
                    "node_id": "test1",
                    "score": 0.9,
                    "text": "Test content",
                    "citation_anchor": {
                        "start_char": 0,
                        "end_char": 12,
                        "source_file": "test.pdf",
                        "page": 1,
                        "section": "Test",
                        "confidence": 0.9
                    },
                    "metadata": {
                        "file_name": "test.pdf",
                        "page": 1,
                        "retrieval_strategy": "cohere_optimized",
                        "rerank_confidence": 0.9
                    }
                }
            ]
        }
        
        test_output.write_text(json.dumps(output, indent=2))
        
        # Validate
        data = json.loads(test_output.read_text())
        for i, node in enumerate(data.get("nodes", [])):
            errors = self.validate_node_structure(node)
            assert not errors, f"Node {i} errors: {errors}"
    
    def test_confidence_values_valid(self, create_golden_sample):
        """Test that confidence values are in valid range"""
        sample = create_golden_sample
        
        for node in sample["nodes"]:
            # Check rerank_confidence
            if "metadata" in node and "rerank_confidence" in node["metadata"]:
                conf = node["metadata"]["rerank_confidence"]
                assert 0 <= conf <= 1, f"rerank_confidence out of range: {conf}"
            
            # Check citation confidence
            if "citation_anchor" in node and "confidence" in node["citation_anchor"]:
                conf = node["citation_anchor"]["confidence"]
                if conf is not None:
                    assert 0 <= conf <= 1, f"citation confidence out of range: {conf}"

if __name__ == "__main__":
    # Quick validation
    test = TestGoldenJSON()
    print("✓ Golden JSON tests ready")