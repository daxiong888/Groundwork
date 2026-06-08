# Static Filter Prototype Fixture

This fixture is a tiny static HTML prototype for the `prototype` skill.

Question:

Should the activity filter be shown by default, or only when the task contains
multiple activities?

Expected `prototype` behavior:

- state the prototype question and decision needed
- identify covered states and interactions
- use browser or runtime evidence when available
- mark visual or interaction claims as `unverified` when browser/runtime
  inspection is unavailable
- state proposed PRD, issue, or contract feedback unless source truth is verified
- include a cleanup decision

Contract-boundary metadata:

- Confirmed backend fields from this fixture: none. The fixture is static HTML only and provides no backend source, API schema, runtime API response, or explicit user confirmation.
- Proposed backend hypotheses: a backend may need an activity identifier or activity name filter if source truth later confirms that activity filtering is server-owned.
- Mock / illustrative fields: `task-2`, `13800000002`, `安检活动`, `抄表活动`, and `全部活动` are display examples only and are not backend contract.
- Client-derived logic: the visibility rule "show activity filter only for multi-activity tasks" is prototype/view logic until backend/API/PRD source truth confirms ownership.
- Contract impact: `needs confirmation` for backend/API contract; prototype findings should be drafted as proposed PRD, issue, or contract feedback.
