---
template_type: "wa_ecology_compliance_analysis"
purpose: "Washington State Department of Ecology compliance analysis for wastewater facilities"
domain: "wa_environmental_engineering"
reasoning_steps:
  - "wa_regulatory_identification"
  - "ecology_requirement_analysis" 
  - "wa_compliance_assessment"
  - "ecology_gap_analysis"
  - "wa_implementation_strategy"
sources:
  - "{{ source_documents | default([]) }}"
project:
  name: "{{ project.name | default('Washington Wastewater Facility') }}"
  type: "{{ project.type | default('Municipal Wastewater Treatment') }}"
  location: "{{ project.location | default('Washington State') }}"
  permit_type: "{{ project.permit_type | default('NPDES Individual Permit') }}"
  design_flow: "{{ project.design_flow | default('To be determined') }}"
---

# Washington State Ecology Compliance Analysis: {{ project.name }}

## Executive Summary
*Comprehensive compliance analysis for Washington State Department of Ecology wastewater facility requirements*

## 1. Washington State Regulatory Framework Identification

### Step 1.1: Primary Washington State Requirements
**Reasoning**: Washington State Department of Ecology administers federal programs and imposes additional state-specific requirements for wastewater facilities.

{% if context %}
**Regulatory Context from Documentation**:
{{ context }}
{% endif %}

**Primary Washington Administrative Code (WAC) Requirements**:
- [ ] **WAC 173-200**: Water Quality Standards for Ground Waters of the State of Washington
- [ ] **WAC 173-201A**: Water Quality Standards for Surface Waters of the State of Washington
- [ ] **WAC 173-216**: State Waste Discharge Permit Program
- [ ] **WAC 173-219**: Wastewater Treatment Facilities - Design Standards
- [ ] **WAC 173-221**: Discharge Standards and Effluent Limitations for Domestic Wastewater Facilities
- [ ] **WAC 173-240**: Submission of Plans and Reports for Construction of Wastewater Facilities
- [ ] **WAC 173-308**: Biosolids Management

### Step 1.2: Federal Requirements Administered by Ecology
**Reasoning**: Ecology administers federal programs with delegated authority, often with additional state requirements.

**Federal Programs (WA Ecology Administration)**:
- [ ] **NPDES Program**: Clean Water Act permits administered by Ecology
- [ ] **40 CFR 133**: Secondary Treatment Standards (federal baseline)
- [ ] **40 CFR 503**: Biosolids Use and Disposal Standards
- [ ] **40 CFR 122**: NPDES Permit Application and Special Requirements

### Step 1.3: Ecology Guidance Documents and Design Standards
**Reasoning**: Ecology guidance provides specific implementation requirements beyond regulatory minimums.

**Key Ecology Guidance Documents**:
- [ ] **Ecology Publication 96-02**: Guidance for Wastewater Treatment Facilities Design
- [ ] **Criteria for Sewage Works Design**: Ecology design standards manual
- [ ] **Water Quality Program Guidance**: Permit application and compliance guidance
- [ ] **Biosolids Management Guidelines**: Class A and Class B biosolids requirements

## 2. Washington-Specific Technical Requirements Analysis

### Step 2.1: Surface Water Discharge Standards (WAC 173-201A)
**Reasoning**: WAC 173-201A establishes water quality criteria that effluent limits must protect.

{% if project.receiving_water %}
**Receiving Water**: {{ project.receiving_water }}
**Water Body Classification**: [Determine from WAC 173-201A]
{% endif %}

**WAC 173-201A Surface Water Criteria**:
| Parameter | Class AA | Class A | Class B | Proposed Limit | Compliance Assessment |
|-----------|----------|---------|---------|----------------|----------------------|
| Temperature (°C) | 16°C (core habitat) | 18°C (core habitat) | 20°C (core habitat) | [Design value] | [Analysis required] |
| pH | 6.5-8.5 | 6.5-8.5 | 6.5-9.0 | [Design range] | [Analysis required] |
| Dissolved Oxygen | ≥9.5 mg/L | ≥8.0 mg/L | ≥6.5 mg/L | [Impact analysis] | [Analysis required] |
| Turbidity | 5 NTU + background | 10 NTU + background | 25 NTU + background | [Design value] | [Analysis required] |

