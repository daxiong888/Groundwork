# Git Boundary Checklist

Target Reader: Codex running Groundwork skills that touch commits, staging, handoff, or git-scope review.
Reader Action Needed: Keep commits and handoffs scoped to intended files only.
Decision Supported: Whether it is safe to stage, commit, or summarize git state without mixing unrelated work.
Scope: Local git status, staging, commit boundary, ignored runtime directories, and unrelated change reporting.
Out of Scope: Remote push, PR creation, history rewrite, force push, or destructive cleanup.
Evidence Level: Groundwork issue #7 acceptance criteria and repository git hygiene rules.

## Required Checks

Before a commit, staging action, or git-boundary review, collect:

```text
git status --short
Intended file allowlist:
Explicit denylist:
git diff --name-only
git diff --cached --name-only
```

## Required Boundary Statement

Report:

- intended files changed
- intended files staged
- unrelated modified files left unstaged
- unrelated untracked files left unstaged
- ignored/runtime files that must not be committed
- any file that is dirty but intentionally out of scope

## Staging Rules

- Do not use `git add .`.
- Do not use `git add -A` unless the user explicitly asks and the allowlist proves every file belongs to the same scope.
- Prefer explicit pathspec staging, for example `git add path/to/file.md path/to/other.csv`.
- Do not stage `.groundwork/*`, `.trellis/*`, temporary tests, logs, generated runtime files, ignored files, production data dumps, secrets, or unrelated docs.
- Do not alter `.gitignore` unless the current task explicitly requires it and the reason is reported.

## Denylist Defaults

Use this as the default denylist unless the user explicitly narrows or expands it:

```text
.groundwork/*
.trellis/*
refer/*
*.log
*.tmp
.env
.env.*
production data dumps
unrelated docs
dependency or lock files unrelated to the task
shared global skills outside this repository
```

## Gate Boundary

Push, PR creation, deployment, remote tracker mutation, migration, destructive commands, history rewrite, and shared skill mutation require explicit approval through the active runtime and the skill gate rule.

