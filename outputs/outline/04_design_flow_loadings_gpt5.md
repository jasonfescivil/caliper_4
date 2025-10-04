assistant: Below is a baseline worksheet you can use and tailor for a small (<1,000 people) municipal WWTP in Washington. Values and methods are tied to Ecology’s Orange Book (Criteria for Sewage Works Design), WAC 173‑240, and WEF MOP 8.

1) Flow definitions and which to use for design
- AADF (annual average design flow): “The average of the daily flow volumes anticipated to occur over a calendar year.” Often used as the plant’s baseline average flow in reports and for peaking estimates when only average data exist [2][9].
- MWDF (maximum week design flow): “Largest volume of flow anticipated to occur during a continuous 7‑day period, expressed as a daily average.” Facilities with only secondary limits must be able to fully biologically treat up to MWDF at all times [2][9].
- MDDF (maximum day design flow): “Largest volume of flow anticipated to occur during a one‑day period, expressed as a daily average.” Facilities with toxics limits must be able to fully biologically treat up to MDDF at all times [2][9].
- PHDF (peak hour design flow): “Largest volume of flow anticipated to occur during a one‑hour period” (hourly average). All units must hydraulically pass 100% of PHDF and PIDF without overtopping or causing backups, recognizing biological treatment may not be achievable at these peaks [9].
- PIDF (peak instantaneous design flow): Maximum instantaneous flow for hydraulic capacity checks [9].
- Note on ADWF: “Average Dry Weather Flow” is not explicitly defined in the Orange Book; use AADF for baseline and document how your dry‑weather data subset relates to AADF in the engineering report per WAC 173‑240‑060 [2][16].

2) Which design flows apply to each unit (Ecology Table G2‑1)
- Biological reactors: design biological capacity at MWDF (secondary) and MDDF when toxics limits apply [1].
- Primary/secondary clarifiers: hydraulic checks at PHDF + recirculation; solids loading at PHDL [1].
- Plant liquid pumping and conveyance: PIDF [1].
- Filters/screens (liquid stream): pass all flows (per applicable duty) [1].
- Disinfection: MDDF (disinfection requirements) and PHDF (hydraulics) for non‑reuse; all flows for reuse/reliability class I [1].
- Equalization/surge: use continuous flow routing to ensure downstream hydraulic limits are not exceeded [1].

3) Baseline per‑capita planning values (Ecology Table G2‑2; includes “normal infiltration”)
- Flow: 100 gpd/person (includes normal infiltration) [3][12].
- BOD5 load: 0.2 lb/person‑day [3].
- TSS load: 0.2 lb/person‑day [3].
- For TN/NH3/TP: not specified in Table G2‑2. Use local data per WAC 173‑240‑060; if no data, WEF MOP 8 provides example influent concentrations used in a design case (TKN 30 mg/L; TP 7 mg/L) as planning surrogates, noting these are examples and not universal [13][6][16].

4) Baseline computations (set service population = P persons)
- Average flow (AADF ≈ ADWF baseline): Qavg = P × 100 gpd/person (includes normal infiltration) [3][12].
- BOD5 load: LBOD = P × 0.2 lb/d [3].
- TSS load: LTSS = P × 0.2 lb/d [3].
- TN/TKN, NH3‑N, TP: compute from measured concentrations and flow per WAC 173‑240‑060 (the engineering report must present at least one year of credible flow/loading data and assess seasonal/diurnal variability) [16]. If adopting WEF MOP 8 example as an interim planning placeholder: TKN ≈ 30 mg/L; TP ≈ 7 mg/L; calculate mass loads from concentration × flow (replace with site data at design) [13][16]. NH3‑N must be characterized because ammonia is a toxic pollutant commonly present in municipal discharges; evaluate per WAC/Orange Book requirements [7].

Example (illustrative only; replace with project P and site data)
- If P = 1,000 persons: Qavg ≈ 100,000 gpd (~0.10 mgd); LBOD ≈ 200 lb/d; LTSS ≈ 200 lb/d [3]. TN/TKN, NH3‑N, TP loads require site concentrations (or documented planning assumptions) applied to Qavg per standard mass balance methods [16][13].

5) Peaking method and seasonality
- Peaking flows: If only AADF is known, Ecology allows estimating PHDF/PIDF using “standard peaking factors” (see Figure C1‑1, Ch. C1) [9]. You may also use Ten States peaking guidance as a commonly used reference, with the Orange Book’s caution that such standards are not absolute and must be applied with professional judgment [6][9]. Harmon method is not cited in the provided sources.
- Choose and document peaking method (Ecology C1 factors or Ten States) and justify in the engineering report; base final design on whichever (average vs peak) is controlling [1][3][16].
- Seasonality: The engineering report must assess diurnal and seasonal flow and loading variability [16]. MOP 8 illustrates that maximum month loads may occur in warm or cold seasons and shows temperature effects on process sizing (e.g., 12–20°C) [13].

