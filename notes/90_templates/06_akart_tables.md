# AKART Analysis Companion Tables and Formula Frames

This library provides reusable table shells and formula frames to support an AKART analysis focused on identifying and documenting “all known, available, and reasonable methods of prevention, control and treatment” [5].

## Option Inventory and Screening

Purpose: Capture the full universe of management and treatment options and screen them for fatal flaws before detailed evaluation [5].

| Option ID | Option Title | Brief Description | Screening Status | Screening Rationale | Key Assumptions | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|

Instructions: Populate from literature reviews, vendor information, and prior studies; record the screening decision and rationale with citations. Document all assumptions that affect inclusion/exclusion. Add footnotes as needed to clarify definitions and status.

## Multi-Criteria Evaluation Matrix

Purpose: Rank feasible options against a transparent set of criteria informed by project objectives and system characteristics [2][1][5].

| Option ID | Criterion | Criterion Definition | Weight | Rating Scale Definition | Option Rating | Weighted Score | Evidence/Source Reference | Assumptions | Notes |
|---|---|---|---|---|---|---|---|---|---|

Instructions: Define criteria and weightings with stakeholder input; rate options using consistent scales. Cite data sources used and note assumptions. Summarize scoring rules in footnotes.

## Cost and Life-Cycle Analysis

Purpose: Structure cost elements for each option over the analysis horizon to support comparative life-cycle decision-making.

| Option ID | Cost Element | Description | Timing/Period | Units Basis | Quantity Basis | Cost Basis | Calculation Method | Aggregated Cost | Evidence/Source Reference | Assumptions | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Extract cost elements from estimates and vendor quotes; state calculation methods and any financial assumptions. Reference source documents and annotate uncertainty drivers in notes.

## Regulatory Conformance Tracking

Purpose: Track how each option satisfies applicable requirements and needed demonstrations of compliance, including prevention of impairment and protection of beneficial uses [5].

| Requirement ID | Requirement Statement | Applicability (Yes/No/Partial) | Compliance Approach | Demonstration/Documentation Needed | Verification Method | Status | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|

Instructions: Compile requirements from governing permits, policies, and standards. For each option, describe how conformance will be demonstrated and verified. Attach references to the controlling documents.

## Risk and Reliability Register

Purpose: Identify, assess, and mitigate option-specific risks to performance, compliance, and safety over the project life [5].

| Option ID | Risk Event | Cause | Consequence | Likelihood Category | Impact Category | Risk Rating Method | Mitigation/Control | Residual Risk | Monitoring/Trigger | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Populate through workshops and expert reviews; define rating categories and method in a footnote. Reference supporting analyses and document assumptions.

## Constructability and Implementation Assessment

Purpose: Evaluate deliverability factors that affect schedule, access, phasing, and integration with existing assets.

| Option ID | Implementation Constraint | Site/Access Considerations | Integration/Interfaces | Phasing Strategy | Schedule Considerations | Resource Requirements | Constructability Assessment | Mitigation Plan | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Gather inputs from design, operations, and construction teams. Record constraints and proposed mitigations with sources (drawings, site walks).

## Operations and Maintenance Plan Summary

Purpose: Outline ongoing O&M requirements and implications for staffing, safety, monitoring, and reliability.

| Option ID | O&M Activity | Frequency/Trigger | Competency/Training | Tools/Parts/Consumables | Operating Envelope | Monitoring/QA/QC | Safety/Confined Space Considerations | O&M Reliability Considerations | Evidence/Source Reference | Assumptions | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Derive activities from process design and equipment documentation. Note monitoring requirements and safeguards. Cite sources and assumptions.

## Environmental and Social Considerations

Purpose: Summarize potential environmental and community impacts and proposed avoidance/minimization/mitigation [5].

| Option ID | Environmental/Social Aspect | Potential Impact | Receptors/Stakeholders | Spatial/Temporal Extent | Reversibility | Mitigation/Enhancement | Residual Impact | Engagement/Communication Needs | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Populate from environmental review and stakeholder input. Document impact pathways, proposed measures, and residuals with supporting references.

## Sensitivity and Uncertainty Register

Purpose: Record key variables, uncertainties, and scenario definitions to test robustness of conclusions.

| Analysis ID | Variable/Assumption | Role in Analysis | Baseline Definition | Plausible Range/Scenarios | Sensitivity Descriptor | Primary Uncertainty Source | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|

Instructions: Identify variables that materially affect outcomes; define ranges based on defensible sources. Document rationale for each range and the method used to assess sensitivity.

## Data and Assumptions Log

Purpose: Maintain a single source of truth for datasets, derivations, and assumptions used throughout the analysis [2][1][5].

| Item ID | Data/Assumption Description | Source and Date | Quality/Completeness Notes | Method of Use | Trace to Analyses/Tables | Validation/Review Notes | Notes |
|---|---|---|---|---|---|---|---|

Instructions: Log each input with provenance and quality notes; link to where it is used and how it was validated. Update as analyses evolve.

