awesome — here are **30 retrieve → generate → judge** command sets, one per prompt.
They use **Cohere `command-a-reasoning-2025`** during *retrieve* (LLM side-effects like expansion/spore/LLM-rerank) **with Cohere rerank**, **OpenAI `gpt-5`** for *generate*, and **Gemini `gemini-2.5-pro`** for *judge*.
All query **`"federal,state,design_standards"`**. Feel free to tweak `--cloud`, `--top-k`, and `--rerank-top-n`.

> quick note: if your environment doesn’t accept `gpt-5` yet, swap `--llm-model gpt-5` for a known-good (e.g., `gpt-4o`).

---

### 01) Feasibility Report Master Outline (WA-small)

```bash
poetry run caliper_v2 retrieve "Produce a master outline for a small-community (<1000) WA wastewater treatment feasibility report. Map each section to WAC 173-240, the Criteria for Sewage Works Design (Orange Book), and federal refs; include purpose per section and citation anchors." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q01_outline.json

poetry run caliper_v2 generate data_v2/context/q01_outline.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q01_outline.md

poetry run caliper_v2 judge --context data_v2/context/q01_outline.json --generation outputs/q01_outline.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q01_outline.json
```

### 02) Regulatory Crosswalk (WAC ↔ CFR ↔ Design Standards)

```bash
poetry run caliper_v2 retrieve "Create a regulatory crosswalk for small WWTPs in Washington: WAC 173-240/173-221/173-200/201A/173-308, RCW 90.48 vs federal (40 CFR 133, 40 CFR 503) and WEF/ASCE/AWWA texts. Output: matrix topic → WA requirement → federal baseline → design notes → citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q02_crosswalk.json

poetry run caliper_v2 generate data_v2/context/q02_crosswalk.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q02_crosswalk.md

poetry run caliper_v2 judge --context data_v2/context/q02_crosswalk.json --generation outputs/q02_crosswalk.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q02_crosswalk.json
```

### 03) Data Inventory & Request List

```bash
poetry run caliper_v2 retrieve "Generate a data inventory & client-request checklist for a small (<1000) WA WWTP feasibility: influent/effluent history, DMRs, flow/level logs, rainfall, water use/billing, septic connections, asset records, SCADA trends, power events, past studies; include minimum spans & formats with citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q03_data_inventory.json

poetry run caliper_v2 generate data_v2/context/q03_data_inventory.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q03_data_inventory.md

poetry run caliper_v2 judge --context data_v2/context/q03_data_inventory.json --generation outputs/q03_data_inventory.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q03_data_inventory.json
```

### 04) Design Flows & Loadings (AADF/MADF/MDD/PHF)

```bash
poetry run caliper_v2 retrieve "Create a design flows & loadings checklist for small WA systems: datasets and steps for AADF, MADF, MDD, Peak Hour, I/I allowances, seasonal peaking, wastewater strength (BOD/TSS/N/TP). Cross-walk to WAC 173-240 & Orange Book; cite federal/WEF calc guidance." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q04_flows_loadings.json

poetry run caliper_v2 generate data_v2/context/q04_flows_loadings.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q04_flows_loadings.md

poetry run caliper_v2 judge --context data_v2/context/q04_flows_loadings.json --generation outputs/q04_flows_loadings.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q04_flows_loadings.json
```

### 05) Population & EDU Projections (OFM-based)

```bash
poetry run caliper_v2 retrieve "Build a population/EDU projection template for small WA communities (<1000): OFM sources, seasonal population, vacancy, institutional loads, EDU factors, uncertainty bands, and reconciliation of billing vs census vs meters. Map to report sections & design flow derivations; cite sources." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q05_population_edu.json

poetry run caliper_v2 generate data_v2/context/q05_population_edu.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q05_population_edu.md

poetry run caliper_v2 judge --context data_v2/context/q05_population_edu.json --generation outputs/q05_population_edu.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q05_population_edu.json
```

### 06) I/I Investigation Plan (Small Systems)

