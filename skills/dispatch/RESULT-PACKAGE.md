# Result Package

## Target Reader

Groundwork verify/triage/handoff users, dispatch reviewers, and runtime adapters returning work to a coordinator.

## Reader Action Needed

Wrap any runtime output in this envelope before claiming the task is ready for review, needs remediation, blocked, or complete enough for the next route.

## Decision Supported

Whether runtime output is a review package, findings package, diagnosis package, direct result, or reviewer findings, and what the next Groundwork route should be.

## Scope

This document defines the unified result envelope and runtime-specific output requirements. It does not define runtime execution mechanics.

## Out of Scope

Runtime execution, clean-review approval, UAT/release readiness, remote writes, tracker mutation, and claiming selector enforcement without adapter evidence.

## Evidence Level

Derived from Groundwork dispatch contracts, managed worktree package rules, and runtime result envelope requirements.

## Unified Result Envelope

```yaml
result_package:
  task_id: ""
  runtime_id: ""
  status: ready_for_review | needs_remediation | blocked | no_execution_needed | no_worktree_needed
  output_type: review_package | findings_package | diagnosis_package | direct_result | review_findings

  runtime_identity:
    runtime_correlation_id: ""
    dispatch_id: ""
    task_id: ""
    parent_thread_identifier: ""
    child_thread_identifier: ""
    initial_thread_title: ""
    current_thread_title: ""
    title_mutation_detected: true | false | unknown

  goal_mode:
    required: true | false
    goal_command_first_line: true | false | unknown
    lint_passed_before_delivery: true | false | unknown
    runtime_goal_mode_evidence: present | absent | unavailable | unknown
    evidence: ""
    failure_action: none | corrective_resend | blocked | needs_remediation

  lifecycle:
    current_state: ""
    archive_ready: true | false | unknown
    archive_blockers: []
    next_lifecycle_route: clean_reviewer | merge_back | branch_cleanup | triage | verify | human_decision | done

  merge_back:
    source_available: worktree_path | patch_bundle | branch_or_head | unavailable | not_applicable
    source_evidence: ""
    reliable_source: true | false | unknown
    applied_to_main_worktree: true | false | not_attempted | unknown
    changed_pathspecs: []
    validation_after_merge: pass | fail | skipped | unverified | not_applicable
    evidence: ""

  branch_cleanup:
    branch_detected: true | false | unknown
    branch_name: ""
    cleanup_recommendation: delete_local | delete_remote | retain | human_decision | no_branch_detected | not_applicable
    approval_required: true | false
    approval_evidence: ""
    cleanup_completed: true | false | not_attempted | unknown
    evidence: ""

  clean_review:
    required: true | false
    reviewer_context: fresh | coordinator_intake | not_required | unknown
    status: pending | passed | failed | blocked | not_required
    findings: []
    evidence: ""

  task:
    title: ""
    task_type: ""
    goal_contract_used: true
    source_truth: ""

  runtime:
    adapter: ""
    execution_profile_requested: ""
    execution_profile_actual: ""
    selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown

  changes:
    changed_files: []
    diff_summary: ""
    diff_or_findings_completeness: complete | redacted_complete | redacted_partial | not_applicable

  validation:
    applicability: applicable | not_applicable
    commands_run: []
    results: ""
    checks_not_run: ""
    evidence: ""

  findings:
    summary: ""
    details: ""
    citations_or_paths: ""

  risk:
    remaining_risks: []
    blockers: []
    recommended_next_route: verify | triage | dispatch_write_task | human_decision | done
```

## Runtime Selector Enforcement

`selector_enforcement` is a runtime evidence field.

- `tool_enforced`: the runtime adapter confirms model/reasoning selectors were applied by tool or API.
- `prompt_preference`: selectors were provided as instructions only.
- `unavailable`: runtime cannot accept selectors.
- `unknown`: selector support was not inspected or reported.

Do not report `tool_enforced` based on Dispatch Package contents alone.

## Runtime-specific Output Requirements

### codex_app_managed_worktree_thread

Required output type: `review_package`.

Groundwork-side admissibility echoed in results:

- Valid managed worktree outputs must correspond to a package with `task_type = write_implementation`, `readiness = ready_for_agent`, `isolation.filesystem = codex_managed_worktree`, present Goal Contract, present source package, present validation package, and `expected_output = review_package`.
- Valid managed worktree outputs must echo `runtime_identity.runtime_correlation_id` from the dispatch package.
- Valid managed worktree outputs must include `goal_mode` evidence when Goal Mode was required and `lifecycle.current_state` when lifecycle closeout or archive routing may follow.
- Inputs that are read-only, planning-only, hybrid before split, addressed to a different runtime, missing Goal Contract, missing source package, missing validation, or expecting anything other than `review_package` should not appear as executable managed worktree results.
- If such an input reaches result reporting, use `status = no_worktree_needed`, `needs_remediation`, or `blocked` with evidence, rather than implying a managed worktree executed.

