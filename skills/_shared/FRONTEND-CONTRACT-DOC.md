# Frontend Contract Document Shape

Target Reader: Frontend engineer integrating against a backend or service contract.
Reader Action Needed: Implement calls and handle responses/errors without reading backend internals.
Decision Supported: Whether the frontend has enough source-backed contract detail to proceed.
Scope: Frontend-facing contract document sections and forbidden internal content.
Out of Scope: PRD background, backend module maps, SQL follow-ups, internal runbooks, or AI narration.
Evidence Level: Groundwork issue #9 acceptance criteria.

Use this shape when a frontend-facing contract artifact is needed:

```text
Frontend Contract
- Endpoint / Method:
- Request Fields:
- Response Fields:
- Error Code / Error Copy:
- Call Rules:
- Boundary Conditions:
- Source Evidence:
- Unverified / Needs Confirmation:
```

Keep the artifact focused on what the frontend needs to call, render, branch, retry, or display. Move backend-internal details to engineering notes only when the target reader explicitly needs them.

