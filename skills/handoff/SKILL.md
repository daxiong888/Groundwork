---
name: handoff
description: Preserve compact continuation state for long-running R&D work without duplicating PRDs plans issues commits or diffs. Use when the user asks for handoff, 下个 session, continuation context, resume notes, or compact state transfer.
---

# handoff

## Trigger Contract

Use this skill when the user needs compact state transfer across sessions, agents, or future continuation.

Should trigger:

- "给下个 session 做 handoff"
- "整理一下后续接手上下文"
- "我要换会话，保存关键状态"
- "给同事一个接手摘要"
- "把当前进展压缩成 continuation notes"

Should not trigger:

- The user asks for a PRD; use `to-prd`.
- The user asks for issue slicing; use `to-issues`.
- The user asks for readiness proof; use `verify`.
- The work is small enough to answer directly.
- The user asks to duplicate full PRDs, diffs, or logs.

## Required Evidence

Reference existing PRDs, issues, plans, commits, diffs, verification notes, lifecycle state, and artifacts. Do not copy secrets, sensitive logs, full diffs, or long documents. If the handoff includes git state, staging, commit boundary, or files that must remain out of scope, use `skills/_shared/GIT-BOUNDARY.md`.

Use `REVIEW-PACKAGE.md` when the next reader needs a review package rather than a basic continuation summary. Use `skills/_shared/SUBAGENT-DELEGATION.md` when the handoff prepares a fresh-context subagent review.

Use `skills/_shared/LIFECYCLE-STATE.md` when the user asks to pause, resume, switch sessions, save state, continue later, or otherwise preserve workstream recovery state.

## Workflow

1. Identify the next reader and next action.
2. Reference existing artifacts instead of duplicating them.
3. Check whether a workstream `artifacts/<workstream-slug>/STATE.md` exists when lifecycle threshold is met.
4. Reference existing `STATE.md` when present, or recommend creating/updating it when the threshold is met.
5. Capture current state, decisions, evidence, gaps, and risks.
6. Capture allowed/disallowed files when file boundary matters.
7. Include audience, continuation goal, source artifacts, evidence, open risks, next skill, do-not-assume, and redaction note when producing a review package.
8. Include only enough detail to resume safely.
9. Recommend the next skill or direct action.

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
- State Freshness:
- State Update Needed:
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
Keep handoff compact by default. Write a handoff file only when durable continuation is needed. Reference secret locations abstractly and never quote secret values.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
