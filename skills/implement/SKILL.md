---
name: implement
description: Execute or review code changes against PRD task plan source diff and test evidence while staying within scope. Use when the user asks to implement, 修改代码, fix a confirmed bug, apply a plan, or review implementation work.
---

# implement

## Trigger Contract

Use this skill when the user asks for code changes, implementation execution, or implementation review.

Should trigger:

- "按这个任务实现"
- "根据这个 plan 改代码"
- "修一下这个 confirmed bug"
- "实现这个接口调整"
- "review 这次实现是否符合 PRD"

Should not trigger:

- Requirements need shaping; use `to-prd`.
- Work needs task slicing; use `to-issues`.
- Task readiness is unknown; use `triage`.
- The user only asks for a plan; use `write-plan`.
- The user asks if the finished work is ready; use `verify`.

## Required Evidence

Inspect relevant files, direct callers/callees, tests, config, and diffs before editing when they affect correctness. Check dirty worktree state before changes. Do not invent exact file paths, APIs, schemas, commands, or runtime behavior before inspection.

## Workflow

1. Confirm source task, scope, and stop condition.
2. If a bug or failing behavior is suspected, run `diagnose` first.
3. Inspect relevant code and tests before editing.
4. Make minimal focused changes.
5. Run the fastest relevant checks.
6. Report local evidence and remaining gaps, but do not claim final readiness.
7. Recommend `verify` for readiness.

## Output Shape

```text
Implementation Summary
Scope
Files Changed
Evidence Inspected
Checks Run
Result
Remaining Gaps
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the requested scoped change is implemented or blocked with evidence. Final readiness belongs to `verify` or the user.

## Gate Rule

If implementation would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, stop before execution and output Proposed Action, Target, Risk, Rollback/Undo, and Approval Needed. Do not execute until explicit user approval.

## Artifact Rule

Do not create durable artifacts unless they are needed for execution, review, verification, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
