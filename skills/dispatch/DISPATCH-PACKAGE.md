# Dispatch Package v2

Default reader: a coordinator deciding whether accepted work is sufficiently specified for package-only routing. This reference is source-validation guidance, not runtime execution or readiness evidence.

## Compact Default Contract

Use this section for the default `ACCEPTED-TASK.md -> Dispatch Package v2` path. The package is package-only: dispatch must not execute work, spawn subagents, create worktrees, mutate branches, run verification, or claim selector enforcement, cache refresh, release readiness, UAT readiness, or clean-review results.

Default output is one human-reviewable package skeleton, not a prose summary plus duplicate matrix. It is not adapter-complete until extended fields are supplied. Set `adapter_completeness: skeleton_only` unless the prompt explicitly asks for an adapter-ready package and the extended details contract has been applied. Omit empty and not-applicable fields.

## Default Output Budget

For lite routes and this default skeleton-only contract, target at most 2,800 characters and 26 non-empty lines. This is a regression budget, not a truncation rule; required fields and semantic completeness take precedence. Every Dispatch output, including lite and split decisions, must start at `dispatch_version: 2` without prose before or after. Do not wrap it in a code fence.

If the complete package does not fit, do not truncate or silently omit tasks, required evidence, or stop conditions. Return a compact `needs_split` decision with the next action, or use the prompt-material route-specific contract and produce a complete extended package. Adapter-ready, clean-review fanout, complex separation, field-level validation, and explicitly requested full-schema outputs are outside this default budget.

```yaml
dispatch_version: 2
adapter_completeness: skeleton_only | adapter_ready
source:
  artifact: ""
  source_truth_status: accepted | external_accepted | issue_ready | mixed | unknown
  readiness_source: ""
  redactions_applied: false | true
tasks:
  - task_id: ""
    title: ""
    readiness: ready_for_agent | ready_for_human | needs_info | blocked | needs_split | accepted_direct
    route: local_direct | local_with_artifact | worktree_isolated | worktree_review_only | automation_candidate
    reason: ""
    expected_output: review_package | findings_package | diagnosis_package | direct_result | review_findings
    required_evidence: ""
    stop_when: ""
policy:
  remote_writes_allowed: false
  destructive_actions_allowed: false
  approval_required: true | false
```

For clean review, use `route: worktree_review_only` and express the review in `expected_output`; clean review is not a separate route. If required evidence is absent, set `readiness: needs_info`, `blocked`, or `needs_split`; do not invent source truth or route a write package as executable.

adapter_ready requires `DISPATCH-PACKAGE-DETAILS.md` and the full fields needed by the consuming adapter, managed worktree route, dependency barrier, or field-level validation. A compact skeleton with `adapter_completeness: skeleton_only` is suitable for coordinator review and routing discussion, not direct adapter consumption.

## Conditional Reference Policy

- Do not load `DISPATCH-PACKAGE-DETAILS.md` unless the prompt asks for an adapter-ready package, full schema, adapter contract, managed worktree admissibility, dependency barrier, legacy compatibility, or field-level validation.
- Do not load `RESULT-PACKAGE.md` unless the prompt asks for result package expectations or returned evidence.
- Do not load `RUNTIME-ADAPTERS.md` unless runtime adapter, runtime capability, or selector behavior is in scope.
- Do not load `ROUTING-PROFILES.md` unless model/profile selection is material.
- Do not load `EXAMPLES.md` unless the user asks for examples or format ambiguity blocks output.
