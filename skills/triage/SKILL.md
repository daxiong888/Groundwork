---
name: triage
description: Classify readiness, blockers, severity, AFK/HITL, lifecycle-state need, closeout, or whether incomplete information should be blocked or handed off. Not for shaping, slicing, code edits, planning, verification reports, dispatch packages, or wiki.
---

# triage

## Trigger Contract

Use for task state, readiness, blockers, AFK/HITL, existing issue ready-for-agent/ready-for-human classification, lifecycle-state, closeout classification, or deciding whether incomplete information should stop as blocked, continue as needs-info, or be preserved for handoff.

Use `triage` when the prompt says verify/tests/done evidence already passed and asks whether an issue/task can be closed. That is a closeout state transition decision; do not route it to `verify` unless the user is asking to first verify whether the evidence passes.

Route away:

- New PRD/spec -> `to-prd`.
- Accepted requirements to tasks -> `to-issues`.
- Implementation plan after readiness -> `write-plan`.
- Code edits -> `implement`.
- Release/UAT/evidence proof -> `verify`.
- Runtime/subagent/worktree routing -> `dispatch`.

## Required Evidence

Inspect task source, PRD/spec, conversation, prior state, blockers, source refs, lifecycle state, and verification expectations. Unknown source -> `needs-info`.

Every verdict includes `Severity` and `State Transition Reason`. Use `skills/_shared/SEVERITY.md`; severity is current blocker/gap impact, not product priority. `AFK` can proceed from available source/acceptance/scope/first inspection/verification without new human decision/access/approval. `HITL` needs human decision, authority/access, manual validation, risky approval, or product/design choice.

Closeout requires `verify` evidence, already-`done` evidence, or explicit `wontfix` owner decision. Otherwise keep open as `verification`, `needs-info`, or `ready-for-human`.

Use `skills/_shared/LIFECYCLE-STATE.md` only to decide if workstream-scoped state is justified. Do not duplicate external issue/PR ownership unless Groundwork recovery needs remain.

Executable `ready-for-agent + AFK` must include a `Goal Contract` using `skills/_shared/GOAL-CONTRACT.md` field names, set `Preferred Runtime` to `dispatch_may_choose`, and name the expected result package. Do not emit child goals for `needs-info`, `ready-for-human`, or HITL-only tasks.

## Severity Derivation

Identify current blocker/gap, strongest affected boundary, blast radius/dependencies/workaround, then assign the highest matching severity. If source, boundary, or workaround is unknown, classify `needs-info` and name missing evidence.

## Workflow

Gather source/outcome; classify state; assign severity and transition reason; separate evidence added/missing; apply readiness contracts; for `ready-for-agent + AFK`, produce an agent brief and Goal Contract while deferring runtime/package selection to `dispatch`; for HITL, output decision/options/risks/next action; decide lifecycle-state need; recommend next route.

## Hard Stops

- Stop before `ready-for-agent` unless acceptance criteria, source/first inspection step, expected output, stop condition, AFK/HITL decision points, blockers, and boundaries are explicit.
- Stop before state change unless previous/current state, severity, transition reason, evidence added, and evidence missing tie to source.
- Stop before lifecycle state, closeout, or external ownership changes when source truth is unclear, mixed, or duplicated.
- Do not treat severity as product priority.
- Do not generate Goal Contracts for missing-info/HITL tasks.
- Do not select or recommend runtime, model, reasoning, worktree, isolation, or parallelization details; `dispatch` owns package routing after readiness.
- Reject project-global `.planning`, `.gsd`, GSD clones, or task databases; redirect only when workstream-scoped `artifacts/<workstream-slug>/STATE.md` is justified.

## Output Shape

Default to one `Triage Verdict`: state, severity, transition reason, material blockers or missing evidence, and next action. Add AFK/HITL when ownership matters; previous state/evidence delta for a real transition; lifecycle recommendation, agent brief, human decision, or artifact recommendation only when the verdict requires it.

Only when an approval is actually required before the next action, include these exact machine-readable gate labels:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
```

Keep these gate labels in English even when the report body follows a non-English session locale.

## Stop Condition

Stop when state, severity, transition reason, material blockers/missing evidence, and next action are explicit. Other fields are conditional on the decision.

## Artifact Rule

Do not create `OUT-OF-SCOPE.md` in MVP. Write an agent brief only when reused for execution, review, or handoff. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
