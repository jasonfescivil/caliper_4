# Caliper Quick Start Guide

**Production-Ready RAG System for Engineering Reports**

This guide covers the 5 most common workflows you'll use daily.

## Prerequisites

```powershell
# Verify environment
cd c:\repos\caliper_4
poetry run caliper_v2 doctor
```

## 1. Quick Retrieval Query

**Use Case**: Fast answers to specific questions  
**Default Provider**: Cohere (retrieval) + Your choice (generation)

```powershell
# Basic retrieval with Cohere
poetry run caliper_v2 retrieve "What are the G1 requirements for engineering reports?" --cloud

# With specific provider for generation
poetry run caliper_v2 retrieve "NPDES permit requirements for WWTPs" --cloud --llm-provider anthropic

# Using a preset
poetry run caliper_v2 retrieve "Design flow calculations" --preset quick-query
```

## 2. Engineering Report Section

**Use Case**: Generate a full report section with citations  
**Recommended**: Cohere retrieval + Claude Sonnet 4.5 or Opus 4.1

```powershell
# Step 1: Retrieve context (with Cohere)
poetry run caliper_v2 retrieve "Population and flow projections for 20-year planning horizon" ^
  --indexes federal,state,design_standards ^
  --top-k 24 ^
  --reranker cohere ^
  --reranker-top-n 20 ^
  --cloud ^
  --out data_v2/context/pop_flow_ctx.json

# Step 2: Generate with Claude Sonnet 4.5
poetry run caliper_v2 generate data_v2/context/pop_flow_ctx.json ^
  --llm-provider anthropic ^
  --llm-model claude-sonnet-4-5 ^
  --style strict-citation ^
  --out outputs/pop_flow_section.md

# Or use the preset (combines both steps conceptually)
poetry run caliper_v2 retrieve "Population projections" --preset engineering-report
```

## 3. Multi-Provider Comparison

**Use Case**: Compare different LLMs on the same content  
**Providers**: All 5 (OpenAI, Anthropic, Gemini, XAI, Cohere)

```powershell
# First, retrieve once
poetry run caliper_v2 retrieve "I&I investigation methodology" ^
  --cloud --out data_v2/context/ii_method.json

# Then generate with each provider
# OpenAI GPT-5
poetry run caliper_v2 generate data_v2/context/ii_method.json ^
  --llm-provider openai --llm-model gpt-5 ^
  --out outputs/ii_method_gpt5.md

# Anthropic Claude Sonnet 4.5
poetry run caliper_v2 generate data_v2/context/ii_method.json ^
  --llm-provider anthropic --llm-model claude-sonnet-4-5 ^
  --out outputs/ii_method_sonnet45.md

# Anthropic Claude Opus 4.1 (most capable)
poetry run caliper_v2 generate data_v2/context/ii_method.json ^
  --llm-provider anthropic --llm-model claude-opus-4-1 ^
  --out outputs/ii_method_opus41.md

# Google Gemini 2.5 Pro
poetry run caliper_v2 generate data_v2/context/ii_method.json ^
  --llm-provider gemini --llm-model gemini-2.5-pro ^
  --out outputs/ii_method_gemini25.md

# xAI Grok-4
poetry run caliper_v2 generate data_v2/context/ii_method.json ^
  --llm-provider xai --llm-model grok-4 ^
  --out outputs/ii_method_grok4.md

# Cohere Command R+
poetry run caliper_v2 generate data_v2/context/ii_method.json ^
  --llm-provider cohere --llm-model command-r-plus ^
  --out outputs/ii_method_cohere.md
```

## 4. Quality Check Workflow

**Use Case**: QC a generated section before final use  
**Recommended**: Claude Opus 4.1 for judging

