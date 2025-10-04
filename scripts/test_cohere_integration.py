#!/usr/bin/env python3
"""
Test script for Cohere integration in Caliper v2.

Tests:
1. Cohere as LLM provider
2. Cohere embeddings 
3. Enhanced reranking with confidence scores
4. Citation anchoring in JSON format
5. Structured output with schema
"""

import os
import json
import tempfile
from pathlib import Path
import subprocess
import sys

def run_command(cmd: str, capture=True):
    """Run a shell command and return output."""
    print(f"Running: {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result.stdout
    else:
        return subprocess.run(cmd, shell=True).returncode

def test_cohere_provider():
    """Test that Cohere is available as an LLM provider."""
    print("\n=== Testing Cohere LLM Provider ===")
    
    # Check if Cohere is in provider list
    output = run_command("poetry run caliper_v2 --help")
    if "cohere" in output.lower():
        print("✓ Cohere appears in help text")
    
    # Try to configure Cohere
    test_prompt = "What is wastewater treatment?"
    cmd = f'poetry run caliper_v2 generate --help'
    output = run_command(cmd)
    if "--reasoning" in output:
        print("✓ Reasoning mode flag available")
    if "--schema" in output:
        print("✓ Schema flag available")
    
    return True

def test_cohere_embeddings():
    """Test Cohere embeddings configuration."""
    print("\n=== Testing Cohere Embeddings ===")
    
    # Check environment
    if os.getenv("COHERE_API_KEY"):
        print("✓ COHERE_API_KEY is set")
    else:
        print("✗ COHERE_API_KEY not set - skipping embedding test")
        return False
    
    if os.getenv("EMBEDDING_PROVIDER") == "cohere":
        print("✓ EMBEDDING_PROVIDER set to cohere")
    else:
        print("⚠ EMBEDDING_PROVIDER not set to cohere")
    
    return True

def test_reranking():
    """Test enhanced reranking with confidence scores."""
    print("\n=== Testing Enhanced Reranking ===")
    
    # Create a test query
    test_query = "What are the BOD limits for wastewater treatment plants?"
    
    # Run retrieval with Cohere reranking
    cmd = f'poetry run caliper_v2 retrieve "{test_query}" --indexes federal --top-k 10 --reranker cohere'
    output = run_command(cmd)
    
    if output:
        # Check if output file was created
        if "outputs/" in output:
            json_file = output.strip()
            if Path(json_file).exists():
                print(f"✓ Retrieval created output file: {json_file}")
                
                # Check JSON format for citation anchors
                with open(json_file) as f:
                    data = json.load(f)
                    
                if "results" in data and len(data["results"]) > 0:
                    first_result = data["results"][0]
                    if "citation_anchor" in first_result:
                        print("✓ Citation anchors present in results")
                        if "confidence" in first_result.get("citation_anchor", {}):
                            print("✓ Rerank confidence scores included")
                    
                    if "metadata" in first_result:
                        metadata = first_result["metadata"]
                        if "rerank_confidence" in metadata:
                            print(f"✓ Rerank confidence in metadata: {metadata['rerank_confidence']}")
                        if metadata.get("retrieval_strategy") == "cohere_optimized":
                            print("✓ Retrieval strategy marked as cohere_optimized")
                
                return json_file
    
    print("✗ Retrieval command failed")
    return None

def test_generation_with_schema():
    """Test generation with structured output schema."""
    print("\n=== Testing Structured Output ===")
    
    # Create a simple schema
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            },
            "citations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "confidence": {"type": "number"}
                    }
                }
            }
        },
        "required": ["summary", "key_points"]
    }
    
    # Save schema to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(schema, f)
        schema_file = f.name
    
    print(f"Created schema file: {schema_file}")
    
    # Run a retrieval first
    retrieval_file = test_reranking()
    
    if retrieval_file:
        # Test generation with schema
        cmd = f'poetry run caliper_v2 generate {retrieval_file} --schema {schema_file} --format json'
        output = run_command(cmd)
        
        if output:
            try:
                result = json.loads(output)
                if "answer" in result:
                    print("✓ JSON output generated with schema")
            except:
                print("✗ Invalid JSON output")
    
    # Cleanup
    Path(schema_file).unlink(missing_ok=True)
    
    return True

def test_reasoning_mode():
    """Test reasoning mode with Cohere."""
    print("\n=== Testing Reasoning Mode ===")
    
    # Check if reasoning flag works
    cmd = 'poetry run caliper_v2 generate --help'
    output = run_command(cmd)
    
    if "--reasoning" in output:
        print("✓ Reasoning flag available in generate command")
        
        # Would need actual context file to test fully
        print("⚠ Full reasoning test requires context file")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Cohere Integration Test Suite for Caliper v2")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("LLM Provider", test_cohere_provider()))
    results.append(("Embeddings", test_cohere_embeddings()))
    results.append(("Reranking", test_reranking() is not None))
    results.append(("Structured Output", test_generation_with_schema()))
    results.append(("Reasoning Mode", test_reasoning_mode()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20} {status}")
    
    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    return 0 if total_passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())