```bash
poetry run caliper_v2 retrieve "Produce an I/I plan for small WA systems: monitoring periods, SSES phases, smoke/dye testing, flow isolation, rainfall correlation, QA/QC, deliverables. Cite EPA SSES, WEF manuals, and WA standards. Output: plan sections + field checklist + minimum instrumentation specs." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q06_ii_plan.json

poetry run caliper_v2 generate data_v2/context/q06_ii_plan.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q06_ii_plan.md

poetry run caliper_v2 judge --context data_v2/context/q06_ii_plan.json --generation outputs/q06_ii_plan.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q06_ii_plan.json
```

### 07) Receiving Water & Limits Screening (TBEL/WQBEL)

```bash
poetry run caliper_v2 retrieve "Create a TBEL/WQBEL screening template for small WA dischargers: receiving water class, mixing zones basics, antidegradation notes, and parameters likely to drive limits. Output: inputs needed, screening steps, citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q07_limits_screen.json

poetry run caliper_v2 generate data_v2/context/q07_limits_screen.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q07_limits_screen.md

poetry run caliper_v2 judge --context data_v2/context/q07_limits_screen.json --generation outputs/q07_limits_screen.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q07_limits_screen.json
```

### 08) Disinfection Alternatives (Chlorine vs UV)

```bash
poetry run caliper_v2 retrieve "Draft a small-system disinfection alternatives matrix: chlorine gas/bleach vs UV (low-pressure). Include dose/residual/dechlor, lamp life, O&M, power, safety, reliability; provide selection checklist; cite WA criteria + WEF guidance." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q08_disinfection.json

poetry run caliper_v2 generate data_v2/context/q08_disinfection.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q08_disinfection.md

poetry run caliper_v2 judge --context data_v2/context/q08_disinfection.json --generation outputs/q08_disinfection.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q08_disinfection.json
```

### 09) Nitrification/Ammonia Removal Feasibility (Cold Weather)

```bash
poetry run caliper_v2 retrieve "Provide a nitrification feasibility checklist for small WA plants in cold climates: temp thresholds, SRT, alkalinity, aeration/energy, process choices (lagoon+polishing, SBR, package). Cite WA design criteria and WEF manuals; output go/no-go + data gaps." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q09_nitrification.json

poetry run caliper_v2 generate data_v2/context/q09_nitrification.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q09_nitrification.md

poetry run caliper_v2 judge --context data_v2/context/q09_nitrification.json --generation outputs/q09_nitrification.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q09_nitrification.json
```

### 10) Biosolids Compliance (40 CFR 503 ↔ WAC 173-308)

```bash
poetry run caliper_v2 retrieve "Create a biosolids compliance checklist for a small WA WWTP: Class A vs B pathways, vector attraction, site controls, monitoring/reporting, land application constraints, storage/contingency. Cross-walk 40 CFR 503 with WAC 173-308; include citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q10_biosolids.json

poetry run caliper_v2 generate data_v2/context/q10_biosolids.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q10_biosolids.md

poetry run caliper_v2 judge --context data_v2/context/q10_biosolids.json --generation outputs/q10_biosolids.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q10_biosolids.json
```

### 11) Site Selection & Constraints

```bash
poetry run caliper_v2 retrieve "Generate a site selection checklist for a small WWTP: setbacks, floodplain, critical areas, noise/odor buffers, access, utilities, cultural/historic screening. Include WA siting and design standards; output constraint matrix + screening map inputs." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q11_site_selection.json

poetry run caliper_v2 generate data_v2/context/q11_site_selection.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q11_site_selection.md

poetry run caliper_v2 judge --context data_v2/context/q11_site_selection.json --generation outputs/q11_site_selection.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q11_site_selection.json
```

### 12) Hydraulic Profile & Headworks Minimums

