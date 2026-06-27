# Groundwork Repository Guidance

## Purpose

Groundwork is a Codex-native evidence-first R&D workflow base. The public skill surface is intentionally small: `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, and `wiki`.

## Repository Layout

- `skills/`: public skill contracts and shared guardrails. Keep public skill surface stable unless an accepted PRD, scoped issue, or maintainer directive explicitly expands it and the candidate passes the shared skill-quality, routing, and eval gates.
- `skills/_shared/`: reusable gates for lifecycle preflight, artifact policy, git topology, git boundary, locale, and subagent delegation.
- `docs/`: canonical product and maintainer documentation. Prefer updating an existing canonical doc over creating a duplicate.
- `evals/prompts/`: CSV regression suites for routing, guardrails, lifecycle, and skill behavior.
- `evals/fixtures/`: small isolated workspaces used by runtime and guardrail eval prompts.
- `evals/baselines/`: dated evidence reports. These are evidence snapshots, not live runtime truth.
- `scripts/`: maintainer utilities. Do not add new runtime dependencies without explicit scope.
- `artifacts/`: scoped lifecycle or handoff artifacts only when artifact-promotion or lifecycle-state thresholds are met.
- `.codex-plugin/plugin.json`: plugin metadata. Do not bump versions or package shape unless release scope requires it.

## Scope Rules

- Do not add new public skills unless an accepted PRD, scoped issue, or maintainer directive explicitly expands the public surface and the candidate passes `skills/_shared/SKILL-QUALITY.md`, routing, and eval gates.
- Prefer shared references, branch/workflow lenses, router behavior, or one-off guides over public skills when the behavior does not have a distinct invocation moment.
- Edit only files needed for the scoped issue or checkpoint.
- Preferred edit areas are `skills/`, `docs/`, `evals/`, and this repo-local `AGENTS.md`.
- Do not mutate shared global skills, production systems, remote data, `.groundwork` runtime contents, `.trellis`, `refer/`, unrelated docs, or dependency/lock files unless the user explicitly expands scope.
- If product behavior or public skill surface is uncertain, mark the task blocked or ask before inventing product truth.

## Evidence And Evals

- Read relevant skill files, docs, fixtures, and issue context before editing.
- Run the fastest relevant eval or validation for the touched area.
- Before treating Groundwork runtime or `codex exec` evals as evidence, confirm whether they use the installed plugin cache. If touched files affect plugin behavior, refresh through the supported marketplace/install path or state that runtime evidence was not refreshed and is not release-gating.
- Runtime/eval reports must name the installed plugin root, local marketplace/source used, cache/source equivalence check or refresh step, and whether the run was a targeted subset or full suite.
- For broad Groundwork changes, include these checks when applicable:
  - `git status --short`
  - `git diff --check`
  - `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`
  - `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`
  - `git diff --name-only`
- Final reports must cite changed files and the exact commands or evidence used. Do not claim a check passed unless it actually ran.

## Build, Test, And Lint

- There is no package manager or lockfile in this repository by default; do not introduce one just to validate documentation or CSV changes.
- Validate plugin metadata with `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` when plugin metadata or broad repository packaging is in scope.
- Validate eval prompt CSV files with `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`.
- Use `git diff --check` for whitespace/conflict-marker checks before reporting changed files as complete.
- Runtime evidence from `evals/run_runtime.py` is release-relevant only when the installed plugin cache/source equivalence or supported marketplace refresh is named. Local source edits alone are not runtime evidence.

## Review Rules

- Treat PRDs, skill files, shared guardrails, eval prompts, and baselines as source-truth-bearing artifacts. Do not rely on memory or summaries when the file is available.
- Map each material acceptance criterion to a source change and a check, or report it as a gap.
- Keep review scope explicit: implementation conformance, readiness, release, UAT, runtime, and git boundary are different claims.
- For durable artifacts, require the shared audience-first header fields from `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`.
- For git boundary review, preserve intended files, unrelated files, staged files, explicit denylist, and ignored/runtime exclusions.

## Done Definition

Groundwork work is locally done only when all applicable items are true:

- Source truth was inspected from local PRD/spec, skill docs, source, tests, fixtures, or verified user input.
- The implementation or documentation diff is minimal and limited to the scoped issue or checkpoint.
- Public skill surface stayed unchanged unless explicitly required and quality-gated.
- Durable artifacts include the required audience-first header fields or the missing fields are reported as gaps.
- Relevant eval prompt CSV, plugin JSON, and whitespace checks were run or explicitly reported as not run with a reason.
- Runtime/cache claims name the installed plugin root and cache/source refresh or equivalence evidence; otherwise they are not claimed.
- Final response separates verified local evidence from unverified runtime, release, UAT, or customer readiness.

## Git Boundary

- Check `git status --short` before and after edits.
- Inspect relevant diffs before staging in a dirty worktree.
- Do not use `git add .`.
- Stage only intended files with explicit pathspecs.
- Do not commit `.groundwork`, `.trellis`, temporary tests, runtime logs, ignored files, unrelated docs, secrets, or production data.
- Prefer small PRs and focused commits. Do not mix unrelated issue checkpoints.

## Artifacts

- Durable artifacts must have the exact audience-first fields required by `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`.
- Prefer updating canonical docs or eval fixtures over creating duplicates.
- Do not copy secrets, credentials, PII, sensitive logs, long diffs, or private request payloads into artifacts.

## Forbidden Behavior

- Do not claim release readiness, UAT readiness, runtime behavior, cache refresh, or marketplace install evidence from local diff alone.
- Do not turn prototype-only mock fields into backend/API contract truth.
- Do not let `verify` pass a readiness claim without scope, covered/not-covered evidence, and explicit missing-evidence handling.
- Do not let `handoff` copy full PRDs, long diffs, raw logs, or lifecycle state files.
- Do not recommend `git add .`, stage unrelated files, or commit ignored runtime scratch.
