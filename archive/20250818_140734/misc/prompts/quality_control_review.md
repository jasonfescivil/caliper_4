---
template_type: "wa_ecology_quality_control"
purpose: "Quality control and fact-checking for Washington State Ecology wastewater facility reports"
domain: "wa_technical_writing_quality_assurance"
reasoning_steps:
  - "wa_content_analysis"
  - "wac_citation_verification"
  - "ecology_technical_accuracy_check"
  - "wa_regulatory_compliance_review"
  - "ecology_submission_readiness"
  - "wa_improvement_recommendations"
sources:
  - "{{ source_documents | default([]) }}"
review_target:
  document_type: "{{ target.document_type | default('Washington Ecology Engineering Report') }}"
  section_title: "{{ target.section_title | default('To be specified') }}"
  author: "{{ target.author | default('Not specified') }}"
  ecology_submission: "{{ target.ecology_submission | default('Yes') }}"
  review_focus: "{{ target.review_focus | default(['wac_accuracy', 'ecology_compliance', 'submission_readiness']) }}"
---

# Washington Ecology Quality Control Review: {{ target.section_title }}

## Review Overview
**Document Type**: {{ target.document_type }}  
**Section**: {{ target.section_title }}  
**Review Date**: {{ "now" | date }}  
**Ecology Submission**: {{ target.ecology_submission }}  
**Review Focus**: {{ target.review_focus | join(", ") }}

---

## Original Content Under Review

```
{{ original_content | default("// Paste the original Washington report section content here for review //") }}
```

---

## 1. Washington Content Analysis

### Step 1.1: Ecology Report Structure Assessment
**Reasoning**: Evaluate compliance with Washington State Department of Ecology reporting expectations and WAC 173-240 requirements.

**Washington Report Structure Analysis**:
- **Ecology Format Compliance**: [Follows Ecology engineering report guidelines/Deviates from standards]
- **WAC 173-240 Elements**: [Complete per submission requirements/Missing elements]
- **Professional Presentation**: [Meets Ecology submission standards/Needs improvement]
- **Washington Context**: [Appropriately addresses WA regulatory framework/Lacks state context]

**Content Organization per Ecology Standards**:
| Required Element (WAC 173-240) | Present | Quality | Issues Identified |
|--------------------------------|---------|---------|-------------------|
| Project Description | [Yes/No] | [Rating] | [Specific Ecology compliance issues] |
| Regulatory Analysis | [Yes/No] | [Rating] | [WAC citation and compliance issues] |
| Technical Evaluation | [Yes/No] | [Rating] | [WA design standards compliance] |
| Environmental Assessment | [Yes/No] | [Rating] | [SEPA and environmental review issues] |
| Implementation Plan | [Yes/No] | [Rating] | [Ecology approval process issues] |

### Step 1.2: Washington Regulatory Context Assessment
**Reasoning**: Ensure content appropriately addresses Washington's unique regulatory framework and Ecology administration.