### Step 2.2: Domestic Wastewater Effluent Standards (WAC 173-221)
**Reasoning**: WAC 173-221 establishes specific effluent limitations for domestic wastewater facilities.

**WAC 173-221 Effluent Limitations**:
| Parameter | Monthly Average | Weekly Average | Daily Maximum | Current/Proposed | Compliance Status |
|-----------|----------------|----------------|---------------|------------------|-------------------|
| BOD₅ (mg/L) | 30 | 45 | [Per permit] | [Current value] | [Assessment needed] |
| TSS (mg/L) | 30 | 45 | [Per permit] | [Current value] | [Assessment needed] |
| pH | 6.0-9.0 units | - | - | [Current range] | [Assessment needed] |
| Fecal Coliform | 200/100mL (geo mean) | 400/100mL (90% < value) | - | [Current value] | [Assessment needed] |

### Step 2.3: Ground Water Protection (WAC 173-200)
**Reasoning**: Ground water protection requirements may affect biosolids management and facility siting.

**WAC 173-200 Ground Water Standards**:
- **Ground Water Quality Criteria**: [Applicable criteria based on site conditions]
- **Antidegradation Requirements**: [Assessment of ground water impact]
- **Monitoring Requirements**: [Ground water monitoring if applicable]

## 3. Ecology Permit and Design Requirements

### Step 3.1: State Waste Discharge Permit (WAC 173-216)
**Reasoning**: Most facilities require both NPDES and state waste discharge permits.

**Permit Requirements Analysis**:
| Permit Component | WAC 173-216 Requirement | Current Status | Compliance Assessment |
|------------------|--------------------------|----------------|----------------------|
| Engineering Report | Required per WAC 173-240 | [Status] | [Assessment] |
| Plans and Specifications | Ecology approval required | [Status] | [Assessment] |
| Operation Plan | Required for permit | [Status] | [Assessment] |
| Monitoring Plan | Per WAC requirements | [Status] | [Assessment] |

### Step 3.2: Design Standards (WAC 173-219)
**Reasoning**: WAC 173-219 establishes specific design requirements for treatment processes.

**WAC 173-219 Design Compliance**:
| Design Element | WAC 173-219 Requirement | Current Design | Compliance Status |
|----------------|--------------------------|----------------|-------------------|
| Treatment Processes | [Minimum treatment level] | [Current/proposed] | [Compliant/Issues] |
| Redundancy | [Backup requirements] | [Current redundancy] | [Assessment] |
| Capacity Design | [Design criteria] | [Current capacity] | [Assessment] |
| Operator Requirements | [Certification levels] | [Current staffing] | [Assessment] |

### Step 3.3: Plan Submission Requirements (WAC 173-240)
**Reasoning**: Ecology requires specific submittals for facility construction and modification approval.

**WAC 173-240 Submission Requirements**:
- [ ] **Engineering Report**: Comprehensive facility assessment per Ecology guidelines
- [ ] **Plans and Specifications**: Detailed design drawings and technical specifications
- [ ] **Environmental Review**: SEPA compliance and environmental assessment
- [ ] **Operation and Maintenance Plan**: Detailed O&M procedures and staffing plan

## 4. Biosolids Management (WAC 173-308)

### Step 4.1: Washington Biosolids Requirements
**Reasoning**: WAC 173-308 imposes additional requirements beyond federal 40 CFR 503.

**WAC 173-308 Biosolids Classification**:
| Biosolids Class | WAC 173-308 Requirements | Current/Proposed Management | Compliance Assessment |
|-----------------|--------------------------|----------------------------|----------------------|
| Class A | [WA-specific requirements] | [Management approach] | [Assessment] |
| Class B | [WA-specific requirements] | [Management approach] | [Assessment] |
| Exceptional Quality | [EQ requirements] | [EQ status] | [Assessment] |

### Step 4.2: Land Application Requirements
**Reasoning**: Land application in Washington requires compliance with both federal and state requirements.

**Land Application Compliance**:
- **Site Restrictions**: [WAC 173-308 site limitations]
- **Application Rates**: [Agronomic vs. pollution limit rates]
- **Monitoring Requirements**: [Soil and ground water monitoring]
- **Notification Requirements**: [Public notification procedures]

## 5. Ecology Compliance Gap Analysis

