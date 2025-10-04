poetry run caliper_v2 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q02_crosswalk.json

poetry run caliper_v2 generate data_v2/context/q02_crosswalk.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q02_crosswalk.md

poetry run caliper_v2 judge --context data_v2/context/q02_crosswalk.json --generation outputs/q02_crosswalk.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q02_crosswalk.json
