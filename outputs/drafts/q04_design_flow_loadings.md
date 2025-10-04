assistant: Certainly. Below is a baseline design flow and loading framework for a small (<1000 population) municipal WWTP in Washington State, with precise definitions and calculations, referencing the Washington Ecology Criteria for Sewage Works Design ("Orange Book"), WEF MOP 8, and key regulations (including WAC 173-240 and AKART). Citations are given inline with section/page labels.

---

## 1. Design Flow Definitions

- **ADWF (Average Dry Weather Flow):**
  - Mean daily flow in dry weather (excludes major rainfall/infiltration/inflow).
  - Used to establish baseline domestic use [3, Table G2–2, p.96].

- **MDDF (Maximum Day Design Flow):**
  - The largest volume of flow anticipated during a one-day period, expressed as a daily average.
  - Required for sizing biological treatment units, esp. with toxics limits [3, G2-1.2.2.A, p.93][1, Table G2-1, p.94].
  
- **MWDF (Maximum Week Design Flow):**
  - The largest volume of flow anticipated during a continuous 7-day period, expressed as a daily average.
  - Principal design basis for treatment plants without toxics limits [3, G2-1.2.2.A, p.93][1, Table G2-1, p.94].

- **PHF/PHDF (Peak Hour Flow/Peak Hour Design Flow):**
  - Highest one-hour flow.
  - Important for hydraulic capacity—must not cause overflow/backups [3, Table G2–1, p.94; 9, Table G2–1, p.93].

---

## 2. Flow Components

**Total flow = BWF + GWI + RDII**

- **BWF (Base Wastewater Flow):**
  - Actual sanitary/domestic flow from residents [3, Table G2–2, p.96].
- **GWI (Groundwater Infiltration):**
  - Steady flow entering the system through defects (often during dry weather).
- **RDII (Rainfall-Dependent Infiltration/Inflow):**
  - Peak, short-term flows during/after storm events.
  - For collection system design, these must be estimated and itemized separately [3, p.96; 7, p.49].

*For small facilities, typical breakdowns may be estimated from local or Ten States defaults, with emphasis on verifying with measured flows if available.*

---

## 3. Flow Values and Peaking Factors

### **Default per capita flow—see Table G2–2 [3, p.96]:**

- Dwellings: 100 gpd/person (includes normal infiltration)
- For 1000 persons: 100,000 gpd = 378 m³/d ADWF

### **Peaking Factor Approaches:**

- Where actual data is unavailable, apply standard peaking factors (Harmon, Ten States, or fixed):
  - *Harmon equation:* Peak Factor = 1 + 14/(4+√P), P = population (for P=1000, PF ≈ 3.44)
  - *Ten States Standards:* Provides tables—typically PF = 3–4 for <1000 pop [6, p.8].

#### **Calculated Flows (for design pop. 1000):**

- **ADWF** = 100 gpd/person × 1000 = **100,000 gpd = 378 m³/d**
- **MDDF** = ADWF × daily peaking factor (often 2.5–3 for small systems) ⇒ 250,000–300,000 gpd = 946–1135 m³/d [1, Table G2-1][3, Table G2-2]
- **MWDF** = Similar to max month/week-average; conservatively set at ADWF × 2.0–2.2 (200,000–220,000 gpd) unless measured data supports less [1, Table G2-1][3, G2-1.2.2].
- **PHDF** = ADWF × hourly peak factor (3–4) ⇒ 300,000–400,000 gpd (1130–1515 m³/d) [3, G2-1.2.2; 9, Table G2–1, p.93].

---

## 4. Loadings (BOD5, TSS, TN, TP, NH₃)

From Table G2-2 [3, p.96]:
- **BOD5:** 0.2 lb/person/d (90 g/person/d)
- **TSS:** 0.2 lb/person/d (90 g/person/d)
- **Typical municipal TN:** Use 0.04 lb/person/d (18 g/person/d)
- **TP:** Use 0.01 lb/person/d (4.5 g/person/d)
- **NH₃:** Use 0.03 lb/person/d (14 g/person/d)
- Align per EPA/WEF MOP 8; default to Orange Book basis.

