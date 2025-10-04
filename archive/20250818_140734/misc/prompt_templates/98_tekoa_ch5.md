# Engineering Judgement – Example Input and Ideal Output

## INPUT 

5	EXISTING AND PROJECTED WASTEWATER CHARACTERISTICS
(WAC 173-240-050(3)(h)(i))
5.1	Introduction
The wastewater generated within Tekoa primarily originates from domestic sources, composed primarily of single-family homes.  Additional contributions come from a mix of commercial and institutional sources: local businesses, schools, and public facilities. See Chapter 3 for a summary of the wastewater sources based on DMR data for the years 2022 through Spring 2025. There are no significant industrial discharges to the system nor are any planned at present. 
Wastewater treatment is a critical public health and environmental protection service, ensuring that effluent discharged to Hangman Creek meets stringent regulatory standards and minimizes impact on the aquatic environment. This is essential to protect public health, to preserve the ecological balance of receiving waters, and comply with environmental regulations. 
This chapter aims to accurately characterize existing wastewater flows and pollutant loads and to project these parameters for the 5 and 20-year planning period to inform this plan’s system evaluation as well as the design of any improvements resulting from the analysis. An accurate understanding of these characteristics is foundational for effective wastewater management. 
5.2	Wastewater Flow Characteristic Terms
Understanding various wastewater flow characteristics and pollutant loads is essential for evaluating the performance of the existing system and to design systems that are not only effective under average conditions but can also handle predictable extremes and withstand population or industry growth. Key terms used throughout this plan are defined in Table 5.2-1 below, along with their typical application in wastewater facility planning.
 
 
Table 5.2 1 Wastewater Flow Characterization Definitions
Parameter	Definition	Source 	Formula
AAF	Average Annual Flow - “The total annual volume divided by 365 days. This value is approximated by the mean of the twelve monthly average flows.”	EPA I&I Guidance. (2014)	Σ Qmonth / 12
ADF	Average Daily Flow - “The average of the daily flow volumes anticipated to occur over a calendar year”

	Ecology. (2008). “Orange Book”	Σ Q24h / n
AADF	Average Annual Design Flow - “The average of the daily flow volumes anticipated to occur over a calendar year.”
	Ecology. (2008). “Orange Book”	Design Planning Value
BOD₅	Five-Day Biochemical Oxygen Demand – “A measure of the amount of oxygen required to stabilize a waste biologically over a 5-d period.”	Metcalf & Eddy/AECOM. (2014)	
TSS	Total Suspended Solids - “Portion of total solids retained on a filter with a specified pore size, measured after being dried at a specified temperature…”	Metcalf & Eddy/AECOM. (2014)	
MWDF	Maximum Week Design Flow - The largest volume of flow anticipated to occur during a continuous 7-day period, expressed as a daily average.	Ecology. (2008). “Orange Book”	Observation
MMDF 	Maximum Month Design Flow - “The largest volume of flow anticipated to occur during a continuous 30-day period, expressed as a daily average.”	Ecology. (2008). “Orange Book”	Max 30-day rolling window through the design-years
MDDF 	Maximum Day Design Flow - “The largest volume of flow anticipated to occur during a one-day period, expressed as a daily average.”	Ecology. (2008). “Orange Book”	Observation of measured flows during design years
PHDF 	Peak Hour Design Flow - “The largest volume of flow anticipated to occur during a one-hour period, expressed as a daily or hourly average.”	Ecology. (2008). “Orange Book”	Measured or PHDF = PFhr × AADF
PIDF 	Peak Instantaneous Design Flow - “The maximum anticipated instantaneous flow.”	Ecology. (2008). “Orange Book”	Measured or PIDF = PFinst × AADF
PF	“Peaking Factor = ratio of peak hourly flow to average daily flow.”	Ecology. (2008). “Orange Book”	PF = QPHF / ADF
MWF	“Maximum Week Flow: highest 7-day average flow in one year.”	Tchobanoglous et al. (2003), Table 3-8	MWF = Σ Q7-d / 7
MMF	“Maximum Month Flow: highest 30-day average flow in one year.”	Tchobanoglous et al. (2003), Table 3-8	MMF = Σ Q30-d / 30


 
Table 5.2 2Wastewater I&I Analysis Definitions