```bash
poetry run caliper_v2 retrieve "Produce a hydraulic profile & headworks minimums checklist for small plants: screens (manual vs mechanical), grit (when justified), bypass rules, hydraulics through units, standby channels. Cite WA criteria & WEF design texts; step-by-step checks + calc placeholders." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q12_hydraulic_headworks.json

poetry run caliper_v2 generate data_v2/context/q12_hydraulic_headworks.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q12_hydraulic_headworks.md

poetry run caliper_v2 judge --context data_v2/context/q12_hydraulic_headworks.json --generation outputs/q12_hydraulic_headworks.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q12_hydraulic_headworks.json
```

### 13) Lagoon Feasibility

```bash
poetry run caliper_v2 retrieve "Develop a lagoon feasibility template for small WA systems: configurations, depth/lining, winter performance/ice cover, polishing, land footprint, seepage/groundwater protection. Cite WA & WEF; output go/no-go table." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q13_lagoon.json

poetry run caliper_v2 generate data_v2/context/q13_lagoon.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q13_lagoon.md

poetry run caliper_v2 judge --context data_v2/context/q13_lagoon.json --generation outputs/q13_lagoon.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q13_lagoon.json
```

### 14) Package/MBR/SBR Screening (≤0.1–0.2 MGD)

```bash
poetry run caliper_v2 retrieve "Build a screening matrix for compact mechanical options (SBR, MBR, package) at very small flows: footprint, operator skill, reliability, CAPEX/OPEX, parts/vendor support. Cite WA & WEF; include ranges and red flags." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q14_package_mbr_sbr.json

poetry run caliper_v2 generate data_v2/context/q14_package_mbr_sbr.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q14_package_mbr_sbr.md

poetry run caliper_v2 judge --context data_v2/context/q14_package_mbr_sbr.json --generation outputs/q14_package_mbr_sbr.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q14_package_mbr_sbr.json
```

### 15) Collection System & Lift Station Mini-Checklist

```bash
poetry run caliper_v2 retrieve "Create a collection system & lift station mini-checklist for feasibility: pipe age/material, CCTV/SMOKE findings, pump curves, wet-well detention, backup power, alarms/telemetry; tie to I/I recommendations and WWTP capacity; cite standards." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q15_collection_lift.json

poetry run caliper_v2 generate data_v2/context/q15_collection_lift.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q15_collection_lift.md

poetry run caliper_v2 judge --context data_v2/context/q15_collection_lift.json --generation outputs/q15_collection_lift.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q15_collection_lift.json
```

### 16) Energy & Standby Power Plan

```bash
poetry run caliper_v2 retrieve "Provide an energy checklist: aeration power estimates, blower/pump efficiency, UV/chlor, standby power sizing, fuel storage, load shedding for small utilities; reliability expectations and WA references. Output: quick energy model inputs + checklist." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q16_energy_power.json

poetry run caliper_v2 generate data_v2/context/q16_energy_power.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q16_energy_power.md

poetry run caliper_v2 judge --context data_v2/context/q16_energy_power.json --generation outputs/q16_energy_power.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q16_energy_power.json
```

### 17) Operations & Staffing Plan

```bash
poetry run caliper_v2 retrieve "Draft an O&M and staffing plan outline for a small WA utility: operator certification, hours, sampling/monitoring duties, lab needs, spare parts, vendor support, telemetry, and training; cite WA references and standards." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q17_ops_staffing.json

poetry run caliper_v2 generate data_v2/context/q17_ops_staffing.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q17_ops_staffing.md

poetry run caliper_v2 judge --context data_v2/context/q17_ops_staffing.json --generation outputs/q17_ops_staffing.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q17_ops_staffing.json
```

### 18) Monitoring & Reporting Plan (DMR/Permit)

```bash
poetry run caliper_v2 retrieve "Create a monitoring/reporting checklist tied to likely permit conditions for small WWTPs: parameters, frequency, methods, flow measurement, QA/QC, recordkeeping. Cross-walk WA permits and federal baselines; output a table with placeholder frequencies and citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q18_monitoring_reporting.json

poetry run caliper_v2 generate data_v2/context/q18_monitoring_reporting.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q18_monitoring_reporting.md

poetry run caliper_v2 judge --context data_v2/context/q18_monitoring_reporting.json --generation outputs/q18_monitoring_reporting.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q18_monitoring_reporting.json
```

