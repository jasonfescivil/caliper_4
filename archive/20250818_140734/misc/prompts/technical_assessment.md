---
template_type: "wa_technical_assessment"
purpose: "Technical assessment for Washington State wastewater facilities per Ecology standards"
domain: "wa_environmental_engineering"
reasoning_steps:
  - "wa_system_characterization"
  - "ecology_performance_analysis"
  - "wac_design_evaluation"
  - "wa_operational_assessment"
  - "ecology_compliance_recommendations"
sources:
  - "{{ source_documents | default([]) }}"
assessment:
  system_type: "{{ system.type | default('Municipal Wastewater Treatment Plant') }}"
  capacity: "{{ system.capacity | default('To be determined') }}"
  location: "{{ system.location | default('Washington State') }}"
  design_flow: "{{ system.design_flow | default('To be determined') }}"
  ecology_region: "{{ system.ecology_region | default('To be determined') }}"
  receiving_water: "{{ system.receiving_water | default('To be determined') }}"
  water_class: "{{ system.water_class | default('To be determined per WAC 173-201A') }}"
evaluation_criteria:
  - "wac_design_compliance"
  - "ecology_performance_standards"
  - "wa_cost_effectiveness"
  - "puget_sound_protection"
  - "tribal_coordination"
---

# Washington State Technical Assessment: {{ system.type }}

## Executive Summary
*Technical evaluation for Washington State wastewater facility per Department of Ecology standards and WAC requirements*

## 1. Washington System Characterization

### Step 1.1: System Description and WAC Classification
**Reasoning**: Establish system characteristics within Washington regulatory framework and Ecology jurisdiction.

{% if context %}
**System Context from Documentation**:
{{ context }}
{% endif %}

**Washington System Overview**:
- **System Type**: {{ system.type }}
- **Design Capacity**: {{ system.capacity }}
- **Design Flow Rate**: {{ system.design_flow }}
- **Location**: {{ system.location }}
- **Ecology Region**: {{ system.ecology_region }}
- **Receiving Water**: {{ system.receiving_water }}
- **Water Classification**: {{ system.water_class }} (per WAC 173-201A)
- **NPDES Permit**: [Ecology-issued permit number and expiration]

**WAC 173-219 System Classification**:
| Design Parameter | WAC 173-219 Category | Current Classification | Compliance Status |
|------------------|----------------------|------------------------|-------------------|
| Design Flow | [<1 MGD / 1-10 MGD / >10 MGD] | [Current flow category] | [Compliant/Issues] |
| Treatment Level | [Primary/Secondary/Advanced] | [Current level] | [Compliant/Issues] |
| Discharge Type | [Surface water/Ground water/Reuse] | [Current discharge] | [Compliant/Issues] |

### Step 1.2: Washington Design Basis and Ecology Standards
**Reasoning**: Evaluate design against current WAC requirements and Ecology guidance.

**WAC 173-219 Design Compliance**:
- **Treatment Standards**: [Required treatment level per WAC 173-219]
- **Design Criteria**: [Ecology Publication 96-02 compliance]
- **Redundancy Requirements**: [Backup system requirements per WAC]
- **Operator Requirements**: [Required operator certification levels]

**Ecology Guidance Application**:
- **Design Manual Compliance**: Ecology "Criteria for Sewage Works Design"
- **Biosolids Guidelines**: WAC 173-308 and Ecology biosolids guidance
- **Pretreatment Standards**: Industrial pretreatment program requirements
- **Construction Standards**: WAC 173-240 plan approval requirements

## 2. Washington Performance Analysis

### Step 2.1: WAC 173-221 Effluent Performance Evaluation
**Reasoning**: Assess performance against Washington domestic wastewater effluent standards.

{% if system.performance_data %}
**Performance Data Analysis**:
{{ system.performance_data }}
{% endif %}

**WAC 173-221 Performance Summary**:
| Parameter | WAC 173-221 Limit | Current Performance | Compliance Status | Ecology Violation History |
|-----------|-------------------|--------------------|--------------------|---------------------------|
| BOD₅ (mg/L) | 30 monthly / 45 weekly | [Actual range] | [Pass/Fail/Marginal] | [Recent violations] |
| TSS (mg/L) | 30 monthly / 45 weekly | [Actual range] | [Pass/Fail/Marginal] | [Recent violations] |
| pH | 6.0-9.0 units | [Actual range] | [Pass/Fail/Marginal] | [Recent violations] |
| Fecal Coliform | 200/100mL geo mean | [Actual range] | [Pass/Fail/Marginal] | [Recent violations] |

