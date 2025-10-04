poetry run caliper_v2 retrieve "Generate a site selection checklist for a small WWTP: setbacks, floodplain, critical areas, noise/odor buffers, access, utilities, cultural/historic screening. Include WA siting and design standards; output constraint matrix + screening map inputs." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q11_site_selection.json

poetry run caliper_v2 generate data_v2/context/q11_site_selection.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q11_site_selection.md

poetry run caliper_v2 judge --context data_v2/context/q11_site_selection.json --generation outputs/q11_site_selection.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q11_site_selection.json