Must include:

- runtime correlation ID and runtime identity fields when available
- thread identifier and thread title display label when available
- worktree type and path when available
- Goal Mode evidence when the package required Goal Mode
- lifecycle status and archive blockers when lifecycle closeout may follow
- merge-back source, reliability, application status, and evidence when merge-back may follow
- branch detection, cleanup recommendation, approval requirement, and cleanup evidence when cleanup may follow
- clean-review requirement, reviewer context, status, findings, and evidence when clean review may follow
- changed files
- diff summary
- validation commands and results
- checks not run and reason
- remaining risks and blockers
- selector enforcement status from the adapter

Must not include:

- read-only, planning-only, hybrid pre-split, or non-managed-runtime tasks as executable worktree packages
- missing Goal Contract, missing source package, missing validation package, or non-review-package inputs as executable worktree outputs
- remote write claims unless explicitly approved and executed
- Codex App worktree/thread creation, staging, committing, pushing, PR creation, validation execution, or selector enforcement claims unless the adapter returns evidence

Adapter mechanics boundary:

- Groundwork consumes or reviews the result package; it does not create Codex App managed worktrees, run child threads, archive threads, or enforce selectors.
- Managed worktree adapter contract details live under `skills/dispatch/adapters/codex_app_managed_worktree_thread/`; that directory is an internal contract package, not a public skill.
- `selector_enforcement = tool_enforced` is valid only when the executing adapter confirms model/reasoning selector application. Otherwise use `prompt_preference`, `unavailable`, or `unknown`.
- Thread titles are display-only labels. If the visible title changes, keep correlating by `runtime_identity.runtime_correlation_id`, report the observed `current_thread_title` when available, and set `title_mutation_detected = true`.
- Older v0.3.2 result packages without `runtime_identity`, `goal_mode`, `lifecycle`, `merge_back`, `branch_cleanup`, or `clean_review` remain readable. If managed worktree lifecycle closeout requires any missing v0.3.3 field, route to `needs_remediation`, `blocked`, or `human_decision` instead of inferring evidence.
- If Goal Mode is required and `goal_mode.runtime_goal_mode_evidence` is `absent`, `unavailable`, or `unknown`, route to `blocked` or `needs_remediation`; do not report `ready_for_review`.
- `review_package_returned` is not archive-ready evidence. Archive readiness requires clean review plus merge/discard evidence or a blocked-with-human-decision closeout path, and `archived` does not imply branch cleanup.
- Do not claim `merged_to_main_worktree`, completed merge-back, or post-merge validation unless `merge_back.reliable_source = true`, `merge_back.applied_to_main_worktree = true`, and supporting evidence are present.
- Do not claim `branch_cleaned` or completed cleanup unless required approval is satisfied and `branch_cleanup.cleanup_completed = true` with evidence. If approval is missing or branch identity is uncertain, route to `human_decision` or `blocked`.
- Do not claim clean review passed from the child implementation package alone. `clean_review.status = passed` requires fresh clean-review evidence or a documented `coordinator_intake` decision that satisfies the low-risk exception in `skills/dispatch/CLEAN-REVIEW-FANOUT.md`.

### codex_subagent

Required output type: `findings_package` or `diagnosis_package`.

Must include:

- subagent role or lens
- prompt/package identifier when available
- files or evidence inspected
- findings, diagnosis, confidence, and gaps
- confirmation that file edits did not occur, unless explicit write-capable subagent execution was approved and supported
- capability detection outcome and whether execution was explicitly requested or approved
- package-only status when dispatch generated a `subagent_package` but no runtime adapter executed it
- selector enforcement status from the adapter or `unknown`

Must not include:

- `review_package` as the subagent runtime output type
- claims that subagent execution, validation, or review happened when dispatch only produced a package
- file edit claims unless write-capable subagent execution was explicitly requested, approved, supported, and evidenced

### main_thread_direct

Required output type: `direct_result`.

Must include:

- action performed or answer given
- files changed, if any
- validation evidence or no-test reason
- risks and next route

### main_thread_readonly

Required output type: `findings_package`.

Must include:

- scope reviewed
- evidence inspected
- findings or decision support
- explicit no-file-edit boundary
- next route

### clean_reviewer

Required output type: `review_findings`.

Must include:

- review lens
- package, diff, or evidence inspected
- findings ordered by severity
- residual risk or missing evidence
- recommended next route

## Status Rules

- Use `ready_for_review` only when the runtime completed its package and provided evidence.
- Use `needs_remediation` when output is incomplete or acceptance criteria are unmet but a scoped fix direction exists.
- Use `blocked` when missing input, missing tools, unsafe state, or unresolved product truth prevents progress.
- Use `no_execution_needed` for read-only or planning outputs that intentionally did not execute runtime work.
- Use `no_worktree_needed` when a non-write route intentionally avoided managed worktree creation.
