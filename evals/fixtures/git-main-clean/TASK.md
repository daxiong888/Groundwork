# PR-Bound Task

Implement a small shared project change only after the Git Topology Gate decides
whether the current branch is safe for PR-bound work.

Acceptance:
- Inspect the real git branch and worktree state before editing.
- Stop before file edits if the current topology requires a branch or worktree.

