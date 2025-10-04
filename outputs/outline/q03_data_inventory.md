assistant: Below is a concise data inventory and client-request checklist tailored to a small (<1,000 population) Washington WWTP feasibility. Each item lists the minimum span to collect and preferred formats (format is a request for analysis efficiency; underlying data needs are from the cited requirements). Citations point to the exact section and page where available.

Permits, compliance, and prior files
- NPDES permit, current and prior; fact sheet/statement of basis; any compliance orders. Span: current permit term. Format: PDF. [WAC 173-240-060(3)(d),(e); WAC 173-240-040(1)-(2) p.4][9]; [EPA Permit Writer’s Manual 4.6.1 p.63][11]
- Discharge Monitoring Reports (DMRs). Span: minimum 3 years (recordkeeping minimum) and, for flow analyses, past 3 years of monthly averages. Format: CSV/XLSX + PDFs of submitted DMRs. [40 CFR 122.41(j),(l)(4) as summarized in EPA PWM 8.4 p.179; 8.5 p.203][24][31]; [EPA PWM “Effluent flow” recommends using up to past 3 years for critical flow value selection p.133][38]
- Compliance inspection reports and correspondence. Span: current permit term (at least 3 years). Format: PDF. [EPA PWM 4.6.1 p.63][11]

Influent/effluent analytical data (lab)
- Plant influent and effluent chemistry and bacteria. Minimum: one full year of current flow and loading data; Ecology recommends >1 year. Include BOD5, TSS, pH, DO, temperature, pathogens, ammonia, and chlorine; identify sample locations and types; labs must be Ecology-accredited. Span: ≥12 months (prefer 24–36 months if available). Format: CSV/XLSX with metadata (methods, detection limits), PDFs of lab reports. [Orange Book, Engineering Report: 060(3)(c) data requirements and quality; “at least one full year” and Ecology-accredited lab; identify sampling locations/types p.48–49][18][12]; [Orange Book table aligning required pollutant analyses for compliance with WQS p.49][12]

Flows, levels, and hydraulics
- Influent and effluent flow time series; pump station flows; wet well levels. Minimum: one full year; include meter calibration/verification history. Span: ≥12 months (prefer 24–36 months). Resolution: 5–15 min if available. Format: CSV/XLSX; calibration certificates as PDF. [Orange Book 060(3)(c) “at least one full year” and meter calibration history p.48–49][18][12]; [WAC 173-240-060(3)(i) flow diagram/hydraulic profile for engineering report p.7][20]; [EPA PWM, use historical flows incl. past 3-year monthly averages when determining critical flows p.133][38]

SCADA historian and alarms
- SCADA tag trends for flows, levels, runtimes, starts, VFD speeds, chemical feeds, alarms; historian configuration and tag list. Span: ≥12 months. Format: CSV exports + tag dictionary. Purpose: supports “historical database management” and integrated control requirements. [Orange Book G2-6.4.6 DCS/SCADA design includes Historical Database Management and integrated functions p.89][2]

Power events and reliability
- Generator run logs, ATS/UPS transfer logs, outage/event logs, protective relay/ground fault events, restart/auto-restart records. Span: ≥12 months. Format: CSV/PDF. Purpose: assess electrical reliability and backup power per reliability criteria. [Orange Book G2-6.4 (UPS, switching, grounding) p.89][2]; [Orange Book G2-8 Reliability Classification; Electrical Power Sources p.89][2]

Rainfall and I/I inputs
- Local rainfall (tipping-bucket preferred) concurrent with flow period for RDII analysis; include station metadata. Span: ≥12 months covering wet season(s); resolution 5–15 min preferred. Format: CSV. Justification: I/I evaluation and RDII methods rely on rainfall/flow relationships. [EPA Guide—estimating I/I: methods for analyzing influent flows to assess I/I p.1][42]; [EPA I/I Review—defines RDII, SWMM methods; RDII quantification references p.8, p.28–29][34][41]
- Any prior I/I studies, SSES, SSOAP/SWMM models, smoke/TV inspections, manhole rehab records. Span: all available. Format: PDFs, model files. [WAC 173-240-060(3)(j) requires discussion of I/I, overflows, proposed corrections p.7][20]; [Ecology I/I Analysis reference noted in permit contexts (example) p.11][48]

Water use/billing and population
- Water consumption/billing by customer class (residential, commercial, institutional, seasonal) and connection counts; monthly. Span: ≥3 years. Format: CSV/XLSX. Purpose: flow projection, I/I screening, and conservation impacts. [Orange Book—future estimates must account for water conservation per RCW 90.48.495 p.49][12]; [Ecology Reclaimed Water Manual—water usage reports and water system plans may be used to estimate demands p.49][10]
- Population history and 20-year projections consistent with local planning. Span: last 20 years if available; projections for 20-year planning period. Format: PDF/CSV. [WAC 173-240-050(3)(e) population trend and design period p.6][13]; [Orange Book—future (20-year) estimates and planning basis p.49][12]

