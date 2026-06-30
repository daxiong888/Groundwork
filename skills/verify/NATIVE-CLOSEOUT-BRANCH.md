# Native Closeout Branch

Target Reader: Codex running `verify` for `native_closeout_package`, merge readiness, cleanup separation, or closeout git-boundary claims.
Reader Action Needed: Check merge readiness and cleanup decisions as separate evidence-backed claims after the required scope block.
Decision Supported: Whether a native closeout package can support merge, hold, cleanup recommendation, or blocked/human-decision status.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/dispatch/adapters/codex_app_managed_worktree_thread/CLOSEOUT-PACKAGE-TEMPLATE.md`, `skills/dispatch/adapters/codex_app_managed_worktree_thread/BRANCH-CLEANUP-CHECKLIST.md`, and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`.
Scope: Native closeout merge gates, git-boundary evidence, merge-source evidence, clean-review status, same-base serialization, and cleanup action separation.
Out of Scope: Performing merge-back, archiving threads, deleting branches, cleaning worktrees, refreshing plugin cache, approving release/UAT, or executing Codex App cleanup.
Evidence Level: Source-validation policy only unless a closeout package includes separately named runtime, git, branch, archive, or cleanup execution evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required References

- Load `SCOPE-EVIDENCE-TEMPLATE.md` first.
- Load `skills/dispatch/adapters/codex_app_managed_worktree_thread/CLOSEOUT-PACKAGE-TEMPLATE.md` for native closeout package fields and merge blockers.
- Load `skills/dispatch/adapters/codex_app_managed_worktree_thread/BRANCH-CLEANUP-CHECKLIST.md` when branch cleanup is in scope.
- Load `RELEASE-READINESS-BRANCH.md` only when the closeout claim also asserts runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh readiness.

## Merge Readiness Rules

When verifying a `native_closeout_package`, treat merge readiness and cleanup decisions as separate claims:

- reject or mark blocked any `merge_decision.recommendation: merge` when `evidence_summary` is empty or missing;
- reject or mark blocked any merge recommendation when `git_boundary_status.status_checked` is not true or `safe_to_stage_or_merge` is not true;
- reject or mark blocked any merge recommendation when intended files, unrelated dirty files, staged files, or explicit denylist evidence is missing from `git_boundary_status`;
- reject or mark blocked any merge recommendation when `review_findings_status` is not `passed`;
- reject or mark blocked any merge recommendation when `merge_decision.merge_source` is `none`, `unknown`, empty, missing, or lacks source evidence;
- reject or mark blocked any merge recommendation when same-base serialization evidence is missing, unknown, or shows another same-base closeout in progress without queue or lock evidence;
- verify that `merge_decision.merge_source` uses only `patch_bundle`, `visible_branch`, `codex_handoff`, `pathspec_checkout`, `none`, or `unknown`.

## Cleanup Separation Rules

- Verify that `cleanup_decision.thread_action`, `cleanup_decision.worktree_action`, and `cleanup_decision.branch_action` remain separate from `merge_decision`.
- Do not treat archive, worktree retention, Codex-managed cleanup permission, or branch cleanup as merge readiness evidence.
- Do not claim thread archive, worktree cleanup, branch deletion, runtime execution, cache refresh, release readiness, or UAT readiness unless the package includes direct evidence for that specific claim.
- Remote branch deletion, destructive cleanup, or force deletion still requires explicit approval and separate execution evidence.
