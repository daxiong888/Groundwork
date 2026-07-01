---
name: implement
description: Scoped code changes, confirmed fixes, diagnose-before-edit work, or read-only implementation conformance review. Not for raw requirements, slicing, readiness/UAT/release verification, handoff, or dispatch.
---

# implement

## Use When

Use this skill for scoped implementation work: code changes, focused remediation, confirmed bug fixes, diagnose-before-edit, explicit PRD/spec bypass, or read-only implementation conformance review against a TASK/PRD/diff.

Do not use for raw requirements, task slicing, readiness/UAT/release verification, dispatch routing, compact continuation context, or planning-only requests.

## Route First

Choose the smallest branch that matches the request:

- `diagnose-before-edit`: inspect or reproduce first; edit only after a confirmed cause, failing check, or concrete test seam exists.
- `ordinary-implementation`: accepted task or explicit PRD/spec bypass; inspect source and write the five-line mini-plan before editing.
- `read-only-conformance`: inspect task/PRD, source, tests, and git boundary; report implementation conformance only and do not edit.
- `gated-implementation`: push, PR, issue closeout, customer-visible, destructive, data-write, deploy, publish, migration, remote mutation, or shared-skill mutation.
- `review-loop-remediation`: fix only cited verification or clean-review findings; rerun the original or narrowest relevant check and mark prior review stale when material files change.

## Evidence Boundary

Before editing, inspect current git state, relevant diffs, source truth, directly affected code/helpers, related tests/checks/config, and the fastest useful verification signal. When maintaining Groundwork itself, apply the repo-local Done Definition before reporting complete.

Do not claim runtime/cache/release/UAT/marketplace/cache-refresh, clean-review, independent verification, or customer readiness from implementation self-checks.

## Required Output

Implementation, diagnosis, gated implementation, blocked implementation, and conformance reports include:

```text
Scope:
Acceptance Map:
Evidence Inspected:
Findings P0/P1/P2:
Non-Readiness Boundary:
Gaps:
Next Action:
```

For nontrivial edit paths, include the five-line `Implementation Mini-Plan` from `LIGHTWEIGHT-PLAN.md`.

## Load Only What Fits

- Lightweight edit plan: `LIGHTWEIGHT-PLAN.md`.
- Behavior-change test loop: `TDD-LITE.md`.
- Post-edit self-review: `SELF-REVIEW.md`.
- Full branch details, conformance fields, gated output, failure branches, review-loop remediation, runtime/cache/release/wiki boundaries, and output skeleton: `IMPLEMENT-BRANCHES.md`.
- QA failure remediation from verify: `skills/verify/QA-FIX-QA.md`.
- Git staging/commit boundary: `skills/_shared/GIT-BOUNDARY.md`.
- Review-loop state and clean-review evidence rules: `skills/_shared/REVIEW-LOOP.md`.

Apply lifecycle, git topology, evidence-boundary, role-separation, runtime, release, wiki, or cognitive-budget shared contracts only when the branch or final claim needs that evidence type.

## Stop Conditions

- Stop before file edits unless the change is trivial and bounded, or the mini-plan is stated.
- Stop before suspected-bug fixes without a reproduction, confirmed cause, failing check, or concrete test seam.
- Stop before PR-bound edits on unsafe topology.
- Stop before staging, committing, pushing, opening a PR, closing issues, publishing, deploying, migrations, destructive commands, or data/remote writes until the matching gate is satisfied.
- Never use `git add .`; stage only explicit intended pathspecs.
