poetry run caliper_v2 retrieve "Produce a master outline for a small-community (<1000) WA wastewater treatment feasibility report. Map each section to WAC 173-240, the Criteria for Sewage Works Design (Orange Book), and federal refs; include purpose per section and citation anchors." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q01_outline.json

poetry run caliper_v2 generate data_v2/context/q01_outline.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q01_outline.md

poetry run caliper_v2 judge --context data_v2/context/q01_outline.json --generation outputs/q01_outline.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q01_outline.json
