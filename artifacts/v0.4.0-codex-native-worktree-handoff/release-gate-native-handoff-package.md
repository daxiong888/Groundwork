# v0.4.0 Release Gate Native Handoff Package

Target Reader: Groundwork release coordinators and Codex App Handoff trial subjects.
Reader Action Needed: Use this package path during the strict v0.4.0 Local to Worktree and Worktree to Local Handoff trial.
Decision Supported: Whether the release-gate Handoff trial used a Groundwork `native_handoff_package` path instead of a direct mechanics-only handoff.
Artifact Type: release-gate native handoff package
Source of Truth: `docs/prd-v0.4.0-codex-native-worktree-handoff-alignment.md`, `skills/handoff/REVIEW-PACKAGE.md`, and `artifacts/v0.4.0-codex-native-worktree-handoff/release-evidence-plan.md`.
Scope: One strict release-gate handoff trial using a real package path for Local to Worktree and Worktree to Local movement.
Out of Scope: Editing production code, committing from the trial subject thread, pushing, creating tags or GitHub releases, UAT readiness, marketplace publishing, and claiming Groundwork executed Codex App Handoff.
Evidence Level: Pre-trial package. Codex App Handoff operation evidence must be recorded separately after the trial.
Safe to Share / Redaction Notes: Use symbolic roots such as `$SOURCE_ROOT`, `$CODEX_WORKTREE_ROOT`, and `$INSTALLED_PLUGIN_ROOT`; redact raw thread ids, operation ids, and local-only paths before committing evidence.

## Native Handoff Package: Local to Worktree

- Direction: local_to_worktree
- Goal: Verify that a v0.4.0 release-gate trial can hand a local Groundwork release candidate to a Codex-managed worktree while using this package path.
- Scope: Read-only trial subject confirms package visibility, cwd, git head, and git status after Handoff.
- Out Of Scope: File edits, commits, pushes, tag creation, release creation, archive cleanup, UAT, and marketplace publishing.
- Base: `main` at the current v0.4.0 release-prep commit.
- Native Context: Codex App Handoff operation evidence will be collected by the coordinator.
- Thread Ref: redacted_before_trial
- Thread Ref Availability: unavailable_before_handoff
- Worktree Path: redacted_before_trial
- Worktree Path Availability: unavailable_before_handoff
- Worktree Association: redacted_before_trial
- Worktree Association Availability: unavailable_before_handoff
- Route Decision Ref: `docs/runtime-dispatch-workflow.md` v0.4.0 release gate checklist.
- Relevant Artifacts:
  - `artifacts/v0.4.0-codex-native-worktree-handoff/release-gate-native-handoff-package.md`
  - `artifacts/v0.4.0-codex-native-worktree-handoff/release-evidence-plan.md`
  - `evals/baselines/2026-06-18-v0.4.0-codex-app-handoff-trial.md`
- Changed Files: none expected from the trial subject.
- Evidence: pending Codex App `handoff_thread` and `get_handoff_status` results.
- Open Risks:
  - Handoff operation may fail or return incomplete native context.
  - The trial validates local Codex App Handoff mechanics only, not UAT or marketplace publishing.
- Next Command: Coordinator invokes Codex App Handoff for the trial subject thread.
- Stop Condition: Trial subject reports cwd, git HEAD, `git status --short`, and package-path visibility from the worktree context.
- Redaction Notes: Redact raw thread ids, operation ids, and local-only paths in committed evidence.

## Native Handoff Package: Worktree to Local

- Direction: worktree_to_local
- Goal: Verify that the same v0.4.0 release-gate trial can return from Codex-managed worktree context to local context while preserving the package-path evidence boundary.
- Scope: Read-only trial subject confirms package visibility, cwd, git head, and git status after return Handoff.
- Out Of Scope: File edits, commits, pushes, tag creation, release creation, archive cleanup, UAT, and marketplace publishing.
- Base: Worktree context produced by the Local to Worktree Handoff operation.
- Native Context: Codex App Handoff operation evidence will be collected by the coordinator.
- Thread Ref: redacted_before_trial
- Thread Ref Availability: unavailable_before_handoff
- Worktree Path: redacted_before_trial
- Worktree Path Availability: unavailable_before_handoff
- Worktree Association: redacted_before_trial
- Worktree Association Availability: unavailable_before_handoff
- Route Decision Ref: `docs/runtime-dispatch-workflow.md` v0.4.0 release gate checklist.
- Relevant Artifacts:
  - `artifacts/v0.4.0-codex-native-worktree-handoff/release-gate-native-handoff-package.md`
  - `artifacts/v0.4.0-codex-native-worktree-handoff/release-evidence-plan.md`
  - `evals/baselines/2026-06-18-v0.4.0-codex-app-handoff-trial.md`
- Changed Files: none expected from the trial subject.
- Evidence: pending Codex App `handoff_thread` and `get_handoff_status` results.
- Open Risks:
  - Return Handoff may fail or return incomplete native context.
  - The trial validates local Codex App Handoff mechanics only, not UAT or marketplace publishing.
- Next Command: Coordinator invokes Codex App Handoff again for the trial subject thread after the Local to Worktree trial succeeds.
- Stop Condition: Trial subject reports cwd, git HEAD, `git status --short`, and package-path visibility from the returned local context.
- Redaction Notes: Redact raw thread ids, operation ids, and local-only paths in committed evidence.
