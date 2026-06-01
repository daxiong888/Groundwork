# Implement Notes: Prototype Contract Boundary

Target Reader: Groundwork maintainer reviewing how prototype boundary guidance was implemented.
Reader Action Needed: Check the touched areas and understand which behaviors were added.
Decision Supported: Whether the implementation matched the prototype contract-boundary PRD.
Scope: Prototype skill guidance and guardrail behavior from the v0.2.x hardening line.
Out of Scope: Backend API implementation, frontend UI implementation, or source-truth contract verification.
Evidence Level: `CHANGELOG.md` v0.2.2, `skills/prototype/SKILL.md`, `skills/prototype/CONTRACT-BOUNDARY.md`, and runtime baseline rows.

## Scope

Add contract-boundary rules to prototype workflow so prototype-only data cannot be mistaken for backend contract.

## Changed Areas

- `skills/prototype/SKILL.md` routes prototype contract-boundary classification to `prototype` when source truth is a prototype, mock, screenshot, or static HTML.
- `skills/prototype/CONTRACT-BOUNDARY.md` defines backend contract candidates, prototype placeholders or mocks, and client-derived view logic.
- Guardrail runtime rows exercise the distinction between prototype classification and source-truth verification.

## Implementation Summary

- Added explicit "prototype artifacts are question tools, not contract sources" behavior.
- Required classification of backend contract candidates, confirmed backend fields, mock fields, and client-derived logic.
- Required `Contract Impact: none / needs confirmation / confirmed update`.
- Disallowed treating mocked JSON fields, prototype convenience statuses, or derived frontend logic as accepted backend schema.

## Recorded Checks

- v0.2.2 baseline row `gr-002` passed by classifying prototype fields into contract candidates, mock data, UI sentinel, and derived UI state.
- v0.2.2 baseline row `rel-008` passed by reporting partial prototype evidence and unverified browser evidence instead of overclaiming.
- v0.2.3 targeted rerun row `gr-002` passed by loading `groundwork:prototype` and keeping backend fields as candidates, not confirmed source truth.

## Remaining Gaps

- Prototype boundary classification does not verify backend source truth. When source-truth contract validation is needed, the next workflow is `verify`.
- Static prototype visual behavior still needs browser/runtime evidence before layout or interaction claims are treated as checked.

