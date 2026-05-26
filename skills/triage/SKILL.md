---
name: triage
description: Classify task readiness blockers AFK HITL ready-for-agent ready-for-human needs-info wontfix closeout, or lifecycle-state ownership decisions based on evidence. Use when the user asks to triage an issue, 看能不能给 agent 做, decide readiness, decide whether local lifecycle state is needed, decide external source-of-truth ownership, unblock, or close a task.
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

Should not trigger:

- The user asks to write a new PRD; use `to-prd`.
- The user asks to split accepted requirements; use `to-issues`.
- The user asks for implementation steps after readiness is known; use `write-plan`.
- The user asks for code edits; use `implement`.
- The user asks for release or UAT evidence; use `verify`.

## Required Evidence

Inspect the task source, PRD/spec, current conversation, known blockers, source references, lifecycle state, and verification expectations. If the evidence source is unknown, classify as `needs-info`.

Use `skills/_shared/LIFECYCLE-STATE.md` only to decide whether workstream-scoped lifecycle state is justified. Do not create a task database, and do not recommend state just because a task is `ready-for-agent`.

If the user asks to create `.planning`, `.gsd`, a GSD clone, or a project-global task directory/database for all tasks, reject that request as stated. Do not offer `.planning` / `.gsd` as scaffold options. If durable continuation state is actually justified, redirect to Groundwork's workstream-scoped `artifacts/<workstream-slug>/STATE.md` boundary; otherwise keep the decision conversation-only or recommend a short PRD to define an external system contract.

## Workflow

1. Gather the task source and current requested outcome.
2. Classify state: `draft`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `verification`, `done`, or `wontfix`.
3. Apply the readiness contracts from `docs/prd.md`.
4. If `ready-for-agent`, produce an agent-ready brief using `AGENT-BRIEF.md`.
5. If `ready-for-human`, state the decision needed and options.
6. Decide whether lifecycle state is needed for cross-session recovery, gap closure, UAT/release reuse, or decision-pending continuation.
7. Recommend `write-plan`, `to-prd`, direct user decision, or closeout as appropriate.

## Output Shape

```text
Triage Verdict
State
Execution: AFK / HITL
Evidence
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

Stop when the state, blockers, AFK/HITL classification, readiness reason, and next action are explicit.

## Artifact Rule

Do not create `OUT-OF-SCOPE.md` in MVP. Write an agent brief only when it will be reused for execution, review, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
