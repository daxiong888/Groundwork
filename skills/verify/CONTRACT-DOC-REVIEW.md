# Contract Document Review

Target Reader: Codex running `verify` for frontend-facing integration or contract documentation.
Reader Action Needed: Check document claims against source truth and remove internal implementation noise.
Decision Supported: Whether a frontend-facing contract doc is accurate enough to hand off.
Scope: Endpoint, method, request, response, errors, call rules, boundary conditions, and source-backed claim review.
Out of Scope: PRD rewriting, backend architecture notes, SQL remediation plans, or internal implementation narration.
Evidence Level: Groundwork issue #9 acceptance criteria and prototype contract-boundary rules.

Frontend contract docs include only:

- endpoint / method
- request fields
- response fields
- error code / error copy
- call rules
- boundary conditions

Frontend contract docs exclude:

- PRD paths
- backend modules
- SQL follow-ups
- internal background
- AI self-narration
- speculative fields from prototypes or mock data

## Review Checklist

```text
Frontend Contract Review
- Target Reader:
- Source Truth Checked:
- Endpoint / Method:
- Request Fields:
- Response Fields:
- Error Codes / Error Copy:
- Call Rules:
- Boundary Conditions:
- Claims Without Source Evidence:
- Internal Noise To Remove:
- Verdict:
```

Rules:

- Check contract claims against backend source, API schema, docs, or explicitly confirmed user evidence.
- Mark missing backend source truth as `unverified`; do not convert a draft into fact.
- Keep implementation notes out of frontend-facing docs unless the target reader needs them to call the API.
- Use `skills/_shared/FRONTEND-CONTRACT-DOC.md` when creating or rewriting a frontend-facing contract artifact.

