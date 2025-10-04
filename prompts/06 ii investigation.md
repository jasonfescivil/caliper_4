poetry run caliper_v2 retrieve "Produce an I/I plan for small WA systems: monitoring periods, SSES phases, smoke/dye testing, flow isolation, rainfall correlation, QA/QC, deliverables. Cite EPA SSES, WEF manuals, and WA standards. Output: plan sections + field checklist + minimum instrumentation specs." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q06_ii_plan.json

poetry run caliper_v2 generate data_v2/context/q06_ii_plan.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q06_ii_plan.md

poetry run caliper_v2 judge --context data_v2/context/q06_ii_plan.json --generation outputs/q06_ii_plan.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q06_ii_plan.json
