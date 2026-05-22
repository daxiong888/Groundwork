# UI Prototype Branch

Use this branch for static HTML, UI state exploration, interaction flows, visual hierarchy, and frontend review artifacts.

Required output:

```text
Prototype Question
Decision Needed
Contract Status
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Contract Impact: none / needs confirmation / confirmed update
Screens / States Covered
Interactions Covered
Browser / Runtime Evidence
Known Gaps
Implementation Implications
PRD / Issue / Contract Updates
Cleanup Decision
```

Rules:

- Default to one minimum verifiable prototype.
- Create multiple variants only when the user asks for options or the problem is explicitly a visual or interaction tradeoff.
- Use browser/runtime verification when layout, responsiveness, hover/focus, animation, or state-transition claims matter.
- If browser/runtime inspection is unavailable, mark visual and interaction claims as `unverified`.
- Apply `CONTRACT-BOUNDARY.md` before any PRD/issue/contract feedback: do not elevate UI mock fields, placeholder payloads, or frontend-only derived values into backend API contract.
- Distinguish real backend fields from mock display fields; label mock display fields `mock / illustrative / not backend contract`.
- Label client-side derivations `derived / illustrative / not backend contract`.
- Do not present a UI prototype as frontend contract without source-backed verification or explicit user confirmation.
- Do not let prototype code become an unowned half-production implementation.
- Keep output question-first: if contract uncertainty remains, ask contract questions instead of inventing backend fields.
