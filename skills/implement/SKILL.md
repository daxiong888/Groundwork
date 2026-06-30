---
name: implement
description: Use when executing implementation-ready code changes, scoped fixes, confirmed bug diagnosis before a minimal fix, explicit PRD-bypass implementation, PR-bound implementation, or read-only implementation conformance review. Do not use when requirements need shaping, task readiness is unknown, the user only wants a plan, or the user asks for readiness/UAT/release verification.
---

# implement

## Use When

Use this skill when the user asks for code changes, implementation execution, scoped remediation, bug diagnosis before a minimal fix, or read-only implementation conformance review against a TASK/PRD/diff.

Examples:

- "按这个任务实现"
- "根据这个 plan 改代码"
- "修一下这个 confirmed bug"
- "先确认是不是真 bug，再做最小修改"
- "明确跳过 PRD 直接实现这个小改"
- "review 这次实现是否符合 TASK.md，但不要判断 ready/UAT"
- "实现这个 issue，最后提交 PR"

## Do Not Use When

- Requirements need shaping and the user has not explicitly bypassed PRD/spec work; use `to-prd`.
- Work needs task slicing; use `to-issues`.
- Task readiness is unknown; use `triage`.
- The user only asks for a plan; use `write-plan`.
- The user asks whether finished work is ready, releaseable, or UAT/customer-safe; use `verify`.
- The user asks for compact continuation context; use `handoff`.

## Runtime Mode Router

Choose the smallest branch that matches the request.

- `diagnose-before-edit`: reproduce or inspect first; continue only when a confirmed cause, failing check, or concrete test seam exists.
- `ordinary-implementation`: accepted task or explicit PRD/spec bypass; inspect source and write a five-line mini-plan before editing.
- `read-only-conformance`: inspect task/PRD, source, tests, and git boundary; report implementation conformance only and do not edit.
- `gated-implementation`: push, PR, issue closeout, customer-visible, destructive, data-write, deploy, publish, migration, or remote mutation; run the appropriate gate before acting.
- `review-loop-remediation`: fix only cited verification or clean-review findings; rerun the original or narrowest relevant check and mark prior review stale when material files change.

## Minimal Evidence Boundary

Before editing, inspect the relevant source truth, current git state, related diffs, direct callers/callees or shared helpers when correctness depends on them, related tests/checks/config, and the fastest useful verification signal.

Apply only the shared contract needed by the active branch:

- `skills/_shared/LIFECYCLE-PREFLIGHT.md` for source-truth and requirement-state checks.
- `skills/_shared/GIT-TOPOLOGY-GATE.md` before PR-bound writes and before commit/push/PR/remote mutation.
- `LIGHTWEIGHT-PLAN.md` before nontrivial edits.
- `TDD-LITE.md` for behavior changes when a failing test/reproduction is feasible.
- `skills/_shared/EVIDENCE-BOUNDARY.md`, `skills/_shared/ROLE-SEPARATION.md`, `skills/_shared/RUNTIME-CAPABILITY.md`, `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, `skills/_shared/LLM-WIKI.md`, or `skills/_shared/COGNITIVE-BUDGET.md` only when the implementation or report makes that evidence claim.
- `skills/_shared/REVIEW-LOOP.md` and `skills/_shared/SUBAGENT-DELEGATION.md` only for reviewable packages, subagent/child-thread work, or clean-review remediation.

When maintaining the Groundwork repository itself, apply the repo-local Done Definition before reporting complete.

## Required Output

Implementation, diagnosis, gated implementation, blocked implementation, and conformance reports include these labels:

```text
Scope:
Acceptance Map:
Evidence Inspected:
Findings P0/P1/P2:
Non-Readiness Boundary:
Gaps:
Next Action:
```

For edit paths, include:

```text
Implementation Mini-Plan
- What:
- Why:
- Files:
- Test:
- Risk:
```

Also report files changed, exact checks run and results, unverified runtime/cache/release/UAT claims, review-loop status when applicable, role-separation evidence fields when material, and `Self-Review` from `SELF-REVIEW.md`.

## Stop Conditions

- Stop before file edits unless the change is trivial and fully bounded, or the five-line mini-plan is stated.
- Stop before fixing a suspected bug unless a reproduction, confirmed cause, failing check, or specific test seam exists.
- Stop before PR-bound edits on `main`/`master`/`trunk`, detached `HEAD`, or an unsafe dirty worktree until branch/worktree topology is decided.
- Stop before staging, committing, pushing, opening a PR, closing issues, publishing, deploying, migrating data, or destructive commands until the matching gate is satisfied.
- Stop when acceptance criteria or source truth are unclear enough that implementation would invent behavior.

## Reference Loading Rules

Load only the reference matching the active branch.

- Lightweight edit plan: `LIGHTWEIGHT-PLAN.md`.
- Behavior-change test loop: `TDD-LITE.md`.
- Post-edit self-review: `SELF-REVIEW.md`.
- Full implementation branch details, conformance fields, gated output, failure branches, review-loop remediation, runtime/cache/release/wiki boundaries, and output skeleton: `IMPLEMENT-BRANCHES.md`.
- QA failure remediation from a verify failure: `skills/verify/QA-FIX-QA.md`.
- Git staging/commit boundary: `skills/_shared/GIT-BOUNDARY.md`.
- Review-loop state and clean-review evidence rules: `skills/_shared/REVIEW-LOOP.md`.

## Gate Rule

If implementation would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, customer-visible change, PR creation, issue closeout, or shared-skill mutation, stop before execution and output `Proposed Action`, `Target`, `Risk`, `Rollback/Undo`, and `Approval Needed`.

Never use `git add .`; stage only explicit intended pathspecs.

## Artifact Rule

Do not create durable artifacts unless needed for execution, review, verification, or handoff. New or materially updated durable artifacts must follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`. Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows.
