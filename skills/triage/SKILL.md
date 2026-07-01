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

Every verdict includes `Severity` and `State Transition Reason`. Use `SEVERITY.md`; severity is current blocker/gap impact, not product priority. `AFK` can proceed from available source/acceptance/scope/first inspection/verification without new human decision/access/approval. `HITL` still needs human decision, authority/access, manual validation, risky approval, or product/design choice.

Closeout requires `verify` evidence, already-`done` evidence, or explicit `wontfix` owner decision. Otherwise keep open as `verification`, `needs-info`, or `ready-for-human`.

Use `skills/_shared/LIFECYCLE-STATE.md` only to decide whether workstream-scoped state is justified. External issue/PR ownership should not be duplicated unless Groundwork recovery needs remain.

Executable `ready-for-agent + AFK` must include a `Goal Contract` using `skills/_shared/GOAL-CONTRACT.md` field names plus preferred runtime recommendation and expected result package. Do not emit executable child goals for `needs-info`, `ready-for-human`, or HITL-only tasks.

## Severity Derivation

Identify the current blocker/gap, map the strongest affected boundary, check blast radius/dependencies/workaround, then assign the highest matching severity. If source, boundary, or workaround is unknown, classify `needs-info` and name missing evidence.

## Workflow

Gather source/outcome; classify state; assign severity and transition reason; separate evidence added/missing; apply readiness contracts; for executable `ready-for-agent + AFK`, produce agent brief with Goal Contract/runtime recommendation; for HITL, output decision/options/risks/next action; decide lifecycle-state need; recommend next route.

## Hard Stops

- Stop before `ready-for-agent` unless acceptance criteria, source/first inspection step, expected output, stop condition, AFK/HITL decision points, blockers, and boundaries are explicit.
- Stop before state change unless previous/current state, severity, transition reason, evidence added, and evidence missing tie to source.
- Stop before lifecycle state, closeout, or external ownership changes when source truth is unclear, mixed, or duplicated.
- Do not treat severity as product priority.
- Do not generate Goal Contracts for missing-info/HITL tasks.
- Do not claim runtime/model/reasoning selector enforcement; recommendations are advisory for `dispatch`.
- Reject project-global `.planning`, `.gsd`, GSD clones, or task databases; redirect only when workstream-scoped `artifacts/<workstream-slug>/STATE.md` is justified.

## Output Shape

Use `Triage Verdict` with state, severity, AFK/HITL, previous state, transition reason, evidence added/missing, blockers, readiness check, lifecycle-state recommendation, agent brief or human decision, next action, and artifact recommendation.

## Stop Condition

Stop when state, severity, transition reason, blockers, AFK/HITL, readiness reason, evidence added/missing, lifecycle-state recommendation, and next action are explicit.

## Artifact Rule

Do not create `OUT-OF-SCOPE.md` in MVP. Write an agent brief only when reused for execution, review, or handoff. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
