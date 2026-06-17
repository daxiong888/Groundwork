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
- Inputs that are read-only, planning-only, hybrid before split, addressed to a different runtime, missing Goal Contract, missing source package, missing validation, or expecting anything other than `review_package` should not appear as executable managed worktree results.
- If such an input reaches result reporting, use `status = no_worktree_needed`, `needs_remediation`, or `blocked` with evidence, rather than implying a managed worktree executed.

Must include:

- thread identifier and thread title when available
- worktree type and path when available
- Goal Mode evidence when the package required Goal Mode
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
