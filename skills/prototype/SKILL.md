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
- "对这个交互做 UI variants 比较再决定"
- "用 Logic/state lab 探一下 reducer、状态机或业务规则"
- "这个流程先用 prototype 看看"

Should not trigger:

- The user only needs PRD wording; use `to-prd`.
- The user explicitly asks for grilling or broad planning clarification before a concrete prototype question exists; use `skills/_shared/GRILLING.md` and route to `to-prd`, decision mapping, or `prototype` only after the next question is clear.
- The user asks to implement production code; use `implement`.
- The user asks for readiness evidence after implementation; use `verify`.
- The user asks to verify frontend contract claims against backend source truth; use `verify`.
- The task is a small direct explanation with no artifact value.
- The user asks for multiple visual variants only as decoration without a decision need.
- The user only asks for final frontend implementation commitment, not prototype exploration; use `implement`.
- The user only asks for server/source truth, not prototype exploration; use `verify`.
- The user only asks for runtime, browser, UAT, release, customer-readiness, marketplace, or installed-plugin evidence; use `verify`.
- "验证这个前端实现是否 ready 联调"; use `verify`.
- "按这个原型实现生产代码"; use `implement`.
- "只想把这个需求写成 PRD 文案"; use `to-prd`.
- "只查后端源码事实，不需要原型"; use `verify` or direct source inspection.
- "把这个静态原型当最终合同验收"; use `verify` for source-truth verification.

## Required Evidence

Identify the prototype question first. Use source, PRD, task, data shape, existing prototype files, or UI notes only as needed to answer that question. For static HTML review, do not claim visual state, layout, responsiveness, or interaction correctness without browser/runtime evidence; mark unavailable evidence as `unverified`.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Prototype contract-boundary review stays in `prototype` when the source of truth is a prototype, mock, screenshot, or static HTML. Classify backend contract candidates, mock/illustrative fields, and client-derived logic, but do not verify source truth or mark backend contract as confirmed unless PRD, backend source, API response, API schema, or explicit user confirmation is actually present.

Use `DECISION-CAPTURE.md` for decision-oriented prototype work. Prototype outputs must separate confirmed decisions, rejected variants, unverified assumptions, mock/illustrative fields, client-derived logic, contract impact, open questions, and next route before downstream PRD, issue, implementation, verification, or handoff work.

Use `UI-VARIANTS.md` when material visual or interaction design uncertainty needs a small set of structurally different alternatives. UI variants are exploratory; they must not be treated as final implementation commitment, backend/API contract truth, runtime evidence, browser evidence, UAT evidence, or release evidence by themselves.

Use `LOGIC-LAB.md` when state-machine, reducer, data-transform, validation, or business-rule uncertainty needs bounded exploration. Logic/state lab output is exploratory; it must not be treated as server truth without source evidence, backend/API contract truth, runtime evidence, browser evidence, UAT evidence, or release evidence by itself.

Use `skills/_shared/VISUAL-HANDOFF-PACKET.md` when a prototype output becomes a visual handoff packet, HTML packet, screenshot-backed review note, generated visual artifact, or frontend/backend review packet. The packet remains a communication artifact unless separate source/API, browser, runtime, UAT, or release evidence is produced and named.

Use `skills/_shared/ROLE-SEPARATION.md` when a prototype materially informs design, skill behavior, frontend/backend contract truth, or downstream implementation. A designer/planner prototype can provide design source and self-check evidence, but it cannot independently verify or clean-review its own material design.

Use `skills/_shared/GRILLING.md` before prototype work only when material ambiguity blocks identifying the prototype question and the unknowns are not yet enumerable. Ask one highest-impact question at a time and treat the result as clarification only. Do not grill when a concrete throwaway UI, state, interaction, visual, or business-rule artifact can answer the question faster; keep that work in `prototype`.

## Workflow

