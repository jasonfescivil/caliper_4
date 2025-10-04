# Verification Agent Specification

## Overview
Add a second, independent LLM agent that verifies and enhances the primary agent's responses by checking citations, identifying gaps, and suggesting improvements.

## Motivation
- **Accuracy**: Double-check factual claims against cited sources
- **Completeness**: Identify missing relevant information
- **Quality**: Improve answer clarity and structure
- **Trust**: Build confidence in RAG outputs for regulatory compliance

## Implementation Design

### 1. Architecture
```
User Query
    ↓
Primary Agent (existing)
    ↓
Response + Citations
    ↓
Verification Agent (new)
    ├── Re-query cited sources
    ├── Check factual accuracy
    ├── Identify gaps
    └── Suggest improvements
    ↓
Enhanced Final Response
```

### 2. Command Interface
```bash
# Enable verification (doubles API cost)
poetry run caliper_v2 agent "question" --indexes federal,state --verify

# Verification-only mode (check existing answer)
poetry run caliper_v2 verify "existing answer with citations" --indexes federal,state

# With different verification model
poetry run caliper_v2 agent "question" --verify --verify-llm anthropic
```

### 3. Verification Process

#### Stage 1: Citation Verification
```python
def verify_citations(answer: str, citations: List[str], indexes: List[str]) -> dict:
    """
    1. Extract all factual claims from answer
    2. Map each claim to its citation
    3. Re-query the cited documents
    4. Compare claim vs source material
    5. Return accuracy score and discrepancies
    """
```

#### Stage 2: Gap Analysis
```python
def identify_gaps(question: str, answer: str, indexes: List[str]) -> List[str]:
    """
    1. Generate alternative queries from the question
    2. Search indexes for related information not in answer
    3. Identify regulatory requirements not mentioned
    4. List potentially relevant documents not cited
    """
```

#### Stage 3: Enhancement Suggestions
```python
def suggest_improvements(answer: str, verification_results: dict) -> str:
    """
    1. Fix any factual inaccuracies
    2. Add missing critical information
    3. Improve citation specificity
    4. Enhance answer structure
    5. Add confidence scores
    """
```

### 4. Verification Prompt Template
```python
VERIFICATION_PROMPT = """
You are an independent verification agent. Your task is to verify and improve the following answer.

ORIGINAL QUESTION: {question}

ANSWER TO VERIFY:
{answer}

CITED SOURCES:
{citations}

VERIFICATION TASKS:
1. CHECK ACCURACY: Verify each factual claim against the cited sources
2. IDENTIFY GAPS: Find important information that should be included
3. ASSESS QUALITY: Evaluate completeness, clarity, and structure
4. SUGGEST IMPROVEMENTS: Provide specific recommendations

OUTPUT FORMAT:
## Verification Report

### Accuracy Check
- ✅ Verified: [list verified claims]
- ⚠️ Unverified: [list claims needing verification]
- ❌ Incorrect: [list any errors found]

### Missing Information
- [List relevant information not included]
- [Suggest additional sources to check]

### Recommended Improvements
- [Specific suggestions to enhance the answer]

### Confidence Score: X/100
[Explanation of score]

### Enhanced Answer (if needed):
[Provide improved version incorporating all findings]
"""
```

### 5. Implementation Steps

#### Phase 1: Basic Verification (Week 1)
- [ ] Add `--verify` flag to agent command
- [ ] Implement citation extraction from response
- [ ] Create verification prompt template
- [ ] Add second LLM call for verification
- [ ] Format and display verification report

#### Phase 2: Advanced Features (Week 2)
- [ ] Re-query cited documents for validation
- [ ] Implement gap analysis with alternative queries
- [ ] Add confidence scoring algorithm
- [ ] Support different LLMs for verification
- [ ] Add verification-only mode

#### Phase 3: Optimization (Week 3)
- [ ] Cache verification results
- [ ] Parallel processing for multi-citation checks
- [ ] Add verification presets (quick/thorough/regulatory)
- [ ] Implement verification history tracking
- [ ] Create verification metrics dashboard

### 6. Example Output

```bash
$ poetry run caliper_v2 agent "What are the biosolids application requirements?" --indexes federal,state --verify

🔍 Agent thinking about: What are the biosolids application requirements?
[... primary agent response ...]

🔬 Verification Agent analyzing response...

## Verification Report

### Accuracy Check
✅ Verified: Federal Class A pathogen limits (CFR 503.32)
✅ Verified: State monitoring frequency (WAC 173-308)
⚠️ Unverified: "30-day waiting period" - citation unclear
❌ Incorrect: Metal limits stated as mg/L should be mg
