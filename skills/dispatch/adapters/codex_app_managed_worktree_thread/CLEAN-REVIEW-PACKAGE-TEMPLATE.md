# Clean Review Package Template

Target Reader: Clean reviewers and read-only subagents reviewing completed managed worktree result packages from fresh context.
Reader Action Needed: Review only the supplied package, produce cited findings, and avoid edits or hidden-context assumptions.
Decision Supported: Whether the returned implementation package appears conformant, needs remediation, is blocked, or has missing evidence before downstream verify, triage, dispatch write task, human decision, or closeout.
Scope: Package-only clean review input shape for managed worktree child results and review packages.
Out of Scope: Child implementation self-review, reviewer file edits, runtime execution, final readiness, UAT/release approval, remote writes, commits, pushes, PRs, archive, or branch cleanup.
Evidence Level: Derived from PRD v0.3.3 FR-7 and managed worktree review/result package contracts.

Use this template when coordinator intake decides a completed managed worktree result or review package needs fresh-context clean review.

```yaml
clean_review_package:
  package_version: 1
  runtime_correlation_id: ""
  task_id: ""
  review_lens: "product | spec | code_quality | security | qa | contract | git_boundary | evidence"

  source:
    source_truth: ""
    acceptance_criteria: ""
    result_package: ""
    review_package: ""
    changed_files: []
    diff_or_findings_completeness: "complete | redacted_complete | redacted_partial | not_applicable"
    redacted_diff_or_detail: ""
    validation_evidence: ""
    checks_not_run: ""
    remaining_risks: []
    coordinator_intake_notes: ""

  context_rules:
    fresh_context_required: true
    parent_memory_allowed: false
    parent_thread_history_allowed: false
    parent_context_fork_allowed: false
    hidden_context_allowed: false
    supplied_artifacts_only: true
    cite_paths_or_package_sections: true

  allowed_actions:
    read_only: true
    file_edits_allowed: false
    spawn_more_agents_allowed: false
    nested_delegation_allowed: false
    runtime_execution_allowed: false
    remote_writes_allowed: false
    destructive_actions_allowed: false

  disallowed_claims:
    child_self_review_counts_as_clean_review: false
    forked_parent_context_counts_as_clean_review: false
    nested_delegation_counts_as_clean_review: false
    final_readiness_approval: false
    uat_or_release_approval: false
    merge_back_completed_without_evidence: false
    archive_completed_without_evidence: false
    branch_cleanup_completed_without_evidence: false
    commit_push_pr_or_remote_mutation_without_evidence: false

  output_required:
    output_type: review_findings
    severity_order: P0_P1_P2_P3
    verdict: "pass | needs_remediation | blocked | unverified"
    coverage:
      covered: []
      not_covered: []
      coverage_notes: ""
    required_sections:
      - scope_reviewed
      - findings
      - evidence_citations
      - missing_evidence
      - recommended_next_route
    recommended_next_route: "verify | triage | dispatch_write_task | human_decision | done"
```

## Reviewer Instructions

- Treat the package as the complete review context.
- Do not rely on parent thread memory, unstated prior decisions, or hidden local context.
- If the reviewer was spawned from a full parent-thread history fork, such as `fork_context=true` or an equivalent inherited-context mode, return `unverified` or `blocked`; do not report a clean review `pass`.
- Do not edit files. If a fix is needed, recommend `dispatch_write_task`.
- Do not spawn more agents unless a separate explicit delegation approves it.
- If unapproved nested agents or child threads were spawned, disclose that topology and return `unverified` or `blocked` for clean-review authority.
- Mark absent validation, redacted-but-needed diff detail, missing source truth, or unclear acceptance mapping as `unverified` or `blocked`.
- Cite package sections, file paths, commands, or supplied observations for each finding.
- Report coverage explicitly. `covered` must name the package areas actually reviewed; `not_covered` must name missing, redacted, unavailable, or intentionally skipped areas.
- Do not treat the child implementation self-review as clean review evidence.
- Do not claim final readiness, UAT, release, merge-back, archive, branch cleanup, commit, push, PR, or remote mutation unless the supplied package includes direct evidence.

## Package Completeness Check

Before reviewing substance, mark the package incomplete when any required item is missing:

- `task_id` or equivalent correlation;
- review lens;
- source truth;
- acceptance criteria;
- result package or review package;
- changed file list or explicit no-change statement;
- validation evidence or checks-not-run explanation;
- explicit fresh-context rules forbidding parent thread history forks;
- read-only allowed actions;
- explicit nested-delegation prohibition;
- output requirements.

Incomplete packages should return `blocked` or `unverified`, not `pass`.
