# Logic Prototype Branch

Use this branch for state machines, data shapes, reducers, business rules, validation logic, or terminal prototypes.

Required output:

```text
Prototype Question
Decision Needed
Contract Status
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
Model / Rule Under Test
Inputs
States / Transitions
Cases Covered
Observed Result
Known Gaps
Implementation Implications
Cleanup Decision
```

Rules:

- Keep logic prototypes small and disposable.
- Prefer deterministic code or tables when behavior must be repeatable.
- Do not treat prototype code as production code.
- Apply `CONTRACT-BOUNDARY.md`: model assumptions, mocked schema fields, and client-derived calculations remain prototype-only unless independently verified by backend/source contract evidence.
- Label mocked fields `mock / illustrative / not backend contract`.
- Label client-derived calculations `derived / illustrative / not backend contract`.
- Do not present a logic prototype as frontend or backend contract without source-backed verification or explicit user confirmation.
- If results contradict PRD/task assumptions, feed that back before implementation.
- Keep the prototype question-first; unresolved contract ambiguity should become explicit contract questions, not invented server behavior.
