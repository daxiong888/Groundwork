# Native Managed Worktree Closeout Package Template

Target Reader: Groundwork coordinators, runtime adapter authors, clean reviewers, and maintainers deciding merge readiness and cleanup actions for one returned Codex-native worktree or handoff result.
Reader Action Needed: Fill this package after review/result package intake and before recommending merge, thread archive, worktree retention, or branch cleanup.
Decision Supported: Whether the task result may merge, must hold, should route to human decision, and which cleanup decisions are separately supported by evidence.
Artifact Type: closeout package template
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md` FR-404/AC-404, V040-005 in `artifacts/v0.4.0-codex-native-worktree-handoff/issue-map.md`, and the V040-001 compatibility map.
Scope: Native closeout schema, merge gates, git-boundary evidence, review status evidence, merge-source evidence, cleanup decision separation, and legacy v0.3.3 field mapping.
Out of Scope: Automatic archive execution, worktree deletion, branch deletion execution, remote writes, commits, pushes, PR creation, tracker mutation, runtime execution, cache refresh, release readiness, UAT readiness, and final acceptance.
Evidence Level: Local schema and contract evidence only. A completed archive, deleted branch, cleaned worktree, runtime execution, cache refresh, release readiness, or UAT readiness requires separate cited evidence.
Safe to Share / Redaction Notes: Safe to share as a schema template. Do not copy secrets, credentials, private URLs, browser cookies, PII, raw logs, private request payloads, or long diffs into package instances.

## Creation Rule

Create the native closeout package after review/result package intake, not before. A closeout package may recommend merge or cleanup actions only when the required evidence is present. It must not claim that archive, worktree cleanup, branch deletion, runtime execution, cache refresh, release, or UAT readiness occurred unless separate evidence proves that action.

## Required Shape

```yaml
native_closeout_package:
  runtime_correlation_id: ""
  task_id: ""
  runtime_id: "codex_app_managed_worktree_thread"
  owner_skill: "dispatch"

  task_verdict: done | partial | blocked | abandoned
  verdict_reason: ""

  evidence_summary: []

  git_boundary_status:
    status_checked: true | false
    intended_files: []
    unrelated_dirty_files: []
    staged_files: []
    explicit_denylist: []
    safe_to_stage_or_merge: true | false

  review_findings_status: passed | findings_open | not_run | not_required

  merge_decision:
    recommendation: merge | do_not_merge | hold | not_applicable | human_decision
    reason: ""
    merge_source: patch_bundle | visible_branch | codex_handoff | pathspec_checkout | none | unknown
    source_evidence: []

  cleanup_decision:
    thread_action: archive_thread | retain_thread | human_decision | not_applicable
    thread_evidence: []
    worktree_action: retain_worktree | allow_codex_managed_cleanup | human_decision | not_applicable
    worktree_evidence: []
    branch_action: delete_local_branch | retain_branch | human_decision | not_applicable
    branch_evidence: []

  blockers: []
  next_route: verify | triage | handoff | done | human_decision
