# Tekoa AKART Analysis - Final De-Specified RAG-Optimized Prompt

## Enhanced CLI Command

```bash
poetry run caliper_v2 agent "
Develop a complete AKART analysis for the Town of Tekoa, Washington by discovering ALL data from indexed documents.

SYSTEM CONTEXT
• Small oxidation-ditch WWTP in eastern Washington
• Search for current population, flow rates, and permit limits in indexed Tekoa documents
• Cold climate with documented winter operational challenges

DISCOVERY INSTRUCTIONS
• Extract all values from indexed documents with explicit citations [filename - page X]
• When multiple sources conflict, note discrepancies and use most recent/authoritative
• Flag as [DATA GAP - recommend source] when information is not found
• For calculations, show work and cite the formula source

SEARCH PRIORITIES
1. Tekoa-specific documents (permits, studies, violations)
2. Washington State regulations and design standards
3. Federal guidance for small cold-climate systems
4. Comparable case studies in the region

DELIVERABLE 1 - System Characterization
□ Find and cite current NPDES permit number and limits
□ Extract flow data (ADF, MMF, PHF) from permits or studies
□ Document all compliance violations with dates and parameters
□ Identify receiving water impairments and TMDL requirements
□ Calculate per-capita flows and loads from available data

DELIVERABLE 2 - Design Basis Development
□ Locate appropriate peaking factors in Orange Book (cite table/figure)
□ Find temperature data and correction factors for 8°C operation
□ Extract I/I contribution from 2017 study or similar
□ Project 20-year population using best available growth data
□ Calculate design flows and loads with all adjustment factors

DELIVERABLE 3 - Technology Evaluation Matrix
□ Identify proven technologies for <0.2 MGD in cold climates
□ Find actual performance data from similar facilities
□ Document land requirements, operator skill needs, reliability
□ Locate cold-weather design modifications and costs
□ Create scoring matrix based on Tekoa-specific constraints

DELIVERABLE 4 - Cost Analysis
□ Extract recent bid tabs for <0.1 MGD facilities
□ Find appropriate cost curves or $/gallon estimates
□ Locate ENR or WSDOT index values for escalation
□ Document available funding programs with current rates
□ Calculate rate impacts using Tekoa's connection count

DELIVERABLE 5 - Regulatory Compliance Path
□ Find all applicable WACs and implementation guidance
□ Extract specific AKART requirements and timelines
□ Document mixing zone provisions and restrictions
□ Identify seasonal discharge limitations
□ Map permit modification process and timeline

DELIVERABLE 6 - Implementation Strategy
□ Extract Tekoa's actual constraints (staffing, budget, access)
□ Find examples of successful phased implementations
□ Document interim compliance measures from other facilities
□ Identify quick wins from O&M optimization studies
□ Create realistic schedule with regulatory milestones

CRITICAL QUESTIONS REQUIRING SPECIFIC ANSWERS
1. What exact I/I flow was documented in Tekoa's 2017 study?
2. Which Washington facilities <0.2 MGD currently meet TP <0.1 mg/L?
3. What are actual 2020+ construction costs for lagoons vs mechanical plants?
4. How did similar facilities address Ecology's 2016 violations?
5. What specific provisions exist for small disadvantaged communities?

ENHANCED SEARCH INSTRUCTIONS
• Use filename searches for: 'Tekoa', 'NPDES', 'WA0023141', 'Hangman', 'AKART'
• Check multiple indexes if initial searches are incomplete
• Verify critical values by finding them in multiple documents
• Note document dates to ensure currency of information

OUTPUT FORMAT
For each finding, use: [CLAIM] + [SOURCE: filename - page/section] + [CONFIDENCE: High/Medium/Low based on source authority and age]

Example: The facility's average flow is 0.07 MGD [SOURCE: 2023_Tekoa_Facility_Study.pdf - page 12] [CONFIDENCE: High]

END WITH
• Summary of key findings with confidence levels
• List of critical data gaps that need field investigation
• Recommended immediate actions based on highest-confidence findings
" \
--indexes "federal,state,design_standards,technical_reports,tekoa,cost_data" \
--expand-query \
--interactive \
--critique-retrieval \
--show-confidence \
--verbose > tekoa_akart_analysis_final.md
```

## Key Improvements Made:

### 1. **Enhanced Discovery Instructions**
- Explicit citation format: [filename - page X]
- Confidence levels for each finding
- Conflict resolution guidance

### 2. **Structured Deliverables**
- Checkbox format for completeness
- Specific search terms provided
- Clear output format requirements

### 3. **Better Search Guidance**
- Priority order for document types
- Specific filenames to search
- Multi-index search encouragement

### 4. **New Features Integration**
- `--expand-query --interactive` for better search coverage
- `--critique-retrieval` to ensure quality results
- `--show-confidence` for answer reliability
- Added `cost_data` index (if you downloaded it)

### 5. **Data Quality Controls**
- Requires confidence assessment
- Flags conflicts between sources
- Emphasizes most recent/authoritative

## Optional Power-User Version:

```bash
# For maximum accuracy with consensus
poetry run caliper_v2 agent "[same prompt]" \
--indexes "federal,state,design_standards,technical_reports,tekoa,cost_data" \
--expand-query \
--multi-llm \
--interactive \
--answer-llm consensus \
--critique-retrieval \
--show-confidence \
--verbose > tekoa_akart_consensus_final.md
```

This de-specified approach is perfect for RAG - it forces the system to actually search and cite rather than hallucinate! Ready to run when your indexing completes.
