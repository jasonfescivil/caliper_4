assistant: Below is a concise, citation‑rich baseline you can adapt for a small (<1,000 PE) municipal WWTP in Washington. It reflects Ecology’s Orange Book, WAC 173‑240 planning/report requirements, AKART, and WEF MOP 8.

Design flow definitions and what controls
- Required design flow terms (Ecology Orange Book):
  - AADF: “Annual Average Design Flow” [2], [9].
  - MMDF: “Maximum Month Design Flow” [2], [9].
  - MWDF: “Maximum Week Design Flow” [2], [9].
  - MDDF: “Maximum Day Design Flow” [2], [9].
  - PHDF: “Peak Hour Design Flow” [9].
  - PIDF: “Peak Instantaneous Design Flow” [9].
- What must be treated/passed:
  - “The biological treatment plant must treat all of the flows up to MWDF for secondary treatment limits, and up to MDDF for treatment plants with toxics” [1], [2].
  - “All units must have the ability to hydraulically pass 100 percent of the PHDF flow … [and] 100 percent of the PIDF flow …” (no overtopping/backups) [9].
- When only AADF is known, Ecology allows estimating PHDF and PIDF “with standard peaking factors” (see C1) [9].
- Note on ADWF: Orange Book references “average dry weather flow” (ADWF) in the parallel‑trains requirement but does not separately define it in G2; use AADF/MMDF/MWDF/MDDF/PHDF/PIDF definitions above, and apply the parallel‑trains criterion based on ADWF as referenced by Ecology [1], [2], [9].

Parallel trains and equalization triggers
- If peak hour flow and solids loading are ≥3× the ADWF and dry‑weather loadings, “multiple parallel trains” are required [1].
- Equalization/surge basins must be checked by “continuous flow routing analysis” to ensure discharges do not exceed downstream hydraulic limits [1].

Flow components (separate and document)
- Base domestic flow: For new systems, default per‑capita flow is 100 gpd/person; “includes normal infiltration” per Ecology’s design‑basis table [3], [12].
- Infiltration/Inflow (I/I): Identify and plan to eliminate/handle excessive I/I so as not to impair treatment; analyze diurnal and seasonal variability, and include combined sewer contributions if present [3], [16]. Account for possible climate‑change impacts on unmitigated I/I in future estimates [7].
- Wet‑weather flows, plant recirculation, and in‑plant recycle flows must be included when determining design flows [1], [3].
- Note: The provided sources discuss I/I generically; specific subcomponents such as GWI and RDII are not defined in the cited excerpts. Track and report base sanitary plus I/I consistently with Ecology’s requirements [1], [3], [16]. Unknown in these citations: formal definitions for BWF/GWI/RDII breakdown.

Baseline per‑capita design inflow and domestic organic loads (new systems)
- Per Ecology Table G2‑2 (new dwellings):
  - Flow: 100 gpd per person (includes normal infiltration) [3], [12].
  - BOD5: 0.2 lb/person‑day [3].
  - TSS: 0.2 lb/person‑day [3].
- For small systems without credible local data, use the above for base sanitary design and then apply peaking per [9] and add I/I/recirculation as warranted by planning and collection‑system data [3], [16].

Peaking method
- Ecology: When AADF is known but PHDF/PIDF are not, estimate with “standard peaking factors” (see C1) [9]. Document selected peaking factors in the engineering report and justify with monitored data where available [16].
- WEF MOP 8 cautions that published standards (e.g., “Ten States Standards”) are guidelines, not absolute values; use engineering judgment and site data when selecting design/peaking parameters [6].

Compute design loadings (method and where defaults exist)
- Use observed data where available; Ecology requires credible data (accredited lab; calibrated meters), with analysis of diurnal/seasonal variability and return streams [16]. EPA/WEF methods may be used to translate concentrations and flows into mass loadings (see MOP 8 example basis using flow and concentration to compute kg/d loads) [13].
- BOD5/TSS (domestic baseline for new systems):
  - BOD5 load = 0.2 lb/person‑day × population [3].
  - TSS load = 0.2 lb/person‑day × population [3].
- TN/TKN, TP, NH3‑N:
  - Use site‑specific concentrations and flows to compute mass loadings (Load = Flow × Concentration in consistent units), as illustrated in MOP 8 (example lists BOD5, TSS, TKN, TP flows and mass loads for design conditions) [13].
  - If no credible data exist, these loadings are unknown in the cited standards; collect at least one full year of monitoring to establish defensible design values and variability [16]. Include seasonality (temperatures; warm/cold condition maxima may differ) [13].

Seasonality and variability to capture
- Analyze and design for:
  - Peak flow rates sustained long enough to affect detention time and hydraulics [1], [3].
  - Diurnal and seasonal variations in flow and loading [16].
  - Process temperature ranges and seasonal maximum‑load timing (MOP 8 example shows 12–20°C and notes max month can occur in warm or cold seasons) [13].
  - Wet‑weather and I/I impacts, including potential climate‑change effects on I/I [1], [3], [7].

Assignment of design flows to unit processes (Ecology Table G2‑1 summary)
- Biological reactors:
  - Design for MWDF and corresponding MWDL to meet secondary limits [1].
  - For facilities with toxics limits, design for MDDF and corresponding MDDL [1], [2].
