# Review Report


Document: `C:\repos\caliper_3\outputs\drafts\q03_data_inventory.md`  
Context: `C:\repos\caliper_3\data_v2\context\q03_data_inventory.json`


## Summary


- Blocking issues: 2
- High risk: 0
- Inconsistencies: 1
- Coverage score: 1.0

## Issues


- [blocking] missing_required: Required content missing: design_period
  - Suggestion: Add material satisfying: design period|planning horizon|20[- ]year
- [blocking] missing_required: Required content missing: flows_link
  - Suggestion: Add material satisfying: Q\s*avg|ADWF|Q\s*max|peaking factor|Q\s*min
- [medium] acronym: Acronym 'SCADA' appears multiple times without definition.
  - Suggestion: Define 'SCADA' on first use.

## Claims assessment


- C1: partial — assistant: **Data Inventory & Client-Request Checklist
- C2: partial — | **Data Type** | **Minimum Span** | **Format** | **Citations** |
- C3: partial — | Inflow/effluent history | 3 years | DMRs | [1,2,10,12,13,17,24,25,28,30,32,39,43,49] |
- C4: partial — | Flow/level logs | 3 years | DMRs | [1,2,10,12,13,17,24,25,28,30,32,39,43,49] |
- C5: partial — | Rainfall | 3 years | Weather records | [12,21,27,43] |
- C6: partial — | Water use/billing | 3 years | Billing records | [12,43] |
- C7: partial — | Septic connections | N/A | Asset records | [1,2,10,12,13,17,28,30,32,39,43,49] |
- C8: partial — | Asset records | N/A | Asset records | [1,2,10,12,13,17,28,30,32,39,43,49] |
- C9: partial — | SCADA trends | 3 years | SCADA data | [6,11,23,36,38] |
- C10: partial — | Power events | 3 years | Power data | [6,11,23,36,38] |
- C11: partial — | Past studies | N/A | Reports | [1,2,10,11,12,13,17,21,23,24,25,28,30,32,36,38,39,43,49] |

## Follow-up retrieve suggestions


```
poetry run caliper_v2 retrieve "assistant: **Data Inventory & Client-Request Checklist" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C1.json"
```
```
poetry run caliper_v2 retrieve "| **Data Type** | **Minimum Span** | **Format** | **Citations** |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C2.json"
```
```
poetry run caliper_v2 retrieve "| Inflow/effluent history | 3 years | DMRs | [1,2,10,12,13,17,24,25,28,30,32,39,43,49] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C3.json"
```
```
poetry run caliper_v2 retrieve "| Flow/level logs | 3 years | DMRs | [1,2,10,12,13,17,24,25,28,30,32,39,43,49] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C4.json"
```
```
poetry run caliper_v2 retrieve "| Rainfall | 3 years | Weather records | [12,21,27,43] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C5.json"
```
```
poetry run caliper_v2 retrieve "| Water use/billing | 3 years | Billing records | [12,43] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C6.json"
```
```
poetry run caliper_v2 retrieve "| Septic connections | N/A | Asset records | [1,2,10,12,13,17,28,30,32,39,43,49] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C7.json"
```
```
poetry run caliper_v2 retrieve "| Asset records | N/A | Asset records | [1,2,10,12,13,17,28,30,32,39,43,49] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C8.json"
```
```
poetry run caliper_v2 retrieve "| SCADA trends | 3 years | SCADA data | [6,11,23,36,38] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C9.json"
```
```
poetry run caliper_v2 retrieve "| Power events | 3 years | Power data | [6,11,23,36,38] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C10.json"
```
