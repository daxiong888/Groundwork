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
   - Backed by explicit API/schema/spec/source evidence when listed as confirmed.
   - If backend is not implemented yet or source truth has not been inspected, record this as a **proposed contract hypothesis** (not accepted fact).

2. **Prototype Placeholder / Mock**
   - Added to make screens/flows understandable.
   - Not backed by server contract evidence.
   - Must be labeled `mock / illustrative / not backend contract`.
   - Must not be copied into PRD acceptance or API contract as fact.

3. **Client-Derived / View Logic**
   - Computed, aggregated, formatted, or inferred in client/prototype.
   - May affect UX behavior but is not server contract by default.
   - Must be labeled `derived / illustrative / not backend contract`.
   - Must not be promoted to backend field/rule without separate confirmation.

## Required Output Guardrails

When producing prototype findings:

- Keep outputs **question-first**: answer the prototype question; do not over-specify backend.
- Add explicit contract uncertainty notes whenever backend evidence is missing.
- If backend implementation has not started, mark contract fields/rules as `proposed` and list open confirmation questions.
- If backend implementation might exist but has not been inspected in this turn, keep fields/rules as `proposed` until source-truth verification happens.
- Convert ambiguity into concrete questions (for backend/PRD/issue), not invented fields.
- If a field/rule appears only in mock data or client derivation, mark it `prototype-only`.
- Include `Contract Status`, `Confirmed Backend Fields`, `Mock / Illustrative Fields`, `Client-derived Logic`, and `Contract Impact: none / needs confirmation / confirmed update`.
- Do not present a prototype as frontend contract unless each contract claim is source-backed or the user explicitly confirms it.
- When feeding findings into PRD, issue, contract, or implementation notes, phrase them as proposed feedback unless source-truth verification or explicit confirmation has already happened.

## Disallowed Moves

- Treating mocked JSON fields as accepted API schema.
- Treating frontend filter/state derivation as server-side rule without evidence.
- Using prototype convenience IDs/statuses/enums as production contract defaults.
- Copying prototype-only fields into implementation guidance as required backend payload.
- Adding backend fields based only on visual storytelling or screen convenience.
- Implying unsupported backend capability.

## Escalation Path

If boundary is unclear:

1. Stop contract claims.
2. Record exact unknowns.
3. Propose minimal validation step (API spec check, backend owner confirmation, source inspection).
4. Proceed with throwaway prototype assumptions clearly tagged as non-contract.

## Feedback Promotion Rule

Prototype findings can inform downstream work, but they do not promote themselves into contract truth.

Use this promotion ladder:

1. `proposed feedback`: the finding comes from static HTML, mock data, screenshot, prototype code, or client-side derivation only.
2. `needs confirmation`: the finding likely affects backend/API/schema/PRD contract, but source truth has not been checked.
3. `confirmed update`: backend source, API/schema evidence, runtime evidence, or explicit user confirmation supports the contract claim.

If the user asks to verify prototype behavior against backend/API/source truth, stop prototype contract promotion and route the source-truth review to `verify`.
