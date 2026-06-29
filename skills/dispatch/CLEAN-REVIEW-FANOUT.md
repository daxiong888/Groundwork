# Clean Review Fan-out Protocol

Target Reader: Groundwork coordinators, dispatch package authors, clean reviewers, and read-only review subagents.
Reader Action Needed: Decide when coordinator intake is enough, when completed implementation packages must fan out to clean review, and what the reviewer may do.
Decision Supported: Whether a completed child result package can remain in coordinator intake or must be routed to `clean_reviewer` / read-only `codex_subagent` before verify, triage, remediation, or closeout.
Artifact Type: shared guardrail
Source of Truth: PRD v0.3.3 FR-7 and Issue 6, dispatch runtime adapter profiles, `skills/_shared/REVIEW-LOOP.md`, and `skills/_shared/LOW-RISK-COORDINATOR-INTAKE.md`.
Scope: Clean review routing thresholds, package-only reviewer context, read-only reviewer actions, coordinator boundaries, and future eval hooks for managed worktree lifecycle hardening.
Out of Scope: Public skill creation, runtime execution, file edits by reviewers, automatic subagent spawning, child implementation self-approval, final readiness, remote writes, commits, pushes, PRs, archive, or branch cleanup.
Evidence Level: Derived from PRD v0.3.3 FR-7 and Issue 6, plus existing dispatch runtime adapter profiles.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Core Rule

Clean review is an independent, fresh-context review of a completed result or review package. It is not the child implementation thread's self-review, and it is not a coordinator skimming the parent conversation.

A reviewer spawned from the parent thread's full history is not a fresh-context clean reviewer, even if it is a different agent. If the attempted reviewer used a full parent-history fork or unapproved nested delegation, the coordinator must disclose the topology and treat Clean Review Evidence as `unverified` or `blocked` until a self-contained fresh-context review is rerun. A human decision may explicitly accept the risk of proceeding without Clean Review Evidence, but it must not relabel forked or nested reviewer output as a clean-review pass.

The coordinator may perform low-cost intake to decide whether the package is complete enough to route. Deep review must fan out when size, risk, volume, missing evidence, or context freshness makes coordinator review unreliable.

Use `skills/_shared/REVIEW-LOOP.md` for the stable post-implementation loop. A clean-review package may pass, block, or find remediation work, but it must not mutate files. When remediation changes material files, the previous clean-review result is stale for the latest diff and the coordinator must route the new package through clean review again unless the low-risk coordinator-intake exception is explicitly recorded.

## Coordinator Intake Boundary

Coordinator intake may:

- check that a result package exists and has `output_type = review_package` or another expected reviewable output;
- check that changed files, acceptance mapping, validation evidence, remaining risks, and next route are present;
- reject incomplete packages as `needs_remediation` or `blocked`;
- decide whether the package is small and low risk enough for direct coordinator handling;
- prepare a `clean_review_package` for `clean_reviewer` or read-only `codex_subagent`.

Coordinator intake must not:

- act as the only deep diff review for large, multiple, or high-risk packages;
- treat child implementation self-review as clean review;
- treat a full parent-context forked reviewer as clean review;
- treat unapproved nested reviewer agents or child threads as clean review evidence;
- infer missing facts from parent memory or hidden conversation context;
- approve closeout, archive, or final readiness solely from a child self-check;
- edit files as part of clean review.

## Fan-out Triggers

Route to `clean_reviewer` or read-only `codex_subagent` when any condition is true:

- multiple child result or review packages return to one coordinator;
- a package is large enough to risk coordinator context overload;
- changed files include public interfaces, schema, migrations, generated artifacts, shared fixtures, state machines, shared config, adapter contracts, or package templates;
- task is P0/P1, security-sensitive, migration-like, customer-visible, or otherwise high-risk;
- validation was skipped, failed, partial, environment-limited, or only manually inspected;
- child implementation performed validation-fix iterations;
- user asks for independent review;
- coordinator context has compacted, is stale, or is managing multiple concurrent returns;
- the package's own completeness, redaction, or evidence boundary is uncertain.

Small, single-package, low-risk returns may stay in coordinator intake only when the package satisfies `skills/_shared/LOW-RISK-COORDINATOR-INTAKE.md`. The coordinator must record the eligibility shape, validation evidence or not-applicable reason, decision reason, evidence refs, and remaining risks. This exception is not `clean_review_passed` and must not be used for archive, branch cleanup, merge, release, UAT, runtime, browser, or final readiness.

## Runtime Choice

```text
clean_reviewer
  Use for review package inspection, diff conformance, product/security/QA/contract/git-boundary/evidence lenses, and no-edits findings.

codex_subagent
  Use for read-only multi-perspective review, independent diagnosis, or package-only findings when a clean reviewer runtime is unavailable or a role-specific reviewer is needed.

main_thread_readonly
  Use for low-cost coordinator intake, package completeness checks, and routing decisions. Do not use it as the default deep reviewer for large, multiple, or high-risk returns.
```

