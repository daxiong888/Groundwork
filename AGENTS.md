# Groundwork Repository Guidance

## Purpose

Groundwork is a Codex-native evidence-first R&D workflow base. The public skill surface is intentionally small: `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, and `wiki`.

## Audience And Document Roles

- `README.md` is the user-facing GitHub entry point for people evaluating or installing Groundwork.
- `README.zh-CN.md` is the Simplified Chinese translation of `README.md`. Keep it in sync when `README.md` changes.
- `README.runtime.md` is the installed runtime package README and is copied into the generated marketplace package as `README.md`.
- `AGENTS.md` is source-checkout-only maintainer guidance for Codex agents working in this repository. It is not bundled into the installed runtime package.
- `docs/` contains canonical maintainer architecture, workflow, PRD, and evidence documents. Prefer linking to an existing canonical doc over making the README carry maintainer detail.

## Architecture Boundary

Groundwork has two layers:

- Runtime Kernel: the installed plugin package. It contains only `.codex-plugin/`, `skills/`, `hooks/hooks.json`, `scripts/codex-hooks/`, `README.md` generated from `README.runtime.md`, and `LICENSE`.
- Maintainer Lab: the source checkout. It contains maintainer guidance, docs, evals, schemas, artifacts, examples, research, ordinary maintainer scripts, local state, and historical evidence.

Runtime-packaged paths are `.codex-plugin/`, `skills/`, `hooks/`, `scripts/codex-hooks/`, `README.runtime.md`, and `LICENSE`. Changes to these paths can affect the installed runtime package and require the runtime package boundary check.

Source-only paths include `AGENTS.md`, `CHANGELOG.md`, `PROJECT.md`, `docs/`, `evals/`, `schemas/`, `artifacts/`, `examples/`, `research/`, maintainer scripts outside `scripts/codex-hooks/`, `.github/`, `.git/`, `.codegraph/`, `.groundwork/`, `.trellis/`, `dist/`, `refer/`, and `node_modules/`. Do not treat these as installed runtime contents.

## Repository Layout

- `skills/`: public skill contracts and shared guardrails. Keep public skill surface stable unless an accepted PRD, scoped issue, or maintainer directive explicitly expands it and the candidate passes the shared skill-quality, routing, and eval gates.
- `skills/_shared/`: reusable gates for lifecycle preflight, artifact policy, git topology, git boundary, locale, and subagent delegation.
- `hooks/`: dormant Codex hook definitions for project opt-in router observability. Hook availability is not hook trust, runtime readiness, or trace consent.
- `scripts/codex-hooks/`: standard-library hook entrypoints bundled in the runtime package. These must stay self-contained and must not import source-only `evals/` modules.
- `docs/`: canonical product and maintainer documentation. Prefer updating an existing canonical doc over creating a duplicate.
- `evals/prompts/`: CSV regression suites for routing, guardrails, lifecycle, and skill behavior.
- `evals/fixtures/`: small isolated workspaces used by runtime and guardrail eval prompts.
- `evals/baselines/`: dated evidence reports. These are evidence snapshots, not live runtime truth.
- `schemas/`: source-validation schemas and schema fixtures. Schema validity is not runtime, cache, release, or UAT evidence by itself.
- `scripts/`: maintainer utilities. Do not add new runtime dependencies without explicit scope. Only `scripts/codex-hooks/` is packaged into the runtime kernel.
- `scripts/build_local_marketplace.py`: builds the generated local marketplace and enforces the runtime package shape.
- `scripts/check_runtime_package_boundary.py`: validates that a package root contains only runtime-approved paths and that runtime README content comes from `README.runtime.md`.
- `scripts/run_plugin_eval_clean.py`: maintainer helper for clean plugin-eval runs; not bundled into the installed runtime package.
- `artifacts/`: scoped lifecycle or handoff artifacts only when artifact-promotion or lifecycle-state thresholds are met.
- `.codex-plugin/plugin.json`: plugin metadata. Do not bump versions or package shape unless release scope requires it.
- `README.runtime.md`: installed package README source. Runtime package validation requires packaged `README.md` to match it.

## Scope Rules

- Do not add new public skills unless an accepted PRD, scoped issue, or maintainer directive explicitly expands the public surface and the candidate passes `skills/_shared/SKILL-QUALITY.md`, routing, and eval gates.
- Prefer shared references, branch/workflow lenses, router behavior, or one-off guides over public skills when the behavior does not have a distinct invocation moment.
- Edit only files needed for the scoped issue or checkpoint.
- Preferred edit areas are `skills/`, `docs/`, `evals/`, and this repo-local `AGENTS.md`.
- Treat README edits as user-facing entry-point edits. Keep them concise, audience-first, and link maintainer detail out to `docs/` and `AGENTS.md`.
- Treat runtime-packaged path edits as package-affecting unless proven otherwise. Run the runtime package boundary check before reporting them complete.
- Do not mutate shared global skills, production systems, remote data, `.groundwork` runtime contents, `.trellis`, `refer/`, unrelated docs, or dependency/lock files unless the user explicitly expands scope.
- If product behavior or public skill surface is uncertain, mark the task blocked or ask before inventing product truth.

## Evidence And Evals

- Read relevant skill files, docs, fixtures, and issue context before editing.
- Run the fastest relevant eval or validation for the touched area.
- Before treating Groundwork runtime or `codex exec` evals as evidence, confirm whether they use the installed plugin cache. If touched files affect plugin behavior, refresh through the supported marketplace/install path or state that runtime evidence was not refreshed and is not release-gating.
- Runtime/eval reports must name the installed plugin root, local marketplace/source used, cache/source equivalence check or refresh step, and whether the run was a targeted subset or full suite.
- Keep evidence layers separate: local source diff, source-validation checks, generated runtime package, installed plugin cache, `codex exec` runtime run, release readiness, UAT readiness, and customer readiness are different claims.
- Hook/router cards, local scores, and `.groundwork/harness/router-observability/` scratch output are observability and improvement evidence only. They do not prove runtime behavior, cache refresh, release readiness, UAT readiness, customer readiness, marketplace readiness, installed-plugin evidence, or hook trust by themselves.
- For routing evidence, do not infer real skill loading from final output shape alone. Preserve `route_evidence_source`, `dispatch_hit_level`, and conservative `skill_hits` semantics: output markers can support output-shape evidence, but they must not be promoted into actual skill-load evidence without a stronger source.
- For broad Groundwork changes, include these checks when applicable:
  - `git status --short`
  - `git diff --check`
  - `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`
  - `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`
  - `python3 scripts/check_runtime_package_boundary.py`
  - `git diff --name-only`
- Final reports must cite changed files and the exact commands or evidence used. Do not claim a check passed unless it actually ran.

## Build, Test, And Lint

- There is no package manager or lockfile in this repository by default; do not introduce one just to validate documentation or CSV changes.
- Validate plugin metadata with `python3 -m json.tool .codex-plugin/plugin.json >/dev/null` when plugin metadata or broad repository packaging is in scope.
- Validate eval prompt CSV files with `python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"`.
- Validate runtime package boundaries with `python3 scripts/check_runtime_package_boundary.py` when runtime-packaged paths, marketplace packaging, hook files, or `README.runtime.md` are touched.
- For README-only or AGENTS-only changes, `git diff --check` is the fastest relevant validation unless the edit also changes package or eval claims.
- For route, hook, or eval behavior changes, add the narrowest relevant unit tests or `python3 -B evals/run_runtime.py --validate-schema --suite <suite>.csv` check. Use broader runtime evidence only when the claim requires it.
- Use `git diff --check` for whitespace/conflict-marker checks before reporting changed files as complete.
- Runtime evidence from `evals/run_runtime.py` is release-relevant only when the installed plugin cache/source equivalence or supported marketplace refresh is named. Local source edits alone are not runtime evidence.

## CodeGraph

- `.codegraph` contains local DB/socket/log state and is intentionally not shared through Git.
- In a new worktree, run `scripts/ensure-codegraph.sh` from that worktree before relying on the CodeGraph MCP; the script initializes the local index when missing and syncs it when present.
- Do not treat a different worktree's CodeGraph index as evidence for the current worktree.

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
- Do not commit `.groundwork`, `.trellis`, `evals/__pycache__/`, temporary tests, runtime logs, ignored files, `dist/`, plugin cache output, unrelated docs, secrets, or production data.
- Prefer small PRs and focused commits. Do not mix unrelated issue checkpoints.

## Codex App Managed Worktree Threads

- When the user explicitly requests a child thread plus Codex-managed worktree, the parent or coordinator must treat that child thread/worktree as the only implementation source for that task.
- If Codex App returns `pendingWorktreeId` without a resolved child thread id and worktree path, wait/poll/resolve the pending worktree or report `blocked`/`human_decision`; do not implement the same task in the parent thread and do not create a backup manual git worktree.
- Any fallback that changes the requested thread/worktree topology requires explicit user approval. If an accidental fallback already exists, disclose it, exclude its changes from the delivery evidence, and keep it out of merge/closeout unless the user explicitly accepts that topology change.

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
