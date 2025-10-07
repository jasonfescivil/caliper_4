# Local LLM Enhancements for the Caliper Dash UI

This document maps previously proposed local LLM augmentations to potential Dash UI features, estimates implementation difficulty, and sketches actionable plans. The goal is to let a small, on-device model complement frontier models inside Caliper without assuming any external API dependencies.

## Hardware assumptions

* Target machine: Ryzen 9 5950X, 64 GB RAM, RTX 4070 SUPER (12 GB VRAM).
* Recommended model class: 7B–13B instruction-tuned models (e.g., Mistral 7B Instruct, Phi-3.1 Mini) running via llama.cpp/LM Studio with GPU offload.

---

## 1. Retrieval Runbook Co-Pilot

**Dash integration potential:** High. The existing Dash UI already surfaces retrieval runs, making it natural to add a "Helper Suggestions" panel.

**Difficulty:** Medium.

### Plan
1. **Data plumbing**
   * Instrument retrieval sessions to persist JSON summaries (already produced under `data_v2`), ensuring the Dash backend can load recent runs.
   * Add a background task (Celery or Dash callback) that triggers the local LLM with a prompt containing recent retrieval metrics.

2. **LLM invocation**
   * Implement a small Python wrapper around LM Studio’s HTTP API or llama.cpp server to submit prompts and receive suggestions.
   * Cache responses for each session to avoid duplicate inference.

3. **UI changes**
   * Add a new Dash card in the retrieval tab displaying: suggested parameter tweaks, rationale, and a "Apply to next run" button that pre-fills CLI/Dash controls.
   * Provide a confidence indicator (e.g., heuristic score from the prompt).

4. **Testing & validation**
   * Unit-test the prompt formatter and API client with mocked LLM responses.
   * Add Cypress/Playwright UI tests to ensure the helper card renders and handles empty states.

---

## 2. Corpus Triage for GraphRAG

**Dash integration potential:** Medium. Fits into document ingestion/status pages but requires additional UX.

**Difficulty:** Medium–High due to preprocessing and status tracking.

### Plan
1. **Ingestion watch**
   * Hook into the document ingestion pipeline to capture new files awaiting GraphRAG indexing.
   * Generate lightweight metadata (file type, size, ingestion timestamp) for prompt context.

2. **Local LLM classification**
   * Prompt the small model to categorize documents (e.g., policy, research, anomaly) and flag formatting issues.
   * Persist the model’s notes alongside ingestion records.

3. **Dash UI updates**
   * Create a "Corpus Triage" table showing pending documents, model-assigned categories, and recommended actions (e.g., "needs manual review").
   * Add filters to prioritize flagged items.

4. **Operational safeguards**
   * Allow users to override or confirm the LLM’s recommendation; track confirmations to refine prompts later.
   * Implement retry logic and timeouts around the local inference server.

---

## 3. Enhance-Stage Quality Sweeps

**Dash integration potential:** High. Enhance outputs are already reviewed before generation, so augmenting with suggestions aligns with existing workflows.

**Difficulty:** Medium.

### Plan
1. **Artifact collection**
   * Ensure enhanced retrieval artifacts (outlines, spores) are accessible to the Dash backend.

2. **Prompt design**
   * Create templates that ask the local LLM to evaluate coverage, missing angles, or propose follow-up queries.

3. **UI enhancements**
   * Add an "LLM Review" sidebar in the Enhance tab with:
     - Top missing concepts or questions.
     - Suggested follow-up retrieval prompts.
     - Quick action buttons to launch additional retrievals.

4. **Feedback loop**
   * Let users mark suggestions as helpful/not helpful; log this to adjust prompting.

5. **Testing**
   * Mock inference outputs in Dash unit tests to verify layout and state transitions.

---

## 4. Judgment Pre-Screening

**Dash integration potential:** Medium. Useful for long drafts but introduces an extra review step that must be optional.

**Difficulty:** Medium–High (needs robust claim detection scaffolding).

### Plan
1. **Content extraction**
   * Parse draft sections and associated evidence from generation artifacts.

2. **Local LLM analysis**
   * Prompt the model to highlight unsupported claims, redundant citations, or sections lacking evidence.
   * Limit scope to summary comments to keep latency manageable.

3. **Dash UI changes**
   * Add a toggle in the Judge tab: "Pre-screen with local assistant." When enabled, display a list of flagged issues before submitting to the frontier judge.
   * Provide checkboxes to include/exclude suggestions when forming the final judgment prompt.

4. **Safeguards**
   * Clearly label the assistant output as advisory to avoid over-reliance.
   * Log recommendations for auditing.

---

## 5. CLI Automation Coach

**Dash integration potential:** Low for the main Dash UI, but feasible within an admin/settings page.

**Difficulty:** Low–Medium.

### Plan
1. **Configuration introspection**
   * Collect environment and provider settings (already parsed in CLI) and expose an internal endpoint the Dash app can query.

2. **Prompting**
   * Feed the settings and recent error logs into the local model to generate guidance (e.g., "You have Anthropic disabled; switch to fallback X").

3. **UI placement**
   * Add a "Configuration Assistant" panel under settings with quick tips, warnings, and links to relevant documentation.

4. **Testing**
   * Use fixture-based tests to ensure the prompt builder handles redacted secrets properly.

---

## Post-Generation Citation Checking Workflow

**Objective:** Let a local LLM validate citations and highlight potential hallucinations after the frontier model completes a draft.

**Difficulty:** Medium–High (requires careful orchestration to maintain trustworthiness).

### Plan
1. **Artifact preparation**
   * Gather the generated draft, citation metadata (source IDs, excerpts), and retrieval context from the `generate` stage.

2. **Chunking strategy**
   * Divide the draft into sections aligned with citations. For each section, create a prompt that includes the relevant passages and source snippets.

3. **Local LLM verification**
   * For each section, ask the local model to:
     - Confirm whether the citation supports the claim.
     - Flag missing citations or unsupported statements.
     - Suggest replacement sources if available in the context.
   * Store results in a structured JSON format (`citation_checks.json`).

4. **Dash UI integration**
   * Introduce a "Citation Audit" tab showing:
     - Summary stats (claims checked, issues found).
     - Interactive list of flagged citations with links to source excerpts.
     - Buttons to accept/override findings and trigger follow-up retrieval for missing support.

5. **Escalation options**
   * Provide a "Send to frontier judge" button that compiles the local findings into a concise prompt for a higher-accuracy re-check, if needed.

6. **Performance considerations**
   * Run checks asynchronously to avoid blocking the main UI. Show progress spinners and allow users to continue other tasks.

7. **Testing**
   * Create synthetic drafts with known citation issues and assert the verification pipeline identifies them.
   * Add snapshot tests for the Dash UI to ensure issue highlighting works as intended.

---

## Implementation Sequencing

1. Start with the **Retrieval Runbook Co-Pilot** (highest impact vs. effort).
2. Follow with **Enhance-Stage Quality Sweeps** to improve generation readiness.
3. Implement the **Citation Checking** workflow to strengthen post-generation trust.
4. Extend to **Corpus Triage** and **Judgment Pre-Screening** as needed.
5. Treat the **CLI Automation Coach** as an optional enhancement for power users.

Each step should include telemetry (success/failure logs, latency metrics) so the local LLM’s effectiveness can be monitored and prompts iterated quickly.
