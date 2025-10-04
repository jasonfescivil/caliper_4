poetry run caliper_v2 retrieve "Generate a data inventory & client-request checklist for a small (<1000) WA WWTP feasibility: influent/effluent history, DMRs, flow/level logs, rainfall, water use/billing, septic connections, asset records, SCADA trends, power events, past studies; include minimum spans & formats with citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q03_data_inventory.json

poetry run caliper_v2 generate data_v2/context/q03_data_inventory.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q03_data_inventory.md

poetry run caliper_v2 judge --context data_v2/context/q03_data_inventory.json --generation outputs/q03_data_inventory.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q03_data_inventory.json
