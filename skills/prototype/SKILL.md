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
- "用原型记录 confirmed decisions、rejected variants、mock fields 和 next route"
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

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Prototype contract-boundary review stays in `prototype` when the source of truth is a prototype, mock, screenshot, or static HTML. Classify backend contract candidates, mock/illustrative fields, and client-derived logic, but do not verify source truth or mark backend contract as confirmed unless PRD, backend source, API response, API schema, or explicit user confirmation is actually present.

Use `DECISION-CAPTURE.md` for decision-oriented prototype work. Prototype outputs must separate confirmed decisions, rejected variants, unverified assumptions, mock/illustrative fields, client-derived logic, contract impact, open questions, and next route before downstream PRD, issue, implementation, verification, or handoff work.

Use `skills/_shared/ROLE-SEPARATION.md` when a prototype materially informs design, skill behavior, frontend/backend contract truth, or downstream implementation. A designer/planner prototype can provide design source and self-check evidence, but it cannot independently verify or clean-review its own material design.

## Workflow

1. State the prototype question, decision needed, and contract sources inspected or unavailable.
2. Choose `LOGIC.md` for state, data, reducer, or business-rule prototypes.
3. Choose `UI.md` for UI/static HTML prototypes, visual states, and interaction review.
4. Keep the artifact throwaway and narrow.
5. Apply `DECISION-CAPTURE.md` so confirmed decisions, rejected variants, assumptions, open questions, and next route are explicit.
6. Apply `CONTRACT-BOUNDARY.md` so prototype-only fields or client-derived logic are never treated as backend contract truth.
7. Verify runtime/browser behavior when visual or interaction claims matter.
8. Draft findings as proposed PRD, issue, contract, or implementation feedback unless source-truth verification or explicit user confirmation has already happened.
9. State cleanup decision: delete, absorb, or keep temporarily with reason and review timing.

Do not stop with a browser opt-in question such as asking whether to open a local URL. If browser/runtime evidence is useful but unavailable or not yet approved, still produce the prototype contract-boundary output first, mark the visual or interaction evidence as `unverified`, and name the smallest follow-up browser check.

## CHECKPOINTS

- STOP before handing prototype findings to frontend, PRD, issue, or contract notes unless contract sources, confirmed backend fields, mock / illustrative fields, client-derived logic, and unverified assumptions are separated.
- STOP before calling any field, state, enum, payload, or rule a confirmed backend contract unless it is source-backed by PRD, backend source, API response, API/schema evidence, or explicit user confirmation.
- STOP before promoting a prototype artifact into a durable source of truth unless `Contract Impact` is `confirmed update`; otherwise record `needs confirmation` and concrete confirmation questions.
- STOP before using a visual artifact, generated image, screenshot, HTML packet, or static prototype as browser/runtime evidence unless an actual browser/runtime run was performed and recorded.
- STOP before claiming UAT, release, customer readiness, marketplace, installed-plugin, browser, or runtime evidence from prototype output alone.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| A field has no backend source | Classify it as mock / illustrative or proposed hypothesis. | Do not list it under confirmed backend fields. |
| A state, status, enum, transition, or rule has no source | Mark it as unverified assumption or client-derived logic. | Ask the smallest contract confirmation question instead of treating it as accepted behavior. |
| Client-derived logic is being treated as backend contract | Reclassify it as `Derived / illustrative / not backend contract`. | Set `Contract Impact` to `needs confirmation` unless backend evidence or user confirmation exists. |
| Prototype behavior conflicts with API/schema/source evidence | Name the conflict and stop contract promotion. | Keep prototype observations separate from confirmed source truth and route source-truth verification to `verify` when needed. |
| Browser or runtime evidence is unavailable for visual or interaction claims | Keep the prototype review in `prototype` but mark visual and interaction claims as `unverified`. | State the missing evidence, name the smallest browser/runtime check, and do not claim verified UI behavior. |
| A visual artifact is being treated as runtime, browser, UAT, release, or customer-readiness evidence | Reclassify it as prototype artifact evidence only. | Route to `verify` for the relevant evidence claim. |

## Do Not

- Do not treat mock data, placeholder payloads, sample IDs, sample states, or visual-only labels as product truth.
- Do not invent backend fields, enums, statuses, endpoints, or persistence rules just to express a prototype rule.
- Do not let prototype polish, browser behavior, or interaction smoothness imply real backend or frontend implementation capability.
- Do not present client-derived labels, filters, counters, sort order, or status mapping as server truth without source evidence.
- Do not treat visual artifacts, screenshots, generated images, static HTML, or prototype packets as browser/runtime/UAT/release evidence without an actual run and recorded evidence.
- Do not turn prototype into implementation or verification; keep it a throwaway decision aid and route production changes to `implement` or source-truth evidence review to `verify`.

## Output Shape

```text
Prototype Question
Decision Needed
Contract Sources
Contract Status
Confirmed Decisions
Rejected Variants
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
Open Questions
Next Route: to-prd / to-issues / implement / verify / handoff / dispatch / cleanup / no follow-up
States Covered
Interactions Covered
Browser / Runtime Evidence
Role:
Design Source:
Self-check Evidence:
Clean Review Evidence:
Independent Verification Evidence:
Runtime Evidence:
Browser Evidence:
UAT Evidence:
Release Evidence:
Readiness Boundary:
Required Next Independent Role:
Known Gaps
Implementation Implications
Proposed PRD / Issue / Contract Feedback
Cleanup Decision
Next Action
Artifact Recommendation
```

Contract boundary outputs must explicitly separate:

- Confirmed decisions (including the evidence level and whether they are only confirmed for prototype use)
- Rejected variants (including the rejection reason and whether they can be reopened)
- Backend contract candidates (source-backed when available; otherwise clearly marked proposed hypotheses)
- Contract sources (PRD, source code, API response, schema, user confirmation, or `not inspected / unavailable`)
- Confirmed backend fields (source-backed by PRD, source code, API response, schema, or explicitly user-confirmed)
- Mock / illustrative fields (`mock / illustrative / not backend contract`)
- Client-derived logic (`Derived / illustrative / not backend contract`)
- Unverified assumptions (unknown source, missing schema/API evidence, or needs user/backend confirmation)
- Contract impact (`none`, `needs confirmation`, or `confirmed update`)
- Open questions (smallest confirmation questions before promotion)
- Next route (`to-prd`, `to-issues`, `implement`, `verify`, `handoff`, `dispatch`, `cleanup`, or `no follow-up`)

Prototype output is not a frontend contract unless contract claims are source-backed or explicitly confirmed by the user.

Feedback wording must preserve the source boundary:

- Use `Proposed PRD / Issue / Contract Feedback` for prototype-only findings, hypotheses, mock-field cleanup, and client-derived behavior notes.
- Use `Contract Impact: needs confirmation` when backend/API/schema/source truth has not been checked.
- Use `Contract Impact: confirmed update` only when backend source, API/schema evidence, runtime evidence, or explicit user confirmation already supports the claim.
- If the user asks whether prototype behavior matches backend/API truth, route to `verify` instead of answering as a prototype review.

## Stop Condition

Stop when the prototype question is answered, the decision or remaining gap is explicit, and cleanup or absorption is decided.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Create prototype files only when they answer a concrete question. Delete or absorb prototype code after the question is answered unless there is a clear temporary retention reason. Temporary retention should normally expire within one iteration or at the next PRD/issue/implementation handoff, whichever comes first.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
