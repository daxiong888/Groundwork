---
name: implement
description: Execute code changes, scoped fixes, bug diagnosis, or read-only implementation conformance reviews against TASK/PRD/diff when the user says phrases like "review 这次实现是否符合 TASK.md", "检查这次实现是否满足 TASK.md", or asks for implementation review without readiness, UAT, release, or customer/front-end handoff verification.
---

# implement

## Trigger Contract

Use this skill when the user asks for code changes, implementation execution, implementation review, or diagnosis before a scoped fix.

Should trigger:

- "按这个任务实现"
- "根据这个 plan 改代码"
- "修一下这个 confirmed bug"
- "修一下这个问题"
- "实现这个接口调整"
- "先确认是不是真 bug，再做最小修改"
- "review 这次实现是否符合 PRD"
- "review 这次实现是否符合 TASK.md 但不要判断 UAT"
- "review 这次实现是否符合 TASK.md，不要判断能否给客户 UAT，不要编辑文件"
- "检查这次实现是否满足 TASK.md，但不做 readiness / UAT 判断"
- "review this implementation against the task without readiness judgment"
- "按这个任务实现并做最小自测"

Should not trigger:

- Requirements need shaping; use `to-prd`.
- Work needs task slicing; use `to-issues`.
- Task readiness is unknown; use `triage`.
- The user only asks for a plan; use `write-plan`.
- The user asks if the finished work is ready; use `verify`.
- The user asks whether an implementation can pass UAT or release; use `verify`.
- The user only asks for a full implementation plan before edits; use `write-plan`.

## Required Evidence

Inspect relevant files, direct callers/callees, tests, config, and diffs before editing when they affect correctness. Check dirty worktree state before changes. Do not invent exact file paths, APIs, schemas, commands, or runtime behavior before inspection.

Use `LIGHTWEIGHT-PLAN.md` before editing: What, Why, Files likely touched, Test/check, Risk. Map acceptance criteria to changes and checks.

For read-only implementation conformance review, do not force a fix plan. Inspect the task/PRD, source, tests, and git boundary when available; report whether the implementation satisfies acceptance, what evidence was checked, what gaps remain, and explicitly avoid UAT/release/readiness verdicts unless the user asks for them.

Use `TDD-LITE.md` for behavior changes when feasible: RED failing test/reproduction, GREEN minimal change, REFACTOR only after green. If no failing test or reproduction is feasible, give a no-test justification and do not claim TDD.

If the work starts from a verification failure, use `skills/verify/QA-FIX-QA.md`: confirm expected, actual, reproduction, severity, minimal diagnosis, fix plan, and re-QA requirement before editing. Fix only the scoped failure and rerun the original failing check.

If using a subagent for review, use `skills/_shared/SUBAGENT-DELEGATION.md`. The reviewer gets fresh context and cannot expand scope or modify files unless explicitly delegated.

## Workflow

1. Confirm source task, scope, and stop condition.
2. Run `git status --short`; if the worktree is dirty, inspect relevant diffs before editing.
3. If a bug or failing behavior is suspected, use the embedded diagnosis branch inside `implement`: reproduce or inspect first, separate confirmed cause from hypothesis, and do not edit speculatively.
4. Inspect relevant code and tests before editing.
5. If this is read-only implementation review, output conformance findings and stop without edits. Otherwise write the `Implementation Mini-Plan` from `LIGHTWEIGHT-PLAN.md`.
6. Use TDD-lite where feasible: RED, GREEN, REFACTOR.
7. Make minimal focused changes.
8. Run the fastest relevant checks, including the original failing check when one exists.
9. Add or update a focused regression test/check when feasible and proportional to risk.
10. If fixing a verify failure, confirm the original failure was re-QA'd or explain why it remains unverified.
11. Run self-review from `SELF-REVIEW.md`.
12. Report local evidence and remaining gaps, but do not claim final readiness.
13. Recommend `verify` for readiness.

## Output Shape

```text
Implementation Summary
Scope
Implementation Mini-Plan
TDD-Lite / No-Test Justification
Files Changed
Evidence Inspected
Checks Run
Self-Review
Result
Remaining Gaps
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the requested scoped change is implemented or blocked with evidence. Final readiness belongs to `verify` or the user.

## Gate Rule

If implementation would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, stop before execution and output Proposed Action, Target, Risk, Rollback/Undo, and Approval Needed. Do not execute until explicit user approval.

Before staging, committing, or reporting commit readiness, follow `skills/_shared/GIT-BOUNDARY.md`. Never use `git add .`; require explicit pathspec staging, intended allowlist, explicit denylist, `git diff --name-only`, `git diff --cached --name-only`, and a statement of unrelated modified, untracked, or ignored files.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Do not create durable artifacts unless they are needed for execution, review, verification, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
