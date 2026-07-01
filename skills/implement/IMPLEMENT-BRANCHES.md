# Implement Branches

Target Reader: Codex running the Groundwork `implement` skill after entry routing.
Reader Action Needed: Apply full branch details, gates, conformance fields, review-loop handling, and output expansion without loading them in the active `SKILL.md` entry.
Decision Supported: Whether to implement, diagnose, stop, remediate a finding, or report conformance only.
Artifact Type: branch-specific implementation reference
Source of Truth: `skills/implement/SKILL.md`, `skills/implement/LIGHTWEIGHT-PLAN.md`, `skills/implement/SELF-REVIEW.md`, and shared evidence-boundary contracts.
Scope: Implementation branch details, gated output, failure handling, review-loop remediation, and evidence-claim boundaries.
Out of Scope: Full PRD shaping, task slicing, final readiness, runtime execution, release approval, or remote mutation without approval.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Source And Gate Workflow

1. Confirm source task, scope, and stop condition.
2. Run lifecycle preflight and git topology gate when the task may write files, create artifacts, or mutate git/remote state.
3. Inspect current branch, dirty state, relevant diffs, and whether branch/worktree is required before editing.
4. Choose the implementation branch:
   - `diagnose-before-edit`: reproduce or inspect first, separate confirmed cause from hypothesis, then continue only with the minimum scoped fix or stop with diagnosis evidence.
   - `read-only-conformance`: inspect task/PRD, source, tests, and git boundary; output conformance findings and stop without edits.
   - `gated-implementation`: run git topology and remote-write gates before editing or remote action.
   - `ordinary-implementation`: continue with the lightweight plan and focused edit path.
5. Inspect relevant code, tests, config, and shared helpers before editing.
6. Use TDD-lite where feasible; otherwise name the no-test justification.
7. Make minimal focused changes.
8. Run the fastest relevant checks, including original failing checks when applicable.
9. If fixing a verify or clean-review failure, record findings addressed and re-QA the original or narrowest failed check.
10. Run `SELF-REVIEW.md` before final reporting.

For nontrivial bug or mechanism work, load `skills/_shared/FIRST-PRINCIPLES.md` and use the Bug Root-Cause Ladder before edits. For material shared-skill, shared-guardrail, readiness-adjacent, or public-surface work, load `skills/_shared/ADVERSARIAL-REVIEW.md` and record adversarial findings when they affect scope, evidence, or remaining gaps.

## Conformance Field Set

Use these labels for read-only conformance review and implementation final reports with conformance evidence:

```text
Scope:
Acceptance Map:
Evidence Inspected:
Findings P0/P1/P2:
Non-Readiness Boundary:
Gaps:
Next Action:
```

`Non-Readiness Boundary` must state that the review is limited to implementation conformance and does not decide UAT, release, customer readiness, deployment readiness, or final acceptance unless the user explicitly asks for that scope.

## Gated Actions

When `Risk Gate` is not `none`, or when the prompt asks for git, customer-visible, data-write, destructive, push, PR, issue-closeout, deploy, publish, migration, remote, or shared-skill execution, include these labels before executing:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
```

For PR-bound work on `main` / `master` / `trunk`, empty branch name, detached `HEAD`, or unsafe dirty worktree, stop before edits and include:

```text
Execution Topology: branch_required / worktree_required / blocked
```

Before staging or committing, follow `skills/_shared/GIT-BOUNDARY.md`: intended allowlist, explicit denylist, `git diff --name-only`, `git diff --cached --name-only`, staged files, unstaged files, untracked files, and ignored/runtime exclusions. Never use `git add .`.

## Evidence Claim Boundaries

- Runtime/model/cache claims require `skills/_shared/RUNTIME-CAPABILITY.md` and the relevant `EB-RUNTIME-001` / `EB-CACHE-001` boundary. Use `unknown`, `unavailable`, or `prompt_preference` rather than silent substitution.
- Release/UAT/marketplace/cache-refresh claims require `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`; otherwise state runtime evidence was not refreshed and is not claimed.
- Wiki context may orient source discovery but does not prove implementation truth. Apply `skills/_shared/LLM-WIKI.md` and inspect qualifying source before changing code.
- Material changes require role-separation evidence fields. Self-check evidence is not clean review, independent verification, UAT evidence, release evidence, or runtime evidence.
- If implementation reveals durable reusable project knowledge and wiki maintenance is not in scope, emit a `Wiki Update Candidate` instead of updating wiki pages.

## Review-Loop Remediation

Use `skills/_shared/REVIEW-LOOP.md` when implementation is performed in a child thread, managed worktree, subagent, or other reviewable execution package.

If fixing clean-review or verify findings:

1. Fix only cited findings or explicitly accepted gap-closure items.
2. Rerun the original failed check or the smallest check that proves the finding closed.
3. Record `findings_addressed`, checks run, checks not run, remaining risks, and self-check evidence.
4. Mark prior clean review stale when material files changed.
5. Route the latest package back to fresh clean review unless a documented low-risk coordinator-intake exception applies.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Bug cannot be reproduced or confirmed | Stop before edits or continue only with source-level diagnosis when enough evidence exists. | Separate confirmed facts from hypotheses and state the smallest safe next check or modification direction. |
| No test seam or feasible check exists | Give a no-test justification before any edit, or stop if behavior would be speculative. | Name the missing seam, why unavailable, alternate evidence, and follow-up verification. |
| Dirty worktree state is present or unclear | Inspect relevant diffs before edits and decide whether current worktree is safe. | List intended files, unrelated dirty/untracked files, and whether edits are blocked, scoped, or need separate topology. |
| Unrelated files appear in the diff or staged set | Stop staging/commit work until the boundary is explicit. | Report allowlist, denylist, `git diff --name-only`, and `git diff --cached --name-only`; leave unrelated files unstaged. |
| Acceptance criteria or source truth is unclear | Stop before implementation or ask the highest-impact clarification question. | Do not infer product behavior; state what is known, missing, and needed. |
| Code edit or bug patch is requested but no source truth, workspace file, task artifact, reproduction path, or test seam is available | Route to `blocked implementation`; do not answer as ordinary direct Q&A and do not patch speculatively. | Output exact implement field labels: `Scope`, `Acceptance Map`, `Evidence Inspected`, `Findings P0/P1/P2`, `Non-Readiness Boundary`, `Gaps`, `Next Action`; for nontrivial bug intent include `Bug Root-Cause Ladder` with unavailable fields marked `not provided` or `unverified`. |

## Full Output Skeleton

```text
Implementation Summary
Scope:
Acceptance Map:
Evidence Inspected:
Findings P0/P1/P2:
Non-Readiness Boundary:
Gaps:
Next Action:
Implementation Mini-Plan
TDD-Lite / No-Test Justification
Files Changed
Checks Run
Unverified Claims
Runtime Capability:
- capability_status:
- selector_enforcement:
- Evidence layer:
- Requested runtime:
- Available runtime:
- Runtime mismatch:
- Fallback proposed:
- User approval required:
Review Loop:
- status:
- previous_review_stale_reason:
- findings_addressed:
- next_review_required:
- next_route:
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
Self-Review
Result
Remaining Gaps
Artifact Recommendation
Bug Root-Cause Ladder
```
