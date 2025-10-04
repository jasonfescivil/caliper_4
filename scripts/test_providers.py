#!/usr/bin/env python3
"""
Diagnostic script for testing LLM providers in Caliper v2.

This script systematically tests each provider (gemini, cohere, grok) to identify
the root cause of any failures. It explicitly reads API keys from environment
variables and provides detailed error reporting.
"""

import os
import sys
import traceback
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from caliper_v2.core.llm_providers import configure_llm_provider
    from llama_index.core import Settings
    # Try to load environment variables
    try:
        from caliper_v2.core.env import load_env
        load_env()
        print("DEBUG: Successfully loaded .env file")
    except ImportError:
        print("DEBUG: Could not import load_env, trying python-dotenv")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("DEBUG: Successfully loaded .env with python-dotenv")
        except ImportError:
            print("DEBUG: No .env loading mechanism available")
except ImportError as e:
    print(f"[ERROR] Failed to import Caliper modules: {e}")
    sys.exit(1)


def test_provider(provider: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Test a single provider configuration and basic functionality.

    Args:
        provider: Provider name (gemini, cohere, grok)
        model: Specific model to test (optional)

    Returns:
        Dict containing test results and any errors
    """
    result = {
        "provider": provider,
        "model": model,
        "api_key_found": False,
        "configuration_success": False,
        "ping_success": False,
        "error": None,
        "traceback": None,
        "llm_info": None
    }

    print(f"\nTesting provider: {provider}")
    if model:
        print(f"   Model: {model}")

    # Step 1: Check API key
    api_key = None
    if provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    elif provider == "cohere":
        api_key = os.getenv("COHERE_API_KEY")
    elif provider == "grok" or provider == "xai":
        api_key = os.getenv("XAI_API_KEY")
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        result["api_key_found"] = True
        print(f"   [OK] API key found for {provider}")
    else:
        result["api_key_found"] = False
        result["error"] = f"No API key found for {provider}"
        print(f"   [FAIL] No API key found for {provider}")
        return result

    # Step 2: Test configuration
    try:
        print(f"   Configuring {provider} provider...")
        configure_llm_provider(provider, model=model, api_key=api_key)

        if Settings.llm:
            result["configuration_success"] = True
            result["llm_info"] = str(Settings.llm)
            print(f"   [OK] Configuration successful: {Settings.llm}")
        else:
            result["configuration_success"] = False
            result["error"] = "LLM configuration succeeded but Settings.llm is None"
            print(f"   [FAIL] Configuration succeeded but Settings.llm is None")
            return result

    except Exception as e:
        result["configuration_success"] = False
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
        print(f"   [FAIL] Configuration failed: {e}")
        print(f"   Full traceback:\n{traceback.format_exc()}")
        return result

    # Step 3: Test basic functionality
    try:
        print(f"   Testing ping with {provider}...")
        response = Settings.llm.complete("ping")
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            if text:
                result["ping_success"] = True
                print(f"   [OK] Ping successful: '{text}'")
            else:
                result["ping_success"] = False
                result["error"] = "Ping returned empty response"
                print(f"   [WARN] Ping returned empty response")
        else:
            result["ping_success"] = False
            result["error"] = "Ping returned invalid response object"
            print(f"   [FAIL] Ping returned invalid response object: {response}")

    except Exception as e:
        result["ping_success"] = False
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
        print(f"   [FAIL] Ping failed: {e}")
        print(f"   Full traceback:\n{traceback.format_exc()}")

    return result


def main():
    """Main diagnostic function."""
    print("Caliper v2 Provider Diagnostic Tool")
    print("=" * 50)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Test LLM providers in Caliper")
    parser.add_argument("--provider", type=str, help="Test a specific provider (openai, gemini, cohere, grok, anthropic)")
    parser.add_argument("--model", type=str, help="Test with a specific model")
    parser.add_argument("--all", action="store_true", help="Test all providers with updated models")
    args = parser.parse_args()

    # Default providers to test with updated models
    default_providers = [
        ("openai", "gpt-5"),  # Use GPT-5 as requested
        ("gemini", "models/gemini-2.5-pro"),  # Use Gemini 2.5 Pro as requested
        ("cohere", "command-a-reasoning-08-2025"),  # Use Command-A as requested
        ("grok", "grok-4"),  # Use Grok-4 as requested
        ("anthropic", "claude-sonnet-4"),  # Use Claude Sonnet 4 as requested
    ]
    
    # Debug: Check if .env is being loaded
    print("DEBUG: Environment variables check:")
    for key in ["OPENAI_API_KEY", "GOOGLE_API_KEY", "COHERE_API_KEY", "XAI_API_KEY", "ANTHROPIC_API_KEY"]:
        value = os.getenv(key)
        if value:
            print(f"  {key}: {'*' * min(len(value), 10)}... (found)")
        else:
            print(f"  {key}: (not found)")
    print()

    results = []

    # Test specific provider if requested
    if args.provider:
        model = args.model
        if not model:
            # Use default model for the provider
            for p, m in default_providers:
                if p.lower() == args.provider.lower():
                    model = m
                    break
        result = test_provider(args.provider, model)
        results.append(result)
    # Test all providers
    elif args.all or not args.provider:
        for provider, model in default_providers:
            result = test_provider(provider, model)
            results.append(result)

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    for result in results:
        status = "PASS" if result["configuration_success"] and result["ping_success"] else "FAIL"
        provider_name = result['provider']
        print(f"{provider_name:<8} | {status}")

        if result["error"]:
            print(f"         Error: {result['error']}")

        if not result["api_key_found"]:
            print(f"         Missing API key: {result['provider'].upper()}_API_KEY")

    print("\n" + "=" * 50)
    print("TROUBLESHOOTING TIPS")
    print("=" * 50)
    print("1. Ensure all required API keys are set in your .env file")
    print("2. Check that model names are correct for each provider")
    print("3. Verify your internet connection for API calls")
    print("4. Check the full tracebacks above for specific error details")
    print("5. Try updating dependencies: poetry update")

    # Return success if all providers work
    all_success = all(r["configuration_success"] and r["ping_success"] for r in results)
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