### Step 2.2: WAC 173-201A Surface Water Protection
**Reasoning**: Evaluate receiving water impact and compliance with Washington surface water standards.

**Surface Water Impact Assessment**:
| WAC 173-201A Parameter | Water Class Standard | Receiving Water Status | Facility Impact | Compliance Assessment |
|------------------------|---------------------|------------------------|-----------------|----------------------|
| Temperature | [16°C/18°C/20°C per class] | [Current/summer conditions] | [Thermal impact] | [Assessment] |
| Dissolved Oxygen | [9.5/8.0/6.5 mg/L per class] | [Current DO levels] | [Impact assessment] | [Assessment] |
| pH | 6.5-8.5 (most classes) | [Receiving water pH] | [Facility contribution] | [Assessment] |
| Turbidity | [5/10/25 NTU + background] | [Current turbidity] | [Facility contribution] | [Assessment] |

### Step 2.3: Washington Biosolids Management (WAC 173-308)
**Reasoning**: Assess biosolids management compliance with Washington requirements beyond federal 40 CFR 503.

**WAC 173-308 Biosolids Assessment**:
| Biosolids Parameter | WAC 173-308 Requirement | Current Management | Compliance Status | Ecology Approval Status |
|---------------------|--------------------------|-------------------|-------------------|-------------------------|
| Classification | [Class A/B/EQ requirements] | [Current class] | [Compliant/Issues] | [Ecology approval status] |
| Pathogen Reduction | [WA-specific requirements] | [Current treatment] | [Compliant/Issues] | [Monitoring compliance] |
| Land Application | [Site restrictions per WAC] | [Current disposal] | [Compliant/Issues] | [Permit compliance] |
| Public Notification | [Enhanced WA requirements] | [Current procedures] | [Compliant/Issues] | [Ecology coordination] |

## 3. WAC Design Standards Evaluation

### Step 3.1: WAC 173-219 Process Design Assessment
**Reasoning**: Evaluate treatment processes against Washington design standards and Ecology guidance.

**Treatment Process WAC Compliance**:
| Treatment Process | WAC 173-219 Requirement | Ecology Guidance Standard | Current Design | Compliance Assessment |
|-------------------|--------------------------|---------------------------|----------------|----------------------|
| Primary Treatment | [WAC minimum requirements] | [Ecology design criteria] | [Current/proposed] | [Adequate/Deficient] |
| Secondary Treatment | [30/30 BOD/TSS + reliability] | [Ecology redundancy standards] | [Current/proposed] | [Adequate/Deficient] |
| Disinfection | [Required for coliform compliance] | [Ecology disinfection guidance] | [Current/proposed] | [Adequate/Deficient] |
| Biosolids Treatment | [WAC 173-308 requirements] | [Ecology biosolids guidance] | [Current/proposed] | [Adequate/Deficient] |

### Step 3.2: Washington Infrastructure and Reliability Assessment
**Reasoning**: Evaluate infrastructure adequacy against WAC reliability requirements and Ecology expectations.

**WAC 173-219 Infrastructure Compliance**:
| Infrastructure Element | WAC 173-219 Requirement | Ecology Standard | Current Condition | Upgrade Priority |
|------------------------|--------------------------|------------------|-------------------|------------------|
| Treatment Redundancy | [Backup treatment required] | [Ecology redundancy guidance] | [Current capability] | [High/Medium/Low] |
| Power Systems | [Emergency power requirements] | [Ecology power standards] | [Current systems] | [High/Medium/Low] |
| Instrumentation | [Required monitoring systems] | [Ecology I&C standards] | [Current systems] | [High/Medium/Low] |
| Operator Facilities | [Required operator amenities] | [Ecology facility standards] | [Current facilities] | [High/Medium/Low] |

### Step 3.3: Ecology Plan Approval Compliance (WAC 173-240)
**Reasoning**: Assess facility modifications against Ecology plan review and approval requirements.

**WAC 173-240 Compliance Assessment**:
- **Engineering Report Requirements**: [Compliance with Ecology engineering report standards]
- **Plans and Specifications**: [Compliance with Ecology design drawing requirements]
- **Environmental Review**: [SEPA compliance and environmental assessment status]
- **Construction Oversight**: [Ecology construction inspection and approval process]

