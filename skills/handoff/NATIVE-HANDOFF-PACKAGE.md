# Native Handoff Package

Target Reader: Codex preparing Local-to-Worktree or Worktree-to-Local continuation.
Reader Action Needed: Produce a compact native handoff package without claiming Groundwork executes official Codex Handoff or native Git operations.
Decision Supported: Whether a future session has enough explicit native context, evidence, changed-file boundary, risks, and stop condition to continue.
Artifact Type: branch-specific handoff reference
Source of Truth: `skills/handoff/SKILL.md`, `skills/handoff/REVIEW-PACKAGE.md`, and Codex-native handoff boundary rules.
Scope: Native handoff schema, availability markers, changed-file boundary, evidence, and redaction rules.
Out of Scope: Creating Codex worktrees, moving threads, staging, committing, pushing, archiving, or performing official Codex Handoff.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share after redacting secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows.

## Required Shape

```yaml
native_handoff_package:
  direction: local_to_worktree | worktree_to_local
  goal: ""
  scope: []
  out_of_scope: []
  base:
    base_ref: ""
    base_commit: ""
    branch: ""
  native_context:
    thread_ref:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
    worktree_path:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
    worktree_association:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
  route_decision_ref: ""
  relevant_artifacts: []
  changed_files: []
  evidence:
    commands_run: []
    checks_passed: []
    checks_failed: []
    not_run: []
  open_risks: []
  next_command: ""
  stop_condition: ""
  redaction_notes: ""
```

## Rules

- The package must be self-contained enough for a new session to continue without hidden parent-session history.
- Cite canonical artifacts instead of copying full PRDs, full issue bodies, long diffs, logs, or transcripts.
- `native_context.thread_ref`, `native_context.worktree_path`, and `native_context.worktree_association` must always include explicit `availability` values.
- Local-to-Worktree packages prepared before Codex creates or exposes the native worktree must set `native_context.worktree_path.availability: unavailable_before_handoff`; do not invent a future path, native ID, or thread reference.
- Worktree-to-Local packages must include `changed_files`, `evidence`, `open_risks`, `stop_condition`, and all `native_context` fields before closeout.
- If visible native context exists, record it with `availability: visible`; if hidden in the current surface, mark it `unavailable_in_current_surface`; if intentionally withheld, mark it `redacted`.
- Worktree-to-Local `changed_files` must list the returned file boundary. If no files changed, include an explicit empty list plus evidence that no files changed.
- Always state `redaction_notes`, even when no sensitive data was present.
- Never instruct a future reader to use `git add .`; use explicit pathspecs and denylist guidance when staging or commit continuation is in scope.

## Boundary

Groundwork prepares this package only. Official Codex Handoff owns moving the thread and code between Local and Worktree and owns Git operations performed by that native flow. Do not claim the native operation happened unless direct runtime/tool evidence is named.
