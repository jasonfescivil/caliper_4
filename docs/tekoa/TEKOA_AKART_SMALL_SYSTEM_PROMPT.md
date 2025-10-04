# Updated Tekoa AKART Analysis - Small System Focus (<0.2 MGD)

## Enhanced CLI Command for Tekoa's 0.07 MGD System

```bash
poetry run caliper_v2 agent "Prepare a complete AKART analysis for the Town of Tekoa, WA (0.07 MGD oxidation ditch, 820 people) using ALL indexed documents. CRITICAL CONTEXT from Tekoa files: Review the 2002 vs 2014 vs 2020 permit evolution showing tightening limits; analyze the 2016 noncompliance notice for BOD/TSS violations during high I/I events documented at 0.24 MGD peak (3.4x average per 2017 I/I study); note the 2022 influent station survey showing deteriorating equipment; reference Hangman Creek's impaired status for temperature/dissolved oxygen affecting ammonia limits. DELIVERABLE 1 - Design Calculations: Using actual Tekoa DMR data, calculate loads assuming 100 mg/L BOD increase in winter per the O&M manual cold weather issues. Apply peaking factors for systems <0.2 MGD from Orange Book Table 3-1 (expect 4.0-4.5 for hourly peaks). Size for 950 people (20-yr) at 70 gpcd plus the documented 170 gpcd I/I. DELIVERABLE 2 - PROVEN Technologies for <0.2 MGD in Cold Climates: Focus on: a) Aerated lagoon (3-cell) with 180-day winter storage and summer land application - cite similar systems in Palouse region; b) SBR package plants like AquaNereda or Fluidyne with proven <0.1 MGD installations in cold climates; c) Extended aeration upgrade of existing oxidation ditch with MBBR media for nitrification; d) Facultative lagoon with 1+ year detention and constructed wetland polishing. Exclude unproven or high-complexity options. DELIVERABLE 3 - Actual Cost Data: Use the 2017 I/I study's $2.8M collection system estimate as baseline. Apply ENR index adjustment from 2017 to 2025. Reference Washington State Public Works Trust Fund actual bid tabs for <0.2 MGD facilities. Include Ecology SRF funding scenarios at 0.5% for disadvantaged communities. DELIVERABLE 4 - Compliance Strategy: Address the specific 2016 violations (BOD >30, TSS >45 during peak flows) with solutions proven to handle 3-4x peaking. Consider the 2020 permit extension conditions requiring facility planning by 2023. Reference Hangman Creek TMDL requiring <0.1 mg/L TP by 2028. DELIVERABLE 5 - Implementation Reality for 820 people: Consider Tekoa's limited staff (0.5 FTE operator per O&M manual), distance to certified labs (90 miles to Spokane), severe winter access issues, and median household income <$35,000 affecting rate impacts. Recommend phased approach with interim operational improvements. SPECIFIC QUESTIONS: 1) Which <0.2 MGD facilities in Eastern WA have successfully met <0.1 mg/L TP? 2) What is typical construction cost per gallon for lagoon vs SBR at 0.07 MGD? 3) How do other Hangman Creek dischargers handle seasonal temperature issues? Include references to: Ecology's Small Community Guidelines, USDA Rural Development funding programs, similar-sized systems (Rosalia, Latah, St. John), and the 2023 update to Orange Book Chapter 3 for small systems." --indexes "federal,state,design_standards,technical_reports,tekoa" --verbose > tekoa_akart_small_system.md
```

## Key Small System Enhancements:

### 1. **Size-Specific Design Criteria**
- Peaking factors 4.0-4.5x for <0.2 MGD
- 70 gpcd design flow (lower than typical)
- I/I at 170 gpcd (extremely high for small system)
- Cold weather BOD increase factors

### 2. **Proven Technologies <0.2 MGD**
- **Aerated Lagoons** - Most common in region
- **SBR Package Plants** - AquaNereda, Fluidyne
- **MBBR Retrofits** - For existing oxidation ditch
- **Extended Detention Lagoons** - 365+ days

### 3. **Real Constraints**
- 0.5 FTE operator (from O&M manual)
- 90 miles to certified lab
- Winter access issues
- Low median income (<$35k)

### 4. **Specific Compliance Issues**
- 2016 violations during 3.4x peak flows
- Hangman Creek TMDL (0.1 mg/L TP by 2028)
- Temperature impacts on ammonia
- 2020 permit extension requirements

### 5. **Regional Examples**
- Rosalia, WA (similar size)
- Latah, WA (lagoon system)
- St. John, WA (SBR upgrade)

## Full Knowledge Base Indexing Commands

### Option 1: Index Everything at Once (Longest but Simplest)
```bash
poetry run caliper_v2 ingest knowledge_base --index all_knowledge --persist --llama-parse
```

### Option 2: Index by Category (Recommended)
```bash
# Federal Regulations
poetry run caliper_v2 ingest knowledge_base/01_federal_regulations --index federal --persist --llama-parse

# State Regulations
poetry run caliper_v2 ingest knowledge_base/02_state_regulations --index state --persist --llama-parse

# Special Districts
poetry run caliper_v2 ingest knowledge_base/03_special_districts --index special_districts --persist --llama-parse

# Design Standards
poetry run caliper_v2 ingest knowledge_base/04_design_standards --index design_standards --persist --llama-parse

# Technical Reports
poetry run caliper_v2 ingest knowledge_base/05_technical_reports --index technical_reports --persist --llama-parse

# Economics/Financing
poetry run caliper_v2 ingest knowledge_base/06_economics_financing --index economics --persist --llama-parse

# Case Studies (includes Tekoa)
poetry run caliper_v2 ingest knowledge_base/08_case_studies --index case_studies --persist --llama-parse
```

### Option 3: Quick Essential Indexes for AKART
```bash
# Just the essentials for Tekoa AKART
poetry run caliper_v2 ingest knowledge_base/01_federal_regulations --index federal --persist --llama-parse
poetry run caliper_v2 ingest knowledge_base/02_state_regulations --index state --persist --llama-parse
poetry run caliper_v2 ingest knowledge_base/04_design_standards --index design_standards --persist --llama-parse
# (Tekoa already done)
```

## Time Estimates:
- Full indexing: ~30-45 minutes
- Essential only: ~15-20 minutes
- Per category: ~5-10 minutes each

The updated prompt now specifically addresses:
- Very small system constraints (<0.2 MGD)
- Proven technologies only
- Real operational limitations from Tekoa docs
- Specific compliance issues from permits
- Regional examples and costs
- Phased implementation for affordability
