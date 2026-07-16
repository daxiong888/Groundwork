# Result Package

Target Reader: Groundwork verify/triage/handoff users, dispatch reviewers, and runtime adapters returning work to a coordinator.

Reader Action Needed: Wrap runtime output before claiming a task is ready for review, needs remediation, is blocked, or can move to the next route.

Decision Supported: Whether output is a review package, findings package, diagnosis package, direct result, or reviewer findings, and which Groundwork route owns the next step.

Scope: Unified result envelope and runtime-specific output requirements. Runtime execution mechanics are out of scope.

Out of Scope: Runtime execution, clean-review approval, UAT/release readiness, remote writes, tracker mutation, and selector enforcement without adapter evidence.

Evidence Level: Derived from dispatch contracts, managed worktree package rules, and runtime result envelope requirements.

## Unified Envelope

```yaml
result_package:
  result_version: 1
  task_id: ""
  runtime_id: ""
  outcome: ready_for_review | needs_remediation | blocked | human_decision | no_execution_needed
  output_type: review_package | findings_package | diagnosis_package | direct_result | review_findings
  runtime_identity: {runtime_correlation_id, dispatch_id, task_id}
  goal_mode: {required, goal_command_first_line, lint_passed_before_delivery, runtime_goal_mode_evidence, evidence, failure_action}
  runtime_lifecycle: {status, state, evidence}
  review: {kind, required, status, reviewer_context, reviewed_material_change_id, findings, evidence}
  review_loop: {status, latest_material_change_id, previous_review_stale_reason, findings_addressed, next_review_required, next_route}
  merge_back: {status, source_available, source_evidence, changed_pathspecs, validation_after_merge, evidence}
  archive: {status, blockers, approval_required, approval_evidence, evidence}
  branch_cleanup: {status, branch_detected, branch_name, approval_required, approval_evidence, evidence}
  task: {title, task_type, goal_contract_used, source_truth}
  runtime: {adapter, execution_profile_requested, execution_profile_actual, selector_enforcement}
  changes: {changed_files, diff_summary, diff_or_findings_completeness}
  validation: {applicability, commands_run, results, checks_not_run, evidence}
  findings: {summary, details, citations_or_paths}
  risk: {remaining_risks, blockers, recommended_next_route}
  adapter_extension: {}
```

## Outcome Rules

`outcome` is the only Result Package summary field. Do not add adapter-specific synonyms such as `status`, `verdict`, or `no_worktree_needed`.

- `ready_for_review`: the returned output is complete enough for its next review step. It does not mean review passed, merge occurred, or archive/cleanup is allowed.
- `needs_remediation`: bounded correction is required before the next review step.
- `blocked`: missing source truth, capability, safe state, required evidence, or another objective prerequisite prevents progress.
- `human_decision`: progress requires an authority, topology, risk-acceptance, retention, or destructive-action choice that must not be inferred.
- `no_execution_needed`: admission or routing evidence proves that no runtime execution was required. Record the reason; do not use it to hide an incomplete executable package.

Legacy `status` values remain readable only at intake. Map `no_worktree_needed` to `no_execution_needed` with the non-admission reason preserved; never emit either legacy field/value in a new Result Package.

## Orthogonal Status Axes

The following axes are independent. A change in one must not advance another without that axis's own evidence.

| Axis | Canonical Statuses | Boundary |
| --- | --- | --- |
| `runtime_lifecycle` | `not_started`, `pending`, `running`, `result_returned`, `failed`, `blocked`, `not_applicable` | Runtime/thread execution only. Adapter-specific detailed states use `state` or `adapter_extension`. |
| `review` | `not_required`, `pending`, `passed`, `findings_open`, `blocked`, `unverified` | `passed` requires the named review evidence; a child self-check is not clean review. |
| `merge_back` | `not_applicable`, `pending`, `applied`, `discarded`, `blocked`, `unverified` | Requires its own source, git-boundary, application, and validation evidence. |
| `archive` | `not_applicable`, `not_ready`, `ready`, `archived`, `retained`, `blocked`, `unverified` | Archive readiness is a coordinator closeout decision; archive does not imply branch cleanup. |
| `branch_cleanup` | `not_applicable`, `pending`, `cleaned`, `retained`, `blocked`, `human_decision`, `unverified` | Requires branch identity and approval evidence; remote/force/unknown cleanup routes to human decision. |

