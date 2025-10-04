<!-- AUTO-GENERATED FROM .ide/rules/06-secrets-env.md | Do not edit here. -->
<!-- Edit .ide/rules/*.md and run scripts/sync_ide_rules.py -->

# Secrets, Environment, and Keys

Loading policy
- python-dotenv is used to load .env automatically when CLI starts.
- Settings (pydantic) may supply values if available; environment variables take precedence.

Expected keys
- OPENAI_API_KEY
- COHERE_API_KEY (optional; enables reranking)
- LLAMA_CLOUD_API_KEY (optional; enables LlamaParse)
- ANTHROPIC_API_KEY (optional)
- GEMINI_API_KEY or GOOGLE_API_KEY (optional)
- XAI_API_KEY (optional)

Windows quick test
- PowerShell:
  $env:OPENAI_API_KEY="sk-..."
  python run_caliper_v2.py info
- Or put OPENAI_API_KEY=... into .env at project root and restart terminal.

Failure behavior (current)
- If no OpenAI key and embed provider not set to 'local', LlamaIndex may raise a clear error.
- If this occurs in wizard, accept the failure and show a prompt recommending:
  a) Set OPENAI_API_KEY and re-run
  b) Retry with --embed-provider local (offline smoke)
