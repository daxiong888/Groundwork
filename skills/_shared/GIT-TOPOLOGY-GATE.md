# Git Topology Gate

Target Reader: Groundwork skills that may write files, commit, push, create PRs, close issues, or deliver PR-bound implementation work.
Reader Action Needed: Decide whether the current git topology is safe before writing or mutating remote state.
Decision Supported: Whether to continue on the current branch, create a feature branch, create a worktree, stop, or ask for explicit approval.
Scope: Pre-write branch/worktree decisions, dirty-worktree handling, PR-bound implementation, pathspec commits, and pre-remote safety gates.
Out of Scope: Full git training, branch naming policy beyond safe defaults, tracker API integration, automatic PR creation, and automatic pushes.
Evidence Level: Based on observed Groundwork session failure where implementation proceeded on `main` and later pushed `main` instead of producing a PR.
Related Issues: #29, #28, #33.

## Core Rule

PR-bound implementation must not start writing files on `main` / `master` / `trunk`, an empty branch name, or detached `HEAD` until Groundwork has made an explicit branch or worktree decision.

This gate runs before file writes and again before commit, push, PR, or remote issue closeout.

## Definitions

### PR-bound implementation

A task is PR-bound when at least one is true:

- the user expects a PR;
- there is a GitHub/GitLab/Linear/Jira issue or task to close;
- the work needs multiple commits or reviewable delivery;
- the work changes shared project files;
- the task is part of a release, UAT, customer-visible change, or multi-session workstream;
- the user asks to push, create PR, close an issue, or deliver code.

### Unrelated dirty files

Dirty files are unrelated when they are outside the current task scope, pre-existing user changes, generated runtime files, historical edits, local notes, caches, temporary tests, or anything the agent cannot explain as part of the current acceptance criteria.

## Pre-write Gate

Before writing files for implementation or delivery, inspect:

```bash
git branch --show-current
git symbolic-ref --short HEAD || true
git status --short
git diff --name-only
git diff --cached --name-only
```

Then decide:

```text
current branch is main/master/trunk + PR-bound implementation
  -> branch_required or worktree_required before edits

branch name is empty or HEAD is detached + PR-bound implementation
  -> branch_required before edits when clean, or worktree_required/blocked when dirty or unsafe

clean worktree + single scoped task
  -> feature branch is acceptable

dirty worktree + all dirty files belong to current task
  -> feature branch is acceptable only after listing dirty files

dirty worktree + unrelated files
  -> worktree_required or blocked

multiple issues / multiple PRs / long-running workstream
  -> prefer worktree
```

## Branch Decision

Use a short, stable branch name:

```text
codex/<feature-or-workstream-slug>
```

Acceptable example:

```bash
git switch -c codex/lifecycle-preflight-gates
```

Only do this when the worktree is clean or the dirty files are listed and all belong to the current task.

## Worktree Decision

Use worktree when unrelated dirty files exist, the task is long-running, or multiple issue streams should stay isolated.

Suggested shape:

```bash
git worktree add ../<repo>-<workstream-slug> -b codex/<workstream-slug>
```

Do not move, stash, discard, or overwrite user changes without explicit approval.

## Pre-remote Gate

Before `push`, `pull --rebase`, PR creation, issue closeout, release tagging, or tracker mutation, show:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
```

Block these by default:

- `git push origin main`;
- direct `main` delivery for PR-bound implementation;
- PR-bound remote mutation from an empty branch name or detached `HEAD`;
- remote issue closeout when no PR can be linked;
- `git add .`;
- destructive git commands such as `reset --hard`, `clean -fd`, or force push;
- committing unrelated dirty files;
- committing ignored runtime scratch such as `.groundwork/runs`, `.groundwork/harness`, `.groundwork/tmp`, `.planning`, or `.gsd`.

## Commit Boundary

Use pathspec commits only:

```bash
git add -- path/to/file-a path/to/file-b
git commit -m "..."
```

Before commit, report:

```text
Allowed files:
Changed files:
Staged files:
Untracked files:
Ignored/runtime files checked:
```

Do not use `git add .` for Groundwork-managed implementation.

## Lifecycle State Integration

This gate is not lifecycle state.

Write branch/worktree details into `artifacts/<workstream-slug>/STATE.md` only when the lifecycle-state threshold is met, for example cross-session continuation, open verification gap, release/UAT checkpoint, or pending human decision.

When written, keep it short:

```text
Canonical Sources:
- GitHub issue #...
- branch codex/...

Open Risks:
- main has unrelated dirty files; continue in worktree ...

Next Skill:
- implement / verify / handoff

Stop Condition:
- stop before push unless PR branch is confirmed
```

## Failure Examples

### Wrong

```text
current branch: main
write files
commit to main
push origin main
close issues manually
```

### Wrong from detached HEAD

```text
current branch:
write files
commit detached HEAD
push origin main
close issues manually
```

### Right

```text
current branch: main
PR-bound task detected
clean worktree confirmed
create codex/<slug>
write scoped files
verify
pathspec commit
push feature branch
create PR with linked issues
```

### Right from detached HEAD

```text
current branch:
detached HEAD confirmed
PR-bound task detected
clean worktree confirmed
create codex/<slug> branch from current HEAD
write scoped files
verify
pathspec commit
push feature branch only after approval gate
create PR with linked issues
```

### Right when dirty unrelated files exist

```text
current branch: main
dirty unrelated files detected
recommend worktree
create codex/<slug> worktree
write only scoped files there
```
