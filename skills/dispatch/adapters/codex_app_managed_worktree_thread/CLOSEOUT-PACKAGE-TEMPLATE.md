# Native Managed Worktree Closeout Package Template

Target Reader: Groundwork coordinators, runtime adapter authors, clean reviewers, and maintainers deciding merge readiness and cleanup actions for one returned Codex-native worktree or handoff result.
Reader Action Needed: Fill this package after review/result package intake and before recommending merge, thread archive, worktree retention, or branch cleanup.
Decision Supported: Whether the task result may merge, must hold, should route to human decision, and which cleanup decisions are separately supported by evidence.
Artifact Type: closeout package template
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-404/AC-404, V040-005, and v0.3.3 compatibility mapping.
Scope: Native closeout schema, merge gates, git-boundary evidence, review status, merge-source evidence, cleanup decision separation, and legacy field mapping.
Out of Scope: Automatic archive execution, worktree deletion, branch deletion, remote writes, commits, pushes, PR creation, tracker mutation, runtime execution, cache refresh, release readiness, UAT readiness, and final acceptance.
Evidence Level: Local schema and contract evidence only. Completed archive, cleanup, runtime execution, cache refresh, release, or UAT claims require separate evidence.
Safe to Share / Redaction Notes: Safe to share as a schema template. Do not copy secrets, credentials, private URLs, cookies, PII, raw logs, request payloads, or long diffs.

## Creation Rule

Create closeout only after review/result intake. A closeout package may recommend merge or cleanup only when evidence is present. It must not claim archive, cleanup, branch deletion, runtime execution, cache refresh, release, or UAT readiness occurred without separate evidence.

## Required Shape

```yaml
native_closeout_package:
  runtime_correlation_id: ""
  task_id: ""
  runtime_id: codex_app_managed_worktree_thread
  owner_skill: dispatch
  input_result_outcome: ready_for_review | needs_remediation | blocked | human_decision | no_execution_needed
  evidence_summary: []
  init_resolution_status: {status, resolution_source, pending_worktree_id, child_thread_identifier, worktree_path, parent_thread_implementation_attempted, manual_fallback_attempted, fallback_approval_evidence}
  git_boundary_status: {status_checked, intended_files, unrelated_dirty_files, staged_files, explicit_denylist, safe_to_stage_or_merge}
  review: {kind, required, status, reviewer_context, reviewed_material_change_id, findings, evidence}
  review_loop: {status, latest_material_change_id, previous_review_stale_reason, findings_addressed, next_review_required, next_route}
  same_base_serialization: {base_ref, base_commit, same_base_closeout_in_progress, queue_or_lock_required, queue_or_lock_evidence, serialized_or_blocked}
  merge_back: {status, recommendation, reason, merge_source, source_evidence}
  archive: {status, recommendation: archive_thread | retain_thread | human_decision | not_applicable, evidence}
  worktree_cleanup: {status, recommendation: retain_worktree | allow_codex_managed_cleanup | human_decision | not_applicable, evidence}
  branch_cleanup: {status, recommendation: delete_local_branch | retain_branch | human_decision | not_applicable, evidence}
  blockers: []
  next_route: clean_reviewer | dispatch_write_task | verify | triage | handoff | done | human_decision
```

## Merge Gate

`merge_back.recommendation: merge` requires all of:

- non-empty `evidence_summary`;
- init status `resolved` or `not_applicable`; pending/failed/blocked/human-decision init blocks merge;
- normal managed worktree resolution source or explicitly approved topology change with approval and merge-source evidence;
- `git_boundary_status.status_checked: true`, intended files, unrelated dirty files, staged files, denylist, and `safe_to_stage_or_merge: true`;
- `review.kind: clean`, `review.required: true`, and `review.status: passed`, with non-empty `reviewer_context` and evidence naming a fresh read-only independent reviewer;
- non-empty `review.reviewed_material_change_id` equal to `review_loop.latest_material_change_id`;
- `review_loop.status: clean_review_passed` and `review_loop.next_review_required: false`;
- known merge source: `patch_bundle`, `visible_branch`, `codex_handoff`, or `pathspec_checkout`, backed by `source_evidence`;
- same-base serialization evidence: base ref/commit, whether same-base closeout is in progress, and queue/lock evidence when needed.

