# Review Report


Document: `C:\repos\caliper_3\outputs\drafts\q02_crosswalk.md`  
Context: `C:\repos\caliper_3\data_v2\context\q02_crosswalk.json`


## Summary


- Blocking issues: 2
- High risk: 0
- Inconsistencies: 5
- Coverage score: 1.0

## Issues


- [blocking] missing_required: Required content missing: design_period
  - Suggestion: Add material satisfying: design period|planning horizon|20[- ]year
- [blocking] missing_required: Required content missing: flows_link
  - Suggestion: Add material satisfying: Q\s*avg|ADWF|Q\s*max|peaking factor|Q\s*min
- [medium] acronym: Acronym 'WAC' appears multiple times without definition.
  - Suggestion: Define 'WAC' on first use.
- [medium] acronym: Acronym 'CFR' appears multiple times without definition.
  - Suggestion: Define 'CFR' on first use.
- [medium] acronym: Acronym 'WEF' appears multiple times without definition.
  - Suggestion: Define 'WEF' on first use.
- [medium] acronym: Acronym 'ASCE' appears multiple times without definition.
  - Suggestion: Define 'ASCE' on first use.
- [medium] acronym: Acronym 'AWWA' appears multiple times without definition.
  - Suggestion: Define 'AWWA' on first use.

## Claims assessment


- C1: partial — assistant: | Topic | WA Requirement | Federal Baseline | Design Notes | Citations |
- C2: partial — | --- | --- | --- | --- | --- |
- C3: partial — | Regulatory Framework | WAC 173-240-050/-060: General sewer plans, engineering reports, plans/specs, O&M manuals for domestic wastewater fa
- C4: partial — general sewer plans, which must be approved by the Department of Ecology.
- C5: partial — | [1,2,3,5,6,7,8,11] |
- C6: partial — | | WAC 173-221: Surface water discharge standards for domestic wastewater treatment facilities | 40 CFR 133: Ocean Discharge Criteria | Was
- C7: partial — reasonable methods of prevention, control,
- C8: partial — treatment" (AKART)
- C9: partial — may be superseded by water quality standards in WAC 173-201A.
- C10: partial — | | WAC 173-201A: Water quality standards for surface waters of the state of Washington | N/A | Washington classifies surface waters based o
- C11: partial — sets specific criteria for dissolved oxygen, fecal coliform, temperature, pH, turbidity,
- C12: partial — toxic substances.
- C13: partial — | | WAC 173-200: Water quality standards for ground waters of the state of Washington | N/A | N/A | [1] |
- C14: partial — | | WAC 173-216: State Waste Discharge Permit Program | N/A | N/A | [1] |
- C15: partial — | | WAC 173-240: Submission of plans
- C16: partial — reports for construction of wastewater facilities | N/A | N/A | [1,7,8,11] |
- C17: partial — | | WAC 173-802: State Environmental Policy Act | N/A | N/A | [1] |
- C18: partial — | | RCW 90.48: Water Pollution Control Act | N/A | Washington's Water Pollution Control Act contains requirements for general sewer plans
- C19: partial — engineering reports, which are reviewed
- C20: partial — approved by the Department of Ecology.

## Follow-up retrieve suggestions


```
poetry run caliper_v2 retrieve "assistant: | Topic | WA Requirement | Federal Baseline | Design Notes | Citations |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C1.json"
```
```
poetry run caliper_v2 retrieve "| --- | --- | --- | --- | --- |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C2.json"
```
```
poetry run caliper_v2 retrieve "| Regulatory Framework | WAC 173-240-050/-060: General sewer plans, engineering reports, plans/specs, O&M manuals for do…" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C3.json"
```
```
poetry run caliper_v2 retrieve "general sewer plans, which must be approved by the Department of Ecology." --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C4.json"
```
```
poetry run caliper_v2 retrieve "| [1,2,3,5,6,7,8,11] |" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C5.json"
```
```
poetry run caliper_v2 retrieve "| | WAC 173-221: Surface water discharge standards for domestic wastewater treatment facilities | 40 CFR 133: Ocean Disc…" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C6.json"
```
```
poetry run caliper_v2 retrieve "reasonable methods of prevention, control," --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C7.json"
```
```
poetry run caliper_v2 retrieve "treatment\" (AKART)" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C8.json"
```
```
poetry run caliper_v2 retrieve "may be superseded by water quality standards in WAC 173-201A." --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C9.json"
```
```
poetry run caliper_v2 retrieve "| | WAC 173-201A: Water quality standards for surface waters of the state of Washington | N/A | Washington classifies su…" --indexes "federal,state,design_standards" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C10.json"
```