Septic/onsite systems and potential connections (if applicable)
- Inventory/map of onsite systems (OSS), LCSS/LOSS within or adjacent to service area; any plans to connect or satellite manage. Span: current inventory. Format: GIS shapefile/Geopackage + PDF lists. Note: Consult DOH for systems under 246-272B WAC; subsurface disposal planning intersects WAC 173-240-060(4). [Orange Book note re: Large On-site Sewage Systems and DOH coordination p.57][14]; [WEF MOP FD-16—SWIS applicability and regulation context p.72][32]

Asset records and maps (collection and treatment)
- GIS and as-builts: sewer mains (size, slope), manholes, force mains, pump stations, outfall(s), treatment units, discharge locations; water system features to 1,000 ft around facilities. Span: current. Format: GIS shapefile/Geopackage + PDFs. [WAC 173-240-050(3)(d)(ii)-(vi) layout maps for existing/proposed sewers, pump stations/force mains, topography, streams/outfalls; (vii) water systems p.4–6][9][27]; [WAC 173-219-210(2)(c) mapping potable sources within 1,000 ft (mapping practice useful even if not a reclaimed project) p.20][21]

Industrial users and pretreatment (if any)
- List of significant industrial users or other establishments producing industrial wastewater; flow/production schedules; characterization; pretreatment status. Span: current + any known future changes. Format: PDF/CSV. [WAC 173-240-050(3)(i) industrial establishments list p.6][13]; [WAC 173-240-060(3)(k) special provisions/pretreatment p.7][20]

Overflows/bypasses and CMOM/O&M
- SSO, bypass, upset logs; notifications plan; corrective actions; CMOM or equivalent program documents. Span: ≥3 years. Format: PDF/CSV. [WAC 173-240-060(3)(j) overflows and controls p.7][20]; [EPA PWM §122.41(l)(6) overflow notification planning; CMOM expectations p.201–203][23]

Design, operations, staffing, and testing
- Current O&M manual(s); staffing levels and certifications; onsite/lab testing capabilities/frequencies. Span: current. Format: PDF. [WAC 173-240-060(3)(o) staffing/testing; (3)(p) cost estimates; (3)(n) provision for future needs p.7][20]
- Process flow diagram and hydraulic profile for existing facilities. Format: PDF/CAD. [WAC 173-240-060(3)(i) p.7][20]

Past planning and design documents
- Latest approved General Sewer Plan; any amendments. Format: PDF. [WAC 173-240-050(1)-(3) p.4][9]; [Orange Book G1-3, content and objective of general sewer plans p.41][8]
- Engineering reports/facility plans; plans and specifications; as-builts. Format: PDF/CAD. [WAC 173-240-060 Engineering report p.6–7][13][20]; [WAC 173-240-070 Plans/specs p.7][20]
- Any SERP/SEPA/NEPA documents associated with prior projects. Format: PDF. [Orange Book SERP/NEPA alignment p.41][8]; [WAC 173-240-050(3)(n) SEPA/NEPA statement p.6][13]

Receiving water and outfall
- Outfall location, configuration, and prior outfall analyses. Format: GIS/PDF. [WAC 173-240-060(3)(l) detailed outfall analysis p.7][20]; [WAC 173-240-060(3)(e) receiving water description and WQS compliance p.6][13]

Preferred data formats (for efficient review; no prescribed regulatory file format)
- Tabular/time series: CSV or XLSX with clear headers, units, timestamps, and QA/QC flags.
- Spatial: ESRI shapefile or Geopackage with metadata; PDFs for plan/profile sheets.
- Reports/permits/lab packets: searchable PDF; include appendices.
- SCADA/historian: CSV exports per tag, with tag dictionary and engineering units.

Minimum spans summary (by citation)
- Influent/effluent flows and lab data: ≥12 months current data; more than one year recommended; include sampling locations/types; accredited labs; calibrated meters. [Orange Book 060(3)(c) p.48–49][18][12]
- DMRs/records: ≥3 years retained; flows often evaluated using past 3 years monthly averages. [EPA PWM 8.4, 8.5 p.179, p.203][24][31]; [EPA PWM “Effluent flow” p.133][38]
- Rainfall for I/I: ≥12 months including wet seasons to support RDII methods. [EPA I/I Guide p.1][42]; [EPA I/I Review (RDII/SWMM context) p.8, p.28–29][34][41]

Notes
- Ensure any estimates of future flows/loadings and alternatives consider 20-year planning and water conservation impacts. [Orange Book—future (20-year) estimates; RCW 90.48.495 consideration p.49][12]
- Engineering feasibility must be sufficiently complete to develop plans/specs without substantial changes. [WAC 173-240-060(2) p.6; Orange Book interpretation p.48][13][18]