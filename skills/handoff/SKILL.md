---
name: handoff
description: Preserve or write compact continuation state for long-running R&D work without duplicating PRDs plans issues commits or diffs. Use when the user asks to create a handoff, save state for next session, continue in the next session, prepare continuation context, resume notes, or compact state transfer; do not use for one-off explanations of what handoff means.
---

# handoff

## Trigger Contract

Use this skill when the user needs compact state transfer across sessions, agents, or future continuation.

Should trigger:

- "给下个 session 做 handoff"
- "下个 session 继续验证"
- "整理一下后续接手上下文"
- "我要换会话，保存关键状态"
- "给同事一个接手摘要"
- "把当前进展压缩成 continuation notes"

Should not trigger:

- The user asks what handoff is or asks for a one-off explanation of Groundwork handoff; answer directly.
- The user asks for a PRD; use `to-prd`.
- The user asks for issue slicing; use `to-issues`.
- The user asks for readiness proof; use `verify`.
- The work is small enough to answer directly.
- The user asks to duplicate full PRDs, diffs, or logs.

## Required Evidence

Reference existing PRDs, issues, plans, commits, diffs, verification notes, lifecycle state, and artifacts. Do not copy secrets, sensitive logs, full diffs, or long documents. If the handoff includes git state, staging, commit boundary, or files that must remain out of scope, use `skills/_shared/GIT-BOUNDARY.md`.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` to decide whether lifecycle state is needed, stale, or only referenced. Use `skills/_shared/ARTIFACT-PROMOTION.md` to separate canonical artifacts from recoverable lifecycle state: handoff should cite PRDs, issue maps, verification reports, and external issues instead of copying them.

Use `REVIEW-PACKAGE.md` when the next reader needs a review package rather than a basic continuation summary. Use `skills/_shared/SUBAGENT-DELEGATION.md` when the handoff prepares a fresh-context subagent review.

Use `skills/_shared/LIFECYCLE-STATE.md` when the user asks to pause, resume, switch sessions, save state, continue later, or otherwise preserve workstream recovery state.

When an existing workstream `artifacts/<workstream-slug>/STATE.md` is present, handoff must reference it instead of copying it. Report the state artifact path, freshness (`fresh`, `stale`, or `unknown`), and whether an update is needed. Do not paste full lifecycle state, PRDs, issue bodies, plans, diffs, logs, or transcripts into the handoff.

## Workflow

1. Identify the next reader and next action.
2. Run lifecycle preflight for source truth, artifact promotion, lifecycle-state need, git topology, and stop condition.
3. Reference existing canonical artifacts instead of duplicating them.
4. Check whether a workstream `artifacts/<workstream-slug>/STATE.md` exists when lifecycle threshold is met.
5. Reference existing `STATE.md` by path when present, with freshness and update-needed status, or recommend creating/updating it when the threshold is met.
6. Capture current state, decisions, evidence, gaps, and risks.
7. Capture allowed/disallowed files when file boundary matters.
8. Include audience, continuation goal, source artifacts, evidence, open risks, next skill, do-not-assume, and redaction note when producing a review package.
9. Include only enough detail to resume safely; default to a one-screen continuation summary when no durable handoff file is needed.
10. Recommend the next skill or direct action.

## CHECKPOINTS

- STOP before producing a final handoff or review package if the continuation goal, source artifacts, evidence, open risks, next skill or direct action, or `Do-Not-Assume` boundary is missing.
- STOP before marking open risks as `None` unless the source artifacts, evidence, git boundary, and verification gaps were checked closely enough to justify that claim.
- STOP before copying PRDs, plans, issue bodies, commits, full lifecycle state, long diffs, logs, or transcripts; cite canonical artifacts and summarize only resume-critical state.
- STOP before asking the next reader to act if the next skill, target file/path/artifact, first command/check, or human decision needed is not executable from the handoff.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Evidence is insufficient for a claim | Move the claim to `Open Gaps`, `Risks`, or `Do-Not-Assume`. | Name the missing source, check, runtime evidence, or artifact instead of presenting the claim as verified. |
| Open risks are missing or unclassified | Stop and classify each material risk by impact on continuation, verification, git boundary, customer/UAT, or artifact scope. | Use `None` only when the checked evidence supports no remaining material risk. |
| Git status or file boundary is unclear | Run or request the git-boundary evidence required for the handoff scope. | Include intended files, explicit denylist, staged/unstaged status, and unrelated dirty/untracked files; never rely on `git add .`. |
| Next step is not executable | Rewrite the next action as a concrete next skill or direct action with target, input artifact, and first check. | If a human decision is required, state the decision and options instead of delegating vague follow-up. |

## Do Not

- Do not turn the handoff into a diary, transcript, or chronological status log.
- Do not copy long diffs, full PRDs, issue bodies, plans, commits, lifecycle state, raw logs, or transcripts.
- Do not hide unverified claims; label them as open gaps, risks, or `Do-Not-Assume`.
- Do not duplicate canonical artifacts when a stable path, issue ID, commit, or redacted source identifier is enough.
- Do not change the compact continuation-state boundary: handoff is a transfer package, not the PRD, plan, issue map, commit history, or durable lifecycle-state owner.

## Output Shape

```text
Current State
Source Artifacts
Decisions Made
Evidence
Open Gaps
Risks
Lifecycle State
- State Artifact:
- State Freshness: fresh / stale / unknown
- State Update Needed: yes / no
- State Reference Mode: existing-state-reference / recommend-state / no-state-needed
Allowed / Disallowed Files
Do-Not-Assume
Redaction Note
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the next session can resume without rediscovering core context.

## Gate Rule

Do not post, push, publish, update trackers, mutate shared skill files, or write remote handoff artifacts without explicit approval with Target, Action, Risk, and Rollback/Undo.

Do not ask a future session to use `git add .`. When handoff includes commit continuation, include intended pathspecs, explicit denylist, and unrelated dirty/untracked files that must stay unstaged.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Follow `skills/_shared/ARTIFACT-PROMOTION.md`: canonical artifacts remain the source of truth, while `STATE.md` remains compact recovery state.
Keep handoff compact by default: cite canonical artifacts, summarize only resume-critical state, and avoid copying full PRDs, issue bodies, plans, diffs, logs, or transcripts. Write a handoff file only when durable continuation is needed. Reference secret locations abstractly and never quote secret values. Existing `STATE.md` remains the lifecycle state owner; handoff is the transfer package, not the durable state layer.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
