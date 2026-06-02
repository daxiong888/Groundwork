---
name: prototype
description: Build revise or review throwaway logic state or UI static HTML prototypes, including prototype contract-boundary classification, to answer a product interaction visual or business-rule question before PRD or implementation.
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
- "评审静态筛选器原型并判断哪些字段能进入后端合同"
- "从原型里区分 backend contract candidate、mock 和 client-derived logic"
- "这个流程先用 prototype 看看"

Should not trigger:

- The user only needs PRD wording; use `to-prd`.
- The user asks to implement production code; use `implement`.
- The user asks for readiness evidence after implementation; use `verify`.
- The user asks to verify frontend contract claims against backend source truth; use `verify`.
- The task is a small direct explanation with no artifact value.
- The user asks for multiple visual variants only as decoration without a decision need.

## Required Evidence

Identify the prototype question first. Use source, PRD, task, data shape, existing prototype files, or UI notes only as needed to answer that question. For static HTML review, do not claim visual state, layout, responsiveness, or interaction correctness without browser/runtime evidence; mark unavailable evidence as `unverified`.

Prototype contract-boundary review stays in `prototype` when the source of truth is a prototype, mock, screenshot, or static HTML. Classify backend contract candidates, mock/illustrative fields, and client-derived logic, but do not verify source truth or mark backend contract as confirmed unless backend source, API schema, or explicit user confirmation is actually present.

## Workflow

1. State the prototype question and decision needed.
2. Choose `LOGIC.md` for state, data, reducer, or business-rule prototypes.
3. Choose `UI.md` for UI/static HTML prototypes, visual states, and interaction review.
4. Keep the artifact throwaway and narrow.
5. Apply `CONTRACT-BOUNDARY.md` so prototype-only fields or client-derived logic are never treated as backend contract truth.
6. Verify runtime/browser behavior when visual or interaction claims matter.
7. Feed findings back into PRD, issue, contract, or implementation notes.
8. State cleanup decision: delete, absorb, or keep temporarily with reason and review timing.

## CHECKPOINTS

- STOP before handing prototype findings to frontend, PRD, issue, or contract notes unless confirmed backend fields, mock / illustrative fields, client-derived logic, and unverified assumptions are separated.
- STOP before calling any field, state, enum, payload, or rule a confirmed backend contract unless it is source-backed by backend source, API/schema evidence, or explicit user confirmation.
- STOP before promoting a prototype artifact into a durable source of truth unless `Contract Impact` is `confirmed update`; otherwise record `needs confirmation` and concrete confirmation questions.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| A field has no backend source | Classify it as mock / illustrative or proposed hypothesis. | Do not list it under confirmed backend fields. |
| A state, status, enum, transition, or rule has no source | Mark it as unverified assumption or client-derived logic. | Ask the smallest contract confirmation question instead of treating it as accepted behavior. |
| Client-derived logic is being treated as backend contract | Reclassify it as `derived / illustrative / not backend contract`. | Set `Contract Impact` to `needs confirmation` unless backend evidence or user confirmation exists. |
| Prototype behavior conflicts with API/schema/source evidence | Name the conflict and stop contract promotion. | Keep prototype observations separate from confirmed source truth and route source-truth verification to `verify` when needed. |

## Do Not

- Do not treat mock data, placeholder payloads, sample IDs, sample states, or visual-only labels as product truth.
- Do not invent backend fields, enums, statuses, endpoints, or persistence rules just to express a prototype rule.
- Do not let prototype polish, browser behavior, or interaction smoothness imply real backend or frontend implementation capability.
- Do not turn prototype into implementation or verification; keep it a throwaway decision aid and route production changes to `implement` or source-truth evidence review to `verify`.

## Output Shape

```text
Prototype Question
Decision Needed
Contract Status
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
States Covered
Interactions Covered
Browser / Runtime Evidence
Known Gaps
Implementation Implications
PRD / Issue / Contract Updates
Cleanup Decision
Next Action
Artifact Recommendation
```

Contract boundary outputs must explicitly separate:

- Backend contract candidates (source-backed when available; otherwise clearly marked proposed hypotheses)
- Confirmed backend fields (source-backed or explicitly user-confirmed)
- Mock / illustrative fields (`mock / illustrative / not backend contract`)
- Client-derived logic (`derived / illustrative / not backend contract`)
- Unverified assumptions (unknown source, missing schema/API evidence, or needs user/backend confirmation)
- Contract impact (`none`, `needs confirmation`, or `confirmed update`)

Prototype output is not a frontend contract unless contract claims are source-backed or explicitly confirmed by the user.

## Stop Condition

Stop when the prototype question is answered, the decision or remaining gap is explicit, and cleanup or absorption is decided.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Create prototype files only when they answer a concrete question. Delete or absorb prototype code after the question is answered unless there is a clear temporary retention reason. Temporary retention should normally expire within one iteration or at the next PRD/issue/implementation handoff, whichever comes first.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
