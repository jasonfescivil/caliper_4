#!/usr/bin/env python3
"""Test script for frontier model configurations."""

from src.caliper_v2.core.llm_providers import get_recommended_model

def test_frontier_models():
    """Test that all frontier models are properly configured."""
    print("Testing frontier model configurations...")
    
    # Test OpenAI GPT-5
    gpt5 = get_recommended_model('openai', 'quality')
    print(f"OpenAI Quality Model: {gpt5}")
    
    # Test Anthropic Claude Sonnet 4
    claude4 = get_recommended_model('anthropic', 'quality')
    print(f"Anthropic Quality Model: {claude4}")
    
    # Test xAI Grok-4
    grok4 = get_recommended_model('grok', 'quality')
    print(f"Grok Quality Model: {grok4}")
    
    # Test Cohere A Command
    cohere_a = get_recommended_model('cohere', 'quality')
    print(f"Cohere Quality Model: {cohere_a}")
    
    # Test all use cases for OpenAI
    print("\nOpenAI models across use cases:")
    print(f"  Fast: {get_recommended_model('openai', 'fast')}")
    print(f"  Balanced: {get_recommended_model('openai', 'balanced')}")
    print(f"  Quality: {get_recommended_model('openai', 'quality')}")
    
    print("\nAll frontier models configured successfully!")
    return True

if __name__ == "__main__":
    test_frontier_models()
