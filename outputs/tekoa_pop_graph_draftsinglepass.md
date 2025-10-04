assistant: Sources located in the Tekoa index

- OFM historical county/city counts (primary spreadsheet):
  - ofm_april1_postcensal_estimates_pop_1960-present.xlsx, workbook p.2. Includes Whitman County municipal histories and Tekoa annual counts through 2024 (Tekoa row matches 2020–2024 = 817, 810, 810, 805, 820) [1].
- OFM county projection growth rates (medium series):
  - Tekoa Facility Plan Draft v4.1, Table “Summary of Projected Population by Method” (3.10 Conclusion), p.58. Lists “WAOFM Medium Forecast Percent Growth for Whitman County” used in Method 1: 2030 = 1.52%, 2035 = 1.36%, 2040 = 1.07%, 2045 = 0.83%. Equation given: Pop = Prevpop × (1 + %Δ) [9]. Method discussion also states the medium forecast’s 2025 estimate most closely matches the 2024 OFM postcensal estimate for Whitman County [6, p.50].
- Base-year Tekoa planning population:
  - Tekoa Facility Plan Draft v4.1, Table 3.6-1 “Tekoa Annual Population and Housing WAOFM Data (2014–2024),” p.44. Tekoa 2024 total population = 820 [8].
- Growth Management Act (GMA) county allocation/assumptions tables:
  - Unknown. No GMA allocation tables for Whitman County are present in the provided indexed pages.
- Tekoa local ERU (Equivalent Residential Unit) conversion method:
  - Unknown. No locally adopted ERU definition or conversion factor is present in the provided indexed pages. The plan shows a housing-based population formula (Population = Housing Units × Occupancy Rate × Avg. Household Size), but not an ERU definition [10, p.53; 8, p.44].

Tekoa projections (using OFM Whitman County medium growth rates)

Method setup
- Base-year population: 2025 = 820 persons (using 2024 OFM estimate for Tekoa and the plan’s note that OFM 2025 medium forecast aligns with 2024 estimate) [8, p.44; 6, p.50].
- Period growth factors (Whitman County, OFM medium): 2030 = +1.52%, 2035 = +1.36%, 2040 = +1.07%, 2045 = +0.83% [9, p.58].
- Recurrence: Pop2030 = Pop2025 × 1.0152; Pop2035 = Pop2030 × 1.0136; Pop2040 = Pop2035 × 1.0107; Pop2045 = Pop2040 × 1.0083 [9, p.58].
- Rounding: Round final-year populations to the nearest whole person; retain full precision between steps.

Results
- 2025: Population = 820; ERUs = unknown (local ERU method not provided).
- 2030: Population = 820 × 1.0152 = 832.464 → 832; ERUs = unknown.
- 2035: 832.464 × 1.0136 = 843.798 → 844; ERUs = unknown.
- 2040: 843.798 × 1.0107 = 852.829 → 853; ERUs = unknown.
- 2045: 852.829 × 1.0083 = 859.903 → 860; ERUs = unknown.

Table (year, population, ERUs)
- 2025 | 820 | unknown
- 2030 | 832 | unknown
- 2035 | 844 | unknown
- 2040 | 853 | unknown
- 2045 | 860 | unknown

Method box (equations and rules)
- Base: Pop2025 = 820 [8, p.44], justified by OFM 2025 ≈ 2024 note [6, p.50].
- Projection equation (OFM medium): Popt = Popprev × (1 + gt), with gt from OFM medium county forecast as reported in the plan’s summary table [9, p.58].
- Rounding: Round each projected year to the nearest whole person. ERU conversion: unknown (no local ERU/PPH/flow per ERU in indexed sources).

Narrative (why this approach is conservative and compliant; assumptions; use in design)

This projection method applies the Washington Office of Financial Management (OFM) Whitman County medium-series growth rates to Tekoa’s planning base population. The base is anchored in OFM’s April 1 postcensal estimate for Tekoa (2024 = 820) [8, p.44] and the plan’s note that OFM’s 2025 county medium forecast matches the 2024 estimate, allowing a 2025 Tekoa base of 820 [6, p.50]. Future-year factors come directly from the plan’s Method 1 summary, which lists OFM medium growth percentages for Whitman County at 2030 (1.52%), 2035 (1.36%), 2040 (1.07%), and 2045 (0.83%), applied multiplicatively to the preceding period [9, p.58]. The resulting 20‑year horizon (to 2045) meets the planning timeframe expected for wastewater facility planning and aligns with county-consistent OFM forecasts, supporting compliance with WAC 173‑240‑060(3)(b) by using recognized population forecasting sources and ensuring internal consistency with local planning practice.

This county-based medium scenario is conservative for Tekoa because it does not assume accelerated growth specific to Tekoa’s location near Spokane County. The plan documents stronger regional growth dynamics in Spokane County and discusses exurban spillover effects [7, p.48], yet our projections adhere to Whitman County medium rates rather than higher localized or housing‑max buildout scenarios. In other words, the method tracks countywide expectations and avoids overstating growth pressure.

Key assumptions and limitations include: (1) the absence of the OFM low and high series and GMA allocation tables in the indexed materials—thus, low/high bounds and county allocation assumptions are unknown here; (2) use of stepwise 5‑year growth factors from the plan’s Method 1 summary rather than the underlying OFM projection workbook; (3) the base-year condition assumes OFM’s 2025 equals 2024 (per plan narrative) [6, p.50]; (4) no explicit treatment of annexations, special generators (e.g., major employers), or housing pipeline; and (5) the locally adopted ERU definition and conversion factor are not available in the indexed pages, so ERU results cannot be computed. The plan does include housing/occupancy/household size data structures [8, p.44; 10, p.53], which can support ERU derivations once the city’s ERU policy (e.g., persons per ERU or gpd per ERU) is provided.

For design flows (e.g., AADF), the normal workflow is: ERUs = Population ÷ (persons per ERU) or via customer-account ERUs; AADF = ERUs × unit flow per ERU; then add non-residential flows and I/I allowances; and apply peaking to obtain MDD and PWWF. Once Tekoa’s adopted ERU definition and per‑ERU flow are supplied (local document not present here), the tabled populations can be converted directly into ERUs and then into design flows for the wastewater facility plan.

Citations
- OFM postcensal estimates workbook: ofm_april1_postcensal_estimates_pop_1960-present.xlsx, p.2 (Whitman County cities incl. Tekoa) [1].
- Tekoa Facility Plan Draft v4.1: Table 3.6-1 (Tekoa 2014–2024 population/housing), p.44 [8]; Section 3.8.2 (OFM forecast selection and 2025 alignment), p.50 [6]; Table “Summary of Projected Population by Method” with OFM medium growth percent list and Method 1 equation, p.58 [9].
- ERU method: unknown in provided index (no local ERU definition located).