# Regulatory Crosswalk Test Commands
## Testing the prompt from "prompts\02 Regulatory Crosswalk.md"

### The Prompt
```
Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations.
```

## Individual Provider Commands

### 1. Cohere (Default/Recommended)

#### Command-R (Standard)
```powershell
poetry run caliper_v2 --llm-provider cohere --llm-model command-r retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_r_cohere.json
```

#### Command-R-Plus (Premium)
```powershell
poetry run caliper_v2 --llm-provider cohere --llm-model command-r-plus retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_cohere_rplus.json
```


#### Command-a(Standard)
```powershell
poetry run caliper_v2 --llm-provider cohere --llm-model command-a-03-2025 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_r_cohere.json
```

#### Command-a-reasoning (Premium)
```powershell
poetry run caliper_v2 --llm-provider cohere --llm-model command-a-reasoning-08-2025 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_cohere_rplus.json
```


### 2. OpenAI

#### GPT-4.1 (Best not gpt-5)
```powershell
poetry run caliper_v2 --llm-provider openai --llm-model gpt-4.1-2025-04-14 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_openai_41.json
```

#### GPT-4o-mini (Cost-effective)
```powershell
poetry run caliper_v2 --llm-provider openai --llm-model gpt-4o-mini retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_openai_mini.json
```

### 3. Anthropic

#### Claude 4.1 Opus 
```powershell
poetry run caliper_v2 --llm-provider anthropic --llm-model claude-opus-4-1-20250805 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_anthropic_opus.json
```

#### Claude 4 Sonnet
```powershell
poetry run caliper_v2 --llm-provider anthropic --llm-model claude-sonnet-4-20250514 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_anthropic_haiku.json
```

### 4. Google Gemini

#### Gemini 2.5 Pro
```powershell
poetry run caliper_v2 --llm-provider gemini --llm-model "models/gemini-2.5-pro" retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_gemini_pro.json
```
### Federal Graph + All Cloud Indexes:
poetry run caliper_v2 --llm-provider gemini --llm-model "models/gemini-2.5-pro" graph retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --graph-dir data_v2/graph_federal --hops 2 --limit 200 --mix-with-text --text-indexes federal,state,design --top-k 60 --rerank-top-n 24 --out data_v2/context/crosswalk_gemini_graph_federal_mixed.json

#### Gemini 2.5 Flash
```powershell
poetry run caliper_v2 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24 --provider gemini --model "models/gemini-2.5-flash" --out data_v2/context/crosswalk_gemini_flash.json
```

### 5. xAI Grok

```powershell
poetry run caliper_v2 --llm-provider grok --llm-model grok-4 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --indexes federal,state,design --top-k 60 --rerank-top-n 24  --out data_v2/context/crosswalk_grok.json
```

## Generation Commands (After Retrieval)

Once you have context files, generate the actual crosswalk:

### Generate with different providers
```powershell
# Using Cohere context, generate with OpenAI
poetry run caliper_v2 generate data_v2/context/crosswalk_cohere.json --style strict-citation --format md --provider openai --model gpt-4o-mini --out outputs/crosswalk_cohere_openai.md

# Using OpenAI context, generate with Cohere
poetry run caliper_v2 generate data_v2/context/crosswalk_openai_mini.json --style strict-citation --format md --provider cohere --model command-r --out outputs/crosswalk_openai_cohere.md

# Using Gemini context, generate with Anthropic
poetry run caliper_v2 --llm-provider grok --llm-model grok-4 generate "C:\repos\caliper_3\data_v2\context\crosswalk_grok.json" --style strict-citation --format md  --out outputs/crosswalk_grok.md
```

## Judge/Review Commands

After generation, evaluate the quality:

```powershell
# Judge the Cohere-generated crosswalk
poetry run caliper_v2 judge --context data_v2/context/crosswalk_cohere.json --generation outputs/crosswalk_cohere_openai.md --provider gemini --model "models/gemini-1.5-pro" --strict --out data_v2/judgments/crosswalk_cohere_judgment.json

# Judge the OpenAI-generated crosswalk  
poetry run caliper_v2 judge --context data_v2/context/crosswalk_openai_mini.json --generation outputs/crosswalk_openai_cohere.md --provider anthropic --model claude-3-5-sonnet-20241022 --strict --out data_v2/judgments/crosswalk_openai_judgment.json
```

## Quick Comparison Test

To quickly test which providers work with your API keys:

```powershell
# Just check API keys
poetry run python -c "import os; keys=['COHERE_API_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY','GEMINI_API_KEY','GOOGLE_API_KEY','XAI_API_KEY']; [print(f'{k}: {'✓' if os.getenv(k) else '✗'}') for k in keys]"

# Run doctor for full diagnostics
poetry run caliper_v2 doctor
```

## Notes

- All commands use `--indexes federal,state,design` to search all three corpora
- `--top-k 60` retrieves 60 initial results  
- `--rerank-top-n 24` reranks and keeps top 24 results
- Output files are named `crosswalk_[provider].json` for easy comparison
- The regulatory crosswalk prompt is complex and will test each provider's ability to handle technical legal/regulatory content

poetry run caliper_v2 --llm-provider cohere --llm-model "command-a-reasoning-08-2025" graph build-cloud --indexes federal,state,design --out-corpus data_v2/cloud_corpus_all --graph-out data_v2/graph --relation-mode heuristic --k-hop 2

poetry run caliper_v2 --llm-provider cohere --llm-model command-a-03-2025 graph retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." --graph-dir data_v2/graph --hops 2 --limit 200 --mix-with-text --text-indexes federal,state,design --top-k 60 --rerank-top-n 24 --out data_v2/context/crosswalk_unified_graph.json


poetry run caliper_v2 --llm-provider grok --llm-model grok-4 generate "C:\repos\caliper_3\data_v2\context\q05_population_edu.json" --style strict-citation --format md --out outputs/q05_population_edu.md

poetry run caliper_v2 --llm-provider grok --llm-model grok-4 generate "C:\repos\caliper_3\data_v2\context\q01_outline.json" --style strict-citation --format md --out outputs/q01_outline.md

poetry run caliper_v2 --llm-provider grok --llm-model grok-4 generate "C:\repos\caliper_3\data_v2\context\q02_crosswalk.json" --style strict-citation --format md --out outputs/q02_crosswalk.md

poetry run caliper_v2 --llm-provider grok --llm-model grok-4 generate "C:\repos\caliper_3\data_v2\context\q03_data_inventory.json" --style strict-citation --format md --out outputs/q03_data_inventory.md

poetry run caliper_v2 --llm-provider grok --llm-model grok-4 generate "C:\repos\caliper_3\data_v2\context\q04_design_flow_loadings.json" --style strict-citation --format md --out outputs/q04_design_flow_loadings.md



poetry run caliper_v2 --llm-provider openai --llm-model gpt-5-mini generate "C:\repos\caliper_3\data_v2\context\q01_outline.json" --style strict-citation --format md --out outputs/q01_outline.md


# Build graph once (if not already)
poetry run caliper_v2 graph build --corpus knowledge_base --out data_v2/graph

# A) Pure text retrieval
poetry run caliper_v2 retrieve "Map every WA G1 subsection to Orange Book specifics and any federal anchors; output a cross-walk table with citations." --indexes "federal,state,design_standards" --search-mode hybrid --top-k 60 --reranker cohere --out data_v2/context/g1_crosswalk_text.json

# B) Graph-only (then optionally a mixed run later)
poetry run caliper_v2 graph retrieve \
  "Map every WA G1 subsection to Orange Book specifics and any federal anchors; output a cross-walk table with citations." \
  --graph-dir data_v2/graph \
  --out data_v2/context/g1_crosswalk_graph.json
