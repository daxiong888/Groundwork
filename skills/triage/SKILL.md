---
name: triage
description: Use when evidence is needed to classify task readiness, blockers, severity, AFK/HITL ownership, lifecycle state, or closeout. Do not use for requirement shaping, task slicing, code edits, implementation planning, verification reports, dispatch packages, or wiki work.
---

# triage

## Trigger Contract

Use this skill when the user wants to decide task state, readiness, blocker status, AFK/HITL routing, or closeout.

Should trigger:

- "triage 一下这个 issue"
- "看看这个任务能不能给 agent 做"
- "这个任务现在 blocked 吗"
- "判断一下 ready-for-agent 还是 ready-for-human"
- "这个 issue 要不要 close"
- "判断是否还要本地 lifecycle state"
- "外部 GitHub issue 已经完整拥有状态，判断是否还要本地 lifecycle state"
- "这个任务状态应该由外部 issue 还是本地 STATE.md 拥有"
- "判断这个任务下一步归 agent、人还是 blocked"
- "这个 issue 能不能 close，缺什么证据"

Should not trigger:

- The user asks to write a new PRD; use `to-prd`.
- The user asks to split accepted requirements; use `to-issues`.
- The user asks for implementation steps after readiness is known; use `write-plan`.
- The user asks for code edits; use `implement`.
- The user asks for release or UAT evidence; use `verify`.
- "把这些 ready issue 分配给 runtime 或 subagent"; use `dispatch`.
- "只写实现计划，不要改代码"; use `write-plan`.
- "验证这次能不能给前端联调"; use `verify`.
- "基于这个 PRD 拆 issues"; use `to-issues`.

## Required Evidence

Inspect the task source, PRD/spec, current conversation, previous state when known, known blockers, source references, lifecycle state, and verification expectations. If the evidence source is unknown, classify as `needs-info`.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Every verdict must include `Severity` and `State Transition Reason`. Use `skills/_shared/SEVERITY.md` as the shared enum. In `triage`, severity describes the current blocker or gap impact, **not overall product priority**.

## Severity Derivation

Use this sequence before assigning severity:

1. Identify the current blocker or gap being triaged, not the feature's business importance.
2. Map the gap to the strongest affected boundary: production safety, security/privacy, release, major acceptance/data/UAT, limited workaround, or wording/evidence hygiene.
3. Check blast radius, dependency impact, and whether a practical workaround exists.
4. Assign the highest matching severity from `skills/_shared/SEVERITY.md`.
5. If the gap source, affected boundary, or workaround is unknown, classify the task as `needs-info`, name the missing evidence, and do not infer product priority as severity.

AFK/HITL is a local execution-routing decision, not a quality score:

- `AFK`: the next action can be completed from available source truth, acceptance criteria, scope boundaries, first inspection step, and verification expectation without a new human product/access/design decision.
- `HITL`: the next action needs a human decision, missing authority, private access not already available, manual validation, approval for risky mutation, or a choice between valid product/design options.

Closeout is allowed only when `verify` evidence shows no material gap remains, the task is already `done` with sufficient linked evidence, or `wontfix` is explicitly justified by a product/owner decision. Attempted closeout without those facts must stay open as `verification`, `needs-info`, or `ready-for-human`, with the missing closeout evidence named.

When moving from `needs-info` to `ready-for-agent`, explicitly list the `Evidence Added` or fields that were completed. Do not mark a task `ready-for-agent` while readiness-blocking fields remain missing.

Use `skills/_shared/LIFECYCLE-STATE.md` only to decide whether workstream-scoped lifecycle state is justified. Do not create a task database, and do not recommend state just because a task is `ready-for-agent`.
If an external issue or PR fully owns source truth and recovery state, recommend no local lifecycle state unless a Groundwork-specific recovery need remains. If local `STATE.md` conflicts with a canonical issue, PRD, source code, tests, runtime evidence, or user-confirmed decision, mark the local state stale and follow the canonical source.

When the verdict is executable `ready-for-agent + AFK`, include a `Goal Contract` in the agent-ready brief using the canonical field names from `skills/_shared/GOAL-CONTRACT.md`. The contract must include a `/goal` command, verification, constraints, boundaries, iteration policy, stop condition, pause condition, non-goals, risk/gate, preferred runtime recommendation, and expected result package. `Pause If` must map to the AFK/HITL decision points so the implementation runtime knows when to pause for human input, source clarification, access, approval, or risk escalation.

Do not generate an executable child goal for `needs-info`, `ready-for-human`, or HITL-only tasks. If the task is HITL, output a human-decision brief instead: name the decision needed, viable options, risks, and the next human action. If business rules, acceptance criteria, source truth, verification expectations, or boundaries are unclear, classify as `needs-info` or `ready-for-human` and do not invent product truth to fill a Goal Contract.