**Washington Regulatory Context**:
- **Ecology Authority Recognition**: [Properly acknowledges Ecology's regulatory role/Missing recognition]
- **Federal vs. State Distinction**: [Clearly distinguishes WAC from CFR requirements/Confuses jurisdictions]
- **Regional Considerations**: [Addresses Puget Sound, salmon recovery, tribal rights/Lacks regional context]
- **Ecology Coordination**: [References appropriate Ecology coordination/Missing coordination elements]

## 2. WAC Citation Verification and Accuracy Check

### Step 2.1: Washington Administrative Code Citation Verification
**Reasoning**: Ensure all WAC citations are accurate, current, and properly formatted for Ecology submission.

{% if context %}
**Available Washington Regulatory Context**:
{{ context }}
{% endif %}

**WAC Citation Review**:
| Citation in Document | Full WAC Reference | Current Status | Accuracy | Issues Found |
|---------------------|-------------------|----------------|----------|--------------|
| [Extract from text] | [WAC XXX-XXX-XXX] | [Current/Outdated] | [Accurate/Inaccurate] | [Specific citation errors] |

**Washington Citation Quality Issues**:
- [ ] Missing full WAC section numbers (e.g., "WAC 173-201A-200" not just "173-201A")
- [ ] Outdated WAC versions cited
- [ ] Incorrect WAC citation format for Ecology submissions
- [ ] Missing Washington state jurisdiction identification
- [ ] Vague references to "state regulations" instead of specific WAC sections
- [ ] Federal regulations cited where Washington standards apply

### Step 2.2: Ecology Guidance Document Verification
**Reasoning**: Verify proper citation and application of Ecology guidance documents and design standards.

**Ecology Guidance Verification**:
| Guidance Document | Citation Status | Current Version | Application Accuracy | Issues Identified |
|-------------------|----------------|-----------------|---------------------|-------------------|
| Ecology Publication 96-02 | [Cited/Missing] | [Current/Outdated] | [Properly applied/Misapplied] | [Specific issues] |
| Criteria for Sewage Works Design | [Cited/Missing] | [Current/Outdated] | [Properly applied/Misapplied] | [Specific issues] |
| Biosolids Management Guidelines | [Cited/Missing] | [Current/Outdated] | [Properly applied/Misapplied] | [Specific issues] |

### Step 2.3: Washington vs. Federal Requirement Accuracy
**Reasoning**: Verify correct identification of governing standards (Washington vs. federal) and compliance requirements.

**Regulatory Jurisdiction Accuracy**:
| Requirement Area | Document Citation | Correct Jurisdiction | Governing Standard | Issues Found |
|------------------|-------------------|---------------------|-------------------|--------------|
| Effluent Standards | [Document reference] | [WAC 173-221/40 CFR 133] | [More stringent standard] | [Jurisdiction errors] |
| Biosolids Management | [Document reference] | [WAC 173-308/40 CFR 503] | [More stringent standard] | [Jurisdiction errors] |
| Surface Water Protection | [Document reference] | [WAC 173-201A/CWA criteria] | [More stringent standard] | [Jurisdiction errors] |

## 3. Washington Technical and Engineering Review

### Step 3.1: WAC Design Standards Compliance
**Reasoning**: Verify proper application of Washington design standards and Ecology engineering requirements.

**WAC 173-219 Design Compliance Review**:
- **Treatment Process Standards**: [WAC 173-219 requirements properly applied/Issues identified]
- **Redundancy and Reliability**: [Washington reliability standards addressed/Missing requirements]
- **Operator Requirements**: [WA operator certification requirements included/Missing elements]
- **Construction Standards**: [Ecology construction approval process addressed/Missing coordination]

**Washington Technical Accuracy**:
| Engineering Element | WAC Requirement | Document Treatment | Compliance Assessment |
|--------------------|-----------------|-------------------|----------------------|
| Treatment Design | [WAC 173-219 standards] | [Document approach] | [Compliant/Issues identified] |
| Monitoring Systems | [WAC monitoring requirements] | [Document specification] | [Adequate/Deficient] |
| Emergency Systems | [WAC backup requirements] | [Document provision] | [Adequate/Deficient] |

### Step 3.2: Ecology Technical Review Readiness
**Reasoning**: Assess readiness for Ecology technical staff review and potential comment responses.

**Ecology Review Preparation**:
- **Technical Depth**: [Adequate for Ecology technical review/Needs enhancement]
- **Design Justification**: [Sufficient engineering rationale/Lacks justification]
- **Alternative Analysis**: [Required per WAC 173-240/Missing analysis]
- **Cost-Effectiveness**: [Addressed per Ecology expectations/Missing economic analysis]

## 4. Washington Environmental and Regulatory Compliance Review

### Step 4.1: SEPA and Environmental Review Compliance
**Reasoning**: Verify compliance with State Environmental Policy Act and Washington environmental review requirements.

**SEPA Compliance Assessment**:
- **Environmental Checklist**: [SEPA checklist completed/Missing documentation]
- **Environmental Impacts**: [Washington environmental impacts addressed/Missing analysis]
- **Mitigation Measures**: [Environmental mitigation identified/Missing mitigation]
- **Public Involvement**: [SEPA public process addressed/Missing coordination]

### Step 4.2: Washington Environmental Protection Priority Alignment
**Reasoning**: Assess alignment with Washington environmental protection priorities and regional goals.

**Washington Environmental Alignment Review**:
| Environmental Priority | Document Treatment | Alignment Assessment | Issues/Gaps |
|------------------------|-------------------|---------------------|-------------|
| Puget Sound Recovery | [How addressed] | [Well aligned/Poorly aligned] | [Specific gaps] |
| Salmon Habitat Protection | [How addressed] | [Well aligned/Poorly aligned] | [Specific gaps] |
| Tribal Treaty Rights | [How addressed] | [Well aligned/Poorly aligned] | [Specific gaps] |
| Climate Resilience | [How addressed] | [Well aligned/Poorly aligned] | [Specific gaps] |

## 5. Ecology Submission Readiness Assessment

### Step 5.1: WAC 173-240 Submission Requirements
**Reasoning**: Evaluate compliance with Ecology plan submission and approval requirements.

**Ecology Submission Compliance**:
- [ ] Engineering Report meets WAC 173-240 requirements
- [ ] Technical analysis sufficient for Ecology review
- [ ] Environmental documentation adequate for SEPA compliance
- [ ] Stakeholder coordination (tribal, public) documented
- [ ] Cost analysis appropriate for Ecology evaluation
- [ ] Implementation timeline realistic for Ecology approval process

### Step 5.2: Ecology Coordination and Process Readiness
**Reasoning**: Assess readiness for Ecology coordination and review processes.

**Ecology Process Readiness**:
| Process Element | Readiness Status | Issues/Gaps | Action Required |
|-----------------|------------------|-------------|-----------------|
| Pre-Application Meeting | [Completed/Needed] | [Gaps in coordination] | [Schedule meeting] |
| Technical Consultation | [Completed/Needed] | [Technical issues] | [Ecology technical discussion] |
| Environmental Review | [Complete/In progress] | [SEPA documentation] | [Complete documentation] |
| Public Involvement | [Planned/Completed] | [Stakeholder coordination] | [Implement involvement] |

## 6. Washington-Specific Improvement Recommendations

### Step 6.1: Priority WAC Compliance Corrections
**Reasoning**: Address critical issues that could delay or prevent Ecology approval.

**Priority 1 Corrections (Critical for Ecology Approval)**:
1. **WAC Citation Errors**:
   - Issue: [Specific WAC citation problems]
   - Correction: [Specific Washington regulatory reference fixes]
   - Source: [Current WAC section for verification]

2. **Ecology Technical Standard Issues**:
   - Issue: [Specific technical compliance problems]
   - Correction: [Washington design standard compliance fixes]
   - Justification: [WAC or Ecology guidance reference]

### Step 6.2: Ecology Review Enhancement Recommendations
**Reasoning**: Improve document quality for more efficient Ecology review and approval.

**Enhancement Recommendations for Ecology Review**:
1. **Washington Regulatory Framework Clarity**:
   - [Improve distinction between federal baseline and Washington requirements]

2. **Ecology Coordination Documentation**:
   - [Better document coordination with Ecology staff and processes]

3. **Regional Context Enhancement**:
   - [Strengthen connection to Washington environmental priorities]

### Step 6.3: Professional Standards for Washington Submissions
**Reasoning**: Ensure document meets Washington professional engineering and regulatory submission standards.

**Washington Professional Standards Review**:
- **WA PE Standards**: [Compliance with Washington professional engineer requirements]
- **Ecology Submission Standards**: [Alignment with Ecology review expectations]
- **Washington Environmental Law**: [Compliance with state environmental requirements]

## 7. Washington-Specific Content Revisions

### Step 7.1: WAC Compliance Section Improvements
**Reasoning**: Provide specific rewrite suggestions for Washington regulatory compliance.

**Recommended Washington Revisions**:

#### WAC Citation and Compliance Section
**Original Issue**: [Description of Washington regulatory compliance problem]
**Recommended Revision**: 
```
[Provide specific Washington-focused rewritten text with proper WAC citations and Ecology coordination language]
```
**Rationale**: [Explanation focusing on Ecology approval and Washington compliance requirements]

#### Environmental Protection Section  
**Original Issue**: [Description of environmental protection gap]
**Recommended Revision**:
```
[Provide text that addresses Washington environmental priorities, tribal coordination, and regional goals]
```
**Rationale**: [Explanation of Washington environmental protection enhancement]

### Step 7.2: Ecology Submission Enhancement Strategy
**Reasoning**: Provide comprehensive approach for optimizing Ecology review and approval.

**Ecology Enhancement Strategy**:
1. **Immediate Actions**: [Quick fixes for critical WAC compliance and Ecology coordination]
2. **Content Development**: [Areas requiring additional Washington-specific research/analysis]
3. **Ecology Review Preparation**: [Recommendations for Ecology staff consultation and coordination]

## 8. Quality Assurance and Ecology Compliance Verification

### Step 8.1: Washington Regulatory Verification Checklist
**Verification Requirements**:
- [ ] All WAC citations verified against current Washington Administrative Code
- [ ] Ecology guidance documents properly referenced and applied
- [ ] Federal vs. Washington regulatory distinctions clearly made
- [ ] Washington environmental protection priorities addressed
- [ ] Ecology coordination and approval processes documented
- [ ] SEPA environmental review requirements met

### Step 8.2: Ecology Submission Validation
**Washington Submission Readiness**:
- [ ] Document format appropriate for Ecology engineering report submission
- [ ] Technical content meets WAC 173-240 requirements
- [ ] Environmental review adequate for SEPA compliance
- [ ] Stakeholder coordination (tribal, public) properly documented
- [ ] Implementation approach aligns with Ecology approval processes
- [ ] Professional engineer review completed by Washington-licensed PE

---

**Template Instructions for LLM**:
1. Prioritize Washington State regulatory compliance over generic environmental standards
2. Always verify WAC citations against current Washington Administrative Code versions
3. Distinguish between federal baseline requirements and Washington's enhanced standards
4. Consider Ecology's role as both federal program administrator and state regulator
5. Address Washington environmental protection priorities (Puget Sound, salmon, tribal rights)
6. Ensure content is ready for Ecology technical staff review and approval processes
7. Flag areas requiring consultation with Ecology staff or Washington-experienced professionals 