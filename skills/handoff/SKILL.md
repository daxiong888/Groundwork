---
name: handoff
description: Use when preserving compact continuation state for long-running R&D work across sessions, agents, review packages, or future continuation. Do not use for one-off explanations, full PRD/diff/log duplication, code edits, readiness verification, dispatch routing, or wiki queries.
---

# handoff

## Use When

Use this skill when the user needs compact continuation state across sessions, agents, worktrees, reviewers, or future continuation.

Do not use for one-off explanations, PRD creation, issue slicing, code edits, readiness proof, dispatch routing, wiki work, direct small answers, or copying full PRDs/diffs/logs/transcripts.

## Route First

- `compact`: default one-screen continuation summary. Cite source artifacts and summarize only resume-critical state.
- `review-package`: review-focused handoff. Load `REVIEW-PACKAGE.md`.
- `native-handoff`: Codex Local/Worktree continuation package. Load `NATIVE-HANDOFF-PACKAGE.md`; Groundwork prepares the package only.
- `state-freshness`: existing lifecycle state must be referenced. Load `STATE-FRESHNESS.md`.
- `complex`: managed worktree, role separation, visual packet, release/cache/runtime/wiki, or clean-review gaps affect continuation.

## Evidence Boundary

Reference existing PRDs, issues, plans, commits, diffs, verification notes, lifecycle state, artifacts, and git state by stable path or identifier. Do not copy full source material, raw logs, transcripts, secrets, credentials, PII, sensitive screenshots, requests, or database rows.

Handoff preserves state and boundaries; it does not become runtime executor, clean reviewer, verifier, coordinator closeout, archive owner, branch cleanup owner, commit path, push path, PR path, tracker mutation path, or native Handoff Git-operation owner.

## Required Output

Keep handoff compact by default: current state, goal, decision, source artifacts, evidence, open gaps, risks, git boundary when relevant, do-not-assume items, redaction note, and next action.

Use branch references for full review, native handoff, lifecycle, visual, role-separation, release/cache/runtime, or wiki fields.

## Load Only What Fits

- Review handoff shape: `REVIEW-PACKAGE.md`.
- Native Local/Worktree handoff schema and rules: `NATIVE-HANDOFF-PACKAGE.md`.
- State freshness algorithm: `STATE-FRESHNESS.md`.
- Complex role/runtime/cache/release/wiki/visual details: `COMPLEX-HANDOFF-BRANCHES.md`.
- Fresh-context review delegation: `skills/_shared/SUBAGENT-DELEGATION.md`.
- Managed worktree separation: `skills/dispatch/COMPLEX-WORK-SEPARATION.md`.
- Git continuation boundary: `skills/_shared/GIT-BOUNDARY.md`.

Apply lifecycle, artifact-promotion, non-executor, git-boundary, evidence-boundary, role-separation, runtime, release, visual-handoff, or wiki shared contracts only when the handoff preserves that evidence class.

## Stop Conditions

- Stop before handoff if continuation goal, source artifacts, evidence, open risks, next action, or do-not-assume boundary is missing.
- Do not mark open risks as `None` unless checked evidence supports it.
- Do not copy long source material; cite canonical artifacts and summarize only resume-critical state.
- Do not ask a future reader to use `git add .`; include explicit pathspecs and denylist guidance when staging/commit continuation is in scope.
- If the user asks handoff to post, push, publish, update trackers, mutate shared skill files, execute native Handoff, or write remote handoff artifacts, stop at the handoff package plus proposed action and route execution to the owning tool or human-approved operator.
