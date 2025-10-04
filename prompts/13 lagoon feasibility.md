poetry run caliper_v2 retrieve "Develop a lagoon feasibility template for small WA systems: configurations, depth/lining, winter performance/ice cover, polishing, land footprint, seepage/groundwater protection. Cite WA & WEF; output go/no-go table." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q13_lagoon.json

poetry run caliper_v2 generate data_v2/context/q13_lagoon.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q13_lagoon.md

poetry run caliper_v2 judge --context data_v2/context/q13_lagoon.json --generation outputs/q13_lagoon.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q13_lagoon.json
