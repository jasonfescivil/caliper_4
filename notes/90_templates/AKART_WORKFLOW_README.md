# AKART Chapter Build Workflow

This README explains how the incremental chapter build works, why the generated `akart_chapter.md` still contains many `TBD – pending input` placeholders, and where you supply project‑specific data.

## 1. Source Files and Their Roles
| File                                                   | Role in build                                                     | Auto‑injected?                                                            | Drives replacement of `TBD`?                                                   |
| ------------------------------------------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `akart_template.md`                                    | Master outline + YAML front matter + structural placeholders.     | Yes (fully parsed & sectionized).                                         | Indirect: It defines where placeholders sit; no project data inside by design. |
| `akart_workflow.md`                                    | Process / phase playbook narrative (phases, gates, deliverables). | Yes (trimmed to first 4000 chars, provided as support text each section). | Not directly; informs style/context only.                                      |
| `akart_tables.md`                                      | Library of table shells & formula frames.                         | Yes (trimmed to first 4000 chars, support block).                         | Not directly; you must manually paste/populate tables after build.             |
| Retrieval JSON (e.g. `outputs/…_retrieval_state.json`) | Regulatory/context snippets (citations).                          | Yes (first 24 nodes summarized).                                          | Not directly; informs narrative wording but placeholders remain.               |
| (Future) Project data file (you create)                | Facility-, site-, and alternative-specific facts.                 | Not yet (see Section 5).                                                  | Would enable auto replacement if wired in.                                     |

## 2. Why Placeholders Persist
The `chapter-build` command intentionally preserves `TBD – pending input` when:
- The template section contains a generic placeholder and no structured project data source exists.
- The injected support texts (workflow, tables, retrieval snippets) lack discrete, mappable facts (capacity, hydrogeologic parameters, alternative IDs, costs, etc.).
- The prompt instructions explicitly say: "Use placeholders 'TBD – pending input' where data missing."

No current code path maps real project values to specific placeholders. Therefore, every data field (design capacity, K, A, Dp, alternative profiles, monitoring frequencies, decision rules, etc.) remains `TBD` until you manually edit the output or implement a project data injection layer (see Section 5).

## 3. End‑to‑End Workflow (Current State)
1. Gather regulatory documents into your retrieval indexes; run `retrieve` to produce a retrieval JSON.
2. Update `akart_template.md` front matter minimally (title, version, prepared_by) if desired.
3. (Optional) Adjust workflow or tables libraries.
4. Run incremental build:
   ```pwsh
   poetry run python -m caliper_v2.cli chapter-build `
     --template akart_template.md `
     --workflow akart_workflow.md `
     --tables akart_tables.md `
     --retrieval outputs/akart_chapter_retrieval_state.json `
     --llm-provider openai --llm-model gpt-5 `
     --out akart_chapter.md --verbose
   ```
5. Open `akart_chapter.md`; systematically replace remaining placeholders (see Section 4 checklist).
6. Insert table shells from `akart_tables.md` into the appropriate sections and populate them with your project data.
7. Maintain parallel logs: assumptions register, decision register, data & model QA log, change log.

## 4. Placeholder Replacement Checklist
Populate these categories after generation:
- Executive & Project: Purpose, scope, preferred AKART determination, capacity, discharge pathways.
- Hydrogeology: K, A, Dp, Lt, ET, monitoring well data, flow direction.
- Constituents & Background: List of COCs, statistical summaries, beneficial uses inventory.
- Alternatives: IDs, descriptions, mechanisms, siting needs, retained/eliminated rationale.
- Screening & Evaluation: Criteria definitions, weights (if any), scoring notes, sensitivity scenarios.
- Performance Targets: Technology-based vs water-quality-based limits, compliance locations & frequencies.
- Impact & Attenuation: Site-specific attenuation demonstrations, mass loading inputs.
- Monitoring Plan: Locations, parameters, methods, frequencies, QA measures, triggers.
- Risk & QA: Risk events, likelihood/impact categories, mitigation, data validation steps.
- Decision Logic: IF/THEN rules, thresholds, tie-breaks, re-evaluation triggers.
- Implementation: Phasing schedule, responsibilities, operator training, commissioning tasks.
- Engagement: Activities, objectives, audiences, timing.
- Appendices: Detailed designs, cost basis, community engagement record, derivations.

## 5. (Optional) Adding Structured Project Data
To auto-populate some placeholders, create a YAML/JSON file (e.g. `akart_project_inputs.yaml`) with keys matching needed fields:
```yaml
project:
  purpose: "Upgrade treatment to meet ..."
  scope: "Collection system + WWTP + land application"
  design_capacity_mgd: 2.5
  discharge_pathways: ["Land application", "Surface water outfall"]
  hydrogeology:
    k_liner: 1e-7
    area_sqft: 45000
    depth_ft: 8
    liner_thickness_ft: 2
    et_rate_in_per_day: 0.15
constituents:
  - id: TN
    basis: "Permit draft"
  - id: BOD5
    basis: "Historical effluent"
alternatives:
  - id: A1
    title: "Baseline + minor process optimization"
  - id: A2
    title: "Biological nutrient removal retrofit"
monitoring:
  compliance_points:
    - name: "MW-1"
      media: groundwater
      parameters: [TN, NO3, BOD5]
```
Then (future enhancement) extend `chapter-build` to parse this file and replace tokens like `{{project.purpose}}` or targeted placeholders. At present this logic is not implemented.

## 6. Limits of Current Implementation
| Aspect | Current | Enhancement Path |
|--------|---------|------------------|
| Resume build mid‑chapter | Not supported | Add per-section manifest & skip completed. |
| Automatic table insertion | Not performed | Inject table shells into section prompts when heading matches. |
| Placeholder substitution | Manual | Implement token pattern + project data map. |
| Token/cost reporting | None | Track per-section tokens via provider API responses. |
| Index health check | Manual (400 errors cause retrieval omission) | Pre-flight test & skip failing indexes gracefully. |

## 7. Recommended Manual Artifacts
Create and maintain alongside `akart_chapter.md`:
- `assumptions_log.md`
- `decision_register.md`
- `data_sources_inventory.md`
- `change_log.md`
- `risk_register.md`
- `monitoring_plan.xlsx` (or .md)

## 8. Rapid Triage: Why a Field Is Still `TBD`
| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| Generic narrative but numeric variable left TBD | No project numeric provided anywhere | Add to project inputs file & (later) enable substitution. |
| Whole section mostly placeholders | Template section had no detail + no targeted support text | Populate manually now. |
| Attenuation parameters missing | No site-specific demonstration text ingested | Compile field/lab data and insert. |
| Tables absent | Not pasted after build | Copy relevant shells from `akart_tables.md` and fill. |

## 9. Minimum Manual Edits Before External Circulation
1. Fill Executive Summary purpose, scope, preferred AKART determination.
2. Populate COCs and background summary.
3. Provide alternative IDs and screening rationale.
4. State decision rules and monitoring framework basics.
5. Insert risk, implementation, and engagement tables.

## 10. Summary
`chapter-build` stitches section text from a structural template plus generic support blocks. It does not yet have a structured data injection layer—hence persistent `TBD` placeholders. Supply project specifics manually or add a project inputs file and extend the command for automated substitution.

---
Status: Doc reflects current code as of this commit.
