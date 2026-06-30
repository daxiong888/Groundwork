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
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
Screens / States Explored
Interactions Explored
Browser / Runtime Evidence
Coverage Evidence Status: prototype_only / browser_verified / runtime_verified / unverified
Known Gaps
Implementation Implications
Proposed PRD / Issue / Contract Feedback
Cleanup Decision
```

Rules:

- Default to one minimum verifiable prototype.
- Create multiple variants only when the user asks for options or the problem is explicitly a visual or interaction tradeoff.
- Use `UI-VERIFY-ROUTER.md` when layout, responsiveness, hover/focus, animation, or state-transition claims matter.
- If browser/runtime inspection is unavailable, mark visual and interaction claims as `unverified`.
- Browser/runtime evidence must include tool, URL/context, action, observation, and limitation.
- Distinguish Browser plugin, Chrome DevTools MCP, Chrome extension tooling, and Playwright/Puppeteer instead of using them interchangeably.
- Apply `CONTRACT-BOUNDARY.md` before any PRD/issue/contract feedback: do not elevate UI mock fields, placeholder payloads, or frontend-only derived values into backend API contract.
- Phrase PRD/issue/contract feedback as proposed feedback unless source-truth verification or explicit user confirmation has already happened.
- Distinguish real backend fields from mock display fields; label mock display fields `mock / illustrative / not backend contract`.
- Label client-side derivations `Derived / illustrative / not backend contract`.
- Do not present a UI prototype as frontend contract without source-backed verification or explicit user confirmation.
- Do not let prototype code become an unowned half-production implementation.
- Keep output question-first: if contract uncertainty remains, ask contract questions instead of inventing backend fields.
