# Git Topology Gate

Target Reader: Groundwork skills that may write files, commit, push, create PRs, close issues, or deliver PR-bound implementation work.
Reader Action Needed: Decide whether the current git topology is safe before writing or mutating remote state.
Decision Supported: Whether to continue on the current branch, create a feature branch, create a worktree, stop, or ask for explicit approval.
Scope: Pre-write branch/worktree decisions, dirty-worktree handling, PR-bound implementation, pathspec commits, and pre-remote safety gates.
Out of Scope: Full git training, branch naming policy beyond safe defaults, tracker API integration, automatic PR creation, and automatic pushes.
Evidence Level: Based on observed Groundwork session failure where implementation proceeded on `main` and later pushed `main` instead of producing a PR.
Related Issues: #29, #28, #33.

## Core Rule

Follow the user's explicit branch/current-directory instruction over this skill's topology defaults, subject to higher-priority instructions and host permissions. Do not create or switch branches or worktrees against that instruction. Inspect relevant diffs and preserve unrelated changes; stop only affected edits when safe separation is impossible. Without an explicit user topology instruction, PR-bound implementation on `main` / `master` / `trunk`, an empty branch name, or detached `HEAD` needs a branch/worktree decision before edits. Local preparation does not authorize commit, push, PR creation, or deployment.

This gate runs before file writes and again before commit, push, PR, or remote issue closeout.

## Definitions

### PR-bound implementation

A task is PR-bound when at least one is true:

- the user expects a PR;
- the accepted task or applicable project instructions require a PR for delivery or issue closeout.

Editing shared files, preparing a user-visible change locally, or asking for review does not by itself imply PR delivery.

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

Honor an explicit user topology instruction first. Otherwise use these defaults:

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
  -> current_branch_ok only when preceding PR-bound topology requirements are satisfied and scoped edits can preserve unrelated changes; otherwise worktree_required or blocked

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

Consider a worktree when unrelated changes cannot be safely separated or concurrent issue streams need isolation. Honor explicit current-directory instructions; if they leave an actual write conflict, report that conflict instead of creating a worktree or stopping unrelated safe work.

Suggested shape:

```bash
git worktree add ../<repo>-<workstream-slug> -b codex/<workstream-slug>
```

Do not move, stash, discard, or overwrite user changes without explicit approval.

## Pre-remote Gate

Before `push`, `pull --rebase`, PR creation, issue closeout, release tagging, or tracker mutation, check existing authorization for the concrete target, scope, and risk. Show this block only when permission is still required; do not ask again for unchanged authorized work:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
```

Existing authorization never permits overwriting unrelated changes or bypassing host permissions. Block these by default:

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

The PR-delivery examples below assume that the user authorized those git/remote actions and did not request a different topology. They do not grant that authorization.

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

### Right when unrelated changes require isolation

On `main` with unrelated changes that cannot safely share the checkout, propose a worktree; create it only with authorization and write only scoped files there.

For “edit here; no worktree, branch change, commit, or push”, inspect relevant diffs, preserve unrelated changes, edit/check only authorized files here when safe, and report local evidence.
