# Groundwork Repository Guidance

## Purpose

Groundwork is a Codex-native evidence-first R&D workflow base. The public skill surface is intentionally small: `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, and `handoff`.

## Scope Rules

- Do not add new public skills unless a GitHub issue explicitly requires it.
- Edit only files needed for the scoped issue or checkpoint.
- Preferred edit areas are `skills/`, `docs/`, `evals/`, and this repo-local `AGENTS.md`.
- Do not mutate shared global skills, production systems, remote data, `.groundwork` runtime contents, `.trellis`, `refer/`, unrelated docs, or dependency/lock files unless the user explicitly expands scope.
- If product behavior or public skill surface is uncertain, mark the task blocked or ask before inventing product truth.

## Evidence And Evals

- Read relevant skill files, docs, fixtures, and issue context before editing.
- Run the fastest relevant eval or validation for the touched area.
- For broad Groundwork changes, include these checks when applicable:
  - `git status --short`
  - `git diff --check`
  - `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`
  - `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`
  - `git diff --name-only`
- Final reports must cite changed files and the exact commands or evidence used. Do not claim a check passed unless it actually ran.

## Git Boundary

- Check `git status --short` before and after edits.
- Inspect relevant diffs before staging in a dirty worktree.
- Do not use `git add .`.
- Stage only intended files with explicit pathspecs.
- Do not commit `.groundwork`, `.trellis`, temporary tests, runtime logs, ignored files, unrelated docs, secrets, or production data.
- Prefer small PRs and focused commits. Do not mix unrelated issue checkpoints.

## Artifacts

- Durable artifacts must have a target reader, reader action, decision supported, scope, out-of-scope boundary, and evidence level.
- Prefer updating canonical docs or eval fixtures over creating duplicates.
- Do not copy secrets, credentials, PII, sensitive logs, long diffs, or private request payloads into artifacts.
