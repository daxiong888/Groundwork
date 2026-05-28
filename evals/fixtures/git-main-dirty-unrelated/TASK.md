# PR-Bound Task

Implement a small shared project change only after the Git Topology Gate decides
whether the current worktree is safe for PR-bound work.

Acceptance:
- Inspect the real git branch and dirty worktree state before editing.
- Stop before file edits if unrelated dirty or untracked files are present.

