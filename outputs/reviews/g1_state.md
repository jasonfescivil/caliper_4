# Review Report


Document: `C:\repos\caliper_3\outputs\drafts\g1_state.md`  
Context: `C:\repos\caliper_3\data_v2\context\g1_state_test.json`


## Summary


- Blocking issues: 2
- High risk: 0
- Inconsistencies: 0
- Coverage score: 1.0

## Issues


- [blocking] missing_required: Required content missing: design_period
  - Suggestion: Add material satisfying: design period|planning horizon|20[- ]year
- [blocking] missing_required: Required content missing: flows_link
  - Suggestion: Add material satisfying: Q\s*avg|ADWF|Q\s*max|peaking factor|Q\s*min

## Claims assessment


- C1: partial — assistant: The G1 requirements for engineering reports are outlined in Table G1-1 [1,2] of the "DOE Orange Book Design Standards" [1,2,3,4,5
- C2: partial — WAC 173-240-060 [8].
- C3: partial — Engineering reports must include detailed, project-specific evaluations of alternatives [1,3] considered to implement projects described in 
- C4: partial — They must be sufficiently complete [1,2,3,8]
- C5: partial — contain appropriate preliminary design details [1,3,8] so that any engineer can develop complete design documents [1,3] (plans
- C6: partial — specifications) without making substantial changes.
- C7: partial — Reports must establish the rationale for specific design criteria [1,3]
- C8: partial — include a description of the project [8], treatment process [8], basic design data
- C9: partial — sizing calculations [8], site recommendations [8],
- C10: partial — relevant data as requested by Ecology.
- C11: partial — Three copies of the report [8] must be submitted for approval [8], except when waived.

## Follow-up retrieve suggestions


```
poetry run caliper_v2 retrieve "assistant: The G1 requirements for engineering reports are outlined in Table G1-1 [1,2] of the \"DOE Orange Book Design S…" --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C1.json"
```
```
poetry run caliper_v2 retrieve "WAC 173-240-060 [8]." --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C2.json"
```
```
poetry run caliper_v2 retrieve "Engineering reports must include detailed, project-specific evaluations of alternatives [1,3] considered to implement pr…" --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C3.json"
```
```
poetry run caliper_v2 retrieve "They must be sufficiently complete [1,2,3,8]" --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C4.json"
```
```
poetry run caliper_v2 retrieve "contain appropriate preliminary design details [1,3,8] so that any engineer can develop complete design documents [1,3] …" --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C5.json"
```
```
poetry run caliper_v2 retrieve "specifications) without making substantial changes." --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C6.json"
```
```
poetry run caliper_v2 retrieve "Reports must establish the rationale for specific design criteria [1,3]" --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C7.json"
```
```
poetry run caliper_v2 retrieve "include a description of the project [8], treatment process [8], basic design data" --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C8.json"
```
```
poetry run caliper_v2 retrieve "sizing calculations [8], site recommendations [8]," --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C9.json"
```
```
poetry run caliper_v2 retrieve "relevant data as requested by Ecology." --indexes "state" --cloud --top-k 40 --reranker cohere --reranker-top-n 20 --out "C:\repos\caliper_3\data_v2\context\retry_C10.json"
```
