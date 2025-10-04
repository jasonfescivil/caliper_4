assistant: Below is a concise population/EDU projection template for small Washington State communities (<1,000) that addresses all required elements and maps them to relevant engineering report sections and best practice sources. Each item references specific guidance or requirements from the provided context.

---

## **Population/EDU Projection Template for Small WA Communities (<1,000)**

### **1. Source and History of Population Data**
- **OFM and Planning Sources**: Use Office of Financial Management (OFM) data or other official local/regional planning agencies for historical and current population counts (last 20 years if available); cite source and concurrence in the report [2][47].
    - **Report Section**: General Sewer Plan (WAC 173-240-050(3)(e),(c)); Engineering Report (WAC 173-240-060(3)(b)).

### **2. Forecast Methodology**
- **Projection Horizon**: Forecast for start of service and end of design period, usually 20 years [2][47].
- **Methods**: Describe method (e.g., trend extrapolation, buildout, demographic models) and obtain/planning agency concurrence [18][28][47].

### **3. Seasonality & Transients**
- **Seasonal Population**: Specify increments for summer/peak season population (e.g., part-time residents, tourists). Use local knowledge, lodging records, or empirical data [18].
- **Institutional Loads**: Quantify transient or institutional residents (e.g., hotel rooms, nursing homes, dorms) as population equivalents, citing the source and calculation method [18][7].
    - **Report Section**: Population/Demographic Analysis.

### **4. Vacancy Rate**
- **Vacancy Adjustment**: Include expected residential housing vacancy rate (use census or local assessor data); apply to gross housing units [18][28].

### **5. Institutional/Commercial/Employment Loads**
- **Partial Population Equivalents**: For schools, employment, commercial, institutional, convert user groups to EDUs using per-person or per-seat design table values (see Table G2-2, p.96) [1][12][42].

### **6. Equivalent Dwelling Units (EDU) Calculations**
- **Factors**: Define 1 EDU in terms of persons, gpd, or design load (100 gpd, 0.2 lb BOD, 0.2 lb SS per person, 24 hr duration for dwellings — Table G2-2) [1].
- **Multiple Land Use Types**: Sum EDUs for residential, commercial, and institutional classes using respective factors [1][42].
    - **Report Section**: Wastewater Flow Projections/EDU Tables.

### **7. Reconciliation of Multiple Data Sources**
- **Billing Units**: Compare number of billable sewer accounts to projected dwellings/EDUs and resolve discrepancies [7].
- **Census vs Meter Data**: Cross-check census population, actual dwelling counts, and metered water use (annual and seasonal) [7][3][18].
- **Document Assumptions**: Note any adjustments or special considerations (e.g., second homes, unmetered leaks).
    - **Report Section**: Data Comparison & Reconciliation.

### **8. Uncertainty and Sensitivity/Bands**
- **Scenarios**: Consider and report multiple growth scenarios (moderate, high, low) to bracket uncertainty in projections—required per best engineering practice [11][18].
- **Sensitivity Analysis**: Show how key factors (e.g., large employer entering/leaving, zoning changes) affect forecasts [11][18].
    - **Report Section**: Projection Uncertainty & Risk.
    - **Engineering Report Section**: Document methods and present bands/ranges (not only single-point estimates).

### **9. Design Flow Derivation**
- **Design Basis**: Use per capita or per EDU flow/BOD/SS values from the DOE Orange Book Table G2-2 [1]. Multiply projected population/EDUs by these values to set design average and peak flows, and for each relevant load parameter [1][3][12][42].
- **I/I and Water Conservation**: Document assumptions or planned adjustments for infiltration/inflow and conservation (use observed metering if available, otherwise cite standard values or justify) [3][37][47].
    - **Report Section**: Design Flows & Load Summary.

---

## **Mapping to Report Sections (per WAC & Orange Book)**
| Topic                        | General Sewer Plan                         | Engineering Report                              |
|------------------------------|--------------------------------------------|-------------------------------------------------|
| OFM/census data, history     | WAC 173-240-050(3)(e), DOE p.47            | WAC 173-240-060(3)(b), DOE p.48                 |
| Method, projection, agencies | WAC 173-240-050(3)(e)                      | WAC 173-240-060(3)(b)                           |
| Seasonal/Transient/Inst.     | WAC 173-240-050(3)(e), see Table G2-2      | WAC 173-240-060(3)(c), Table G2-2               |
| Vacancy adjustment           | Documented in population projection        | Project methods and assumptions section          |
| EDU factors                  | Table G2-2, DOE p.96                       | Used in flow/loading/design basis (DOE p.96)     |
| Meter vs billing vs census   | Data sources section, reconcile in text    | Detailed reconciliation and explanation section  |
| Uncertainty bands            | Optional/appendix                          | Required: scenarios/sensitivity, risk section    |
| Design flows/loads           | Estimate flows/loads/EDUs in plan basis    | Translate to flows/loads for sizing/treatment    |

---

## **Sources Cited**
- Washington DOE Criteria for Sewage Works Design ("Orange Book"), Table G2-2, p.96 (per capita and EDU unit values) [1]
- WAC 173-240-050 and -060: Plan and Engineering Report content [47][20][44]
- WEF and EPA best practice (population/EDU forecast, sensitivity, data reconciliation) [7][11][18][28][42]
- Design flow derivation (use Table G2-2 values; see DOE Orange Book p.96 and process per context) [1][3][12][42]
- Meter, billing, and census comparison: Orange Book, WEF, EPA (see examples [7], [18], [28])
- Uncertainty/scenarios: WEF/WEF FD-5 Gravity Sewer Manual, Sec. 3.10 [11]; DOE Orange Book G1-4.1.1 [38]

---

**Summary Table (Values from DOE Orange Book Table G2-2):**

| Land Use              | Units       | Flow (gpd) | BOD (lb/d) | SS (lb/d) | Duration (hr) |
|-----------------------|-------------|------------|------------|-----------|---------------|
| Dwelling              | per person  | 100        | 0.2        | 0.2       | 24            |
| School w/ cafeteria   | per person  | 16         | 0.04       | 0.04      | 8             |
| Motel                 | per room    | 130        | 0.26       | 0.26      | 24            |
| Restaurant            | per seat    | 50         | 0.2        | 0.2       | 16            |
| Trailer court         | per trailer | 300        | 0.6        | 0.6       | 24            |

*(For full values, see Table G2-2 [1])*

---

**References:**  
[1] DOE_Orange_Book_Design_Standards.pdf, p.96, Table G2-2  
[2] DOE_Orange_Book_Design_Standards.pdf, p.48  
[3] WEF_FD-16_Facilities_Design.pdf, p.99  
[7] AWWA_PPWTF_Infiltration_Inflow_Analysis.pdf, p.15  
[11] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf, p.75  
[12] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf, p.57  
[18] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf, p.55  
[28] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf, p.54  
[42] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf, p.56  
[44][46][47] WAC_173-240_Wastewater_Submission_Plans.pdf, p.4,6,7

---

**Inclusion of all above elements ensures compliance with Ecology and national best practice.**