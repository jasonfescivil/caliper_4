poetry run caliper_v2 retrieve "Create a biosolids compliance checklist for a small WA WWTP: Class A vs B pathways, vector attraction, site controls, monitoring/reporting, land application constraints, storage/contingency. Cross-walk 40 CFR 503 with WAC 173-308; include citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q10_biosolids.json

poetry run caliper_v2 generate data_v2/context/q10_biosolids.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q10_biosolids.md

poetry run caliper_v2 judge --context data_v2/context/q10_biosolids.json --generation outputs/q10_biosolids.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q10_biosolids.json