`Preferred Runtime` and `Execution Profile Recommendation` are recommendations only. `triage` may recommend values such as `codex_app_managed_worktree_thread` for non-trivial executable write work with source truth and validation present, or lighter profiles for direct/read-only work, but later `dispatch` makes the final runtime route. `triage` must not claim model/reasoning selector enforcement; it may only state profile preferences and routing rationale.

## Workflow

1. Gather the task source and current requested outcome.
2. Classify state: `draft`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `verification`, `done`, or `wontfix`.
3. Assign severity for the current blocker or gap using `Severity Derivation`.
4. State the transition reason and separate `Evidence Added` from `Evidence Missing`.
5. Apply the readiness contracts from `docs/prd.md`.
6. If executable `ready-for-agent + AFK`, produce an agent-ready brief using `AGENT-BRIEF.md`, including `Goal Contract` and `Execution Profile Recommendation`.
7. If `ready-for-human`, state the human decision needed, options, risks, and specific next action.
8. If `needs-info`, `ready-for-human`, or HITL-only, do not emit a dispatchable `/goal`; use evidence missing or a human-decision brief instead.
9. Decide whether lifecycle state is needed for cross-session recovery, gap closure, UAT/release reuse, or decision-pending continuation.
10. Recommend `write-plan`, `implement`, `verify`, direct user decision, `triage closeout`, or gap closure as appropriate.

## CHECKPOINTS

- STOP before marking `ready-for-agent` unless acceptance criteria, source/evidence or first inspection step, expected output, stop condition, AFK/HITL decision points, blockers, and out-of-scope boundaries are explicit.
- STOP before changing state unless the previous/current state, severity, transition reason, `Evidence Added`, and `Evidence Missing` can be tied to the task source.
- STOP before recommending lifecycle state, closeout, or external ownership changes when the source of truth is unclear, mixed, or would duplicate an external issue without a recovery need.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Evidence source is unknown or missing | Classify as `needs-info`. | Ask for the highest-impact missing source, field, or first inspection step. |
| Blocker is unresolved or a human choice is required | Classify as `ready-for-human` or keep `needs-info`. | Name options, risks, and the exact human decision needed; do not produce an agent-ready brief. |
| Source truth or ownership conflicts | Mark source truth as `mixed` or `unknown`. | Explain the conflict and stop before lifecycle duplication, closeout, or tracker mutation. |
| Closeout is requested without verify/done/wontfix evidence | Keep open as `verification`, `needs-info`, or `ready-for-human`. | Name the missing closeout evidence and recommend `verify`, gap closure, or owner decision before closeout. |
| Local lifecycle state conflicts with canonical source truth | Mark lifecycle state as stale. | Follow the canonical source and do not let stale `STATE.md` drive closeout, readiness, or ownership. |
| External tracker already owns task state and recovery facts | Recommend no local lifecycle state unless a Groundwork recovery threshold remains. | Cite the external owner and keep local output conversation-only or paste-ready for that tracker. |

## Do Not

- Do not treat severity as product priority; it is only the current blocker or gap impact.
- Do not generate an agent-ready brief while any readiness-blocking field remains missing.
- Do not generate an executable `/goal` for `needs-info`, `ready-for-human`, or HITL-only tasks.
- Do not claim `triage` enforces runtime, model, or reasoning selectors; runtime and execution profile fields are recommendations for `dispatch`.
- Do not create local lifecycle state, task databases, or closeout actions just because a task is `ready-for-agent`.
- Do not let `.planning`, `.gsd`, project-global task directories, or stale `STATE.md` override Groundwork source-truth and lifecycle-state boundaries.

## Output Shape

```text
Triage Verdict
State
Severity: P0 / P1 / P2 / P3 / none
Execution: AFK / HITL
Previous State
State Transition Reason
Evidence
Evidence Added
Evidence Missing
Blockers
Readiness Check
Lifecycle State Recommendation
- Needed: yes / no
- Reason:
- Artifact:
- External Task Source:
Agent Brief or Human Decision
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the state, severity, transition reason, blockers, AFK/HITL classification, readiness reason, evidence added/missing, and next action are explicit.

## Gate Rule

If the user asks to create `.planning`, `.gsd`, a GSD clone, or a project-global task directory/database for all tasks, reject that request as stated. Do not offer `.planning` / `.gsd` as scaffold options. If durable continuation state is actually justified, redirect to Groundwork's workstream-scoped `artifacts/<workstream-slug>/STATE.md` boundary; otherwise keep the decision conversation-only or recommend a short PRD to define an external system contract.

## Artifact Rule

Do not create `OUT-OF-SCOPE.md` in MVP. Write an agent brief only when it will be reused for execution, review, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