Runtime completion does not imply review pass. Review pass does not imply merge. Merge or discard does not imply archive. Archive does not imply branch cleanup. Child runtimes report evidence; coordinator closeout owns merge, archive, and cleanup decisions.

`review.reviewed_material_change_id` must equal `review_loop.latest_material_change_id` before `review.kind: clean` with `review.status: passed` can support closeout. This freshness field belongs to the generic Result Package base; adapters may consume it but must not copy or redefine it in `adapter_extension`.

## Selector Enforcement

`selector_enforcement` is returned evidence, not the request-side `selector_policy`. Use the canonical statuses and proof rules from `skills/_shared/RUNTIME-CAPABILITY.md`; Dispatch Package content alone cannot prove enforcement.

## Runtime Output Requirements

| Runtime | Output Type | Required Evidence | Must Not Claim |
| --- | --- | --- | --- |
| `codex_app_managed_worktree_thread` | `review_package` | accepted write task, worktree isolation, Goal Contract, source package, verification expectation, correlation id, changed files, diff summary, validation, runtime lifecycle, and managed-worktree adapter delta | read-only/planning/hybrid pre-split execution, missing Goal Contract/source/validation, or thread/worktree/validation/selector/merge/cleanup evidence not returned by adapter |
| `codex_subagent` | `findings_package` or `diagnosis_package` | role/lens, package id, inspected evidence, findings/diagnosis, confidence/gaps, no-edit confirmation unless write execution was approved and evidenced, capability/approval status | `review_package`, execution/validation/review claims when only a package was generated, file edits without explicit approved support |
| `main_thread_direct` | `direct_result` | action/answer, files changed if any, validation or no-test reason, risks, next route | independent review, runtime isolation, selector enforcement |
| `main_thread_readonly` | `findings_package` | reviewed scope, evidence inspected, findings, no file edits | implementation or package execution |
| `clean_reviewer` | `review_findings` | supplied package scope, coverage covered/not covered, findings, missing evidence, no edits | final readiness, merge/archive/branch cleanup, runtime execution |

## Managed Worktree Rules

- Valid managed worktree results must correspond to a package with `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, Goal Contract, source package, validation package, and `expected_output = review_package`.
- Echo `runtime_identity.runtime_correlation_id`; thread titles are display-only. If title changes, preserve correlation id and set mutation evidence.
- Goal Mode evidence is required when requested; absent/unavailable/unknown Goal Mode evidence routes to `blocked` or `needs_remediation`, not `ready_for_review`.
- `pendingWorktreeId` alone is pending init, not child-thread/worktree success.
- `runtime_lifecycle.status: result_returned` is not archive-ready; archive readiness requires its own review and merge/discard/retention evidence. `archived` does not imply branch cleanup.
- Merge-back claims require reliable source, applied-to-main evidence, changed pathspecs, and validation status.
- Branch cleanup completion requires branch identity, approval where needed, and cleanup evidence.
- `review.kind: clean` with `review.status: passed` requires fresh independent review. Low-risk coordinator intake uses `review.kind: coordinator_intake` and cannot be promoted to clean-review evidence.
- A clean-review pass requires a non-empty base `review.reviewed_material_change_id` matching base `review_loop.latest_material_change_id`; mismatched or missing ids keep the latest material change unreviewed.
- Managed-worktree-only registry, init, thread-title, worktree-path, and review-package fields belong under the adapter delta in `adapters/codex_app_managed_worktree_thread/RESULT-PACKAGE-TEMPLATE.md`. The generic `review_loop` remains in the base envelope for every reviewable runtime.

Older v0.3.2 result packages remain readable. If lifecycle closeout needs missing v0.3.3 fields, route to `needs_remediation`, `blocked`, or `human_decision` instead of inferring evidence.
