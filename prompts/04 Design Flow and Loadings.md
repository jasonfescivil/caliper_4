poetry run caliper_v2 retrieve "Build a population/EDU projection template for small WA communities (<1000): OFM sources, seasonal population, vacancy, institutional loads, EDU factors, uncertainty bands, and reconciliation of billing vs census vs meters. Map to report sections & design flow derivations; cite sources." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q05_population_edu.json

poetry run caliper_v2 generate data_v2/context/q05_population_edu.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q05_population_edu.md

poetry run caliper_v2 judge --context data_v2/context/q05_population_edu.json --generation outputs/q05_population_edu.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q05_population_edu.json
