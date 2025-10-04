Below is a concise, standards-based workflow to determine design flows, peaking, pump selection, and wet well volume for a wastewater lift station serving a town of 400 people. Where WA Ecology requires local data, use measured/water-use data if available; otherwise use best-practice defaults noted.

1) Confirm planning basis and design horizon
- Verify the project is consistent with an approved General Sewer Plan and proceed through engineering report → design submittals per Ecology’s sequence (WAC 173-240; Figure G1‑1) [9, G1‑2.2; Figure G1‑1].
- Set the design peak based on a minimum 20‑year forecast; firm station capacity shall be ≥ peak hourly design flow (PHDF) [1, p.260, C2‑1.2.1].

2) Establish average daily flow (ADF)
- Preferred: use local water consumption or measured wastewater data to substantiate per‑capita flow per Ecology [5, C1‑3.3.1].
- If local data are not available, a defensible best‑practice default is 60 gpcd (225 L/cap/d) scaled by population [8, §5.3.1].
- Example (town of 400): ADF = 400 × 60 gpcd = 24,000 gpd.

3) Account for infiltration/inflow (I/I)
- Ecology’s per‑capita approach is intended to cover “normal” I/I, but add an allowance where conditions are unfavorable (older sewers, high groundwater, illicit connections) based on actual data when possible [5, C1‑3.3.1; C1‑3.3.3].
- Define ADFdesign = ADF + I/Iextra (if applicable) [5, C1‑3.3.3].

4) Determine peak hour factor (PHF) and PHDF
- Use Ecology’s peaking factor (ratio of peak hourly to average daily flow) from Figure C1‑1; minimum 2.5 [5, C1‑3.3.2].
- For population 0.4 thousand, interpolate between 0.3k (~3.8) and 0.5k (~3.6) → PHF ≈ 3.7 (≥2.5) [5, C1‑3.3.2].
- Compute PHDF:
  - PHDF (gpd) = ADFdesign × PHF [5, C1‑3.3.2].
  - Convert to gpm: PHDF (gpm) = PHDF (gpd) ÷ 1440.
  - Example (no extra I/I): PHDF = 24,000 × 3.7 = 88,800 gpd = 61.7 gpm.

5) Define minimum flow conditions
- Review minimum flows and how the station will operate at low flow (level control, pump turndown) [1, p.260, C2‑1.2.1].

6) Develop system hydraulics and force main sizing
- Evaluate full range of hydraulic conditions (new vs. aged pipe, min/max flows, 1 vs. multiple pumps) to define highest and lowest heads; keep operation within pump manufacturer’s normal range [1, p.260, C2‑1.2.2; 2, p.262, C2‑1.2.2].
- Select conservative head loss coefficients to allow for installation/aging [1, p.260, C2‑1.2.2; 2, p.262, C2‑1.2.2].
- Size the force main to balance: small enough to minimize solids deposition but large enough for good pump selection and reasonable surge protection needs; consider cost‑benefit [1, p.260, C2‑1.2.2]. On constant‑speed stations, ensure capacity provides a minimum scour velocity in the force main [2, p.262, C2‑1.2.3].
- Prepare the system head curve(s) for overlay on pump curves; these will be included in the O&M documentation [3, p.266–267, C2‑1.7].

7) Select number and size of pumps (firm capacity and redundancy)
- The station must pass the peak design flow (PHDF) with the largest pump out of service; correlate number of pumps to wet well size to avoid rapid cycling [1, p.260, C2‑1.2.3; 2, p.262, C2‑1.2.3].
- Provide equipment redundancy consistent with EPA Class I reliability: one redundant pump sized to match the largest unit; separate starters/controls per unit [3, p.266–267, C2‑1.8.1; C2‑1.8.2].
- Pump type/capability: sewage pumps able to pass ≥3‑inch solids; suction and discharge ≥4 inches (exceptions for grinder/STEP only as allowed) [2, p.262, C2‑1.2.4].
- Verify the selected pumps operate within the acceptable region across the computed system curves (min/max heads/flows) [1, p.260, C2‑1.2.2; 2, p.262, C2‑1.2.2].

8) Size the wet well
- Provide adequate intake conditions, anti‑vortex submergence, minimized prerotation, and geometry that minimizes solids deposition (trench or hopper with side slopes ≥45°, 60° preferred) [2, p.262–263, C2‑1.2.5].
- For constant‑speed pumps, the minimum volume between pump ON and OFF levels is: V = t × Q ÷ 4, where t = minimum time between starts (per manufacturer/utility) and Q = pump capacity (gpm) [2, p.262, C2‑1.2.5].
  - Example (illustrative only): If Qpump ≈ 62 gpm and t = 10 min, Vmin ≈ (10 × 62)/4 = 155 gallons between ON/OFF.
- Coordinate pump count and wet well volume to avoid excessively short run/rest cycles [2, p.262, C2‑1.2.3; C2‑1.2.5].
- Incorporate provisions to limit grease/clogging and allow periodic flushing (e.g., drawdown/recycle piping) as needed [2, p.263–264, C2‑1.2.5; C2‑1.3].

9) Controls, measurement, and documentation
- Provide suitable flow measurement at the station and run timers on all pumps [2, p.265, C2‑1.4].
- Include in the O&M manual: pump/motor/force main design data and pump curve with computed system curve showing the design operating point; startup/shutdown procedures; critical safety; spare parts; contingency planning [3, p.266–267, C2‑1.7].

10) Reliability and emergency power
- Design for EPA Class I reliability with redundancy, alarms/telemetry, and standby power [3, p.266–268, C2‑1.8.1; C2‑1.8.2].
- Provide emergency power capability sized to start and operate pumps at peak possible load plus ancillary equipment; use ATS for permanent generators at larger stations [3, p.268, C2‑1.8.3].

11) Site and ancillary checks (as applicable)
- Site selection, flood protection (station fully operational during 100‑year flood/wave action), access, fire protection, piping layout, noise control (especially with generators) per Ecology standards [1, p.260–261, C2‑1.1.2–C2‑1.1.6; 3, p.266, C2‑1.6.2].

Quick numeric example (town of 400; replace with local data if available)
- ADF: 400 × 60 gpcd = 24,000 gpd [8, §5.3.1].
- PHF: ≈3.7 for 0.4k population (≥2.5 min) [5, C1‑3.3.2].
- PHDF: 24,000 × 3.7 = 88,800 gpd = 61.7 gpm [5, C1‑3.3.2].
- Firm capacity: ≥61.7 gpm with largest pump out of service [1, p.260, C2‑1.2.1; 1/2, C2‑1.2.3].
- Pumps: solids‑handling, ≥3‑inch passage, ≥4‑inch suction/discharge [2, p.262, C2‑1.2.4].
- Wet well (constant‑speed, illustrative): If one pump Q ≈ 62 gpm and t = 10 min (manufacturer/utility requirement), Vmin between ON/OFF ≈ 155 gal [2, p.262, C2‑1.2.5].
- Verify hydraulics across min/max conditions; select force main for balance of velocity/head and scour [1, p.260, C2‑1.2.2; 2, p.262, C2‑1.2.3].