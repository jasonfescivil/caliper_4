# Final Enhanced AKART Analysis Prompt for Tekoa with Indexed Documents

## Complete CLI Command

```bash
poetry run caliper_v2 agent "Prepare a complete AKART analysis for the Town of Tekoa, WA using the following indexed documents: 1) NPDES Permit WA0023141 (2014) and permit extension (2020) for current effluent limits and compliance requirements; 2) 2016 Ecology Noncompliance Notice for specific violations and corrective actions needed; 3) 2017 I&I Reduction Cost Estimate for infiltration/inflow baseline data and costs; 4) 2022 Tekoa Influent Station Survey Report for current facility condition; 5) Tekoa STP O&M Manual Addendum for operational issues; 6) 2022 Hangman Creek Receiving Water Study for stream conditions and TMDL requirements; 7) 2023 Tekoa Wastewater Facility Study for treatment performance data. Based on these documents, provide: DELIVERABLE 1 - Extract actual DMR data from the NPDES permit monitoring reports showing the 0.07 MGD average flow, calculate ADF, MMF, MDF, PHF using Orange Book Table 3-1 peaking factors, and determine actual influent/effluent BOD5, TSS, TKN, NH3-N, and TP loads from the facility study. Include temperature corrections for the documented 8°C winter wastewater temperatures. DELIVERABLE 2 - Develop AKART evaluation workflow that addresses the specific compliance issues from the 2016 noncompliance notice while meeting WAC 173-240-130 requirements. Create evaluation matrix comparing: a) Oxidation ditch rehabilitation (current system), b) Aerated lagoon with winter storage and land application, c) SBR package plant replacement, d) Extended aeration lagoon (Biolac-type), e) Facultative lagoon with constructed wetland. Include the actual I&I flows from the 2017 study in sizing calculations. DELIVERABLE 3 - Using the Hangman Creek water quality data, determine if discharge limits need to be more stringent than secondary treatment (30/30) due to receiving water conditions, ammonia toxicity at 8°C, or Spokane River TMDL for phosphorus. Reference the permit's mixing zone provisions and any seasonal discharge restrictions. DELIVERABLE 4 - Apply actual cost data from the 2017 I&I study to develop planning-level cost estimates, using 20-year present worth at 3% discount rate. Score alternatives based on: ability to meet permit limits during 2016 violations, operator skill level per O&M manual issues, land requirements from facility study site plan, and cold weather reliability. DELIVERABLE 5 - Identify specific data gaps by comparing what's in the indexed documents versus what's needed for final design: missing DMR parameters, incomplete I&I flow monitoring per EPA >120 gpcd criteria, soil percolation data for land application per WAC 173-240-050, updated 7Q10 for Hangman Creek, and coordination items with Ecology Eastern Regional Office based on the 2020 permit extension conditions. Include specific page references from the indexed documents and note any conflicting information between sources." --indexes "federal,state,design_standards,technical_reports,tekoa" --verbose > tekoa_akart_complete.md
```

## Key Document-Specific References Added:

### 1. **From NPDES Permit WA0023141**
- Current effluent limits
- Monitoring requirements
- DMR data availability
- Mixing zone provisions
- Special conditions

### 2. **From 2016 Noncompliance Notice**
- Specific violations to address
- Required corrective actions
- Timeline for compliance

### 3. **From 2017 I&I Cost Estimate**
- Actual infiltration rates
- Inflow volumes
- Cost data for improvements
- Baseline flow data

### 4. **From 2022 Influent Station Survey**
- Current equipment condition
- Capacity limitations
- Upgrade needs

### 5. **From Hangman Creek Study**
- Water quality parameters
- TMDL requirements
- Temperature data
- Flow statistics

### 6. **From O&M Manual Addendum**
- Operational challenges
- Staffing issues
- Equipment problems
- Process control needs

## Alternative Focused Queries Using Tekoa Documents:

### For Compliance History:
```bash
poetry run caliper_v2 query "What were the specific violations in the 2016 Tekoa noncompliance notice and what corrective actions were required?" --index tekoa --self-reflect
```

### For Actual Performance Data:
```bash
poetry run caliper_v2 query "What are the actual influent and effluent characteristics from Tekoa's oxidation ditch based on the facility study and DMR data?" --index tekoa --search-mode hybrid
```

### For Receiving Water Requirements:
```bash
poetry run caliper_v2 query "Based on the Hangman Creek receiving water study, what effluent limits are needed to protect water quality beyond standard secondary treatment?" --index tekoa --self-reflect
```

### For Cost Data:
```bash
poetry run caliper_v2 query "What were the cost estimates from the 2017 Tekoa I&I reduction study and how do they scale to full facility improvements?" --index tekoa
```

## Expected Enhanced Output:

The agent will now:
1. **Quote actual permit limits** from WA0023141
2. **Reference specific violations** from 2016
3. **Use real I&I data** from 2017 study
4. **Apply actual costs** where available
5. **Address known operational issues** from O&M manual
6. **Consider Hangman Creek conditions** from receiving water study
7. **Build on existing facility data** from 2023 study

This approach grounds the AKART analysis in Tekoa's actual situation rather than generic guidance!
