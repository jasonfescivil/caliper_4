---
chapter_number: 4
chapter_title: "Population, Flow, and Loading Projections"
project:
  name: "TBD – Project Name"
  owner: "TBD – City/Utility"
  location: "TBD – County, Washington"
  report_version: "Draft 0.1"
  prepared_by: "TBD – Consultant"
  date: "TBD"
planning_horizon:
  start_year: 2025
  end_year: 2045
  intermediate_years: [2030, 2035, 2040]
service_area:
  description: "TBD"
  acres_total: null
  subbasins:
    - name: "Downtown"
      acres: null
    - name: "North Ridge"
      acres: null
units:
  flow_primary: "mgd"     # mgd for summaries, allow gpd in tables where specified
  flow_secondary: "gpd"
  load_primary: "lb/d"
  concentration: "mg/L"
  population: "persons"
assumptions:
  rounding:
    flow_mgd: 0.01
    flow_gpd: 10
    load_lbd: 1
  significant_figures: 3
  allow_defaults: false  # if true, use defaults below when inputs missing
defaults:
  per_capita:
    flow_gpcd: 90
    BOD5_lb_per_capita_day: 0.17
    TSS_lb_per_capita_day: 0.20
    TN_lb_per_capita_day: 0.013
    TP_lb_per_capita_day: 0.002
    NH3_lb_per_capita_day: 0.010
  edu:
    persons_per_edu: 2.4
    flow_gpd_per_edu: 220
  employment:
    flow_gpd_per_employee: 20
  concentrations_mgL:
    BOD5: 250
    TSS: 250
    TN: 40
    TP: 6
    NH3: 25
regulatory:
  jurisdiction: "Washington State"
  citations:
    - tag: "WAC 173-240"
      title: "Submission of Plans and Reports for Construction of Wastewater Facilities"
    - tag: "AKART"
      title: "All Known, Available, and Reasonable methods of prevention, control, and Treatment"
    - tag: "Ecology CSWD"
      title: "Criteria for Sewage Works Design (Orange Book)"
    - tag: "EPA CMOM/SSO"
      title: "EPA guidance on capacity, management, operation, and maintenance"
    - tag: "WEF MOP 8"
      title: "Design of Municipal Wastewater Treatment Plants"
data_sources:
  narrative_sources:
    - "Workflow guidance (GPT-5 narrative) – prior .md"
    - "Equations/tables (GPT-5 tables) – prior .md"
  quantitative_sources:
    - name: "OFM population series"
      url_or_ref: "TBD"
    - name: "Local comprehensive plan"
      url_or_ref: "TBD"
    - name: "Metered flow records"
      url_or_ref: "TBD"
population_methods: # Provide at least one series; LLM will reconcile/choose planning series
  per_capita:
    factors:
      flow_gpcd: null    # overrides defaults if provided
    base_population_year: 2025
    base_population_value: null
    annual_growth_rate_pct: null
  edu_housing_unit:
    persons_per_edu: null
    base_EDUs_year: null
    base_EDUs_value: null
    edu_growth_rate_pct: null
  employment_based:
    employees_base_year: null
    employees_base_value: null
    flow_gpd_per_employee: null
  regression_or_return_ratio:
    description: "TBD – model relating ADWF to population/EDU"
    coefficients: {}
  cohort_official_forecast:
    source: "OFM / PSRC / County forecast"
    series:
      # year: population
      2025: null
      2030: null
      2035: null
      2040: null
      2045: null
reconciliation:
  selected_method: "TBD"
  rationale: "TBD – reasons for selecting the planning population series"
I_I:  # Infiltration & Inflow
  gwi_allowance_gpad: null   # gallons per acre-day
  rdii_method: "percent_of_ADWF"  # or "unit_hydrograph", "per_inch_mile"
  rdii_percent_of_ADWF: null
  monitoring_summary: "TBD – meters, smoke tests, CCTV"
peaking:
  method: "harmon" # one of: harmon | ten_states | fixed
  harmon:
    # Pf = 1 + 14/(4 + (P/1000)^0.5) — document exact form used in text
    use_standard_form: true
  ten_states:
    md_peaking_factor_min: 2.5
  fixed:
    MDDF_over_ADWF: 2.5
    PHF_over_MDDF: 1.8
seasonality:
  seasons: ["annual", "max_month", "wet_weather", "dry_weather"]
  adjustments:
    max_month_multiplier_on_ADWF: null
    temperature_notes: "TBD"
safety_contingency:
  flow_multiplier: 1.10
  load_multiplier: 1.10
scenarios:
  - name: "Base"
    notes: "Most likely"
  - name: "Low"
    notes: "Conservative low-growth"
  - name: "High"
    notes: "High-growth"
