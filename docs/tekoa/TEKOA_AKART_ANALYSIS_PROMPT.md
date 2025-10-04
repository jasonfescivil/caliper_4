# Enhanced AKART Analysis Prompt for Town of Tekoa, WA

## Corrected CLI Command

```bash
poetry run caliper_v2 agent "Prepare a complete AKART analysis for the Town of Tekoa, WA (2025 population ≈ 820; 20-yr planning pop ≈ 950). The Town operates an aging oxidation-ditch package plant that averages 0.07 MGD (2015-2025 DMR record) and discharges intermittently to Hangman Creek. DELIVERABLES: 1) DMR-based design calculations – Derive ADF, MMF (30-day), MDF (7-day), PHF (use Peaking Factor curves for small systems in Orange Book Table 3-1); compute per-capita and total loads for BOD5, TSS, TKN, NH3-N, and TP; include seasonal temperature corrections for winter wastewater temps as low as 8°C (eastern-WA climate). 2) AKART evaluation workflow – Step-by-step process that satisfies WAC 173-240-130 (engineering reports) and the AKART requirements in WAC 173-200-080(4)(d); provide a fill-in matrix for technology screening, life-cycle cost (present worth), operator skill, land, and cold-weather performance. 3) Candidate technologies for <0.10 MGD, cold climate – Summarize aerated lagoon + winter storage & land application, Biolac-type extended-aeration lagoon, modular SBR, oxidation-ditch upgrade, and facultative lagoon + wetland polishing; cite secondary (30/30/10/1) vs. advanced effluent limits under WAC 173-221 and cold-weather design tips from EPA Design Manual and MOP 8. 4) Down-selection logic – Show how to narrow the list to two planning-level alternatives (e.g., Lagoon + Irrigation vs. SBR + Creek Outfall) using a weighted scoring matrix and 20-year net-present-worth comparison at 3% discount rate per State RCW 39.94. 5) Data gaps & next steps – List additional data needed beyond DMRs including I/I analysis per EPA criteria (>120 gpcd base infiltration or >275 gpcd total), soil percolation tests for land application per WAC 173-240-050, groundwater mounding analysis, 7Q10 flow for Hangman Creek, effluent toxicity for ammonia limits, operator certification requirements per WAC 173-230, and Spokane River TMDL implications for nitrogen. Include specific references to: Criteria for Sewage Works Design (Orange Book, 2008), Tables 3-1 (peaking factors), G3-5 (small system curves), Section G3-1.1.3 and G3-4 (AKART for mixing zones); WAC 173-200-080(4)(d) (AKART definition); WAC 173-240-130 (engineering report requirements); WAC 173-221-040 (technology-based limits); EPA Process Design Manual for Land Treatment (2006); WEF MOP 8 (cold weather operations); and coordination requirements with Ecology Eastern Regional Office." --indexes "federal,state,design_standards,technical_reports" --verbose > tekoa_akart_analysis.md
```

## Key Enhancements Added:

### 1. **Specific Numeric Standards**
- Secondary limits: 30/30/10/1 (BOD/TSS/TN/TP mg/L)
- EPA I/I thresholds: >120 gpcd infiltration, >275 gpcd total
- Discount rate: 3% per State requirements

### 2. **Additional Regulatory Context**
- **Spokane River TMDL** - Critical for nitrogen limits since Hangman Creek is a tributary
- **WAC 173-230** - Operator certification requirements
- **WAC 173-240-050** - Land application site criteria
- **WAC 173-221-040** - Technology-based effluent limits

### 3. **Technical References**
- Orange Book **Table 3-1** - Peaking factors by flow range
- Orange Book **Table G3-5** - Small system specific curves
- **EPA Process Design Manual for Land Treatment (2006)** - For LA systems
- **WEF MOP 8** - Cold weather design and operations

### 4. **Planning-Level Cost Guidance**
Add request for:
- Capital cost curves for 0.10 MGD facilities
- O&M cost factors (power, chemicals, labor)
- 20-year life cycle per State funding requirements

### 5. **Hangman Creek Specific Issues**
- Intermittent discharge challenges
- Temperature impacts on ammonia toxicity
- Phosphorus limits due to lake downstream
- Flow augmentation requirements

## Alternative Focused Queries for Specific Topics:

### For DMR Analysis:
```bash
poetry run caliper_v2 query "How do you calculate design flows and loads from DMR data for a 0.07 MGD facility per Orange Book Table 3-1 and include temperature corrections for 8°C winter wastewater?" --index design_standards --search-mode hybrid --self-reflect
```

### For AKART Matrix:
```bash
poetry run caliper_v2 query "Provide an AKART evaluation matrix template per WAC 173-240-130 with scoring criteria for cost, performance, operability, and environmental impacts" --index state --self-reflect
```

### For Cold Weather Design:
```bash
poetry run caliper_v2 query "What are cold weather design considerations for lagoons and SBRs in eastern Washington with 8°C winter wastewater temperatures?" --index "technical_reports,design_standards" --search-mode hybrid
```

## Expected Comprehensive Output Structure:

1. **Executive Summary**
   - Current situation
   - Recommended alternatives
   - Planning-level costs

2. **Design Basis Memorandum**
   - Population projections
   - Flow projections with peaking
   - Mass loading calculations
   - Temperature corrections

3. **AKART Analysis**
   - Technology screening matrix
   - Fatal flaw analysis
   - Detailed evaluation of 4-5 options
   - Selection of 2 alternatives

4. **Planning-Level Designs**
   - Process flow diagrams
   - Preliminary sizing
   - Site requirements
   - Staffing needs

5. **Cost Analysis**
   - Capital costs (±30%)
   - O&M costs
   - 20-year present worth
   - Funding options

6. **Implementation Plan**
   - Permitting timeline
   - Design/construction schedule
   - Interim compliance measures
