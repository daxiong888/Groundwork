---
name: triage
description: Classify readiness, blockers, severity, AFK/HITL, lifecycle-state need, closeout, or whether incomplete information should be blocked or handed off. Not for shaping, slicing, code edits, planning, verification reports, dispatch packages, or wiki.
---

# triage

## Trigger Contract

Use for task state, readiness, blockers, AFK/HITL, existing issue ready-for-agent/ready-for-human classification, lifecycle-state, closeout classification, or deciding whether incomplete information should stop as blocked, continue as needs-info, or be preserved for handoff.

Route away:

- New PRD/spec -> `to-prd`.
- Accepted requirements to tasks -> `to-issues`.
- Implementation plan after readiness -> `write-plan`.
- Code edits -> `implement`.
- Release/UAT/evidence proof -> `verify`.
- Runtime/subagent/worktree routing -> `dispatch`.

## Required Evidence

Inspect task source, PRD/spec, conversation, prior state, blockers, source refs, lifecycle state, and verification expectations. Unknown source -> `needs-info`.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Every verdict includes `Severity` and `State Transition Reason`. Use `SEVERITY.md`; severity is current blocker/gap impact, not product priority. `AFK` can proceed from available source/acceptance/scope/first inspection/verification without new human decision/access/approval. `HITL` needs human decision, authority/access, manual validation, risky approval, or product/design choice.

Closeout requires `verify` evidence, already-`done` evidence, or explicit `wontfix` owner decision. Otherwise keep open as `verification`, `needs-info`, or `ready-for-human`.

Use `skills/_shared/LIFECYCLE-STATE.md` only to decide if workstream-scoped state is justified. Do not duplicate external issue/PR ownership unless Groundwork recovery needs remain.

Executable `ready-for-agent + AFK` must include a `Goal Contract` using `skills/_shared/GOAL-CONTRACT.md` field names, preferred runtime recommendation, and expected result package. Do not emit child goals for `needs-info`, `ready-for-human`, or HITL-only tasks.

## Severity Derivation

Identify current blocker/gap, strongest affected boundary, blast radius/dependencies/workaround, then assign the highest matching severity. If source, boundary, or workaround is unknown, classify `needs-info` and name missing evidence.

## Workflow

Gather source/outcome; classify state; assign severity and transition reason; separate evidence added/missing; apply readiness contracts; for `ready-for-agent + AFK`, produce agent brief with Goal Contract/runtime recommendation; for HITL, output decision/options/risks/next action; decide lifecycle-state need; recommend next route.

## Hard Stops

- Stop before `ready-for-agent` unless acceptance criteria, source/first inspection step, expected output, stop condition, AFK/HITL decision points, blockers, and boundaries are explicit.
- Stop before state change unless previous/current state, severity, transition reason, evidence added, and evidence missing tie to source.
- Stop before lifecycle state, closeout, or external ownership changes when source truth is unclear, mixed, or duplicated.
- Do not treat severity as product priority.
- Do not generate Goal Contracts for missing-info/HITL tasks.
- Do not claim runtime/model/reasoning selector enforcement; recommendations are advisory for `dispatch`.
- Reject project-global `.planning`, `.gsd`, GSD clones, or task databases; redirect only when workstream-scoped `artifacts/<workstream-slug>/STATE.md` is justified.

## Output Shape

Use `Triage Verdict` with state, severity, AFK/HITL, previous state, transition reason, evidence added/missing, blockers, readiness check, lifecycle recommendation, agent brief or human decision, next action, and artifact recommendation.

For `needs-info`, `blocked`, HITL, risky approval, or any other gate-bearing triage, include these exact machine-readable gate labels before the next action detail:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
```

Keep these gate labels in English even when the report body follows a non-English session locale.

## Stop Condition

Stop when state, severity, transition reason, blockers, AFK/HITL, readiness reason, evidence added/missing, lifecycle-state recommendation, and next action are explicit.

## Artifact Rule

Do not create `OUT-OF-SCOPE.md` in MVP. Write an agent brief only when reused for execution, review, or handoff. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