```powershell
# Step 1: Retrieve
poetry run caliper_v2 retrieve "Treatment process selection" ^
  --cloud --out data_v2/context/treatment_ctx.json

# Step 2: Generate
poetry run caliper_v2 generate data_v2/context/treatment_ctx.json ^
  --llm-provider anthropic --llm-model claude-sonnet-4-5 ^
  --out outputs/treatment_section.md

# Step 3: Enhance context (optional but recommended)
poetry run caliper_v2 enhance ^
  --in data_v2/context/treatment_ctx.json ^
  --out data_v2/context/treatment_ctx_enhanced.json ^
  --write-outline --rewrite-spore

# Step 4: Judge quality with most capable model
poetry run caliper_v2 judge ^
  --context data_v2/context/treatment_ctx_enhanced.json ^
  --generation outputs/treatment_section.md ^
  --llm-provider anthropic --llm-model claude-opus-4-1 ^
  --out data_v2/judgments/treatment_judgment.json ^
  --strict
```

## 5. Deep Research with GraphRAG

**Use Case**: Complex regulatory compliance research  
**Best For**: When you need relationship and entity context

```powershell
# Mixed retrieval: GraphRAG + text retrieval
poetry run caliper_v2 graph retrieve ^
  "Regulatory requirements for lagoon systems in Washington State" ^
  --graph-dir data_v2/graph_state ^
  --mix-with-text ^
  --text-indexes federal,state ^
  --top-k 40 ^
  --reranker cohere ^
  --reranker-top-n 24 ^
  --out data_v2/context/lagoon_regs_mixed.json

# Generate with your preferred provider
poetry run caliper_v2 generate data_v2/context/lagoon_regs_mixed.json ^
  --llm-provider anthropic --llm-model claude-opus-4-1 ^
  --style technical-report
```

## Provider Selection Guide

### Cohere
- **Best For**: Retrieval (embeddings + reranking)
- **Model**: `command-r-plus` or `command-r7b-12-2024`
- **Use When**: All retrieval operations (best semantic search)

### OpenAI
- **Best For**: Fast, reliable generation
- **Model**: `gpt-5` (or `gpt-4o` for cost)
- **Use When**: Quick drafts, standard tasks

### Anthropic Claude
- **Best For**: Engineering writing, technical accuracy
- **Models**: 
  - `claude-sonnet-4-5` - Best balance (speed + quality)
  - `claude-opus-4-1` - Highest quality, use for final QC
- **Use When**: Report sections, technical documents, judging

### Google Gemini
- **Best For**: Long context, data analysis
- **Model**: `gemini-2.5-pro`
- **Use When**: Large documents, comparative analysis

### xAI Grok
- **Best For**: Fast iteration, exploration
- **Model**: `grok-4`
- **Use When**: Quick prototypes, testing ideas

## Common Issues & Fixes

### "No OPENAI_API_KEY found"
```powershell
# Check your .env file
notepad .env
# Ensure: OPENAI_API_KEY=sk-...
```

### "Index 'federal' not found"
```powershell
# Check available indexes
poetry run caliper_v2 doctor
# Ingest if needed
poetry run caliper_v2 ingest knowledge_base/federal --index federal --persist
```

### "Cohere API error"
```powershell
# Verify Cohere key
poetry run caliper_v2 doctor
# Check .env: COHERE_API_KEY=...
```

### "Cloud retrieval failed"
```powershell
# Check LlamaCloud connection
poetry run caliper_v2 doctor
# Verify .env has:
# LLAMA_CLOUD_API_KEY=...
# FEDERAL_BASE_ID=...
# FEDERAL_SUMMARY_ID=...
# (Same for STATE_ and DESIGN_)
```

## Helper Scripts

Location: `c:\repos\caliper_4\scripts\`

- `quick_retrieve.bat` - Fast retrieval with good defaults
- `generate_section.bat` - Generate from existing context
- `check_system.bat` - Validate environment before work
- `switch_provider.bat` - Quick provider switching

## Configuration

Edit `.caliper.yml` to change defaults without editing commands each time.

## Need Help?

1. Run `poetry run caliper_v2 --help`
2. Check `poetry run caliper_v2 doctor` for environment issues
3. Review `.caliper.yml` for configuration options
4. See `docs/` for detailed documentation

## Daily Workflow Example

```powershell
# Morning: Check system
poetry run caliper_v2 doctor

# Research phase: Retrieve with Cohere
poetry run caliper_v2 retrieve @prompts/section_3_requirements.md --cloud

# Writing phase: Generate with Claude
poetry run caliper_v2 generate data_v2/context/latest