```

## Merge Decision Rules

- `merge_decision.recommendation: merge` requires non-empty `evidence_summary`.
- `merge_decision.recommendation: merge` requires `git_boundary_status.status_checked: true`.
- `merge_decision.recommendation: merge` requires `git_boundary_status.safe_to_stage_or_merge: true`.
- `merge_decision.recommendation: merge` requires `review_findings_status: passed`.
- `merge_decision.recommendation: merge` requires a known merge source: `patch_bundle`, `visible_branch`, `codex_handoff`, or `pathspec_checkout`.
- `merge_decision.recommendation: merge` is blocked when `merge_decision.merge_source` is `none`, `unknown`, empty, missing, or not backed by `source_evidence`.
- `merge_decision.recommendation: merge` is blocked when intended files, unrelated dirty files, staged files, or explicit denylist evidence is missing from `git_boundary_status`.
- If any merge gate is missing or unsafe, use `do_not_merge`, `hold`, or `human_decision`, name the blocker, and set `next_route` to `verify`, `triage`, or `human_decision`.
- `review_findings_status: not_required` does not satisfy merge readiness for a write result. Use `not_applicable` when there is no result to merge.

## Cleanup Decision Rules

- Cleanup decisions are separate from merge decisions. Thread archive, worktree retention, Codex-managed cleanup, and branch cleanup must never appear as merge recommendations.
- `cleanup_decision.thread_action: archive_thread` is a recommended next action, not evidence that the thread was archived. A completed archive claim requires separate Codex runtime or user-supplied evidence.
- `cleanup_decision.worktree_action: allow_codex_managed_cleanup` is permission to let native Codex retention/cleanup semantics apply, not evidence that a worktree was deleted.
- `cleanup_decision.worktree_action: retain_worktree` means the worktree should remain available for review, remediation, merge-back, audit, or human inspection.
- `cleanup_decision.branch_action: delete_local_branch` requires branch identity, merge/discard status, protected/default/base branch checks, worktree status evidence, and approval evidence from `BRANCH-CLEANUP-CHECKLIST.md`.
- Unknown branch state must use `cleanup_decision.branch_action: human_decision` or `retain_branch`, not `delete_local_branch`.
- Remote branch deletion, force deletion, protected/default branch handling, and unknown ownership remain outside native closeout automation and require explicit human approval.
- Cleanup actions must not claim release readiness, UAT readiness, runtime execution, or cache/source equivalence.

## Legacy Compatibility Mapping

The fields below are legacy v0.3.3 compatibility fields. Do not populate them inside `native_closeout_package` except when reading or mapping an older package.

| Legacy or deprecated field | Native target | Rule |
| --- | --- | --- |
| `closeout_package` | `native_closeout_package` | Deprecated package root for v0.4.0 native closeout. |
| `lifecycle.current_state` | `task_verdict`, `blockers`, `next_route` | Deprecated Groundwork-owned progression. Keep only as compatibility evidence when reading old packages. |
| `lifecycle.closeout_decision` | `merge_decision` plus `cleanup_decision` | Deprecated broad decision. Split merge readiness from cleanup actions. |
| `archive_ready` | `cleanup_decision.thread_action` plus evidence | Legacy readiness flag. It does not prove archive execution. |
| `branch_cleanup_required` | `cleanup_decision.branch_action` | Legacy route hint. Map only after branch evidence is inspected. |
| `merge_recommendation` | `merge_decision.recommendation` | Legacy/deprecated. Native packages must not use it. |
| `cleanup_action` | `cleanup_decision.thread_action`, `cleanup_decision.worktree_action`, `cleanup_decision.branch_action` | Legacy/deprecated. Native packages must split cleanup by action type. |

## Preservation Requirements

Before recommending merge or cleanup, the package must state:

- task verdict and verdict reason;
- evidence summary and source references;
- git boundary status, including intended files, unrelated dirty files, staged files, explicit denylist, and safe-to-stage-or-merge result;
- review findings status and review evidence;
- merge source and source evidence, or the blocker that prevents merge;
- cleanup evidence for thread, worktree, and branch actions separately;
- blockers, open risks, and next route;
- why any missing evidence does not block the selected non-merge cleanup action, or the blocker that prevents cleanup.

## Eval Hooks

Native closeout evals should reject:

- `merge_decision.recommendation: merge` with empty or missing `evidence_summary`;
- `merge_decision.recommendation: merge` when `git_boundary_status.status_checked` is false or missing;
- `merge_decision.recommendation: merge` when `git_boundary_status.safe_to_stage_or_merge` is not true;
- `merge_decision.recommendation: merge` when `review_findings_status` is not `passed`;
- `merge_decision.recommendation: merge` when `merge_decision.merge_source` is `none`, `unknown`, empty, or missing;
- packages that put archive, worktree retention, Codex-managed cleanup, or branch cleanup under merge decision fields;
- packages that claim archive, worktree cleanup, branch deletion, runtime execution, cache refresh, release readiness, or UAT readiness without separate evidence;
- native packages that retain `merge_recommendation` or `cleanup_action` without marking those fields legacy/deprecated.
