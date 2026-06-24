Target Reader: Codex running the `prototype` skill when material visual or interaction uncertainty needs comparison before PRD, issue, implementation, or visual handoff work.
Reader Action Needed: Decide whether to create or review UI variants, capture the selected or rejected options, and preserve evidence boundaries.
Decision Supported: Whether UI variants answered a design question, what remains unverified, and what must not be treated as implementation or contract truth.
Artifact Type: prototype UI-variants reference
Source of Truth: docs/prd-v0.5-prototype-first-skill-expansion.md FR-531 and artifacts/v0.5-prototype-first-skill-expansion/issue-map.md V050-005B.
Scope: Material UI/interaction variant triggers, should-not-trigger cases, variant comparison output, rejected variants, mock fields, client-derived logic, and evidence boundaries.
Out of Scope: Production frontend implementation, public `visual-handoff` skill creation, backend/API source-truth verification, browser QA, runtime execution, UAT, release, customer readiness, or final implementation commitment.
Evidence Level: Source-validation guidance only; UI variants are exploratory prototype artifacts and are not backend/API, browser, runtime, UAT, release, acceptance, or final implementation evidence by themselves.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, screenshots, or private payloads.

# UI Variants

Use UI variants when the prototype question is a material visual or interaction design uncertainty that cannot be answered by one obvious static prototype.

UI variants are exploratory comparison artifacts. They may help choose or reject a direction, but they are not final frontend implementation commitment, browser evidence, runtime evidence, UAT evidence, release evidence, or backend/API contract truth by themselves.

## Trigger Boundary

UI variants should trigger when at least one is true:

- Material visual hierarchy, layout density, navigation shape, or interaction model is uncertain.
- The user asks for options, alternatives, comparison, or variant review to make a product/design decision.
- A selected screen needs a side-by-side treatment before visual handoff, PRD wording, issue slicing, or implementation planning.
- The tradeoff affects user behavior, accessibility, information architecture, review cost, or downstream frontend/backend coordination.

UI variants should not trigger when:

- The request is decoration-only, cosmetic polish, or style exploration with no decision need.
- One minimum prototype is enough to answer the question.
- The user asks whether a UI claim is source/API truth, runtime truth, browser truth, UAT evidence, release evidence, or customer readiness; route that claim to `verify`.
- The user asks to implement production frontend code; route to `implement`.
- The requested output would be treated as final implementation commitment without separate accepted scope and implementation evidence.

## Required Output

```text
Prototype Question
Decision Needed
Variant Set
Selected Variant or Current Preference
Rejected Variants
Contract Sources
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
Open Questions
Next Route: to-prd / to-issues / implement / verify / handoff / dispatch / cleanup / no follow-up
Browser / Runtime Evidence
Evidence Boundary
Cleanup Decision
```

## Variant Rules

- Keep the variant set small and decision-oriented. Prefer two or three structurally different alternatives over many cosmetic permutations.
- Name the decision each variant tests, such as density, grouping, progressive disclosure, navigation, empty/error treatment, or action placement.
- Record rejected variants with the rejection reason and evidence level.
- If no variant is selected, state the blocking unknown instead of implying convergence.
- Use `DECISION-CAPTURE.md` for confirmed decisions, rejected variants, unverified assumptions, `Contract Impact`, open questions, and next route.
- Use `CONTRACT-BOUNDARY.md` before any PRD, issue, contract, visual handoff, or implementation feedback.
- Use `skills/_shared/VISUAL-HANDOFF-PACKET.md` only when the variants become a visual handoff packet; preserve its `Mock vs Confirmed Field Badges`, `Do Not Implement / Do Not Assume`, and `Evidence Boundary` sections.

## Evidence Boundary

- UI variant output may support `confirmed for prototype` design decisions and proposed feedback only.
- Mock fields must be labeled `mock / illustrative / not backend contract`.
- Client-derived display logic must be labeled `Derived / illustrative / not backend contract`.
- Source/API/schema truth requires named PRD, source code, API response, schema, runtime evidence, or explicit user confirmation.
- Browser evidence requires an actual browser run with tool, URL/context, action, observation, and limitation.
- Runtime evidence requires an actual command/tool execution with scope, output, and limitation.
- UAT and release evidence require separate verification packages for those claims.
- Final frontend implementation commitment requires accepted implementation scope and production code evidence, not UI variant output alone.

## Hard Stops

- Stop before treating UI variant output as final frontend implementation commitment.
- Stop before promoting variant mock data, visual labels, placeholder payloads, or client-derived values into backend/API/schema truth.
- Stop before treating a variant artifact, screenshot, generated image, static HTML, or visual handoff packet as runtime/browser/UAT/release evidence without the qualifying run and recorded evidence.
- Stop before using UI variant selection to bypass PRD, issue, or implementation acceptance criteria.
