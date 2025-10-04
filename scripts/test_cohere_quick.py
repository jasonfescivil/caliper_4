#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Test 1: Check environment
print("=== Environment Check ===")
print(f"COHERE_API_KEY: {'SET' if os.getenv('COHERE_API_KEY') else 'NOT SET'}")
print(f"EMBEDDING_PROVIDER: {os.getenv('EMBEDDING_PROVIDER', 'not set')}")
print(f"COHERE_MODEL: {os.getenv('COHERE_MODEL', 'not set')}")

# Test 2: Configure Cohere LLM
print("\n=== Cohere LLM Configuration ===")
try:
    from src.caliper_v2.core.llm_providers import configure_llm_provider
    configure_llm_provider('cohere')
    print("[OK] Cohere LLM configured")
    
    from llama_index.core import Settings
    if Settings.llm:
        print(f"[OK] LLM class: {Settings.llm.__class__.__name__}")
        print(f"[OK] Model: {getattr(Settings.llm, 'model', 'unknown')}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 3: Configure Cohere Embeddings
print("\n=== Cohere Embeddings Configuration ===")
try:
    from src.caliper_v2.core.llm_providers import configure_embedding_provider
    configure_embedding_provider('cohere')
    print("[OK] Cohere embeddings configured")
    
    if Settings.embed_model:
        print(f"[OK] Embed model class: {Settings.embed_model.__class__.__name__}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 4: Check CLI integration
print("\n=== CLI Integration ===")
import subprocess
result = subprocess.run(
    ["poetry", "run", "caliper_v2", "--help"],
    capture_output=True,
    text=True
)

if "cohere" in result.stdout.lower():
    print("[OK] 'cohere' found in CLI help")
else:
    print("[FAIL] 'cohere' not found in CLI help")

# Check generate command
result = subprocess.run(
    ["poetry", "run", "caliper_v2", "generate", "--help"],
    capture_output=True,
    text=True
)

if "--schema" in result.stdout:
    print("[OK] --schema flag available")
if "--reasoning" in result.stdout:
    print("[OK] --reasoning flag available")

print("\n=== Test Complete ===")