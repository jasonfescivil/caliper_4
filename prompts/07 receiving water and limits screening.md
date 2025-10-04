poetry run caliper_v2 retrieve "Create a TBEL/WQBEL screening template for small WA dischargers: receiving water class, mixing zones basics, antidegradation notes, and parameters likely to drive limits. Output: inputs needed, screening steps, citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q07_limits_screen.json

poetry run caliper_v2 generate data_v2/context/q07_limits_screen.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q07_limits_screen.md

poetry run caliper_v2 judge --context data_v2/context/q07_limits_screen.json --generation outputs/q07_limits_screen.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q07_limits_screen.json
