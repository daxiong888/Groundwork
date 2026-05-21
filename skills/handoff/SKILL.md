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

Reference existing PRDs, issues, plans, commits, diffs, verification notes, and artifacts. Do not copy secrets, sensitive logs, full diffs, or long documents.

## Workflow

1. Identify the next reader and next action.
2. Reference existing artifacts instead of duplicating them.
3. Capture current state, decisions, evidence, gaps, and risks.
4. Include only enough detail to resume safely.
5. Recommend the next skill or direct action.

## Output Shape

```text
Current State
Source Artifacts
Decisions Made
Evidence
Open Gaps
Risks
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the next session can resume without rediscovering core context.

## Gate Rule

Do not post, push, publish, update trackers, mutate shared skill files, or write remote handoff artifacts without explicit approval with Target, Action, Risk, and Rollback/Undo.

## Artifact Rule


Follow `skills/_shared/ARTIFACT-POLICY.md`: every new or materially updated durable artifact must include the audience-first header, and local artifacts must follow the shared directory policy under `.groundwork/tasks/<task-id>/` or `.groundwork/shared/` unless the user specifies another target.
Keep handoff compact by default. Write a handoff file only when durable continuation is needed. Reference secret locations abstractly and never quote secret values.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