- Clarifiers: Size for PHDF plus recirculation for hydraulic rates and for peak solids loading (PHDL) [1].
- Pumps/flow structures: PIDF [1].
- Disinfection: Use MDDF for disinfection requirements and PHDF for hydraulics (non‑reuse/non‑Class I plants) [1].
- Aeration: Size oxygen transfer for peak BOD/TKN loading (PHDL) [1].
- Equalization: Perform continuous routing analysis to not exceed downstream hydraulic limits [1].

Safety factors and performance expectations
- “In all cases, the engineer must justify that the wastewater treatment plant design proposal includes an appropriate safety factor” to ensure compliance at maximum flow/loading [1].
- Ecology requires statistical validation of test data at 95% confidence, and “larger safety factors” when peaking is high or variability is high [10].
- Associated requirements to achieve biological treatment between MMDF and MDDF include I/I reduction, step‑feed, contact‑stabilization, adequate clarifier sizing, and SVI control [9].

Planning, reporting, and regulatory anchors (citations to include in submittals)
- WAC 173‑240 (planning/engineering report):
  - General sewer plan content and need; sufficiently complete to proceed to design [17].
  - Engineering report must quantify present/future flows and waste strength; include I/I assessment; diurnal/seasonal variability; industrial contributions; sampling locations/methods; future 20‑year projections; climate‑change impacts on I/I [16], [7].
- AKART and water‑quality compliance:
  - AKART applies; for domestic wastewater AKART is secondary treatment (Ch. 173‑221 WAC), but more stringent treatment may be required to meet water‑quality standards; mixing zones and antidegradation per Ch. 173‑201A WAC [15], [8].
- Treatment regulations and design loading framework (Ecology Orange Book G2‑1.2): MWDF/MDDF definitions and treatment expectations [2], [9].
- Permitting context (NPDES, general permits as applicable): Ecology issues NPDES permits and may require additional general permits (e.g., Industrial Stormwater; Puget Sound Nutrient General Permit) depending on discharge and location [4].
- WEF MOP 8: Use as technical guidance and for design examples; treat “standards” like Ten States as guidelines, not absolutes; apply engineering judgment and site data [6], [13].

Short, adaptable baseline template (fill with your project’s numbers)
- Population served (design year): [insert], per WAC 173‑240 and sewer plan [17], [16].
- Base sanitary flow (new systems): Qbase = 100 gpd/person × population (includes normal infiltration) [3], [12].
- I/I allowance: [insert method/data basis]; document wet‑weather, diurnal, seasonal variability; plan to reduce excessive I/I [3], [16], [7].
- AADF: [compute/document] [2], [9].
- MWDF: [define per data/forecast] [2], [9].
- MDDF: [define per data/forecast] [2], [9].
- PHDF and PIDF: [estimate from monitored data; or from AADF using standard peaking factors per C1] [9].
- BOD5 load: 0.2 lb/person‑day × population (new systems baseline) [3]; verify/adjust with monitoring [16].
- TSS load: 0.2 lb/person‑day × population (new systems baseline) [3]; verify/adjust with monitoring [16].
- TN/TKN, NH3‑N, TP loads: derive from measured concentrations × design flows for AADF/MMDF/MWDF/MDDF; include seasonal ranges (per MOP 8 approach) [13], [16]. Unknown defaults in the cited standards; collect data.
- Unit‑process assignment of design flows/loadings: per Table G2‑1 (biological reactors at MWDF/MDDF; clarifiers at PHDF+recirc and PHDL; pumps at PIDF; disinfection at MDDF for disinfection and PHDF hydraulics; aeration at PHDL) [1].
- Parallel trains: required if peak hour flow and solids loading ≥3× ADWF/dry‑weather load (per Ecology) [1].
- Equalization: verify via continuous flow routing [1].
- Safety factor: document basis; meet 95% confidence on test data; increase for high peaking/variability [10], [1].

Key quotes to include for context
- “The biological treatment plant must treat all of the flows up to MWDF for secondary treatment limits, and up to MDDF for treatment plants with toxics.” [1]
- “All units must have the ability to hydraulically pass 100 percent of the PHDF … [and] 100 percent of the PIDF …” [9]
- “If the peak hour treatment plant flow and solids loading values are at least three times the average dry weather flow and loading values, multiple parallel trains … must be included …” [1]
- “Testing data analysis must include statistical validation at a 95% confidence level… Ecology will require larger safety factors for systems that have high peaking factors or for testing results with a high degree of variability.” [10]
- “The process design of treatment units should be based on either the average design flow or the peak design flow, whichever is controlling,” considering wet‑weather flows and recycle flows [1], [3].

References to cite in your submittal
- Ecology Orange Book, General Considerations and Design Loading (G2‑1.2: definitions, associated requirements; Table G2‑1 design condition summary) [2], [9], [1].
- Ecology Orange Book, Design Basis for New Sewage Works (Table G2‑2) [3], [12].
- Ecology Orange Book, Engineering report content and data quality (G1; WAC 173‑240‑060 guidance) [16], [7].
- WAC 173‑240‑050/‑060 (planning/report content; sufficiently complete; population/flow/quality; I/I) [17], [16].
- AKART and water quality: Ch. 173‑221 WAC, Ch. 173‑201A WAC (as summarized in Orange Book) [15], [8].
- WEF MOP 8: design caution on “standards” and example approach to compute loads from flow and concentration with seasonal temperatures [6], [13].
- NPDES and related permits context [4].