## Decision Register

Purpose: Record key decisions, alternatives considered, and conditions for revisiting the decision.

| Decision ID | Decision Statement | Alternatives Considered | Basis/Rationale | Stakeholder Inputs | Date | Conditions/Triggers to Revisit | Linked Risks/Assumptions | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|---|

Instructions: Complete this table contemporaneously with decision-making. Attach the evidence base and note any dependencies or conditions.

## Implementation Roadmap

Purpose: Plan the pathway from selection to operation, including sequencing, dependencies, and verification steps.

| Work Package | Deliverable | Owner | Start | Finish | Dependencies | Acceptance/Verification | Risk Controls | Change Management Notes | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Build from project management plans; record acceptance criteria and verification steps. Keep change management notes current.

## Monitoring and Performance Verification Plan

Purpose: Define how performance, compliance, and effectiveness will be measured and reported over time [5].

| Metric ID | Performance Objective | Metric Definition | Location/Point of Compliance | Method/Procedure | Frequency/Durations | Quality Assurance Measures | Trigger/Alert Criteria | Response/Corrective Action | Records/Reporting | Evidence/Source Reference | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|

Instructions: Align metrics with objectives and compliance obligations; define methods and QA/QC. Document triggers and responses with references.

---

# Formula Frames

Use these generic frames to structure calculations; define variables for each project context and document all assumptions.

1) Discharge through a barrier with a loss term (from AKART-related groundwater evaluation) [5]
- Expression: q = k · a · (d / l) − e
- Variable meanings (generic):
  - q: discharge term
  - k: conductance/permeability coefficient
  - a: area term
  - d: fluid depth term
  - l: barrier thickness term
  - e: loss term representing evapotranspiration or analogous removal
- Notes: Calibrate variables to the specific system; state measurement bases and units in the assumptions log.

2) Mass loading to a receiving domain (from AKART-related groundwater evaluation) [5]
- Expression: m = q · c
- Variable meanings (generic):
  - m: mass loading term
  - q: discharge term
  - c: concentration term
- Notes: Define averaging periods and aggregation rules in the analysis plan; document data sources and quality.

Instructions for formula use: For each expression, specify the analysis period, spatial boundaries, data sources, and transformations. Record derivations, intermediate steps, and QA checks in the Data and Assumptions Log. Clearly state any site-specific attenuation, prevention, control, or treatment effects relied upon and provide supporting evidence [5].

Sources:

[1] WEF_FD-6_Sanitary_Sewer_Rehabilitation.pdf - p.124
[2] WEF_FD-6_Sanitary_Sewer_Rehabilitation.pdf - p.123; Used to Characterize
[3] 2010_EPA_Permit_Writers_Manual.pdf - p.235; A.1 Acronyms and Abbreviations
[4] 2010_EPA_Permit_Writers_Manual.pdf - p.253
[5] 1996_Ecology_02_Guidance_Document.pdf - p.39; 4.2.2
[6] 2010_EPA_Permit_Writers_Manual.pdf - p.238; Exhibit A-1 Acronyms and abbreviations (continued)
[7] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf - p.172; TABLE 5-7. Sewer Analysis Softwarea
[8] EPA_Guide_Part503_Biosolids_Rule.pdf - p.58; Recordkeeping and Reporting Requirements
[9] WEF_FD-6_Sanitary_Sewer_Rehabilitation.pdf - p.1; Contents
[10] 2010_EPA_Permit_Writers_Manual.pdf - p.237
[11] WAC_173-240_Wastewater_Submission_Plans.pdf - p.18
[12] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf - p.363; 10.2.4.6. General Notes
[13] 2010_EPA_Permit_Writers_Manual.pdf - p.43; Exhibit 3-1 Permit components
[14] WAC_173-240_Wastewater_Submission_Plans.pdf - p.11; WAC 173-240-104 Ownership and operation and maintenance
[15] WEF_FD-6_Sanitary_Sewer_Rehabilitation.pdf - p.19; List of Tables
[16] 2013_WEF_FD-5_gravity-sanitary-sewer-design-and-construction.pdf - p.51; GRAVITY SANITARY SEWER DESIGN AND CONSTRUCTION
[17] 2023_CFR_40-503_Biosolids_Standards.pdf - p.1; Environmental Protection Agency
[18] DOE_Orange_Book_Design_Standards.pdf - p.89; Wastewater
[19] 2023_CFR_40-503_Biosolids_Standards.pdf - p.28; § 503.42 General requirements.
[20] EPA_Sanitary_Sewer_Evaluation_9100WGB6.pdf - p.50; SUMMARY
[21] WEF_FD-6_Sanitary_Sewer_Rehabilitation.pdf - p.20; List of Figures
[22] EPA_Sanitary_Sewer_Evaluation_9100WGB6.pdf - p.2; FOR
[23] EPA_Sanitary_Sewer_Evaluation_9100WGB6.pdf - p.2; FOR
[24] 2010_EPA_Permit_Writers_Manual.pdf - p.254