1. State the prototype question, decision needed, and contract sources inspected or unavailable.
2. If no concrete prototype question exists because material ambiguity is not yet enumerable, apply `skills/_shared/GRILLING.md` instead of inventing a prototype scope.
3. Choose `LOGIC.md` for simple state, data, reducer, or business-rule prototypes.
4. Choose `LOGIC-LAB.md` when logic exploration needs explicit state-machine, reducer, transform, validation, or business-rule cases.
5. Choose `UI.md` for a single UI/static HTML prototype, visual state, or interaction review.
6. Choose `UI-VARIANTS.md` when material visual or interaction uncertainty requires multiple structurally different alternatives.
7. Keep the artifact throwaway and narrow.
8. Apply `DECISION-CAPTURE.md` so confirmed decisions, rejected variants, assumptions, open questions, and next route are explicit.
9. Apply `CONTRACT-BOUNDARY.md` so prototype-only fields or client-derived logic are never treated as backend contract truth.
10. Apply `skills/_shared/VISUAL-HANDOFF-PACKET.md` when the output is meant for frontend/backend visual review or handoff; include `Mock vs Confirmed Field Badges`, `Do Not Implement / Do Not Assume`, and `Evidence Boundary`.
11. Verify runtime/browser behavior when visual or interaction claims matter.
12. Draft findings as proposed PRD, issue, contract, or implementation feedback unless source-truth verification or explicit user confirmation has already happened.
13. State cleanup decision: delete, absorb, or keep temporarily with reason and review timing.

Do not stop with a browser opt-in question such as asking whether to open a local URL. If browser/runtime evidence is useful but unavailable or not yet approved, still produce the prototype contract-boundary output first, mark the visual or interaction evidence as `unverified`, and name the smallest follow-up browser check.

## CHECKPOINTS

- STOP before handing prototype findings to frontend, PRD, issue, or contract notes unless contract sources, confirmed backend fields, mock / illustrative fields, client-derived logic, and unverified assumptions are separated.
- STOP before calling any field, state, enum, payload, or rule a confirmed backend contract unless it is source-backed by PRD, backend source, API response, API/schema evidence, or explicit user confirmation.
- STOP before promoting a prototype artifact into a durable source of truth unless `Contract Impact` is `confirmed update`; otherwise record `needs confirmation` and concrete confirmation questions.
- STOP before treating a visual handoff packet as source/API, browser, runtime, UAT, release, customer-readiness, or implementation evidence unless the qualifying evidence is produced and named.
- STOP before using a visual artifact, generated image, screenshot, HTML packet, or static prototype as browser/runtime evidence unless an actual browser/runtime run was performed and recorded.
- STOP before claiming UAT, release, customer readiness, marketplace, installed-plugin, browser, or runtime evidence from prototype output alone.
- STOP before treating UI variants as final frontend implementation commitment.
- STOP before treating Logic/state lab output as server truth without source evidence.
- STOP before using prototype to answer non-enumerable material ambiguity. Apply `skills/_shared/GRILLING.md` first, ask one highest-impact question, and keep the result as clarification rather than prototype, acceptance, or implementation readiness evidence.

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
- Do not treat UI variants as final frontend implementation commitment.
- Do not treat Logic/state lab output as server truth without source evidence.
- Do not turn prototype into implementation or verification; keep it a throwaway decision aid and route production changes to `implement` or source-truth evidence review to `verify`.
- Do not use prototype to replace shared grilling when the user needs clarification before the prototype question can be named.

## Output Shape

Prototype output uses schema layering:

- Base fields are always required.
- Branch extension must use exactly one of `LOGIC.md`, `LOGIC-LAB.md`, `UI.md`, or `UI-VARIANTS.md`; that branch extends the base and does not require unrelated branch fields.
- `Visual Handoff Packet` is conditional and appears only when a handoff or review packet is produced.
- The role-separation evidence block is conditional and appears only when materiality thresholds apply.
- `Coverage Evidence Status` must be `prototype_only`, `browser_verified`, `runtime_verified`, or `unverified`.
- `browser_verified` and `runtime_verified` require tool/context/action/observation/limitation evidence; otherwise use `prototype_only` or `unverified`.

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
States Explored
Interactions Explored
Browser / Runtime Evidence
Coverage Evidence Status: prototype_only / browser_verified / runtime_verified / unverified
Visual Handoff Packet
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

Visual handoff packet output must include the required sections from `skills/_shared/VISUAL-HANDOFF-PACKET.md` or mark unavailable sections as `not applicable`. Its `Mock vs Confirmed Field Badges` and `Do Not Implement / Do Not Assume` sections must prevent mock fields, illustrative fields, and client-derived logic from becoming confirmed backend/API/schema truth.

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
