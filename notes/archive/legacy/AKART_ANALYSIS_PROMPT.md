# AKART Analysis for Small Eastern Washington Community

## Comprehensive CLI Command

```bash
poetry run caliper_v2 agent "I need to perform an AKART analysis for a town of 820 people in eastern Washington. I have DMR data with once-daily recordings of influent/effluent parameters. Please provide: 1) A complete list of calculations needed from DMR data to size treatment options (including design flows, BOD/TSS/nitrogen/phosphorus loads, peaking factors, and temperature corrections for eastern WA climate), 2) Step-by-step AKART evaluation process per Washington State requirements including screening criteria, 3) Typical treatment technologies suitable for communities under 1000 people in cold climates, 4) How to narrow options to 2 alternatives for facility planning level analysis, 5) What additional data beyond DMR reports is needed for preliminary sizing. Include specific WAC and EPA design manual references." --indexes "federal,state,design_standards,technical_reports" --verbose
```

## Alternative Focused Queries

If the comprehensive query is too broad, break it into these focused queries:

### 1. DMR Data Analysis Requirements
```bash
poetry run caliper_v2 query "What calculations are required from DMR discharge monitoring reports to determine design flows and loads for wastewater treatment plant sizing? Include peaking factors, temperature corrections, and population projections." --index "federal,design_standards" --search-mode hybrid --self-reflect
```

### 2. AKART Requirements and Process
```bash
poetry run caliper_v2 query "What is the AKART analysis process per WAC 173-240 and how do you evaluate treatment alternatives for small communities under 1 MGD?" --index state --search-mode hybrid --self-reflect
```

### 3. Small Community Treatment Options
```bash
poetry run caliper_v2 agent "What wastewater treatment technologies are suitable for communities of 800-1000 people in eastern Washington with cold winters? Consider lagoons, SBR, oxidation ditches, and constructed wetlands. Include pros/cons and typical costs." --indexes "state,design_standards,technical_reports"
```

### 4. Facility Planning Requirements
```bash
poetry run caliper_v2 query "What are the requirements for facility planning and preliminary engineering reports for small wastewater systems per EPA and Washington state?" --index "federal,state" --self-reflect
```

## Key Information the System Should Provide:

### From DMR Data Calculations:
- Average daily flow (ADF)
- Maximum monthly flow (MMF)
- Peak hourly flow (PHF) using peaking factors
- BOD5 loading (lbs/day)
- TSS loading (lbs/day)
- TKN/Ammonia loading
- Total Phosphorus loading
- Temperature statistics (important for eastern WA)
- Per capita flow and load calculations

### AKART Evaluation Criteria:
- WAC 173-240 requirements
- Technology screening matrix
- Life cycle cost analysis
- Environmental impacts
- Operator requirements
- Land requirements
- Cold weather performance

### Suitable Technologies for 820 people:
- Facultative lagoons (with seasonal discharge)
- Aerated lagoons
- Sequencing Batch Reactors (SBR)
- Oxidation ditches
- Constructed wetlands (summer polishing)
- Package plants

### Narrowing to 2 Alternatives:
- Initial screening (fatal flaws)
- Comparative scoring matrix
- Present worth analysis
- Community acceptance
- Regulatory feasibility

## Expected Outputs:

The agent should provide:
1. **Calculation templates** for DMR data analysis
2. **AKART evaluation matrix** template
3. **Technology fact sheets** for small communities
4. **Cost curves** for planning level estimates
5. **Regulatory citations** for each requirement
6. **Example calculations** for 820 PE system

## Pro Tips:

- Use `--verbose` to see the agent's reasoning process
- The agent will search multiple indexes to compile comprehensive information
- Export results to a file: `poetry run caliper_v2 agent "..." > akart_analysis.md`
- Follow up with specific queries on any topic that needs more detail
