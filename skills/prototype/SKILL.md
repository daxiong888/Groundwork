---
name: prototype
description: Build revise or review throwaway logic state or UI static HTML prototypes that answer a specific question. Use when the user asks to 做静态原型, prototype UI, run a state model, test interactions, or explore business rules before PRD or implementation.
---

# prototype

## Trigger Contract

Use this skill when a throwaway artifact can answer a product, state, interaction, visual, or business-rule question faster than full implementation.

Should trigger:

- "做个静态原型"
- "跑一下这个状态模型"
- "用原型验证这个交互"
- "做一个 HTML 页面给前端评审"
- "评审这个静态 HTML 原型"
- "这个流程先用 prototype 看看"

Should not trigger:

- The user only needs PRD wording; use `to-prd`.
- The user asks to implement production code; use `implement`.
- The user asks for readiness evidence after implementation; use `verify`.
- The task is a small direct explanation with no artifact value.
- The user asks for multiple visual variants only as decoration without a decision need.

## Required Evidence

Identify the prototype question first. Use source, PRD, task, data shape, existing prototype files, or UI notes only as needed to answer that question. For static HTML review, do not claim visual state, layout, responsiveness, or interaction correctness without browser/runtime evidence; mark unavailable evidence as `unverified`.

## Workflow

1. State the prototype question and decision needed.
2. Choose `LOGIC.md` for state, data, reducer, or business-rule prototypes.
3. Choose `UI.md` for UI/static HTML prototypes, visual states, and interaction review.
4. Keep the artifact throwaway and narrow.
4a. Apply `CONTRACT-BOUNDARY.md` so prototype-only fields or client-derived logic are never treated as backend contract truth.
5. Verify runtime/browser behavior when visual or interaction claims matter.
6. Feed findings back into PRD, issue, contract, or implementation notes.
7. State cleanup decision: delete, absorb, or keep temporarily with reason.

## Output Shape

```text
Prototype Question
Decision Needed
States Covered
Interactions Covered
Known Gaps
Implementation Implications
PRD / Issue / Contract Updates
Cleanup Decision
Next Action
Artifact Recommendation
```

Contract boundary outputs must explicitly separate:

- Backend contract candidates (source-backed when available; otherwise clearly marked proposed hypotheses)
- Prototype-only placeholders/mocks (must not become contract)
- Client-derived/transient logic (must not be promoted as API contract)

## Stop Condition

Stop when the prototype question is answered, the decision or remaining gap is explicit, and cleanup or absorption is decided.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Create prototype files only when they answer a concrete question. Delete or absorb prototype code after the question is answered unless there is a clear temporary retention reason.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