Parameter	Definition	Source 	Equation / Derivation
ADW	Average Dry Weather Flow - “Flow during a period of extended dry weather (7–14 d) and seasonally high groundwater. Flow includes sanitary flow and infiltration, and excludes significant industrial and commercial flows (assumes no inflow during dry weather conditions).”	EPA I/I Guide (2014)	ADW = (Total DWF) / (Dry Period Length)
GWI	Groundwater Infiltration (GWI) – “…The average of the low nighttime flows (midnight to 6 am) per day for the same time period, minus significant industrial or commercial nighttime flows.”
Because the City doesn’t record hourly flow data, GWI was estimated using the Max Weekly Infiltration (MWI).  See below.	EPA I/I Guide (2014)	See MWI
BSF	Base Sanitary Flow – “The portion of wastewater which includes domestic, commercial, institutional, and industrial sewage and specifically excludes infiltration and inflow.” 	EPA I/I Guide (2014)	BSF = QADWF – QGWI
DWF	“All flow in a sewer (includes sanitary flow and infiltration) except that caused directly by rainfall. Measured during a period of extended dry weather (7 to 14 days) and seasonally high groundwater.”	EPA I/I Guide (2014)	QDWF = QS + QGWI
Infiltration	Infiltration – “Water other than sanitary wastewater that enters a sewer system from the ground through defective pipes, pipe joints, connections, or manholes. Infiltration does not include inflow.”	EPA I/I Guide (2014)	
Inflow	Inflow - “Water other than sanitary wastewater that enters a sewer system from sources such as roof leaders, cellar/foundation drains, yard drains, area drains, drains from springs and swampy areas, manhole covers, cross connections between storm sewers and sanitary sewers, and catch basins. Inflow does not include infiltration.”	EPA I/I Guide (2014)	
Total I/I 	“Infiltration plus inflow - total extraneous wastewater entering the system.”	40 CFR § 35.2005(b)(20–21)	QI/I = QDWF – BSF
Inflow Volume	Inflow Volume - “Total inflow volume for a single event: area between storm hydrograph & dry-weather hydrograph.”	EPA I/I Guide (2014)	∫(QI/I dt)
MWI	Maximum Weekly Infiltration – “The highest daily flow at seasonal high groundwater after a dry period of three days or more minus the base sanitary flow.”	EPA I/I Guide (2014)	Subtract BSF from highest daily flow after a dry period of three days or more during high seasonal groundwater.
AWWF	Average Wet-Weather Flow – “ arithmetic mean of daily flows during wet-weather periods.”

Wet weather understood to be from November to May for the purposes of this report.  	EPA Quick Guide (2014)	QAWWF = Σ Qwet / n
PWWF	Peak Wet-Weather Flow – “highest instantaneous flow during a storm (typically 2-hr peak).”	EPA Quick Guide (2014)	— (by observation)
RDII	“Rainfall-Induced Infiltration: short-term increase in infiltration as a result of rain.”	Tchobanoglous et al. (2003), Table 3-8	—
WWF	“Highest daily flow during & immediately after a significant storm event.”	Tchobanoglous et al. (2003), Table 3-8	— (by observation)

 
 
5.3	Wastewater Flow Summary
WAC 173-240-050(3)(g))
Discharge Monitoring Reports (DMRs) from 2022 through 2024 were analyzed to determine historical influent flows to WWTP for the design period. This data, which represents actual measured flows to and from the facility (taken daily), provides the basis for characterizing system hydraulics in this report. The flow data along with OFM population data, was used to generate Table 5.3-1, which summarizes total system flows, average daily flows, estimated total Equivalent Residential Units (ERUs), and the average daily flow per ERU. The table is followed by a
Table 5.3 1 Summary of Annual Wastewater Flow and ERUs 2022 to 2024 
Year	Total Flow Entire System 
(MG/Year)	Average Daily Flow (ADF) 
(gpd)	Total Equivalent Residential Units (ERU)	Average Daily Flow Per ERU 
(gpd/ERU)
2022	49.1	134,520	460	292
2023	42.87	117,452	460	255
2024	36.8	100,486	461	218