## Clean Review Package Requirements

The reviewer receives only the supplied package and cited artifacts. The package must be self-contained enough that a reviewer can work without parent session memory.

Required inputs:

- runtime correlation or task identifier;
- review lens;
- source truth and acceptance criteria;
- result package or child review package;
- changed file list and redacted diff/detail when applicable;
- validation evidence and checks not run;
- allowed and disallowed reviewer actions;
- required output format and severity ordering.

Use `skills/dispatch/adapters/codex_app_managed_worktree_thread/CLEAN-REVIEW-PACKAGE-TEMPLATE.md` for the canonical package shape.

## Reviewer Action Rules

Reviewers are read-only by default:

- `read_only` must be `true`;
- `file_edits_allowed` must be `false`;
- `spawn_more_agents_allowed` must be `false`;
- runtime invocation must disable parent thread history forks (`fork_context=false` or equivalent) when that control is available;
- reviewer output from `fork_context=true`, equivalent full-history fork, or unapproved nested delegation must be `unverified` or `blocked`, not `pass`;
- reviewer output must be findings, not patches;
- reviewer must cite supplied package sections, paths, commands, or evidence;
- missing evidence must be `unverified` or `blocked`, not guessed;
- reviewer must not rely on parent memory, hidden thread context, or non-supplied artifacts;
- reviewer must not claim runtime execution, validation, merge-back, archive, branch cleanup, commit, push, PR, or remote mutation unless the supplied package contains evidence for that action.

If review reveals a required write, route a separate write implementation task through dispatch. Do not convert the clean review task itself into an edit task.

## Output Handling

Clean review output should be routed as:

```text
review_findings
- verdict: pass | needs_remediation | blocked | unverified
- findings: P0/P1/P2/P3 ordered
- coverage:
  - covered:
  - not_covered:
- evidence: cited package sections, paths, commands, or observations
- missing_evidence:
- recommended_next_route: verify | triage | dispatch_write_task | human_decision | done
```

`pass` means the reviewer found no blocking package-level conformance issue within the supplied evidence. It is not UAT, release, customer-readiness, archive, merge-back, or final acceptance approval.

`coverage.covered` and `coverage.not_covered` are mandatory. A clean review that does not declare what was and was not covered must route to `unverified` or `blocked`, not `pass`, because closeout cannot infer review scope from findings alone.

## Remediation Loop

When clean review returns `needs_remediation`:

- route writes to `dispatch_write_task`, the original child implementation route, or `implement`; do not let the clean reviewer edit files;
- keep remediation scoped to cited findings, accepted gap-closure items, and required checks;
- require the implementer to return updated `Self-check Evidence`, `findings_addressed`, checks run, checks not run, and remaining risks;
- set `review_loop.previous_review_stale_reason` when material files changed after the prior clean review;
- set `review_loop.next_review_required = true` unless a documented low-risk coordinator-intake exception applies;
- route the updated package back to `clean_reviewer` or read-only `codex_subagent` before verify, merge-back, archive, branch cleanup, or closeout claims.

Loop exits are limited to `clean_review_passed`, `blocked`, `human_decision`, or documented `low_risk_coordinator_intake`. These exits still do not prove runtime, browser, UAT, release, archive, branch cleanup, commit, push, PR, remote mutation, or final readiness.

## Expected Eval Hooks

Later eval coverage should include:

- main thread performs intake only, then routes multiple child packages to `clean_reviewer`;
- large package or public-interface change routes to `clean_reviewer` or read-only `codex_subagent`;
- low-cost coordinator intake remains allowed for small, low-risk, complete packages only when the shared low-risk eligibility shape is recorded;
- low-cost coordinator intake is rejected for multiple packages, P0/P1 findings, public interfaces, schema, migrations, shared fixtures, state machines, shared config, adapter contracts, package templates, customer-visible/security/privacy/data-write/release/UAT risk, skipped/failed/partial validation, validation-fix iterations, stale coordinator context, or user-requested independent review;
- low-cost coordinator intake is rejected when it is relabeled as `clean_review_passed` or used for release, UAT, archive, branch cleanup, merge, commit, push, PR, runtime, browser, or final readiness;
- child implementation self-review is rejected as clean review;
- clean reviewer output that edits files is rejected;
- clean reviewer output that relies on hidden parent context is rejected;
- clean reviewer output from `fork_context=true` or equivalent full parent-history fork is rejected;
- clean reviewer output routed through unapproved nested agents or child threads is rejected or marked `unverified` or `blocked`;
- missing validation evidence is reported as `unverified` or `blocked`;
- clean review output declares `covered` and `not_covered` review scope;
- clean review pass does not claim final readiness, archive, merge-back, branch cleanup, commit, push, PR, or remote mutation.
- clean-review findings route to scoped remediation, then stale prior review evidence triggers a new clean-review pass before downstream closeout.
