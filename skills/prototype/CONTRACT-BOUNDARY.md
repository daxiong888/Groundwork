# Prototype Contract Boundary Rules

Use this checklist whenever a prototype touches data shape, payload examples, state labels, filters, or business rules that might be mistaken for backend contract.

## Purpose

Prevent prototype artifacts from silently redefining server contract.

Prototype artifacts are question tools, not contract sources.

## Boundary Model

Classify every field/rule you reference into one class:

1. **Backend Contract Candidate**
   - Server-owned field/rule.
   - Backed by explicit API/schema/spec/source evidence.
   - Safe to propose as contract input (with citation/evidence).

2. **Prototype Placeholder / Mock**
   - Added to make screens/flows understandable.
   - Not backed by server contract evidence.
   - Must be labeled as mock/placeholder.
   - Must not be copied into PRD acceptance or API contract as fact.

3. **Client-Derived / View Logic**
   - Computed, aggregated, formatted, or inferred in client/prototype.
   - May affect UX behavior but is not server contract by default.
   - Must not be promoted to backend field/rule without separate confirmation.

## Required Output Guardrails

When producing prototype findings:

- Keep outputs **question-first**: answer the prototype question; do not over-specify backend.
- Add explicit contract uncertainty notes whenever backend evidence is missing.
- Convert ambiguity into concrete questions (for backend/PRD/issue), not invented fields.
- If a field/rule appears only in mock data or client derivation, mark it `prototype-only`.

## Disallowed Moves

- Treating mocked JSON fields as accepted API schema.
- Treating frontend filter/state derivation as server-side rule without evidence.
- Using prototype convenience IDs/statuses/enums as production contract defaults.
- Copying prototype-only fields into implementation guidance as required backend payload.

## Escalation Path

If boundary is unclear:

1. Stop contract claims.
2. Record exact unknowns.
3. Propose minimal validation step (API spec check, backend owner confirmation, source inspection).
4. Proceed with throwaway prototype assumptions clearly tagged as non-contract.
