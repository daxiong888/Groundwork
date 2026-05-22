# UI Prototype Branch

Use this branch for static HTML, UI state exploration, interaction flows, visual hierarchy, and frontend review artifacts.

Required output:

```text
Prototype Question
Decision Needed
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
- Do not let prototype code become an unowned half-production implementation.
- Keep output question-first: if contract uncertainty remains, ask contract questions instead of inventing backend fields.
