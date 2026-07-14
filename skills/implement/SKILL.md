---
name: implement
description: Non-trivial or uncertain bug fixes, patch/code edits, "修 bug", "直接 patch", "改代码", confirmed fixes, diagnose-before-edit, blocked implementation when source truth is missing, or read-only implementation conformance review. Not for obvious text-only typo edits, raw requirements, slicing, readiness/UAT/release verification, handoff, or dispatch.
---

# implement

## Use When

Use this skill for scoped implementation work: code changes, focused remediation, "修 bug", "直接 patch", "改代码", confirmed bug fixes, diagnose-before-edit, explicit PRD/spec bypass, blocked implementation when source truth is missing, or read-only implementation conformance review against a TASK/PRD/diff.

Do not use for raw requirements, task slicing, readiness/UAT/release verification, dispatch routing, compact continuation context, or planning-only requests.

## Route First

Choose the branch that matches the current decision and risk. Gating overrides ordinary execution; branch selection limits procedure loading, not solution depth:

- `diagnose-before-edit`: inspect or reproduce first; edit only after a confirmed cause, failing check, or concrete test seam exists.
- `ordinary-implementation`: accepted task or explicit PRD/spec bypass; inspect source and write the five-line mini-plan before editing.
- `read-only-conformance`: inspect task/PRD, source, tests, and git boundary; report implementation conformance only and do not edit.
- `gated-implementation`: push, PR, issue closeout, customer-visible, destructive, data-write, deploy, publish, migration, remote mutation, or shared-skill mutation.
- `review-loop-remediation`: fix only cited verification or clean-review findings; rerun the original or narrowest relevant check and mark prior review stale when material files change.

## Solution Depth

Minimize unrelated scope, not the depth required to solve the confirmed cause. For nontrivial bug or mechanism work, apply `skills/_shared/FIRST-PRINCIPLES.md` before choosing a fix. A fix is minimal only among solutions that address the confirmed cause, restore affected invariants, cover known affected paths, and have a falsifiable verification signal.

Do not substitute a smaller symptom mask, local duplication, fallback, or workaround while leaving the confirmed cause intact. If the sufficient root-cause fix exceeds accepted scope or authority, stop and surface the required expansion instead of silently under-fixing.

## Evidence Boundary

Before editing, inspect current git state, relevant diffs, source truth, directly affected code/helpers, related tests/checks/config, and the fastest useful verification signal.

Do not claim runtime/cache/release/UAT/marketplace/cache-refresh, clean-review, independent verification, or customer readiness from implementation self-checks.

## Required Output

Keep interactive final answers outcome-first and proportional. Omit empty, unchanged, and not-applicable fields; do not print internal planning or self-review scaffolding unless it changes the result.

- Ordinary implementation: outcome, files changed, checks run with results, and remaining risk or skipped verification.
- Diagnosis without edits: confirmed cause, decisive evidence, and the smallest safe next action.
- Read-only conformance: findings first by severity, then material evidence gaps and the non-readiness boundary. Include acceptance mapping only when it helps locate a gap.
- Blocked work: blocker, inspected evidence, and the one decision or input needed to continue.
- Gated action: add the stable English labels `Proposed Action`, `Target`, `Risk`, `Rollback/Undo`, and `Approval Needed` only when approval is actually required before the next action.

For nontrivial edit paths, use the five-line `Implementation Mini-Plan` from `LIGHTWEIGHT-PLAN.md` before editing, but keep it internal unless the user asks for the plan or a material scope decision needs review.

The gate field labels are stable machine-readable contract labels. Keep them in English even when the report body follows a non-English session locale. Load the full output skeleton only for an explicit audit/debug package, durable artifact, or machine-consumed report.

## Load Only What Fits

- Lightweight edit plan: `LIGHTWEIGHT-PLAN.md`.
- Behavior-change test loop: `TDD-LITE.md`.
- Post-edit self-review: `SELF-REVIEW.md`.
- Root-cause ladder for nontrivial bug or mechanism work: `skills/_shared/FIRST-PRINCIPLES.md`.
- Adversarial self-check for high-risk, shared-guardrail, public-skill, readiness-adjacent, or material conformance work: `skills/_shared/ADVERSARIAL-REVIEW.md`.
- Full branch details, conformance fields, gated output, failure branches, review-loop remediation, runtime/cache/release/wiki boundaries, and output skeleton: `IMPLEMENT-BRANCHES.md`.
- QA failure remediation from verify: `skills/verify/QA-FIX-QA.md`.
- Git staging/commit boundary: `skills/_shared/GIT-BOUNDARY.md`.
- Review-loop state and clean-review evidence rules: `skills/_shared/REVIEW-LOOP.md`.

Apply lifecycle, git topology, evidence-boundary, role-separation, runtime, release, wiki, or cognitive-budget shared contracts only when the branch or final claim needs that evidence type.

## Stop Conditions

- Stop before file edits unless the change is trivial and bounded, or the mini-plan is prepared. Show it only under the visibility rule above.
- Stop before suspected-bug fixes without a reproduction, confirmed cause, failing check, or concrete test seam.
- Stop before PR-bound edits on unsafe topology.
- Stop before staging, committing, pushing, opening a PR, closing issues, publishing, deploying, migrations, destructive commands, or data/remote writes until the matching gate is satisfied.
- Never use `git add .`; stage only explicit intended pathspecs.