### 19) Reliability & Redundancy Minimums

```bash
poetry run caliper_v2 retrieve "Summarize reliability classification expectations and minimum redundancy for small WWTPs: duty/standby for critical units, bypass rules, emergency storage, alarm/telemetry. Cite WA criteria and WEF standards; output compliance checklist." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q19_reliability.json

poetry run caliper_v2 generate data_v2/context/q19_reliability.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q19_reliability.md

poetry run caliper_v2 judge --context data_v2/context/q19_reliability.json --generation outputs/q19_reliability.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q19_reliability.json
```

### 20) Phasing & Modular Expansion

```bash
poetry run caliper_v2 retrieve "Provide a phasing plan template for a small community (<1000): initial 'starter' capacity, modular add-ons, temporary facilities during construction, and triggers for expansion. Map sections to WAC engineering report requirements and design standards; include citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q20_phasing.json

poetry run caliper_v2 generate data_v2/context/q20_phasing.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q20_phasing.md

poetry run caliper_v2 judge --context data_v2/context/q20_phasing.json --generation outputs/q20_phasing.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q20_phasing.json
```

### 21) Construction Sequencing & Bypass Controls

```bash
poetry run caliper_v2 retrieve "Create a construction sequencing & bypass control checklist for small WWTP upgrades: temporary pumps, storage, permit coordination, wet-weather contingencies, and public notice requirements as applicable; cite WA guidance and WEF best practices." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q21_construction_bypass.json

poetry run caliper_v2 generate data_v2/context/q21_construction_bypass.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q21_construction_bypass.md

poetry run caliper_v2 judge --context data_v2/context/q21_construction_bypass.json --generation outputs/q21_construction_bypass.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q21_construction_bypass.json
```

### 22) Cost Opinion (CAPEX/OPEX) + Life-Cycle

```bash
poetry run caliper_v2 retrieve "Generate a cost opinion template: CAPEX (site/civil/process/elec/I&C), soft costs, contingency, and OPEX (power, chemicals, labor, residuals). Include life-cycle comparison (NPV) for alternatives and small-system cost caveats; cite standard references." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q22_cost_lifecycle.json

poetry run caliper_v2 generate data_v2/context/q22_cost_lifecycle.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q22_cost_lifecycle.md

poetry run caliper_v2 judge --context data_v2/context/q22_cost_lifecycle.json --generation outputs/q22_cost_lifecycle.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q22_cost_lifecycle.json
```

### 23) Funding & Affordability Snapshot (SRF/USDA/CDBG)

```bash
poetry run caliper_v2 retrieve "Prepare a funding/affordability snapshot for small WA utilities: typical SRF/USDA/CDBG requirements, affordability metrics, disadvantaged community considerations, and documentation to collect. Output: checklist + citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q23_funding_affordability.json

poetry run caliper_v2 generate data_v2/context/q23_funding_affordability.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q23_funding_affordability.md

poetry run caliper_v2 judge --context data_v2/context/q23_funding_affordability.json --generation outputs/q23_funding_affordability.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q23_funding_affordability.json
```

### 24) Public & Stakeholder Engagement Plan

```bash
poetry run caliper_v2 retrieve "Outline a right-sized public involvement plan for a small WWTP feasibility: stakeholders, meeting cadence, notices, comment tracking, decision record integration; include minimal compliance expectations and cite WA references." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q24_public_engagement.json

poetry run caliper_v2 generate data_v2/context/q24_public_engagement.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q24_public_engagement.md

poetry run caliper_v2 judge --context data_v2/context/q24_public_engagement.json --generation outputs/q24_public_engagement.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q24_public_engagement.json
```

### 25) Risk Register (Tech/Reg/Schedule/Funding)

