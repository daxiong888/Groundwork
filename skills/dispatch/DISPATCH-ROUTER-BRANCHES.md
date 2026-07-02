# Dispatch Router Branches

Target Reader: Codex running `dispatch` after selecting lite matrix, full package, clean review fanout, or complex separation.
Reader Action Needed: Apply runtime routing behavior, selector honesty, route constraints, and hard stops without loading them in the active `SKILL.md` entry.
Decision Supported: Which post-readiness runtime/package route is appropriate, what package is emitted, and which tasks must stop, split, or return to triage.
Artifact Type: branch-specific dispatch reference
Source of Truth: `skills/dispatch/SKILL.md`, `DISPATCH-PACKAGE.md`, `RESULT-PACKAGE.md`, and shared runtime/evidence contracts.
Scope: Dispatch-internal package task classification, post-readiness runtime/package route behavior, package-only boundaries, selector honesty, split rules, and execution gates.
Out of Scope: Upstream raw-intent classification, raw requirement intake, draft PRD intake, ordinary implementation, ordinary verification, runtime execution, thread/worktree creation, remote writes, tracker mutation, final readiness, release, UAT, or customer acceptance.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required Routing Behavior

Dispatch task classification happens only after the active entry route already has accepted, ready, or returned runtime-material work. It must not decide whether raw user intent belongs to `to-prd`, `to-issues`, `triage`, `verify`, `implement`, `handoff`, `wiki`, or direct response.

Dispatch must:

- confirm source truth, issue set, readiness source, and evidence level before routing;
- classify each task as `write_implementation`, `read_only_review`, `planning_only`, `hybrid`, `diagnosis`, `verification`, or `direct`;
- consume the Goal Contract when present and identify missing required fields;
- assign exactly one `runtime_id` per routed task;
- assign exactly one route decision: `local_direct`, `local_with_artifact`, `worktree_isolated`, `worktree_review_only`, or `automation_candidate`;
- assign isolation level, execution profile, validation expectation, and expected Result Package;
- identify parallelization eligibility and conflict/dependency groups when evidence exists;
- preserve the distinction between package-wide `runtime_policy.max_parallel_units` and group-level `tasks[].parallelization.max_parallel_group_size`;
- route read-only and planning-only tasks away from `worktree_isolated`;
- split hybrid work before any write worktree package is generated;
- default write implementation tasks to managed worktree only when readiness, Goal Contract, source package, verification expectation, and concrete worktree justification are present;
- keep `automation_candidate` recommendation-only;
- report Runtime mismatch when requested runtime and available/proposed runtime differ;
- keep wiki pages, wiki summaries, audits, and external graph/search/index output within `EB-WIKI-001`.

## Selector And Capability Honesty

Use `skills/_shared/RUNTIME-CAPABILITY.md` and `skills/_shared/COGNITIVE-BUDGET.md` when runtime or model selection is material.

- `tool_enforced` is valid only when the adapter confirms selector support.
- Use `prompt_preference`, `unavailable`, or `unknown` when selector support is not evidenced.
- User-observed model menu seeds are dated `user_supplied` facts, not universal runtime truth.
- Concrete model mapping is evidence-bound and secondary to profile routing.
- Fast/Spark-like profiles cannot be final clean reviewer, final verifier, public skill approver, release/UAT authority, or customer authority.

## Route-Specific Loading

- Lite matrix: load only this file plus `ROUTING-PROFILES.md` when execution profile detail is needed.
- Full package: load `DISPATCH-PACKAGE.md`; load `RESULT-PACKAGE.md` only for returned-result expectations.
- Clean review fanout: load `CLEAN-REVIEW-FANOUT.md`; clean reviewers are read-only and cannot remediate their own findings.
- Managed worktree or closeout: load `COMPLEX-WORK-SEPARATION.md`, `RUNTIME-ADAPTERS.md`, and adapter docs only as needed.
- Examples: load `EXAMPLES.md` only when an example package is useful for the active route.

## No-Execution Boundary

Dispatch applies `skills/_shared/NON-EXECUTOR-BOUNDARY.md`.

It must not:

- call runtime/thread/subagent tools from dispatch output alone;
- execute package contents or write files in target runtimes;
- claim selector enforcement, runtime execution, validation, clean review, cache refresh, release, UAT, or closeout happened from package text;
- create, update, schedule, or archive automations from an `automation_candidate` recommendation;
- silently substitute subagents for child-thread/worktree runtimes or child-thread/worktree runtimes for subagents.

## Execution Gate

If the user asks dispatch to execute, emit:

```text
Proposed Action:
Target Runtime:
Required Tool Capability:
Risk:
Rollback/Undo:
Approval Needed:
```

Proceed only after explicit approval and tool availability are both confirmed.

## Clean Review Claims

When a clean-review claim is blocked, unverified, invalid, inherited from parent context, or requires a future fresh reviewer, do not emit `clean_review: passed`, `clean_review_passed: true`, or `Clean Review Evidence: passed`.

Use explicit missing/required/fresh-pass-required wording. A clean review pass is implementation-conformance evidence only; it is not release, UAT, runtime, browser, archive, branch cleanup, commit, push, PR, customer, or final readiness evidence.
