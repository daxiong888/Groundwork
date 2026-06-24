Target Reader: Codex running the `prototype` skill when prototype data, state, or UI output could be mistaken for backend/API truth.
Reader Action Needed: Classify prototype fields and rules before downstream PRD, issue, implementation, verification, or handoff work.
Decision Supported: Whether a prototype field/rule is confirmed contract, proposed feedback, mock-only, client-derived, or blocked pending confirmation.
Artifact Type: prototype contract-boundary reference
Source of Truth: docs/prd-v0.5-prototype-first-skill-expansion.md FR-530, AC-B4, AC-C3 and artifacts/v0.5-prototype-first-skill-expansion/issue-map.md V050-005A.
Scope: Backend/API contract candidates, prototype placeholders, mock fields, client-derived logic, source evidence, contract impact, and evidence boundaries.
Out of Scope: Backend/API implementation, source-truth verification, public visual-handoff skill creation, UI variant mechanics, logic/state lab mechanics, runtime execution, browser QA, UAT, release, or customer readiness.
Evidence Level: Source-validation guidance only; prototype outputs are not backend/API, browser, runtime, UAT, release, or acceptance evidence by themselves.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, or private payloads.

# Prototype Contract Boundary Rules

Use this checklist whenever a prototype touches data shape, payload examples, state labels, filters, or business rules that might be mistaken for backend contract.

## Purpose

Prevent prototype artifacts from silently redefining server contract.

Prototype artifacts are question tools, not contract sources.

Do **not** assume backend APIs already exist during prototyping. In early discovery, treat backend shape as unknown until verified.

## Boundary Model

Classify every field/rule you reference into one class:

1. **Backend Contract Candidate**
   - Server-owned field/rule when such ownership exists.
   - Backed by explicit PRD, source code, API response, API schema, spec, or user-confirmed evidence when listed as confirmed.
   - If backend is not implemented yet or source truth has not been inspected, record this as a **proposed contract hypothesis** (not accepted fact).

2. **Prototype Placeholder / Mock**
   - Added to make screens/flows understandable.
   - Not backed by server contract evidence.
   - Must be labeled `mock / illustrative / not backend contract`.
   - Must not be copied into PRD acceptance or API contract as fact.

3. **Client-Derived / View Logic**
   - Computed, aggregated, formatted, or inferred in client/prototype.
   - May affect UX behavior but is not server contract by default.
   - Must be labeled `Derived / illustrative / not backend contract`.
   - Must not be promoted to backend field/rule without separate confirmation.

4. **Confirmed Backend/API Contract**
   - Backed by named PRD, backend source, API response, API schema, runtime evidence, or explicit user confirmation.
   - Must cite the evidence source in `Contract Sources`.
   - Must not be inferred from a visual artifact, static HTML, screenshot, generated image, fixture-only payload, or client derivation.

## Required Output Guardrails

When producing prototype findings:

- Keep outputs **question-first**: answer the prototype question; do not over-specify backend.
- Add explicit contract uncertainty notes whenever backend evidence is missing.
- If backend implementation has not started, mark contract fields/rules as `proposed` and list open confirmation questions.
- If backend implementation might exist but has not been inspected in this turn, keep fields/rules as `proposed` until source-truth verification happens.
- Convert ambiguity into concrete questions (for backend/PRD/issue), not invented fields.
- If a field/rule appears only in mock data or client derivation, mark it `prototype-only`.
- Include `Confirmed Decisions`, `Rejected Variants`, `Contract Sources`, `Contract Status`, `Confirmed Backend Fields`, `Mock / Illustrative Fields`, `Client-derived Logic`, `Unverified Assumptions`, `Contract Impact: none / needs confirmation / confirmed update`, `Open Questions`, and `Next Route`.
- Do not present a prototype as frontend contract unless each contract claim is source-backed or the user explicitly confirms it.
- When feeding findings into PRD, issue, contract, or implementation notes, phrase them as proposed feedback unless source-truth verification or explicit confirmation has already happened.
- Keep visual artifacts separate from browser/runtime evidence. A screenshot, generated image, static HTML file, or visual handoff artifact is not browser evidence unless an actual browser run is performed and recorded.
- Keep runtime, UAT, release, customer-readiness, marketplace, and installed-plugin claims out of prototype output unless an actual qualifying run or evidence package is produced and named.

## Disallowed Moves

- Treating mocked JSON fields as accepted API schema.
- Treating frontend filter/state derivation as server-side rule without evidence.
- Using prototype convenience IDs/statuses/enums as production contract defaults.
- Copying prototype-only fields into implementation guidance as required backend payload.
- Adding backend fields based only on visual storytelling or screen convenience.
- Implying unsupported backend capability.
- Presenting client-computed labels, sort order, filters, counters, or status derivations as server truth without source evidence.
- Treating visual artifacts as browser/runtime/UAT/release evidence without actual run evidence.

## Escalation Path

If boundary is unclear:

1. Stop contract claims.
2. Record exact unknowns.
3. Propose minimal validation step (PRD check, source inspection, API response/schema check, or backend owner confirmation).
4. Proceed with throwaway prototype assumptions clearly tagged as non-contract.

## Feedback Promotion Rule

Prototype findings can inform downstream work, but they do not promote themselves into contract truth.

Use this promotion ladder:

1. `proposed feedback`: the finding comes from static HTML, mock data, screenshot, prototype code, or client-side derivation only.
2. `needs confirmation`: the finding likely affects backend/API/schema/PRD contract, but source truth has not been checked.
3. `confirmed update`: PRD, backend source, API response/schema evidence, runtime evidence, or explicit user confirmation supports the contract claim.

If the user asks to verify prototype behavior against backend/API/source truth, stop prototype contract promotion and route the source-truth review to `verify`.

## Contract Evidence Boundary

Use these labels exactly when evidence boundaries matter:

- Prototype artifact evidence: may support `confirmed for prototype` decisions, rejected variants, or proposed feedback only.
- Source/API/schema/user-confirmation evidence: required before a field/rule is a confirmed backend/API contract.
- Browser evidence: requires an actual browser run with tool, URL/context, action, observation, and limitation.
- Runtime evidence: requires an actual runtime/tool execution with command/tool, scope, output, and limitation.
- UAT/release/customer readiness: out of scope for `prototype` unless a separate verification package explicitly provides that evidence.