### **Applied to 1000 persons:**

| Parameter | lbs/d | kg/d |
|-----------|-------|------|
| BOD5      | 200   | 91   |
| TSS       | 200   | 91   |
| TN        | 40    | 18   |
| TP        | 10    | 4.5  |
| NH₃-N     | 30    | 13.6 |

- Values represent annual averages; adjust by same peaking factors for MDDF/MWDF and for diurnal/week/month peaks as applicable [3, Table G2-2].

---

## 5. Seasonality

- **Seasonal effects**: Must analyze min/max month flows and loads to assess impact of I/I (wet season) and lower dilution (dry season).
- **Temperature**: Max-month BOD/TSS can occur any time of year—performance at cold-season low temperature must be accounted for in design [13, p.214, MOP 8][3, Table G2-2].

---

## 6. Safety Factors

- Safety factors must be inserted into flows and loadings, especially:
  - If variability is high
  - Where only short-term or limited data is available
- Larger factors are required where peaking is pronounced (i.e., small systems, or high I/I) [1, p.94; 10, p.84].
- WAC 173-240 and Ecology require the design proposal to include justification ("the engineer must justify that the wastewater treatment plant design proposal includes an appropriate safety factor," Orange Book, Table G2-1, p.94) [1, Table G2-1; 3, G2-1.2.2].

---

## 7. Regulatory Citations

- **WAC 173-240:** Governs engineering reports, requires statement and justification of present/future flow & loadings, and adherence to AKART [15, G3-1.1.6, p.179; 7, Table WAC 173-240-060, p.49].
- **AKART:** All known, available, and reasonable technology—requires secondary treatment as a minimum, more if needed to meet water quality standards [15, p.179].
- **Orange Book (Criteria for Sewage Works Design):** Process, unit sizing, flows, and loadings—see especially G2-1, G2-2, Table G2-1, and G2-2 (p.87–97) [1, 3, 12].
- **WEF MOP 8:** Industry standard for cross-comparison, underlines that these are baseline values—must adjust by local conditions and actual data [6, p.8; 13, p.214].

---

## 8. Summary Table (for 1000 persons, small municipality)

| Flow Type | Value (gpd) | Value (m³/d) | Description/Citation            |
|-----------|-------------|--------------|---------------------------------|
| ADWF      | 100,000     | 378          | Table G2-2 [3, p.96]            |
| MDDF      | 250,000–300,000 | 946–1135 | Table G2-1, PF~3.0 [1, 3]       |
| MWDF      | 200,000–220,000 | 757–833  | Table G2-1, PF~2.0–2.2 [1, 3]   |
| PHDF      | 300,000–400,000 | 1130–1515 | Table G2-1, PF~3.0–4.0 [1, 3]   |

| Loading | Value (lb/d) | Value (kg/d) | Per Capita [3, p.96] |
|---------|--------------|--------------|----------------------|
| BOD5    | 200          | 91           | 0.2 lb/person/d      |
| TSS     | 200          | 91           | 0.2 lb/person/d      |
| TN      | 40           | 18           | 0.04 lb/person/d     |
| TP      | 10           | 4.5          | 0.01 lb/person/d     |
| NH₃-N   | 30           | 13.6         | 0.03 lb/person/d     |

**Note: For BWF, subtract GWI and expected RDII to get "true" residential sanitary flow if needed for process design** [3, Table G2-2, p.96; 7, p.49].

---

### **All design values must be confirmed and adjusted by actual monitoring records when available; if only historic or projected data exist, use above with added safety factors as justified in the engineering report.** [16, Table WAC 173-240-060, p.48; 7, p.49]

---

**Key sources:**  
- WA Ecology Orange Book, Ch. G2, Tables G2-1 and G2-2, pp. 93–97 [1, 3, 9, 12]  
- WAC 173-240 [7, Table, p.49; 15, p.179]  
- AKART [15, p.179]  
- WEF MOP 8 [6, p.8; 13, p.214]  

---

**For project-specific design, always justify values based on at least one year of credible inflow/organic loading data with safety factor rationale per Orange Book and WAC requirements.** [10, p.84; 7, p.49]