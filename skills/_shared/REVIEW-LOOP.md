Target Reader: Groundwork implementers, child-thread coordinators, clean reviewers, verifiers, and maintainers.
Reader Action Needed: Use this contract to keep post-implementation self-check, clean review, remediation, and re-review in a stable loop.
Decision Supported: Whether a completed implementation package may proceed, needs scoped remediation, needs a fresh clean review, is blocked, or requires a human decision.
Artifact Type: shared guardrail
Source of Truth: `skills/_shared/ROLE-SEPARATION.md`, `skills/dispatch/CLEAN-REVIEW-FANOUT.md`, `skills/verify/QA-FIX-QA.md`, and managed worktree result/review package contracts.
Scope: Review-loop states, evidence labels, remediation flow, package fields, and forbidden authority upgrades after child-thread or subagent implementation.
Out of Scope: Runtime execution, automatic subagent spawning, public skill creation, final readiness approval, release/UAT approval, archive, branch cleanup, commits, pushes, PRs, or tracker mutation.
Evidence Level: Source-validation policy only. This contract does not prove runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, selector-enforcement, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

# Review Loop

## Core Loop

Material child-thread or subagent implementation work follows this loop:

```text
implementation + self-check
-> fresh read-only clean review
-> scoped remediation when findings exist
-> self-check the remediation
-> fresh read-only clean review of the latest diff
-> verify/readiness only when the claimed boundary needs it
```

The loop is stable evidence handling, not automatic runtime execution. A package may recommend the next runtime, but it must not claim a clean reviewer, subagent, child thread, cache refresh, runtime, browser run, release gate, or remote mutation happened unless direct evidence exists.

## Evidence Rules

- `Self-check Evidence` comes from the implementer or child implementation thread. It may include tests, checks, diff inspection, and implementation conformance notes.
- `Self-check Evidence` must not be relabeled as `Clean Review Evidence`, `Independent Verification Evidence`, readiness, UAT evidence, release evidence, archive evidence, or branch cleanup evidence.
- `Clean Review Evidence` requires a fresh-context reviewer or documented low-risk coordinator intake that satisfies `skills/dispatch/CLEAN-REVIEW-FANOUT.md`.
- Clean reviewers are read-only. If a clean reviewer edits files, applies a patch, or directly fixes a finding, that reviewer becomes an implementer for the changed material. A new independent clean review is required before `clean_review_passed`.
- Any material fix after clean review makes the previous clean review stale for the latest diff. Record `previous_review_stale_reason` and require re-review.
- A clean review pass is implementation-conformance evidence only. It is not final readiness, UAT, release, runtime, browser, merge-back, archive, branch cleanup, commit, push, PR, or customer approval.

## Review Loop States

Use these states when packaging post-implementation work:

```text
self_check_complete
clean_review_pending
clean_review_passed
needs_remediation
remediation_in_progress
remediation_self_check_complete
blocked
human_decision
low_risk_coordinator_intake
```

Loop exit states are limited to:

```text
clean_review_passed
blocked
human_decision
low_risk_coordinator_intake
```

`low_risk_coordinator_intake` is allowed only for small, single-package, low-risk returns with clear current validation evidence and no fan-out trigger. It still does not approve archive, branch cleanup, release, UAT, or final readiness.

## Required Package Fields

Result and review packages that participate in this loop must carry a `review_loop` object. Managed worktree result packages place it at `result_package.review_loop`. Clean-review input packages place the reviewed implementation's loop state at `clean_review_package.source.review_loop`; that field is source context for the reviewer, not proof that clean review has already passed.

```yaml
review_loop:
  status: "self_check_complete | clean_review_pending | clean_review_passed | needs_remediation | remediation_in_progress | remediation_self_check_complete | blocked | human_decision | low_risk_coordinator_intake"
  latest_material_change_id: ""
  previous_review_stale_reason: ""
  findings_addressed: []
  next_review_required: "true | false"
  next_route: "clean_reviewer | dispatch_write_task | verify | triage | human_decision | done"
```

Set `next_review_required: true` whenever the latest material change has not received fresh clean review evidence. Use an empty `previous_review_stale_reason` only when no earlier clean review is being reused or referenced.

## Remediation Flow

When clean review returns findings:

1. Keep the review output read-only and route writes through `dispatch_write_task`, `implement`, or the original child thread when that route is still scoped and safe.
2. Fix only cited findings or explicitly accepted gap-closure items.
3. Rerun the original failed check or the smallest check that proves the finding closed.
4. Record `findings_addressed`, self-check evidence, checks run, checks not run, and remaining risks.
5. Mark the previous clean review stale when material files changed.
6. Route the latest package back to fresh clean review unless the coordinator records a valid low-risk exception.

Do not turn one review finding into broad cleanup, unrelated refactoring, or hidden scope expansion.

## Forbidden Claims

Hard failures:

- implementer self-review or self-run tests are described as clean review passed;
- a clean reviewer fixes its own finding and declares clean review passed for the fixed change;
- a package claims a previous clean review still covers a later material fix;
- clean review pass is used as release, UAT, runtime, browser, archive, branch cleanup, commit, push, PR, or final readiness evidence;
- a review package omits covered/not-covered scope and still claims pass;
- a package claims subagent, child-thread, runtime, cache, or selector execution from prompt preference alone.

## Skill Ownership

- `implement` owns implementation, scoped remediation, self-check evidence, and reviewable result packages.
- `dispatch` owns routing to clean review, remediation, verify, triage, or human decision.
- `clean_reviewer` or a read-only `codex_subagent` owns fresh clean review findings.
- `verify` owns scope-first evidence sufficiency and readiness claims after the loop provides current review evidence.
- `handoff` may preserve loop state, but it must not upgrade evidence or close the loop.
