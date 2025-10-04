# 🚀 Indexing Optimization Guide

## Current Setup Analysis

### What You're Using:
- **Embeddings**: OpenAI text-embedding-ada-002 (1536 dimensions)
- **Chunking**: 2000 tokens with 400 overlap
- **Parser**: SimpleNodeParser (basic splitting)
- **Storage**: FAISS + BM25 pickle files

### Optimization Options

## 1. 🎯 Upgrade Embeddings (Better Quality)

### Option A: OpenAI text-embedding-3-small (Better + Cheaper)
```python
# In cli.py, add:
from llama_index.embeddings.openai import OpenAIEmbedding
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
```
- **Benefits**: 1.5x better performance, 5x cheaper than ada-002
- **Cost**: ~$0.02 per million tokens

### Option B: OpenAI text-embedding-3-large (Best Quality)
```python
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")
```
- **Benefits**: Highest quality, 3072 dimensions
- **Cost**: ~$0.13 per million tokens

## 2. 📄 Smarter Document Parsing

### Current: SimpleDirectoryReader
- Basic PDF extraction
- May miss tables, formatting

### Upgrade: LlamaParse (Best for Complex PDFs)
```bash
pip install llama-parse
# Set LLAMA_CLOUD_API_KEY in .env
```
```python
from llama_parse import LlamaParse
parser = LlamaParse(result_type="markdown")
documents = parser.load_data(file_path)
```
- **Benefits**: Preserves tables, headers, structure
- **Perfect for**: Regulatory docs with complex formatting

## 3. 🔪 Advanced Chunking Strategies

### Option A: Semantic Chunking
```python
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()
parser = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=embed_model,
)
```
- **Benefits**: Chunks at natural semantic boundaries
- **Drawback**: Slower, requires embedding calls during parsing

### Option B: Sentence Window Parsing
```python
from llama_index.core.node_parser import SentenceWindowNodeParser

parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_text",
)
```
- **Benefits**: Better context retrieval
- **Use case**: When you need surrounding context

## 4. 🏷️ Enhanced Metadata Extraction

```python
# Add to your parsing pipeline
def extract_regulation_metadata(document):
    metadata = {}

    # Extract CFR/WAC numbers
    cfr_pattern = r'\d{1,2}\s*CFR\s*§?\s*\d+\.?\d*'
    wac_pattern = r'WAC\s*\d{3}-\d{3}-\d{3,4}'

    if cfr_match := re.search(cfr_pattern, document.text):
        metadata['regulation_number'] = cfr_match.group()
        metadata['regulation_type'] = 'CFR'

    # Extract dates
    date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    if date_match := re.search(date_pattern, document.text):
        metadata['effective_date'] = date_match.group()

    return metadata
```

## 5. 🔧 Quick Improvements (No Code Changes)

### A. Adjust Chunk Size Based on Document Type
```bash
# For technical standards (more context needed)
poetry run caliper_v2 ingest knowledge_base/06_design_standards --index design_standards --persist --chunk-size 3000 --chunk-overlap 500

# For simple regulations (smaller chunks OK)
poetry run caliper_v2 ingest knowledge_base/05_special_districts --index special_districts --persist --chunk-size 1000 --chunk-overlap 200
```

### B. Add Reranking (If you have Cohere API key)
```bash
# In .env add:
COHERE_API_KEY=your_key_here

# Query with reranking
poetry run caliper_v2 query "your question" --index federal_regs --rerank
```

## 6. 📊 Recommended Immediate Actions

1. **Keep current setup** - It's good!
2. **Consider upgrading** embeddings to text-embedding-3-small
3. **Add metadata extraction** for regulation numbers
4. **Test different chunk sizes** for different document types

## 7. 🎯 Document-Specific Settings

| Document Type | Recommended Chunk Size | Overlap | Reason |
|--------------|------------------------|---------|---------|
| Federal CFRs | 2000-2500 | 400-500 | Complex cross-references |
| State WACs/RCWs | 1500-2000 | 300-400 | More structured |
| Design Standards | 2500-3000 | 500 | Technical context needed |
| Technical Reports | 2000 | 400 | Mixed content |

## 8. 💡 Testing Your Index Quality

```bash
# Test retrieval precision
poetry run caliper_v2 query "What is 40 CFR 503?" --index federal_regs --search-mode bm25

# Test semantic understanding
poetry run caliper_v2 query "Requirements for pathogen reduction in biosolids" --index federal_regs --search-mode vector

# Test hybrid for best results
poetry run caliper_v2 query "EPA requirements for land application of sewage sludge" --index federal_regs --search-mode hybrid
```

## Summary

Your current setup is **solid for a v1**! The main areas for improvement:
1. Newer embedding models (3-small or 3-large)
2. Smarter parsing for complex PDFs
3. Document-specific chunking strategies
4. Metadata extraction for better filtering

But honestly? **Start using what you have** - it's good enough for 90% of use cases!
