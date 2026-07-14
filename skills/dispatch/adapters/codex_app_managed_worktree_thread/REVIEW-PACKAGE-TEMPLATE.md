# Managed Worktree Review Package Template

Target Reader: child implementation threads returning evidence for coordinator clean review.
Reader Action Needed: return this package after implementation, validation, or blocker. Do not return `review_passed`.
Decision Supported: whether the coordinator can run clean review and route to `verify`, `triage`, `dispatch_write_task`, `human_decision`, or `done`.
Scope: one accepted write implementation package from a Codex-managed worktree child thread.
Out of Scope: clean-review approval, release/UAT readiness, remote writes, and claims not supported by child evidence.
Evidence Level: derived from Groundwork Result Package and managed-worktree review package contracts.

```text
Review package:
- Output type: review_package
- Outcome: ready_for_review | needs_remediation | blocked | human_decision
- Outcome rule: ready only when validation passed or is reviewably not applicable; if Goal Mode is required, runtime Goal Mode evidence is present.
- Child threads must not output review_passed.

Runtime:
- Runtime ID / Adapter: codex_app_managed_worktree_thread
- runtime_correlation_id:
- dispatch_id:
- runtime_identity.task_id:
- parent_thread_identifier:
- child_thread_identifier:
- initial_thread_title:
- current_thread_title:
- title_mutation_detected: true | false | unknown
- Thread title is display-only; correlate by Runtime Correlation ID.
- Worktree type: Codex-managed
- Worktree path if available, or unavailable:

Registry:
- Base ref:
- Branch:
- Artifact path:
- Owner skill: dispatch
- Thread status: result_returned | failed | blocked
- State event ref:
- Created at:
- Last checked at:

Runtime lifecycle:
- Status: result_returned | failed | blocked
- State: result_returned | failed | blocked
- Evidence:

Merge-source evidence:
- Source available: worktree_path | patch_bundle | branch_or_head | unavailable | not_applicable
- Source / evidence:
- Reliable source: yes | no | unknown
- Changed pathspecs:
- Blockers:

Review handoff:
- Fresh clean review required: yes | no
- Suggested reviewer context: fresh | not_required | unknown
- Evidence package complete: yes | no

Task:
- Dispatch version / ID / title:
- Task type: write_implementation
- Readiness: ready_for_agent
- Source link/path or redacted source identifier:
- Redacted self-contained source package:
- Acceptance criteria / checked:
- Non-goals:
- Base branch / commit:

Goal Contract evidence:
- Present:
- Outcome targeted:
- Source truth used:
- Acceptance criteria mapping:
- Verification followed:
- Constraints, iteration policy, stop/pause/risk gates:

Goal Mode evidence:
- Required:
- Goal command first line:
- Lint passed before delivery:
- Runtime evidence: present | absent | unavailable | unknown
- Evidence:
- Failure action: none | corrective_resend | blocked | needs_remediation

Selector enforcement:
- Requested model profile / reasoning / cost-latency bias:
- Enforcement status: tool_enforced | prompt_preference | unavailable | unknown
- Evidence:

Changes:
- Changed files:
- Diff summary / base:
- Diff completeness: complete | redacted_complete | redacted_partial | not_applicable
- Completeness assertion:
- Redacted patch/detail with reviewable context:
- Omitted hunks and why safe:

Validation:
- Applicability:
- Skipped category/reason:
- Commands run:
- Results:
- Redacted relevant output:
- Checks not run and reason:

Risk and route:
- Remaining risks:
- Blockers:
- Recommended next route: verify | triage | dispatch_write_task | human_decision | done
```

## Hard Stops

- Missing runtime Goal Mode evidence when required => `blocked` or `needs_remediation`, not `ready_for_review`.
- `result_returned` is not review pass, merge, or archive-ready evidence. Those are independent coordinator-owned axes.
- Registry fields must match thread lifecycle state and cite the artifact/log event for the latest transition.
- Report merge-source evidence only. Do not claim main-worktree application or post-merge validation from the child package.
- Do not make archive or branch-cleanup recommendations from the child package.
- Child packages must not mark clean review passed.
- `low_risk_coordinator_intake` is not clean-review evidence and must not set clean review passed.
- Child packages must not recommend `merge_back`, `archive`, `branch_cleanup`, or `retain` as runtime lifecycle actions; those are coordinator decisions after review and closeout evidence.
- Older v0.3.2 packages remain readable. Missing runtime identity, Goal Mode, merge-source, thread-state, or evidence-package fields route to `needs_remediation`, `blocked`, or `human_decision`.
