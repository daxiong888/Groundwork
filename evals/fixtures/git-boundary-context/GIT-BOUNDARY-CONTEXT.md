# Git Boundary Context Fixture

Target Reader: Codex running Groundwork `verify` in an isolated git-boundary eval.
Reader Action Needed: Preserve the intended-file and unrelated-file boundary from fixture evidence.
Decision Supported: Whether the git-boundary review can report intended, unrelated, denied, and staged files without relying on repo-root drift.
Scope: Simulated read-only git-boundary context for prompt regression.
Out of Scope: Real repo-root dirty state, staging, committing, cleanup, or filesystem mutation.
Evidence Level: Fixture-provided command output and file intent labels.

## Intended Files

- `docs/requirements.md`

## Unrelated Files

- `notes/scratch.md` is an unrelated modified file.
- `tmp/local-note.md` is an unrelated untracked file.

## Simulated Read-Only Command Evidence

```text
$ git status --short
 M docs/requirements.md
 M notes/scratch.md
?? tmp/local-note.md

$ git diff --name-only
docs/requirements.md
notes/scratch.md

$ git diff --cached --name-only
```

## Expected Boundary

- Intended allowlist: `docs/requirements.md`.
- Explicit denylist: `notes/scratch.md`, `tmp/local-note.md`, `.groundwork/*`, `.trellis/*`, `refer/*`, logs, temp files, secrets, unrelated docs, and dependency or lock files unrelated to this fixture.
- Staged files: none.
- Do not recommend `git add .`.
