---
name: handoff
description: Preserve compact continuation state across sessions, agents, review packages, or future work. Not for one-offs, full PRD/diff/log copies, code edits, readiness, dispatch, or wiki queries.
---

# handoff

## Use When

Use when the user needs compact continuation state across sessions, agents, worktrees, reviewers, or future continuation.

Do not use for one-off explanations, PRD creation, issue slicing, code edits, readiness proof, dispatch routing, wiki work, direct small answers, or copying full PRDs/diffs/logs/transcripts.

## Route First

- `compact`: default one-screen continuation. Cite sources and summarize only resume-critical state.
- `review-package`: review-focused handoff. Load `REVIEW-PACKAGE.md`.
- `native-handoff`: Codex Local/Worktree continuation package. Load `NATIVE-HANDOFF-PACKAGE.md`; this route prepares the package only.
- `state-freshness`: existing lifecycle state must be referenced. Load `STATE-FRESHNESS.md`.
- `complex`: managed worktree, role separation, visual packet, release/cache/runtime/wiki, or clean-review gaps affect continuation.

## Evidence Boundary

Reference existing PRDs, issues, plans, commits, diffs, verification notes, lifecycle state, artifacts, and git state by stable path or ID. Do not copy full source material, logs, transcripts, secrets, credentials, PII, sensitive screenshots, requests, or database rows.

Handoff preserves state and boundaries; it is not runtime executor, clean reviewer, verifier, coordinator closeout, archive owner, branch cleanup owner, commit/push/PR path, tracker mutation path, or native Handoff Git-operation owner.

## Required Output

Keep handoff compact by default: current state, continuation goal, canonical sources, material gaps/risks, and next action. Add decisions, evidence detail, git boundary, do-not-assume items, or redaction note only when the next reader needs them to continue safely.

Use branch references for full review, native handoff, lifecycle, visual, role-separation, release/cache/runtime, or wiki fields.

## Load Only What Fits

- Review handoff shape: `REVIEW-PACKAGE.md`.
- Native Local/Worktree handoff schema and rules: `NATIVE-HANDOFF-PACKAGE.md`.
- State freshness algorithm: `STATE-FRESHNESS.md`.
- Complex role/runtime/cache/release/wiki/visual details: `COMPLEX-HANDOFF-BRANCHES.md`.
- Root-cause/minimal-solution summary for complex continuation: `skills/_shared/FIRST-PRINCIPLES.md`.
- Strongest remaining risk, unverified assumptions, or claim-boundary notes: `skills/_shared/ADVERSARIAL-REVIEW.md`.
- Fresh-context review delegation: `skills/_shared/SUBAGENT-DELEGATION.md`.
- Managed worktree separation: `skills/dispatch/COMPLEX-WORK-SEPARATION.md`.
- Git continuation boundary: `skills/_shared/GIT-BOUNDARY.md`.

Apply lifecycle, artifact, non-executor, git, evidence, role, runtime, release, visual, or wiki contracts only when the handoff preserves that evidence class.

## Stop Conditions

- Stop before handoff if continuation goal, source artifacts, evidence, open risks, next action, or do-not-assume boundary is missing.
- Do not mark open risks as `None` unless checked evidence supports it.
- Do not copy long source material; cite canonical artifacts and summarize only resume-critical state.
- Do not ask a future reader to use `git add .`; include explicit pathspecs and denylist guidance when staging/commit continuation is in scope.
- If asked to post, push, publish, update trackers, mutate shared skill files, execute native Handoff, or write remote artifacts, stop at the package plus proposed action and route execution to the owning tool or approved operator.
