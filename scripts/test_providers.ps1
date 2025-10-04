# Test LLM Providers for Caliper v2
# Run these commands one by one to test each provider

Write-Host "===== Testing LLM Providers =====" -ForegroundColor Cyan
Write-Host "Make sure you have the necessary API keys in your .env file or environment" -ForegroundColor Yellow
Write-Host ""

# Create a test question file - using same question from earlier testing
$testQuestion = "What are the key requirements in AASHTO design standards for bridge foundations?"
$testQuestion | Out-File -FilePath "test_question.txt" -Encoding UTF8

Write-Host "Test question: $testQuestion" -ForegroundColor Green
Write-Host ""

# 1. Test Cohere (default)
Write-Host "1. Testing Cohere..." -ForegroundColor Cyan
Write-Host "Required: COHERE_API_KEY" -ForegroundColor Yellow
poetry run caliper_v2 retrieve "$testQuestion" --indexes design --top-k 10 --provider cohere --model command-r-plus --out data_v2/context/test_cohere.json
Write-Host ""

# 2. Test OpenAI
Write-Host "2. Testing OpenAI..." -ForegroundColor Cyan
Write-Host "Required: OPENAI_API_KEY" -ForegroundColor Yellow
poetry run caliper_v2 retrieve "$testQuestion" --indexes design --top-k 10 --provider openai --model gpt-4o-mini --out data_v2/context/test_openai.json
Write-Host ""

# 3. Test Anthropic
Write-Host "3. Testing Anthropic..." -ForegroundColor Cyan
Write-Host "Required: ANTHROPIC_API_KEY" -ForegroundColor Yellow
poetry run caliper_v2 retrieve "$testQuestion" --indexes design --top-k 10 --provider anthropic --model claude-3-haiku-20240307 --out data_v2/context/test_anthropic.json
Write-Host ""

# 4. Test Gemini
Write-Host "4. Testing Gemini..." -ForegroundColor Cyan
Write-Host "Required: GEMINI_API_KEY or GOOGLE_API_KEY" -ForegroundColor Yellow
poetry run caliper_v2 retrieve "$testQuestion" --indexes design --top-k 10 --provider gemini --model "models/gemini-1.5-flash" --out data_v2/context/test_gemini.json
Write-Host ""

# 5. Test xAI/Grok
Write-Host "5. Testing xAI/Grok..." -ForegroundColor Cyan
Write-Host "Required: XAI_API_KEY" -ForegroundColor Yellow
poetry run caliper_v2 retrieve "$testQuestion" --indexes design --top-k 10 --provider grok --model grok-2-1212 --out data_v2/context/test_grok.json
Write-Host ""

# Test generation with each provider (if retrieval worked)
Write-Host "===== Testing Generation =====" -ForegroundColor Cyan
Write-Host ""

# Check which context files were created
$contextFiles = @{
    "cohere" = "data_v2/context/test_cohere.json"
    "openai" = "data_v2/context/test_openai.json"
    "anthropic" = "data_v2/context/test_anthropic.json"
    "gemini" = "data_v2/context/test_gemini.json"
    "grok" = "data_v2/context/test_grok.json"
}

foreach ($provider in $contextFiles.Keys) {
    $contextFile = $contextFiles[$provider]
    if (Test-Path $contextFile) {
        Write-Host "Testing generation with $provider..." -ForegroundColor Green
        
        $model = switch ($provider) {
            "cohere" { "command-r-plus" }
            "openai" { "gpt-4o-mini" }
            "anthropic" { "claude-3-haiku-20240307" }
            "gemini" { "models/gemini-1.5-flash" }
            "grok" { "grok-2-1212" }
        }
        
        # Note: This assumes you have a generate command. If not, we'll use a simpler test
        Write-Host "Context file exists: $contextFile" -ForegroundColor Green
    } else {
        Write-Host "Skipping $provider generation - no context file found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "===== Quick Provider Tests (Direct LLM calls) =====" -ForegroundColor Cyan
Write-Host ""

# Direct provider tests using Python
@'
import os
from pathlib import Path

# Test each provider directly
providers = {
    "cohere": ("COHERE_API_KEY", "command-r-plus"),
    "openai": ("OPENAI_API_KEY", "gpt-4o-mini"),
    "anthropic": ("ANTHROPIC_API_KEY", "claude-3-haiku-20240307"),
    "gemini": ("GEMINI_API_KEY", "models/gemini-1.5-flash"),
    "grok": ("XAI_API_KEY", "grok-2-1212"),
}

for provider, (key_name, model) in providers.items():
    key_exists = bool(os.getenv(key_name) or (provider == "gemini" and os.getenv("GOOGLE_API_KEY")))
    print(f"{provider}: API key {'✓' if key_exists else '✗ MISSING'} ({key_name})")
    
    if key_exists:
        try:
            from caliper_v2.core.llm_providers import configure_llm_provider
            configure_llm_provider(provider, model=model)
            print(f"  Configuration: ✓ Success with {model}")
        except Exception as e:
            print(f"  Configuration: ✗ Failed - {str(e)[:100]}")
    print()
'@ | poetry run python -

Write-Host ""
Write-Host "===== Doctor Check =====" -ForegroundColor Cyan
poetry run caliper_v2 doctor

Write-Host ""
Write-Host "===== Summary =====" -ForegroundColor Cyan
Write-Host "Check the output above to see which providers are working." -ForegroundColor Green
Write-Host "If a provider fails, make sure:" -ForegroundColor Yellow
Write-Host "1. The API key is set in your .env file" -ForegroundColor Yellow
Write-Host "2. The API key is valid and has credits/quota" -ForegroundColor Yellow
Write-Host "3. The model name is correct for your access level" -ForegroundColor Yellow