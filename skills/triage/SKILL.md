---
name: triage
description: Classify task readiness, blockers, severity, AFK/HITL ownership, lifecycle-state need, or closeout. Not for requirement shaping, slicing, code edits, implementation planning, verification reports, dispatch packages, or wiki work.
---

# triage

## Trigger Contract

Use when the user needs task state, readiness, blocker, AFK/HITL, lifecycle-state, or closeout classification.

Route away:

- New PRD/spec -> `to-prd`.
- Accepted requirements to tasks -> `to-issues`.
- Implementation plan after readiness -> `write-plan`.
- Code edits -> `implement`.
- Release/UAT/evidence proof -> `verify`.
- Runtime/subagent/worktree routing -> `dispatch`.

## Required Evidence

Inspect task source, PRD/spec, conversation, prior state when known, blockers, source refs, lifecycle state, and verification expectations. Unknown source -> `needs-info`.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Every verdict must include `Severity` and `State Transition Reason`. Use `skills/_shared/SEVERITY.md`; severity is current blocker/gap impact, not product priority.

AFK/HITL:

- `AFK`: next action can proceed from available source truth, acceptance, scope, first inspection step, and verification expectation without new human decision/access/approval.
- `HITL`: needs human decision, missing authority/access, manual validation, risky approval, or a choice among valid product/design options.

Closeout requires `verify` evidence, already-`done` evidence, or explicit `wontfix` owner decision. Otherwise keep open as `verification`, `needs-info`, or `ready-for-human`.

Use `skills/_shared/LIFECYCLE-STATE.md` only to decide whether workstream-scoped state is justified. External issue/PR ownership should not be duplicated unless Groundwork recovery needs remain.

Executable `ready-for-agent + AFK` must include a `Goal Contract` using `skills/_shared/GOAL-CONTRACT.md` field names plus preferred runtime recommendation and expected result package. Do not emit executable child goals for `needs-info`, `ready-for-human`, or HITL-only tasks.

## Severity Derivation

1. Identify current blocker/gap, not business importance.
2. Map strongest affected boundary: production safety, security/privacy, release, major acceptance/data/UAT, limited workaround, or wording/evidence hygiene.
3. Check blast radius, dependency impact, and workaround.
4. Assign highest matching severity.
5. If source/boundary/workaround is unknown, classify `needs-info` and name missing evidence.

## Workflow

1. Gather task source and requested outcome.
2. Classify state: `draft`, `needs-info`, `ready-for-agent`, `ready-for-human`, `in-progress`, `verification`, `done`, or `wontfix`.
3. Assign severity and transition reason; separate `Evidence Added` from `Evidence Missing`.
4. Apply readiness contracts from `docs/prd.md`.
5. If executable `ready-for-agent + AFK`, produce agent brief from `AGENT-BRIEF.md` with Goal Contract and Execution Profile Recommendation.
6. If HITL/ready-for-human, output human decision needed, options, risks, and next action.
7. Decide whether lifecycle state is needed for recovery, gap closure, UAT/release reuse, or decision-pending continuation.
8. Recommend `write-plan`, `implement`, `verify`, direct user decision, closeout triage, or gap closure.

## Hard Stops

- Stop before `ready-for-agent` unless acceptance criteria, source/first inspection step, expected output, stop condition, AFK/HITL decision points, blockers, and boundaries are explicit.
- Stop before state change unless previous/current state, severity, transition reason, evidence added, and evidence missing tie to source.
- Stop before lifecycle state, closeout, or external ownership changes when source truth is unclear, mixed, or duplicated.
- Do not treat severity as product priority.
- Do not generate Goal Contracts for missing-info/HITL tasks.
- Do not claim runtime/model/reasoning selector enforcement; recommendations are advisory for `dispatch`.
- Reject project-global `.planning`, `.gsd`, GSD clones, or task databases; redirect only when workstream-scoped `artifacts/<workstream-slug>/STATE.md` is justified.

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

Stop when state, severity, transition reason, blockers, AFK/HITL, readiness reason, evidence added/missing, lifecycle-state recommendation, and next action are explicit.

## Artifact Rule

Do not create `OUT-OF-SCOPE.md` in MVP. Write an agent brief only when reused for execution, review, or handoff. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
