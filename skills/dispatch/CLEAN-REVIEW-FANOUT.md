# Clean Review Fan-out Protocol

Target Reader: Groundwork coordinators, dispatch package authors, clean reviewers, and read-only review subagents.
Reader Action Needed: Decide when coordinator intake is enough, when completed implementation packages must fan out to clean review, and what reviewers may do.
Decision Supported: Whether a completed result/review package can stay in coordinator intake or must route to `clean_reviewer` / read-only `codex_subagent`.
Artifact Type: shared guardrail
Source of Truth: PRD v0.3.3 FR-7/Issue 6, dispatch runtime adapter profiles, `REVIEW-LOOP.md`, and `LOW-RISK-COORDINATOR-INTAKE.md`.
Scope: Clean-review routing thresholds, package-only reviewer context, read-only actions, coordinator boundaries, and eval hooks.
Out of Scope: Public skill creation, runtime execution, reviewer file edits, automatic subagent spawning, self-approval, final readiness, remote writes, commits, pushes, PRs, archive, or branch cleanup.
Evidence Level: Source-validation policy for clean-review routing.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Core Rule

Clean review is independent fresh-context review of a completed package. It is not child self-review, coordinator skim, parent-history fork, or unapproved nested delegation. If the reviewer used full parent history or unapproved nesting, disclose topology and mark clean-review evidence `unverified` or `blocked` until a self-contained fresh review runs.

Coordinator intake may check package completeness, reject incomplete packages, decide whether low-risk intake applies, or prepare a clean-review package. It must not perform deep review for large/multiple/high-risk packages, infer hidden context, approve closeout/archive/final readiness from child self-check, or edit files.

Use `REVIEW-LOOP.md` for post-implementation loop. Remediation changes make prior clean review stale unless a recorded low-risk coordinator-intake exception applies.

## Fan-out Triggers

Route to `clean_reviewer` or read-only `codex_subagent` when any applies: multiple returned packages; large package; public interface/schema/migration/generated artifact/shared fixture/state machine/shared config/adapter contract/package template changed; P0/P1/security/privacy/customer-visible/data-write/release/UAT risk; skipped/failed/partial validation; validation-fix iterations; user asks independent review; coordinator context is stale/compacted/multi-return; package completeness/redaction/evidence boundary is uncertain.

Small single-package low-risk returns may stay in coordinator intake only when `LOW-RISK-COORDINATOR-INTAKE.md` is satisfied. That exception is not `clean_review_passed` and cannot support archive, branch cleanup, merge, release, UAT, runtime, browser, or final readiness.

## Runtime Choice

- `clean_reviewer`: review package inspection, diff conformance, product/security/QA/contract/git/evidence lenses, no edits.
- `codex_subagent`: read-only multi-perspective review, diagnosis, or package-only findings when clean reviewer is unavailable or role-specific review is needed.
- `main_thread_readonly`: low-cost intake and routing only; not default deep reviewer for large/multiple/high-risk returns.

## Clean Review Package

Reviewer receives only supplied package and cited artifacts. Required inputs: task/correlation id, review lens, source truth, ACs, result/review package, changed files/diff detail, validation evidence/checks not run, allowed/disallowed actions, output format, severity ordering. Use `CLEAN-REVIEW-PACKAGE-TEMPLATE.md` for canonical shape.

Reviewer rules: read-only, `file_edits_allowed: false`, no nested agents, no parent memory/hidden context, cite supplied evidence, missing evidence is `unverified`/`blocked`, findings not patches, and no runtime/validation/merge/archive/branch/remote claims without supplied evidence. If a write is required, route a separate write task.

## Output And Loop

```text
review_findings
- verdict: pass | needs_remediation | blocked | unverified
- findings: P0/P1/P2/P3 ordered
- coverage: covered / not_covered
- evidence:
- missing_evidence:
- recommended_next_route: verify | triage | dispatch_write_task | human_decision | done
```

`pass` means no blocking package-level conformance issue within supplied evidence. It is not UAT, release, customer readiness, archive, merge-back, branch cleanup, or final acceptance. Covered/not-covered scope is mandatory.

When findings require writes, route remediation to a write owner, keep it scoped, require self-check/checks/risks, mark previous review stale when material files changed, and rerun clean review before verify, merge-back, archive, branch cleanup, or closeout claims unless valid low-risk intake applies.

## Eval Hooks

Reject coordinator-only deep review for large/multiple/high-risk returns, self-review as clean review, reviewer edits, parent-history/forked/nested reviewers as clean-review pass, missing validation guessed as pass, clean review without covered/not-covered scope, low-risk intake relabeled as clean review, and any clean-review pass that claims final readiness/archive/merge/branch/remote/runtime/release/UAT.
