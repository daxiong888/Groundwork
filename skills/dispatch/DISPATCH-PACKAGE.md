# Dispatch Package v2

## Target Reader

Groundwork dispatch users and reviewers producing the default package-only routing output from an accepted task artifact.

## Reader Action Needed

Generate or inspect a compact Dispatch Package v2 skeleton without treating package generation as execution.

## Decision Supported

Whether accepted work has enough named source truth, readiness, runtime routing, safety policy, and validation expectations for a human-reviewable dispatch package skeleton.

## Scope

This compact contract is the default `ACCEPTED-TASK.md -> Dispatch Package v2` read path. It is intentionally short and does not include the extended adapter-ready schema.

## Out of Scope

Runtime execution, Codex App thread creation, subagent spawning, worktree creation, branch mutation, remote writes, tracker mutation, field-level adapter validation, and final readiness decisions.

## Evidence Level

Derived from Groundwork dispatch package-only boundaries and the extended details contract in `DISPATCH-PACKAGE-DETAILS.md`.

## Compact Default Contract

Use this section for the default `ACCEPTED-TASK.md -> Dispatch Package v2` path. The package is package-only: dispatch must not execute work, spawn subagents, create worktrees, mutate branches, run verification, or claim selector enforcement, cache refresh, release readiness, UAT readiness, or clean-review results.

Default output is a human-reviewable package skeleton, not adapter-complete until extended fields are supplied. Set `adapter_completeness: skeleton_only` unless the prompt explicitly asks for an adapter-ready package and the extended details contract has been applied.

```yaml
dispatch_version: 2
adapter_completeness: skeleton_only | adapter_ready
source:
  prd: ""
  issue_set: ""
  readiness_source: ""
  source_truth_status: accepted | external_accepted | issue_ready | mixed | unknown
  redactions_applied: ""
runtime_policy:
  allow_parallel: true | false
  max_parallel_units: 1
  remote_writes_allowed: false
  destructive_actions_allowed: false
tasks:
  - task_id: ""
    title: ""
    task_type: write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ready_for_agent | ready_for_human | needs_info | blocked | needs_split | accepted_direct
    runtime_id: codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer | not_applicable
    runtime_reason: ""
    dispatch_native_alignment:
      route_decision:
        route: local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate
        reason: ""
        why_not_worktree: ""
        why_worktree_if_selected: ""
        expected_touched_files: []
      source_package:
        known_source_or_first_inspection_step: ""
        redactions_applied: ""
      policy:
        remote_writes_allowed: false
        destructive_actions_allowed: false
        approval_required: true | false
      verification_expectation:
        fastest_signal: ""
        required_evidence: ""
        release_readiness_claimed: false
      runtime_evidence:
        evidence_owner: codex_runtime | adapter | user_supplied | not_applicable
        worktree_creation_claimed: false
        handoff_execution_claimed: false
        runtime_success_claimed: false
        cache_refresh_claimed: false
    isolation:
      context: thread | subagent_prompt | none | review_package
      filesystem: codex_managed_worktree | current_workspace | none | tool_dependent
      diff_surface: required | not_required | optional
    goal_contract:
      outcome: ""
      source_truth: ""
      acceptance_criteria_mapping: ""
      verification: ""
      constraints: ""
      boundaries: ""
      stop_when: ""
      result_package_expected: review_package | findings_package | diagnosis_package | direct_result | review_findings
    runtime_package:
      adapter: ""
      expected_output: review_package | findings_package | diagnosis_package | direct_result | review_findings
```

If required evidence is absent, set `readiness: needs_info`, `blocked`, or `needs_split`; do not invent source truth or route a write package as executable.

adapter_ready requires `DISPATCH-PACKAGE-DETAILS.md` and the full fields needed by the consuming adapter, managed worktree route, dependency barrier, or field-level validation. A compact skeleton with `adapter_completeness: skeleton_only` is suitable for coordinator review and routing discussion, not direct adapter consumption.

## Conditional Reference Policy

- Do not load `DISPATCH-PACKAGE-DETAILS.md` unless the prompt asks for an adapter-ready package, full schema, adapter contract, managed worktree admissibility, dependency barrier, legacy compatibility, or field-level validation.
- Do not load `RESULT-PACKAGE.md` unless the prompt asks for result package expectations or returned evidence.
- Do not load `RUNTIME-ADAPTERS.md` unless runtime adapter, runtime capability, or selector behavior is in scope.
- Do not load `ROUTING-PROFILES.md` unless model/profile selection is material.
- Do not load `EXAMPLES.md` unless the user asks for examples or format ambiguity blocks output.