6) Wet‑weather flow disaggregation (for planning and I/I control)
- Separate and quantify: Base Wastewater Flow (BWF), Groundwater Infiltration (GWI), and Rainfall‑Derived I/I (RDII) using measured data. Ecology requires characterization of I/I and a plan to eliminate/handle excessive I/I to avoid inadequately treated discharges or process impairment [3][16]. Design flow determinations must consider wet‑weather flows and recycles [1][3].
- Note: the 100 gpd/person planning flow includes “normal infiltration” per Table G2‑2; quantify GWI/RDII above “normal” with field data and incorporate into MWDF/MDDF/PHDF/PIDF as appropriate [12][16].

7) Biological treatment capacity and hydraulics expectations (Ecology)
- Must fully biologically treat up to MWDF (secondary limits) and up to MDDF where toxics limits apply [2][9][1].
- All units must be able to hydraulically pass 100% of PHDF and PIDF without overtopping or causing more than minor backups; biological treatment may not be achievable at these instantaneous rates [9].
- Where needed to cost‑effectively achieve biological treatment between MMDF and MDDF, consider step‑feed, EQ, SVI control, I/I reduction, adequate clarifier sizing (Ecology measures) [9].
- If peak hour plant flow and solids loading are ≥3× average dry‑weather values, provide multiple parallel trains [1][9].

8) Safety factors and data quality
- Engineer must justify an appropriate safety factor to ensure compliance with permit and WQS at maximum flow/loading conditions [1].
- Re‑rating/data‑based loading: test data must be statistically validated at 95% confidence; Ecology may require larger safety factors for high peaking or variable results [10].
- Use Ecology‑accredited labs for chemistry and properly calibrated meters for flow; include at least one year of data and explicitly identify sampling locations, sample types, and locations of return streams in the report [16][7].

9) Regulatory anchors and compliance expectations
- AKART and WQS: Domestic wastewater must receive AKART; for domestic facilities AKART is secondary treatment (Ch. 173‑221 WAC). Where technology‑based standards are insufficient to meet WQS, more stringent requirements apply (Ch. 173‑201A WAC; mixing zones, toxics criteria) [15][8].
- Treatment regulations and design loadings: Ecology requires sizing and operating to meet permit limits under defined design flows (MWDF for secondary; MDDF for toxics) [2][9].
- Engineering report content (WAC 173‑240‑060): must include present/future quantity and quality, I/I analysis, diurnal/seasonal variation, and be sufficiently complete for P&S without substantial changes [16].
- General sewer plan (WAC 173‑240‑050): service boundaries, flows, I/I problems and remedies, alternatives, costs, and compliance statements [17].
- NPDES and permits: Nearly all municipal WWTPs discharging to surface waters must have an NPDES permit; additional general permits may apply (e.g., Puget Sound Nutrient General Permit) [4].

10) How to apply this baseline to your plant
- Set P (people) and document current and projected populations for a 20‑year design life per Ecology [16].
- Compute Qavg ≈ P × 100 gpd/person (includes normal infiltration) [3][12].
- Estimate MWDF/MDDF/PHDF/PIDF using measured data; if unavailable, apply standard peaking factors per Ecology C1 and/or Ten States, with justification [9][6].
- Establish BOD5/TSS loads from Table G2‑2 (0.2 lb/person‑d each) [3].
- Establish TN/NH3/TP from plant data (required) and, if necessary, use interim planning surrogates from WEF MOP 8 examples with clear caveats and replacement by site data at design [13][16][6].
- Account for recycles/returns and wet‑weather surcharges in all unit process checks (see Table G2‑1 and bullets above) [1].
- Include safety factors and demonstrate compliance at maximum flow/loading conditions; consider EQ or process configuration changes if needed [1][9][10].

Selected supporting quotes
- “The biological treatment plant must treat all of the flows up to MWDF for secondary treatment limits, and up to MDDF for treatment plants with toxics.” [1][9]
- “All units must have the ability to hydraulically pass 100 percent of the PHDF…[and] PIDF…” [9]
- “The engineer must justify that the wastewater treatment plant design proposal includes an appropriate safety factor that ensures compliance with permit limits and water quality standards at the maximum flow and loading conditions.” [1]
- “The design organic loading should be computed in the same manner used in determining design flow.” [3]
- “The report must…include…characterization of waste loading…[and] Current I/I flows…Assessment of diurnal…[and] seasonal variations.” [16]
- “When the AADF is known, and PHDF and PIDF flows are not known…the AADF, in conjunction with standard peaking factors, may be used to estimate the PHDF and PIDF…” [9]
- MOP 8 cautions against viewing standards as absolute and provides example design influent concentrations (e.g., TKN 30 mg/L, TP 7 mg/L) for planning context [6][13].