industrial_commercial:
  contributors:
    - name: "TBD – Industry A"
      flow_mgd: null
      BOD5_lb_d: null
      TSS_lb_d: null
      TN_lb_d: null
      TP_lb_d: null
      NH3_lb_d: null
process_unit_governing_values:
  mapping_rules:
    headworks_hydraulics: "PHF/PHDF"
    primary_treatment: "MDDF (or MWDF if specified by authority)"
    secondary_biological: "MDDF (nutrient loads as applicable)"
    tertiary_filtration: "MDDF (or filter loading per criteria)"
    disinfection_hydraulics: "PHF/PHDF"
    solids_handling: "Loads at MDDF; include seasonality if required"
qa_checks:
  - "All tables present and cross-referenced in text"
  - "Units consistent with YAML 'units'"
  - "Values rounded per 'assumptions.rounding'"
  - "Regulatory citations match 'regulatory.citations' tags/titles"
---

# Chapter 4. {{chapter_title}}

> **Purpose.** Establish defensible population projections and translate them to design flows and pollutant loadings for the new WWTP, consistent with Washington State Ecology (AKART/WAC), federal guidance, and recognized industry standards.

## 4.1 Data Sources and Key Assumptions
- **Service Area:** {{service_area.description}}
- **Planning Horizon:** {{planning_horizon.start_year}}–{{planning_horizon.end_year}} (checkpoints: {{planning_horizon.intermediate_years}})
- **Primary Data Sources:** {{#each data_sources.quantitative_sources}}{{name}}; {{/each}}
- **Regulatory References:** {{#each regulatory.citations}}{{tag}} – {{title}}; {{/each}}
  
**Table 4-1. Input Assumptions and Units**

| Item | Value | Unit | Notes |
|---|---:|---|---|
| Persons per EDU | {{population_methods.edu_housing_unit.persons_per_edu}} | persons/EDU | |
| Per Capita Flow | {{population_methods.per_capita.factors.flow_gpcd}} | gpcd | |
| GWI Allowance | {{I_I.gwi_allowance_gpad}} | gpad | |
| RDII Method | {{I_I.rdii_method}} | — | {{I_I.monitoring_summary}} |
| Peaking Method | {{peaking.method}} | — | See §4.4 |
| Safety Factors | flow×{{safety_contingency.flow_multiplier}}, load×{{safety_contingency.load_multiplier}} | — | |

## 4.2 Population Projection Methods
Briefly describe each method and present the series.

**Table 4-2. Population Projections by Method (persons)**

| Year | Per Capita | EDU/HU | Employment | Regression | Cohort/Official |
|---:|---:|---:|---:|---:|---:|
| {{planning_horizon.start_year}} | TBD | TBD | TBD | TBD | TBD |
| {{planning_horizon.intermediate_years[0]}} | TBD | TBD | TBD | TBD | TBD |
| {{planning_horizon.intermediate_years[1]}} | TBD | TBD | TBD | TBD | TBD |
| {{planning_horizon.intermediate_years[2]}} | TBD | TBD | TBD | TBD | TBD |
| {{planning_horizon.end_year}} | TBD | TBD | TBD | TBD | TBD |

**Selection Rationale.** {{reconciliation.rationale}}

**Table 4-3. Selected Planning Population (persons)**

| Year | Selected Series |
|---:|---:|
| {{planning_horizon.start_year}} | TBD |
| {{planning_horizon.intermediate_years[0]}} | TBD |
| {{planning_horizon.intermediate_years[1]}} | TBD |
| {{planning_horizon.intermediate_years[2]}} | TBD |
| {{planning_horizon.end_year}} | TBD |

## 4.3 I/I Characterization (BWF, GWI, RDII)
Explain monitoring and allowances; distinguish dry vs. wet weather components.

**Table 4-4. I/I Allowances and Components**

| Component | Basis | Value | Unit |
|---|---|---:|---|
| BWF (Base Wastewater Flow) | Per-capita/EDU | TBD | mgd |
| GWI (Groundwater Infiltration) | {{I_I.gwi_allowance_gpad}} gpad × acres | TBD | mgd |
| RDII (Rainfall-Dependent I/I) | {{I_I.rdii_method}} | TBD | mgd |

## 4.4 Flow Projections and Peaking
Define equations; state peaking approach (Harmon/Ten States/fixed). Show example equation once and define symbols.

**Table 4-5. Average Day Flow (ADWF/DADF) by Year**

| Year | Population | ADWF (mgd) | Notes |
|---:|---:|---:|---|
| {{planning_horizon.start_year}} | TBD | TBD | |
| ... | ... | ... | |
| {{planning_horizon.end_year}} | TBD | TBD | |

**Table 4-6. Peaking Factors and Design Flows**

| Year | PF_MD (–) | MDDF (mgd) | PF_PH (–) | PHF/PHDF (mgd) | MWDF (mgd)\* |
|---:|---:|---:|---:|---:|---:|
| {{planning_horizon.start_year}} | TBD | TBD | TBD | TBD | TBD |
| ... | ... | ... | ... | ... | ... |
| {{planning_horizon.end_year}} | TBD | TBD | TBD | TBD | TBD |

\* Use MWDF only if required by the authority/criteria; otherwise mark n/a.

## 4.5 Pollutant Loadings (BOD₅, TSS, TN, TP, NH₃–N)
State L = Q × C; identify concentration or per-capita/EDU basis; explain ammonia partitioning assumptions.

**Table 4-7. Basis for Load Calculations**

| Constituent | Basis (per-capita/EDU/conc.) | Value | Units |
|---|---|---:|---|
| BOD₅ | per-capita or concentration | TBD | lb/d or mg/L |
| TSS  | per-capita or concentration | TBD | lb/d or mg/L |
| TN   | per-capita or concentration | TBD | lb/d or mg/L |
| TP   | per-capita or concentration | TBD | lb/d or mg/L |
| NH₃–N | per-capita or concentration | TBD | lb/d or mg/L |

**Table 4-8. Projected Loadings at Design Flows (Base Season)**

| Year | ADWF (mgd) | BOD₅ (lb/d) | TSS (lb/d) | TN (lb/d) | TP (lb/d) | NH₃–N (lb/d) |
|---:|---:|---:|---:|---:|---:|---:|
| {{planning_horizon.start_year}} | TBD | TBD | TBD | TBD | TBD | TBD |
| ... | ... | ... | ... | ... | ... | ... |
| {{planning_horizon.end_year}} | TBD | TBD | TBD | TBD | TBD | TBD |

**Table 4-9. Seasonal Adjustments (if applicable)**

| Season | Flow Multiplier | Concentration/Load Notes |
|---|---:|---|
| Annual | 1.00 | — |
| Max Month | TBD | e.g., temperature effects |
| Wet Weather | TBD | RDII effects |
| Dry Weather | TBD | — |

## 4.6 Safety/Contingency Factors
Describe and apply the multipliers set in YAML; note rationale (AKART/CSWD prudence).

## 4.7 Governing Design Values by Process Unit
Explain mapping rules from YAML and present the governing values.

**Table 4-10. Governing Design Values by Process Unit**

| Process Unit | Governing Flow/Load Basis | Value | Unit | Notes |
|---|---|---:|---|---|
| Headworks/Hydraulics | {{process_unit_governing_values.mapping_rules.headworks_hydraulics}} | TBD | mgd | |
| Primary Treatment | {{process_unit_governing_values.mapping_rules.primary_treatment}} | TBD | mgd | |
| Secondary Treatment | {{process_unit_governing_values.mapping_rules.secondary_biological}} | TBD | mgd & lb/d | |
| Tertiary/Filtration | {{process_unit_governing_values.mapping_rules.tertiary_filtration}} | TBD | mgd | |
| Disinfection | {{process_unit_governing_values.mapping_rules.disinfection_hydraulics}} | TBD | mgd | |
| Solids Handling | {{process_unit_governing_values.mapping_rules.solids_handling}} | TBD | lb/d | |

## 4.8 Scenario/Sensitivity Analysis
If scenarios are defined, summarize Base/Low/High effects on sizing.

**Table 4-11. Scenario Comparison (End Year)**

| Scenario | Planning Pop. | ADWF (mgd) | MDDF (mgd) | PHF (mgd) | BOD₅ (lb/d) | TN (lb/d) |
|---|---:|---:|---:|---:|---:|---:|
| Base | TBD | TBD | TBD | TBD | TBD | TBD |
| Low  | TBD | TBD | TBD | TBD | TBD | TBD |
| High | TBD | TBD | TBD | TBD | TBD | TBD |

## 4.9 Regulatory Conformance Checklist
- {{#each regulatory.citations}}**{{tag}}** — {{title}}: Conformance notes (TBD).{{/each}}

## 4.10 Assumptions, Uncertainties, and Monitoring/Refinement Plan
Summarize key assumptions, data gaps, and how future monitoring/model updates will refine projections.

## 4.11 Recommendations
Concise bullets on design allowances, data collection priorities, and submittal needs.

## 4.12 References
List sources from YAML and any local plans/records used.

> *End of Chapter 4.*