If any gate is missing or unsafe, use `do_not_merge`, `hold`, or `human_decision`, name the blocker, and route to `clean_reviewer`, `dispatch_write_task`, `verify`, `triage`, or `human_decision` as appropriate. Coordinator intake, self-review, stale review evidence, mismatched material-change ids, `review_loop.next_review_required: true`, and `review.status: not_required` do not satisfy write-result merge readiness.

## Cleanup Gate

Archive, worktree cleanup, and branch cleanup are separate from merge and from each other. Each records its own status, recommendation, and evidence.

- `pendingWorktreeId` is pending init evidence only, not merge or cleanup evidence.
- Manual git worktree fallback is not Codex-managed worktree evidence. Disclose it, exclude its changes from merge evidence, and route to `human_decision` unless explicit user approval accepts the topology.
- `archive.recommendation: archive_thread` and `worktree_cleanup.recommendation: allow_codex_managed_cleanup` are recommendations/permissions, not completed-action evidence.
- `delete_local_branch` requires branch identity, merge/discard status, protected/default/base branch checks, worktree status evidence, and approval evidence from `BRANCH-CLEANUP-CHECKLIST.md`.
- Unknown branch state uses `human_decision` or `retain_branch`; remote deletion, force deletion, protected/default branch handling, and unknown ownership require explicit human approval.
- Cleanup actions must not claim release readiness, UAT readiness, runtime execution, or cache/source equivalence.

## Legacy Compatibility Mapping

| Legacy field | Native target | Rule |
| --- | --- | --- |
| `closeout_package` | `native_closeout_package` | Deprecated root. |
| `result_package.status` | `input_result_outcome` | Intake-only mapping to the canonical outcome enum. |
| `lifecycle.current_state` | Result `runtime_lifecycle` plus `blockers` | Compatibility evidence only; never carries review/merge/archive/cleanup state. |
| `lifecycle.closeout_decision` | `merge_back`, `archive`, `worktree_cleanup`, and `branch_cleanup` | Split every decision axis. |
| `archive_ready` | `archive.status` plus evidence | Does not prove archive execution. |
| `branch_cleanup_required` | `branch_cleanup.recommendation` | Map only after branch evidence is inspected. |
| `merge_recommendation` | `merge_back.recommendation` | Native packages must not use this broad field. |
| `cleanup_action` | `archive`, `worktree_cleanup`, and `branch_cleanup` | Native packages must split cleanup by action type. |
| `serial_closeout` | `same_base_serialization` | Preserve queue/lock evidence before merge readiness. |

## Runtime Init Mapping

| Result init status | Closeout status | Resolution source | Rule |
| --- | --- | --- | --- |
| `not_started` | `not_applicable` or `blocked` | `not_applicable` | Use `not_applicable` only when no managed worktree was required. |
| `pending` | `pending` | `not_applicable` | Pending ids are wait/poll evidence only. |
| `child_thread_created` | `resolved` | `codex_managed_worktree` | Requires child thread identifier and worktree path. |
| `failed` / `blocked` | `failed`, `blocked`, or `human_decision` | `not_applicable` | Match retained failure evidence and decision need. |
| approved fallback topology | `resolved` | `approved_topology_change` | Requires explicit approval plus merge-source evidence. |

## Regression Boundaries

Reject closeout packages that merge without required evidence, combine independent axes, claim archive/cleanup/runtime/cache/release/UAT completion without separate evidence, retain broad legacy fields as native fields, treat pending worktree ids as resolved, or use a manual fallback without explicit approval.