## 4. Washington Operational Assessment

### Step 4.1: Ecology Operations and Maintenance Standards
**Reasoning**: Assess operational practices against Washington operator certification and O&M requirements.

**Washington Operational Requirements**:
| Operational Element | WAC/Ecology Requirement | Current Practice | Compliance Assessment | Improvement Priority |
|---------------------|--------------------------|------------------|----------------------|---------------------|
| Operator Certification | [Required WA certification level] | [Current staff certification] | [Compliant/Deficient] | [Training needs] |
| O&M Manual | [Required per Ecology standards] | [Current manual status] | [Current/Needs update] | [Update requirements] |
| Maintenance Program | [Preventive maintenance required] | [Current program] | [Adequate/Deficient] | [Program improvements] |
| Record Keeping | [WAC record keeping requirements] | [Current procedures] | [Compliant/Issues] | [Procedure updates] |

### Step 4.2: Washington Monitoring and Reporting Compliance
**Reasoning**: Evaluate monitoring program adequacy against WAC requirements and Ecology expectations.

**Washington Monitoring Requirements**:
| Monitoring Component | WAC/Permit Requirement | Current Program | Compliance Status | Enhancement Needs |
|----------------------|-------------------------|-----------------|-------------------|-------------------|
| Effluent Monitoring | [WAC 173-221 + permit] | [Current frequency/parameters] | [Compliant/Issues] | [Program adjustments] |
| Receiving Water | [WAC 173-201A protection] | [Current monitoring] | [Adequate/Insufficient] | [Monitoring expansion] |
| Biosolids Monitoring | [WAC 173-308 requirements] | [Current testing] | [Compliant/Issues] | [Testing improvements] |
| Operations Monitoring | [Process control requirements] | [Current monitoring] | [Adequate/Insufficient] | [System improvements] |

## 5. Washington Regulatory and Environmental Compliance

### Step 5.1: Ecology Permit Compliance Status
**Reasoning**: Assess current compliance with Ecology-issued permits and WAC requirements.

**Ecology Permit Compliance Summary**:
| Permit Requirement | Current Status | Compliance Trend | Ecology Enforcement Risk | Action Required |
|--------------------|----------------|-------------------|--------------------------|-----------------|
| Effluent Limits | [Compliant/Violations] | [Improving/Stable/Declining] | [High/Medium/Low] | [Specific actions] |
| Monitoring Requirements | [Compliant/Issues] | [Improving/Stable/Declining] | [High/Medium/Low] | [Specific actions] |
| Reporting Schedule | [Current/Late] | [Improving/Stable/Declining] | [High/Medium/Low] | [Specific actions] |
| Special Conditions | [Compliant/Issues] | [Improving/Stable/Declining] | [High/Medium/Low] | [Specific actions] |

### Step 5.2: Washington Environmental Protection Goals
**Reasoning**: Evaluate alignment with Washington environmental protection priorities and regional goals.

**Washington Environmental Alignment**:
- **Puget Sound Recovery**: [Contribution to Puget Sound Action Agenda goals]
- **Salmon Recovery**: [Support for salmon habitat protection and restoration]
- **Climate Change**: [Facility resilience and greenhouse gas reduction]
- **Tribal Treaty Rights**: [Coordination with tribal fishing and water rights]

## 6. Washington Risk Assessment

### Step 6.1: Ecology Enforcement and Regulatory Risk
**Reasoning**: Assess risk of Ecology enforcement action and permit modifications.

**Ecology Enforcement Risk Matrix**:
| Risk Factor | Probability | Consequence | Risk Level | Mitigation Strategy |
|-------------|-------------|-------------|------------|---------------------|
| Permit Violations | [High/Med/Low] | [Ecology enforcement action] | [High/Med/Low] | [Compliance improvements] |
| WAC Non-Compliance | [High/Med/Low] | [Consent order/penalties] | [High/Med/Low] | [Regulatory compliance] |
| Receiving Water Impact | [High/Med/Low] | [Enhanced permit conditions] | [High/Med/Low] | [Environmental protection] |
| Public Complaints | [High/Med/Low] | [Increased Ecology scrutiny] | [High/Med/Low] | [Community relations] |

### Step 6.2: Washington Environmental and Public Health Risks
**Reasoning**: Evaluate risks specific to Washington environmental protection priorities.

