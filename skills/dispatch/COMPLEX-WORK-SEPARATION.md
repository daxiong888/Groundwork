# Complex Work Separation Policy

Target Reader: coordinators, dispatch package authors, implementers, clean reviewers, verifiers, and handoff authors.
Reader Action Needed: decide when nontrivial work must split planning, implementation, clean review, verification, and coordination roles.
Decision Supported: whether a task stays lightweight or needs fresh role separation before verification, merge-back, archive, cleanup, or closeout.
Scope: dispatch-time separation thresholds, role responsibilities, low-risk exceptions, and cross-skill ownership for managed worktree work.
Out of Scope: public skill creation, runtime execution, automatic subagents, reviewer/verifier edits, final readiness approval, commits, pushes, PRs, tracker mutation, archive, branch cleanup, or lifecycle mutation.
Evidence Level: derived from PRD v0.3.3 FR-9 / Issue 8 plus clean-review fanout and dispatch routing contracts.

## Core Rule

Complex work must not let one role plan, implement, clean-review, verify, and coordinate closeout for its own change.

Normal chain:

```text
planner -> implementer -> clean reviewer -> verifier -> coordinator closeout
```

Implementer self-check is implementation evidence only. It is not clean review, final approval, readiness, merge-back approval, archive approval, or closeout approval.

## Separation Required

Use `skills/_shared/ROLE-SEPARATION.md` as base threshold. The dispatch-specific triggers below are additive; one trigger is enough:

- P0/P1 or otherwise high-risk work;
- security, privacy, auth, permissions, data correctness, or customer-visible readiness;
- DB schema, migrations, public API/interface, contracts, package schemas, adapter contracts, or state machines;
- cross-cutting/multi-module changes, shared config, shared fixtures, generated artifacts, or package templates;
- dependent issue chain requiring merge-back or base refresh before later tasks;
- validation missing, weak, skipped, partial, failed, environment-limited, or manual-only;
- child implementer performed validation-fix iterations before returning a package;
- multiple child result/review packages return to one coordinator;
- coordinator context is compacted, stale, overloaded, or concurrent;
- user requests independent, security, QA, contract, release, or UAT evidence.

## Lightweight Exception

Small, single-scope, low-risk work may stay lightweight only when all apply:

- tiny/local and not public API, schema, migration, security, auth, permissions, data correctness, or customer-readiness work;
- no shared contract, package template, state machine, generated artifact, shared fixture, or shared config affected;
- clear source truth and acceptance signal;
- validation is simple/current, or no-test/no-runtime boundary is explicitly acceptable;
- one result package and coordinator has enough context for intake;
- no clean-review fanout trigger applies.

If true, dispatch may use `main_thread_direct`, `main_thread_readonly`, or one lightweight implementation path.

## Role Boundaries

| Role | May | Must not |
| --- | --- | --- |
| Planner | identify source truth, ACs, risk, scope, dependencies, validation expectations; recommend managed worktree/review/verification/human decision; split mixed work | write implementation files; approve own plan; claim runtime, validation, readiness, merge-back, archive, cleanup, or closeout |
| Implementer | execute one accepted implementation goal; run focused checks; self-check against ACs; return result/review package with files/checks/risks/gaps/next route | output `review_passed`; final-review own work; close readiness, merge-back, archive, cleanup, commit, push, PR, tracker decisions; expand scope without dispatch |
| Clean Reviewer | inspect supplied package/artifacts/diff/AC map/checks; return severity-ordered findings; mark missing evidence `unverified`/`blocked`; recommend next route | edit files; rely on hidden parent context; merge/archive/cleanup/commit/push/PR/remote mutate; turn review pass into UAT/release/customer/final acceptance |
| Verifier | judge scoped evidence sufficiency for claimed readiness; return `pass`, `partial`, `fail`, or `blocked`; recommend triage/gap/re-verify/block | execute implementation; replace clean review; mutate files/remotes/trackers/branches/archives/lifecycle unless explicit threshold and approval apply; close tasks directly |
| Coordinator | intake result packages/findings; decide separation, clean review, verification, remediation, serialization, merge-back, archive, cleanup, or human decision; preserve dependent-task barriers | become deep reviewer of record for complex/high-risk/multiple/stale/weak-evidence packages; treat child self-check as clean review; claim readiness/closeout without owning-role evidence |

## Routing Rules

- Use `skills/dispatch/CLEAN-REVIEW-FANOUT.md` when completed package needs fresh-context review.
- Use `skills/dispatch/ROUTING-PROFILES.md` to choose the lightest runtime satisfying threshold and ownership boundary.
- Use `skills/verify/SKILL.md` for evidence sufficiency/readiness, not implementation conformance alone.
- Use `skills/handoff/SKILL.md` only for compact continuation/review context; handoff is not execution, clean review, verification, or closeout.

## Eval Hooks

Reject: child implementer claiming `review_passed`; P1/API/migration/security/auth/permissions/data/package-schema/adapter work skipping clean review; verifier replacing clean review or implementation; handoff executing follow-up work; coordinator closeout based only on child self-check for complex work.

Allow: small low-risk direct work; coordinator intake for a complete single low-risk package when no fanout trigger applies; read-only planning/review without managed-worktree ceremony unless a write implementation task exists.
