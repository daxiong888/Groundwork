---
name: handoff
description: Use when preserving compact continuation state for long-running R&D work across sessions, agents, or future continuation. Use for handoff notes, review packages, resume context, and compact state transfer. Do not use for one-off explanations of handoff, full PRD/diff/log duplication, readiness verification, implementation, or wiki queries.
---

# handoff

## Use When

Use this skill when the user needs compact state transfer across sessions, agents, worktrees, or future continuation.

Examples:

- "给下个 session 做 handoff"
- "下个 session 继续验证"
- "整理一下后续接手上下文"
- "我要换会话，保存关键状态"
- "给同事一个接手摘要"
- "把当前进展压缩成 continuation notes"

## Do Not Use When

- The user asks what handoff is; answer directly.
- The user asks for a PRD; use `to-prd`.
- The user asks for issue slicing; use `to-issues`.
- The user asks for implementation; use `implement`.
- The user asks for readiness proof; use `verify`.
- The user asks for durable wiki knowledge; use `wiki`.
- The work is small enough to answer directly.
- The user asks to duplicate full PRDs, diffs, logs, or transcripts.

## Runtime Mode Router

- `compact`: default one-screen continuation summary. Cite source artifacts and summarize only resume-critical state.
- `review-package`: when the next reader needs a review handoff. Load `REVIEW-PACKAGE.md`.
- `native-handoff`: when continuation crosses Codex Local and Worktree. Load `NATIVE-HANDOFF-PACKAGE.md`; Groundwork prepares the package only and does not perform official Codex Handoff or native Git operations.
- `state-freshness`: when an existing `artifacts/<workstream-slug>/STATE.md` must be referenced. Load `STATE-FRESHNESS.md`.
- `complex`: when managed worktree, role separation, visual packet, release/cache/runtime/wiki, or clean-review gaps affect continuation. Load `COMPLEX-HANDOFF-BRANCHES.md`.

## Minimal Evidence Boundary

Reference existing PRDs, issues, plans, commits, diffs, verification notes, lifecycle state, artifacts, and git state by stable path or identifier. Do not copy full PRDs, plans, issue bodies, commits, long diffs, raw logs, transcripts, secrets, credentials, PII, sensitive screenshots, requests, or database rows.

Apply only the shared contract needed by the active branch:

- `skills/_shared/NON-EXECUTOR-BOUNDARY.md` before preparing continuation, review, or native handoff packages.
- `skills/_shared/LIFECYCLE-PREFLIGHT.md`, `skills/_shared/ARTIFACT-PROMOTION.md`, and `skills/_shared/LIFECYCLE-STATE.md` when lifecycle state or recovery state is in scope.
- `skills/_shared/GIT-BOUNDARY.md` when staging, commit continuation, or allowed/disallowed files matter.
- `skills/_shared/EVIDENCE-BOUNDARY.md`, `skills/_shared/ROLE-SEPARATION.md`, `skills/_shared/RUNTIME-CAPABILITY.md`, `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, `skills/_shared/VISUAL-HANDOFF-PACKET.md`, or `skills/_shared/LLM-WIKI.md` only when the handoff preserves that evidence class.

## Required Output

Use this compact shape unless a branch reference requires more:

```text
Current State
Goal
Current Decision
Source Artifacts
Decisions Made
Evidence
Role:
Design Source:
Self-check Evidence:
Clean Review Evidence:
Independent Verification Evidence:
Runtime Evidence:
Browser Evidence:
UAT Evidence:
Release Evidence:
Readiness Boundary:
Required Next Independent Role:
Open Gaps
Risks
Lifecycle State
- State Artifact:
- State Freshness: fresh / stale / unknown
- State Update Needed: yes / no
- State Reference Mode: existing-state-reference / recommend-state / no-state-needed
Allowed / Disallowed Files
Git Boundary
Do-Not-Assume
Visual Packet Evidence Boundary
Redaction Note
Next Action
Artifact Recommendation
```

Keep the handoff compact by default. Write a handoff file only when durable continuation is needed.

## Stop Conditions

- Stop before producing a handoff if continuation goal, source artifacts, evidence, open risks, next skill/direct action, or `Do-Not-Assume` boundary is missing.
- Stop before marking open risks as `None` unless the checked source artifacts, evidence, git boundary, and verification gaps support that claim.
- Stop before copying long source material; cite canonical artifacts and summarize only resume-critical state.
- Stop before asking the next reader to act if the next skill, target file/path/artifact, first command/check, or human decision is not executable.

## Reference Loading Rules

Load only the reference matching the active branch.

- Review handoff shape: `REVIEW-PACKAGE.md`.
- Native Local/Worktree handoff schema and rules: `NATIVE-HANDOFF-PACKAGE.md`.
- State freshness algorithm: `STATE-FRESHNESS.md`.
- Complex role/runtime/cache/release/wiki/visual branch details: `COMPLEX-HANDOFF-BRANCHES.md`.
- Fresh-context review delegation: `skills/_shared/SUBAGENT-DELEGATION.md`.
- Managed worktree separation: `skills/dispatch/COMPLEX-WORK-SEPARATION.md`.
- Git continuation boundary: `skills/_shared/GIT-BOUNDARY.md`.

## Gate Rule

Do not post, push, publish, update trackers, mutate shared skill files, execute native Handoff, or write remote handoff artifacts without explicit approval with `Target`, `Action`, `Risk`, and `Rollback/Undo`.

Do not ask a future session to use `git add .`; include explicit pathspecs and denylist guidance when staging or commit continuation is in scope.

## Artifact Rule

New or materially updated durable artifacts must follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`, `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`, and `skills/_shared/ARTIFACT-PROMOTION.md`. Existing `STATE.md` remains the lifecycle state owner; handoff is the transfer package, not the durable state layer.