**Washington Environmental Risk Assessment**:
- **Surface Water Protection**: [Risk to WAC 173-201A water quality standards]
- **Ground Water Protection**: [Risk to WAC 173-200 ground water quality]
- **Tribal Coordination**: [Risk to tribal treaty rights and consultation requirements]
- **Puget Sound Impact**: [Risk to regional recovery efforts and Action Agenda goals]

## 7. Washington Implementation Recommendations

### Step 7.1: Ecology Compliance Priority Actions
**Reasoning**: Prioritize actions based on Ecology enforcement priorities and WAC compliance requirements.

**Priority 1 Actions (Immediate - 0-3 months)**:
1. **Critical Ecology Compliance**:
   - Specific action: [Address immediate WAC violations or permit non-compliance]
   - Timeline: [Immediate implementation schedule]
   - Ecology coordination: [Required Ecology notification/approval]

2. **High-Risk Items**:
   - Specific action: [Address high-risk operational or environmental issues]
   - Timeline: [Implementation schedule]
   - Cost estimate: [Order of magnitude with Ecology approval costs]

### Step 7.2: WAC Compliance and System Improvements (3-18 months)
**Reasoning**: Plan systematic improvements to achieve full WAC compliance and Ecology approval.

**Priority 2 Actions**:
1. **WAC 173-219 Design Compliance**: [System modifications for design standard compliance]
2. **Enhanced Monitoring**: [Monitoring system improvements per WAC requirements]
3. **Operator Training**: [Certification and training per Washington requirements]

### Step 7.3: Long-term Washington Strategy (18+ months)
**Reasoning**: Plan for future Washington requirements and regional environmental goals.

**Strategic Considerations**:
1. **Ecology Rule Updates**: [Anticipate future WAC modifications and Ecology priorities]
2. **Regional Coordination**: [Align with Puget Sound recovery and regional initiatives]
3. **Climate Adaptation**: [Prepare for climate change impacts and adaptation requirements]

## 8. Washington Cost-Benefit Analysis

### Step 8.1: Ecology Compliance Costs
**Reasoning**: Estimate costs specific to Washington regulatory compliance and Ecology approval processes.

**Washington Compliance Cost Summary**:
| Improvement Category | Capital Cost | Annual O&M Cost | Ecology Fees | Lifecycle Cost |
|---------------------|--------------|-----------------|---------------|----------------|
| WAC Compliance Upgrades | [$ estimate] | [$ estimate] | [Permit fees] | [$ estimate] |
| Enhanced Monitoring | [$ estimate] | [$ estimate] | [Approval costs] | [$ estimate] |
| Ecology Coordination | [$ estimate] | [$ estimate] | [Review fees] | [$ estimate] |

### Step 8.2: Washington Funding and Implementation Strategy
**Reasoning**: Leverage Washington-specific funding programs and Ecology coordination.

**Washington Implementation Strategy**:
- **Ecology Funding Programs**: [Water Quality Financial Assistance and grant opportunities]
- **Ecology Technical Assistance**: [Utilize Ecology technical support and guidance]
- **Regional Partnerships**: [Coordinate with other Washington utilities and regional programs]
- **Phased Implementation**: [Align with Ecology review timelines and approval processes]

## 9. Quality Assurance and Ecology Technical Review

### Step 9.1: Washington Technical Standards Verification
**Verification Requirements**:
- [ ] All WAC design standards properly applied and referenced
- [ ] Ecology guidance documents incorporated into analysis
- [ ] Washington operator certification requirements addressed
- [ ] Ecology permit conditions and special requirements included

### Step 9.2: Ecology Professional Review Requirements
**Washington Professional Review Needs**:
- [ ] Professional engineer licensed in Washington State
- [ ] Ecology coordination and pre-application consultation
- [ ] Environmental review per State Environmental Policy Act (SEPA)
- [ ] Tribal consultation coordination (if applicable)

---

**Template Instructions for LLM**:
1. Always reference specific WAC sections with full citations (e.g., "WAC 173-219-110")
2. Distinguish between WAC requirements and Ecology guidance document recommendations
3. Consider Washington-specific environmental priorities (salmon, Puget Sound, tribal rights)
4. Address both technical compliance and Ecology approval process requirements
5. Reference Ecology regional offices and staff coordination needs
6. Flag areas requiring Washington-licensed professional engineer review or Ecology consultation 