# Caliper v2 Enhancement Roadmap

## ✅ Already Implemented
1. **Enhanced Embeddings** - text-embedding-3-small
2. **LlamaParse Integration** - Better PDF parsing with tables
3. **Metadata Extraction** - Regulatory numbers, agencies, years
4. **Hybrid Search** - BM25 + Vector with --search-mode
5. **Citations System** - Inline [1][2] with source footnotes
6. **Multi-Index Federation** - Query across indexes with commas
7. **Answer Self-Reflection** - --self-reflect flag for answer refinement
8. **Agentic RAG** - ReAct agent with tool use

## 🔄 Implementing Next (Today)
1. **Retrieval Self-Critique** (2 hours)
   - Evaluate retrieved chunks before synthesis
   - Filter out irrelevant results
   - Improve precision

2. **Query Expansion** (1-2 hours)
   - Generate alternative phrasings
   - Handle acronyms/technical terms
   - Merge results from variants

3. **Answer Confidence Scoring** (30 min)
   - 0-100 confidence score
   - Based on source support
   - Highlight uncertainties

## 🚀 High Priority Enhancements

### 1. Dual Embedding with Router (4-6 hours)
- Use multiple embedding models
- LLM router selects best results
- Handles edge cases better
- Implementation sketch in TEKOA_AKART_SMALL_SYSTEM_PROMPT.md

### 2. Multimodal Support (1-2 days)
- Extract images/diagrams from PDFs
- Use GPT-4V or Claude for image understanding
- Critical for engineering drawings
- Store image embeddings separately

### 3. Math Rendering (2-3 hours)
- Detect LaTeX/math in responses
- Render equations properly
- Important for design calculations

### 4. Incremental Indexing (4-5 hours)
- Hash-based change detection
- Only re-index modified files
- Critical for large knowledge bases
- Use LlamaIndex's built-in hash tracking

### 5. Web UI (1 week)
- Dash or Gradio interface
- Document upload
- Visual query builder
- Export to Word/PDF

## 🔮 Future Enhancements

### Advanced RAG Features
1. **HyDE (Hypothetical Document Embeddings)**
   - Generate hypothetical answer first
   - Embed and search with that
   - Better for complex queries

2. **Recursive Retrieval**
   - Start broad, then narrow
   - Follow references between docs
   - Build complete context

3. **Graph RAG**
   - Build knowledge graph from docs
   - Traverse relationships
   - Better for "how does X relate to Y"

### Operational Features
1. **Usage Analytics**
   - Track queries and performance
   - Identify knowledge gaps
   - Optimize indexes

2. **Feedback Loop**
   - User ratings on answers
   - Retrain embeddings
   - Improve over time

3. **Multi-User Support**
   - User authentication
   - Per-project indexes
   - Audit trails

### Integration Features
1. **API Endpoints**
   - REST API for queries
   - Webhook notifications
   - Third-party integrations

2. **Document Sync**
   - Watch folders for changes
   - Auto-index new documents
   - Version control integration

3. **Export Formats**
   - Generate Word reports
   - PDF with formatting
   - Markdown with citations

## 📊 Implementation Priority Matrix

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Query Expansion | High | Low | TODAY |
| Retrieval Critique | High | Low | TODAY |
| Confidence Scoring | Medium | Very Low | TODAY |
| Incremental Indexing | High | Medium | HIGH |
| Math Rendering | Medium | Low | HIGH |
| Dual Embeddings | Medium | Medium | MEDIUM |
| Multimodal | High | High | MEDIUM |
| Web UI | High | High | LOW |

## 🛠️ Technical Debt
1. Add comprehensive error handling
2. Implement proper logging levels
3. Add performance benchmarks
4. Create integration tests
5. Document API properly

## 📈 Success Metrics
- Query response time < 3s
- Retrieval precision > 85%
- User satisfaction > 4.5/5
- Zero hallucination rate
- 100% citation accuracy
