# Complex Work Separation Policy

Target Reader: Groundwork coordinators, dispatch package authors, implementers, clean reviewers, verifiers, and handoff authors.
Reader Action Needed: Decide when nontrivial work must be split across planning, implementation, clean review, verification, and coordination roles.
Decision Supported: Whether a task can stay lightweight or must require fresh role separation before verification, merge-back, archive, branch cleanup, or closeout.
Scope: Dispatch-time separation thresholds, role responsibilities, low-risk exceptions, and cross-skill ownership boundaries for complex managed worktree work.
Out of Scope: Public skill creation, runtime execution, automatic subagent spawning, implementation file edits by reviewers or verifiers, final readiness approval, commits, pushes, PRs, tracker mutation, archive, branch cleanup, or lifecycle state mutation.
Evidence Level: Derived from PRD v0.3.3 FR-9 / Issue 8 and the existing clean review fan-out and dispatch routing contracts.

## Core Rule

Complex work must not let one role plan, implement, clean-review, verify, and coordinate closeout for its own change.

The normal separation chain is:

```text
planner -> implementer -> clean reviewer -> verifier -> coordinator closeout
```

An implementer may self-check and report validation evidence. That self-check is implementation evidence only; it is not clean review, final approval, readiness, merge-back approval, archive approval, or closeout approval.

## Separation Required

Start with the canonical base materiality threshold in `skills/_shared/ROLE-SEPARATION.md`. The dispatch-specific triggers below are additive operational triggers for managed worktree, package-return, and coordinator closeout contexts.

Require role separation when any base threshold or dispatch-specific condition is true:

- the task is P0/P1 or otherwise high-risk;
- the change affects security, privacy, auth, permissions, data correctness, or customer-visible readiness;
- the change touches DB schema, migrations, public API, public interfaces, contracts, package schemas, adapter contracts, or state machines;
- the work is cross-cutting, multi-module, or changes shared config, shared fixtures, generated artifacts, or package templates;
- the work belongs to a dependent issue chain where later write tasks rely on merge-back or base refresh;
- validation evidence is missing, weak, skipped, partial, failed, environment-limited, or manually inspected only;
- the child implementer performed validation-fix iterations before returning a package;
- multiple child result or review packages return to one coordinator;
- coordinator context is compacted, stale, overloaded, or managing concurrent package returns;
- the user requests independent review, security review, QA review, contract review, or release/UAT evidence.

These thresholds are additive. One trigger is enough to require separation.

## Lightweight Exception

Small, single-scope, low-risk work may remain lightweight when all of these are true:

- the change is tiny, local, and not public API, schema, migration, security, auth, permissions, data correctness, or customer-readiness work;
- no shared contract, package template, state machine, generated artifact, shared fixture, or shared config is affected;
- the work has a clear source truth and acceptance signal;
- validation is simple and current, or a no-test/no-runtime boundary is explicitly acceptable for the task type;
- there is only one result package and the coordinator has enough context for intake;
- no clean review fan-out trigger applies.

When the exception applies, dispatch may keep the task in `main_thread_direct`, `main_thread_readonly`, or a single lightweight implementation path. Do not add ceremony only because separation exists as a policy.

## Role Boundaries

### Planner

Planner is read-only.

Planner may:

- identify source truth, acceptance criteria, risk, scope boundaries, dependencies, and validation expectations;
- recommend whether a task needs managed worktree implementation, clean review, verification, or human decision;
- split work when a single task combines planning, implementation, review, or verification responsibilities.

Planner must not:

- write implementation files;
- approve its own plan as clean review;
- claim runtime execution, validation, readiness, merge-back, archive, branch cleanup, or closeout.

### Implementer

Implementer owns scoped write execution.

Implementer may:

- execute exactly one accepted implementation goal in the authorized workspace or managed worktree;
- run focused checks and report validation evidence;
- self-check the changed files against acceptance criteria;
- return a result or review package with changed files, checks, risks, gaps, and recommended next route.

Implementer must not:

- output `review_passed` or claim clean review approval for its own work;
- act as the final reviewer of record;
- close readiness, merge-back, archive, branch cleanup, commit, push, PR, or tracker decisions;
- expand scope into unrelated issues or dependent write tasks without routing back through dispatch.

### Clean Reviewer

Clean reviewer owns fresh-context read-only review.

Clean reviewer may:

- inspect the supplied package, cited artifacts, changed files, diff evidence, acceptance map, and checks;
- return `review_findings` ordered by severity;
- mark missing evidence as `unverified` or `blocked`;
- recommend `verify`, `triage`, `dispatch_write_task`, `human_decision`, or `done`.

Clean reviewer must not:

- edit files;
- rely on hidden parent context or unsupplied memory;
- perform merge-back, archive, branch cleanup, commit, push, PR, or remote mutation;
- turn a clean review pass into UAT, release, customer-readiness, or final acceptance approval.

### Verifier

Verifier owns scope-first evidence sufficiency.

Verifier may:

- judge whether source, diff, test, runtime, browser, data, environment, UAT, or release evidence is sufficient for the claimed readiness question;
- return `pass`, `partial`, `fail`, or `blocked` within the stated verification scope;
- recommend `triage closeout`, `gap closure`, `re-verify`, or `blocked needs-info`.

Verifier must not:

- execute runtime implementation work;
- replace clean review;
- mutate files, remotes, trackers, branches, archives, or lifecycle state unless an explicit artifact/state threshold and approval path applies;
- close tasks directly without routing the state decision back through triage or coordinator closeout.

### Coordinator

Coordinator owns routing and closeout decisions.

Coordinator may:

- perform intake checks on result packages and review findings;
- decide whether separation thresholds require clean review, verification, remediation, serialization, merge-back, archive, branch cleanup, or human decision;
- preserve barriers between dependent tasks until merge-back and base refresh evidence exists.

Coordinator must not:

- become the deep reviewer of record for complex, high-risk, multiple, stale-context, or weak-evidence packages;
- treat child implementer self-check as clean review;
- claim readiness, merge-back, archive, branch cleanup, or closeout without the required evidence from the owning role.

## Routing Rules

- Use `skills/dispatch/CLEAN-REVIEW-FANOUT.md` when the completed package needs fresh-context review.
- Use `skills/dispatch/ROUTING-PROFILES.md` to choose the lightest runtime that satisfies the threshold and ownership boundary.
- Use `skills/verify/SKILL.md` when the question is evidence sufficiency or readiness, not implementation conformance alone.
- Use `skills/handoff/SKILL.md` only to preserve compact continuation state or review context; handoff is not execution, clean review, verification, or closeout.

## Expected Eval Hooks

Future evals should reject:

- a complex child implementer claiming `review_passed` or final review approval;
- P1, public API, migration, security, auth, permissions, data correctness, package schema, or adapter contract work that skips fresh clean review;
- a verifier replacing clean review or runtime implementation;
- a handoff package acting as the executor of follow-up work;
- coordinator closeout based only on child self-check for complex work.

Future evals should allow:

- small, low-risk direct work to remain lightweight;
- coordinator intake for a complete, single, low-risk package when no fan-out trigger applies;
- read-only planning and review tasks to avoid managed worktree ceremony unless a concrete write implementation task is created.
