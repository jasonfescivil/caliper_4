# Test Regulatory Crosswalk Prompt with Different Providers
# This uses the prompt from "prompts\02 Regulatory Crosswalk.md"

$prompt = "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations."

Write-Host "===== Testing Regulatory Crosswalk with All Providers =====" -ForegroundColor Cyan
Write-Host "Prompt: $prompt" -ForegroundColor Yellow
Write-Host ""

# Test with federal, state, and design indexes
$indexes = "federal,state,design"

# 1. COHERE - Original/Default
Write-Host "1. Testing with Cohere (command-r)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider cohere --model command-r `
  --out data_v2/context/crosswalk_cohere.json

Write-Host ""

# 2. COHERE - Premium model
Write-Host "2. Testing with Cohere (command-r-plus)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider cohere --model command-r-plus `
  --out data_v2/context/crosswalk_cohere_plus.json

Write-Host ""

# 3. OPENAI GPT-4o
Write-Host "3. Testing with OpenAI (gpt-4o)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider openai --model gpt-4o `
  --out data_v2/context/crosswalk_openai_4o.json

Write-Host ""

# 4. OPENAI GPT-4o-mini
Write-Host "4. Testing with OpenAI (gpt-4o-mini)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider openai --model gpt-4o-mini `
  --out data_v2/context/crosswalk_openai_mini.json

Write-Host ""

# 5. ANTHROPIC Claude 3.5 Sonnet
Write-Host "5. Testing with Anthropic (claude-3-5-sonnet)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider anthropic --model claude-3-5-sonnet-20241022 `
  --out data_v2/context/crosswalk_anthropic_sonnet.json

Write-Host ""

# 6. ANTHROPIC Claude 3 Haiku
Write-Host "6. Testing with Anthropic (claude-3-haiku)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider anthropic --model claude-3-haiku-20240307 `
  --out data_v2/context/crosswalk_anthropic_haiku.json

Write-Host ""

# 7. GEMINI 1.5 Pro
Write-Host "7. Testing with Gemini (1.5-pro)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider gemini --model "models/gemini-1.5-pro" `
  --out data_v2/context/crosswalk_gemini_pro.json

Write-Host ""

# 8. GEMINI 1.5 Flash
Write-Host "8. Testing with Gemini (1.5-flash)..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider gemini --model "models/gemini-1.5-flash" `
  --out data_v2/context/crosswalk_gemini_flash.json

Write-Host ""

# 9. xAI GROK
Write-Host "9. Testing with xAI/Grok..." -ForegroundColor Cyan
poetry run caliper_v2 retrieve "$prompt" `
  --indexes $indexes `
  --top-k 60 --rerank-top-n 24 `
  --provider grok --model grok-2-1212 `
  --out data_v2/context/crosswalk_grok.json

Write-Host ""

# List created files
Write-Host "===== Checking Output Files =====" -ForegroundColor Cyan
Get-ChildItem "data_v2/context/crosswalk_*.json" | ForEach-Object {
    Write-Host "✓ Created: $($_.Name) ($('{0:N0}' -f ($_.Length / 1KB)) KB)" -ForegroundColor Green
}

Write-Host ""
Write-Host "===== Generation Commands (if retrieval succeeded) =====" -ForegroundColor Yellow
Write-Host "To generate from these contexts, use:" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Example with Cohere context:"
Write-Host 'poetry run caliper_v2 generate data_v2/context/crosswalk_cohere.json --style strict-citation --format md --provider openai --model gpt-4o-mini --out outputs/crosswalk_cohere_gen.md'
Write-Host ""
Write-Host "# Example with OpenAI context:"
Write-Host 'poetry run caliper_v2 generate data_v2/context/crosswalk_openai_mini.json --style strict-citation --format md --provider cohere --model command-r --out outputs/crosswalk_openai_gen.md'