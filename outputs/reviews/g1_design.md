# Review Report


Document: `C:\repos\caliper_3\outputs\drafts\g1_design.md`  
Context: `C:\repos\caliper_3\data_v2\context\g1_design_test.json`


## Summary


- Blocking issues: 1
- High risk: 0
- Inconsistencies: 0
- Coverage score: 1.0

## Issues


- [blocking] missing_required: Required content missing: flows_link
  - Suggestion: Add material satisfying: Q\s*avg|ADWF|Q\s*max|peaking factor|Q\s*min

## Claims assessment


- C1: partial — assistant: G1 requirements for engineering reports [2]:
- C2: partial — Statement of the problem
- C3: partial — review of existing conditions [2]
- C4: partial — conditions required for the design period [2]
- C5: partial — Evaluation of alternative methods, if available [2]
- C6: partial — General layouts, including stages of development [2]
- C7: partial — Establishment of engineering criteria, preliminary sizing,
- C8: partial — design [2] to inform cost estimates [2]
- C9: partial — Exploration of financing methods [2]
- C10: partial — Environmental impact assessment [2]
- C11: partial — Consideration of confined space entry requirements per OSHA regulations [2]

## Follow-up retrieve suggestions


```
poetry run caliper_v2 retrieve "assistant: G1 requirements for engineering reports [2]:" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C1.json"
```
```
poetry run caliper_v2 retrieve "Statement of the problem" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C2.json"
```
```
poetry run caliper_v2 retrieve "review of existing conditions [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C3.json"
```
```
poetry run caliper_v2 retrieve "conditions required for the design period [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C4.json"
```
```
poetry run caliper_v2 retrieve "Evaluation of alternative methods, if available [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C5.json"
```
```
poetry run caliper_v2 retrieve "General layouts, including stages of development [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C6.json"
```
```
poetry run caliper_v2 retrieve "Establishment of engineering criteria, preliminary sizing," --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C7.json"
```
```
poetry run caliper_v2 retrieve "design [2] to inform cost estimates [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C8.json"
```
```
poetry run caliper_v2 retrieve "Exploration of financing methods [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C9.json"
```
```
poetry run caliper_v2 retrieve "Environmental impact assessment [2]" --indexes "design" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C10.json"
```