```bash
poetry run caliper_v2 retrieve "Produce a risk register template for small WWTP projects: technical (I/I uncertainty, winter nitrification), regulatory (limits, biosolids), schedule (windows, permits), funding (match, timing). Include likelihood/impact scoring and mitigations with citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q25_risk_register.json

poetry run caliper_v2 generate data_v2/context/q25_risk_register.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q25_risk_register.md

poetry run caliper_v2 judge --context data_v2/context/q25_risk_register.json --generation outputs/q25_risk_register.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q25_risk_register.json
```

### 26) QA/QC Plan for Feasibility Work

```bash
poetry run caliper_v2 retrieve "Create a QA/QC plan outline: document control, calculation checks, citation verification, traceability to source chunks, and mitigation for scanned/long-table pitfalls. Reference evaluation/judging practices and standards; output checklist + procedures." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q26_qaqc.json

poetry run caliper_v2 generate data_v2/context/q26_qaqc.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q26_qaqc.md

poetry run caliper_v2 judge --context data_v2/context/q26_qaqc.json --generation outputs/q26_qaqc.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q26_qaqc.json
```

### 27) Asset Management Starter Plan

```bash
poetry run caliper_v2 retrieve "Provide a starter asset management outline for a small utility: inventory, condition grading, criticality, renewal planning, basic CMMS/spreadsheet setup, and tie-in with feasibility recommendations; cite best practices and WA references." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q27_asset_mgmt.json

poetry run caliper_v2 generate data_v2/context/q27_asset_mgmt.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q27_asset_mgmt.md

poetry run caliper_v2 judge --context data_v2/context/q27_asset_mgmt.json --generation outputs/q27_asset_mgmt.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q27_asset_mgmt.json
```

### 28) Reclaimed Water / Land Application Pre-Screen

```bash
poetry run caliper_v2 retrieve "Draft a reclaimed water or land application pre-screen: WAC 173-219 gateway, target quality, storage/seasonality, acreage, soils/permitting, and monitoring. Include go/no-go decision points with citations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q28_reclaimed_prescreen.json

poetry run caliper_v2 generate data_v2/context/q28_reclaimed_prescreen.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q28_reclaimed_prescreen.md

poetry run caliper_v2 judge --context data_v2/context/q28_reclaimed_prescreen.json --generation outputs/q28_reclaimed_prescreen.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q28_reclaimed_prescreen.json
```

### 29) Odor & Aesthetics Minimization

```bash
poetry run caliper_v2 retrieve "Create a small-plant odor/aesthetics checklist: likely sources, covers/chem feed basics, setbacks/landscaping, complaint handling, measurement/screening tools; cite design standards and WA considerations." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q29_odor_aesthetics.json

poetry run caliper_v2 generate data_v2/context/q29_odor_aesthetics.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q29_odor_aesthetics.md

poetry run caliper_v2 judge --context data_v2/context/q29_odor_aesthetics.json --generation outputs/q29_odor_aesthetics.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q29_odor_aesthetics.json
```

### 30) SCADA/Telemetry Minimal Architecture

```bash
poetry run caliper_v2 retrieve "Provide a SCADA/telemetry minimal architecture checklist for a small WWTP: alarms, remote notification, data retention, cybersecurity basics, integration with lift stations; include reliability expectations and references." \
  --indexes "federal,state,design_standards" --cloud --top-k 60 --reranker cohere --rerank-top-n 24 \
  --llm-provider cohere --llm-model command-a-reasoning-2025 \
  --out data_v2/context/q30_scada_min.json

poetry run caliper_v2 generate data_v2/context/q30_scada_min.json \
  --style strict-citation --format md --llm-provider openai --llm-model gpt-5 > outputs/q30_scada_min.md

poetry run caliper_v2 judge --context data_v2/context/q30_scada_min.json --generation outputs/q30_scada_min.md \
  --llm-provider google --llm-model gemini-2.5-pro --strict \
  --out data_v2/judgments/q30_scada_min.json
```