Guidance for ERU estimation and flow analysis was taken from {{ Cite_Guidance_Document, e.g., Washington State Department of Ecology's "Criteria for Sewage Works Design" (Orange Book) }}. The Orange Book provides standardized methodologies and typical values used in Washington State, ensuring consistency in engineering assessments. <<check>>
The average annual flow to the WWTP over this period was calculated to be {{ Calculated_Average_Annual_Flow }} gpd. This value is utilized for long-term operational planning, estimating annual O&M costs, and as a fundamental baseline for developing flow projections and assessing overall plant loading against its design capacity.
 
5.3.1	ERU Calculations
The amount of wastewater generated by a typical single-family home, the Equivalent Residential Unit (ERU) is a fundamental parameter in wastewater planning, representing the daily hydraulic contribution generated by a single home or dwelling.  The ERU flow was estimated in multiple ways to as a check against error and to account for the strengths and weaknesses of each method.  In facility plans, the ERU concept is used to normalize contributions from various types of connections (residential, commercial, institutional) to a common unit, which simplifies the process of projecting future wastewater flows based on anticipated growth in housing and commercial development. Because of the contribution from I&I and other factors such as the larger variety of uses which make up the commercial and industrial units, residential units are the simplest basis to use as a common basis. 
5.3.2	Wastewater ERU 
The rationale behind using winter water consumption data for estimating BSF is that outdoor water use, such as landscape irrigation, is minimal or nonexistent during these colder months. Additionally, while groundwater levels might be seasonally high (potentially increasing infiltration), the direct impact of rainfall-induced inflow is generally less compared to wetter storm seasons like spring, making winter flows more representative of sanitary contributions plus persistent infiltration. To account for the normal portion of metered winter water use which typically doesn’t end up in the wastewater system, a factor of .9 was applied to the BSF.

5.4	Inflow and Infiltration Analysis
5.4.1	Estimating Average Base Sanitary Flow (BSF)
According to Washington State OFM (WAOFM), a typical single-family home in Tekoa is estimated to have an average of 2.22 residents in 2024. Since the City doesn’t collect water meter readings in the winter due to snow and freezing, source (well) data was used to calculate a per unit average.  Although cleanly delineated year-round meter data would be preferable to winter consumption data alone, winter consumption data is preferable to summer data as a basis for ERU calculations since fewer residents are using domestic water for recreation or irrigation.  To adjust for the fact that not all of the water purchased during any season will make it to the drain, a factor of .95 was applied to the resulting figures, which are summarized in Table 5.3 2 below.
To estimate the Average Base Sanitary Flow (BSF) per ERU, which represents the wastewater flow originating purely from sanitary sources (excluding significant I&I contributions), the previously derived ERU value by the total number of ERU for the year 2024 (461) to arrive at a figure of 87,776 gpd.  See Table 5.3 2 below.  
 
Table 5.4 1 BSF Calculation Summary (Method 1)
Parameter	Notes	Figures
Total Nov. - Apr. Consumption	From source consumption data	   15,302,000 
Residential Consumption Volume (Gal)	Accounts for DSL and removes commercial flow	   12,394,620 
Winter Residential Flow (gpd)	Residential consumption divided by 181 days (Nov. through Apr.)	           68,479 
Per Capita Winter Residential Flow (gpd)	Assumed 820 population and factored by .95	79
Residential ERU (gpd)	Assumes 2.22 persons per household from OFM	                 190 
Base Sanitary Flow (gpd)	Residential ERU applied to total ERUs (461)	           87,776 

Table 5.4 2 I&I Segregation (GWI and RDII)
Parameter	Formula	Value (MGD)
Groundwater Infiltration (GWI)	ADWPeak – BSF = GWI	0.071
Rainfall-Derived Infiltration & Inflow (RDII)	RDII = AWWF - ADWF	57

## END OF INPUT

TASK
Review the input from ## INPUT to ## END OF INPUT and:
1) Extract the key claims and assess them for completeness according to the Department of Ecology's standards on the subjects mentioned in the INPUT, use Task 2 below as a classification system.
2) For each claim, classify: Supported | Partially Supported | Contradicted | Insufficient Evidence.  If a claim is partially supported, suggest reading to help to user find where the claim is either contradicted or insufficiently evidenced.
3) ONLY if overall alignment is acceptable, draft a coherent, concise section that presents the judgement and cites supporting sources inline.  If the engineering judgments provided are not explained, note that for the user.
4) If any contradictions are found, or the engineering judgments are NOT well-supported or well-explained, warn clearly and quote the conflicting guidance. Suggest sections for reading to provide additional education, and provide a helpful socratic question which aims to point the user in the right direction.
5) When citing claims, include brief quotes and then respond.
6) Finally, Summarize identified gaps or weak points, in list form, in the user's input.  List them as “Open Issues” with what to verify next.

OUTPUT FORMAT
- Respond to each "Task" (1-6) above with thoroughly, bulleted narrative output.
- Produce the following Table: Claim-by-Claim Table (Claim | Status | Evidence snippet with citation)
- Open Issues (if any)

CONSTRAINTS
- Use only retrieved context; no fabrication.
- Prefer precise citations (file + page/section), include quotes to support claims.