### Step 5.1: Current vs. Ecology Requirements
**Reasoning**: Systematic comparison against Washington-specific requirements identifies compliance gaps.

{% if project.current_performance %}
**Current System Performance**:
{{ project.current_performance }}
{% endif %}

**Washington Compliance Gap Matrix**:
| WAC Section | Requirement | Current Status | Gap Identified | Priority Level |
|-------------|-------------|----------------|----------------|----------------|
| WAC 173-201A | Surface water protection | [Assessment] | [Gap analysis] | [High/Med/Low] |
| WAC 173-221 | Effluent limitations | [Assessment] | [Gap analysis] | [High/Med/Low] |
| WAC 173-219 | Design standards | [Assessment] | [Gap analysis] | [High/Med/Low] |
| WAC 173-240 | Plan approval | [Assessment] | [Gap analysis] | [High/Med/Low] |

### Step 5.2: Ecology Enforcement and Compliance History
**Reasoning**: Understanding Ecology's enforcement priorities helps prioritize compliance efforts.

**Enforcement Risk Assessment**:
- **Ecology Inspection History**: [Recent inspection results and violations]
- **Regional Enforcement Trends**: [Ecology enforcement priorities in region]
- **Consent Order Risk**: [Potential for enforcement action]
- **Permit Renewal Implications**: [Impact on permit renewal]

## 6. Washington-Specific Implementation Strategy

### Step 6.1: Ecology Approval Process
**Reasoning**: Navigate Ecology's specific review and approval procedures.

**Implementation Timeline**:
1. **Pre-Application Consultation** (30-60 days):
   - Meet with Ecology staff to discuss project scope
   - Review preliminary design concepts
   - Identify potential permit conditions

2. **Engineering Report Submission** (Per WAC 173-240):
   - Comprehensive facility assessment
   - Alternatives analysis
   - Environmental review

3. **Plans and Specifications** (Following Engineering Report approval):
   - Detailed design documents
   - Technical specifications
   - Construction oversight plan

### Step 6.2: Ecology Stakeholder Coordination
**Reasoning**: Coordinate with relevant Washington agencies and stakeholders.

**Stakeholder Coordination**:
- **Department of Ecology**: Primary regulatory oversight
- **Department of Health**: Drinking water protection coordination
- **Local Health Departments**: Local permitting coordination
- **Puget Sound Partnership**: Regional coordination (if applicable)
- **Tribal Governments**: Treaty rights consultation (if applicable)

## 7. Cost and Implementation Considerations

### Step 7.1: Washington-Specific Cost Factors
**Reasoning**: Account for Washington-specific requirements in cost estimates.

**Additional Cost Considerations**:
- **Enhanced Treatment**: Requirements beyond federal minimums
- **Ecology Permit Fees**: State permit application and review fees
- **Consultant Coordination**: Ecology-experienced engineering firms
- **Extended Review**: Ecology review timelines and iterations

### Step 7.2: Funding Opportunities
**Reasoning**: Leverage Washington-specific funding programs.

**Washington Funding Sources**:
- **Ecology Loans and Grants**: Water Quality Financial Assistance
- **Community Development Block Grants**: Rural community assistance
- **USDA Rural Development**: Rural utility funding
- **Federal/State Revolving Funds**: Low-interest loan programs

## 8. Quality Assurance and Ecology Compliance Verification

### Step 8.1: WAC Citation Verification
**Verification Requirements**:
- [ ] All WAC citations current and accurately referenced
- [ ] Ecology guidance documents properly cited
- [ ] Cross-references between federal and state requirements verified
- [ ] Permit condition language consistent with regulations

### Step 8.2: Ecology Review Preparation
**Ecology Submission Readiness**:
- [ ] Engineering report format consistent with Ecology expectations
- [ ] Technical analysis meets WAC 173-240 requirements
- [ ] Environmental review adequate for SEPA compliance
- [ ] Stakeholder coordination documented

---

**Template Instructions for LLM**:
1. Always cite specific WAC sections with full numbers (e.g., "WAC 173-201A-240")
2. Distinguish between federal baseline and Washington state requirements
3. Reference Ecology guidance documents by publication number
4. Consider both current Ecology priorities and historical enforcement patterns
5. Address permit application process and Ecology review expectations
6. Flag areas requiring consultation with Ecology staff or experienced Washington consultants 