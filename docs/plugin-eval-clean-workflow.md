# Plugin Eval Clean Workflow

Target Reader: Groundwork maintainers running token and behavior benchmarks for runtime-package work.
Reader Action Needed: Run Plugin Eval from isolated targets without polluting source checkouts, benchmark targets, or later scenarios.
Decision Supported: Whether a Plugin Eval benchmark result is clean enough to compare across Groundwork runtime-package changes.
Artifact Type: maintainer doc
Source of Truth: `scripts/run_plugin_eval_clean.py`, `scripts/build_local_marketplace.py`, repo-local `AGENTS.md`, and the current Plugin Eval benchmark behavior.
Scope: Clean local benchmark path discipline, required evidence fields, command shape, and package-boundary hygiene.
Out of Scope: Publishing releases, proving UAT/customer readiness, replacing Plugin Eval, changing Groundwork public skill contracts, or claiming runtime/cache evidence without an installed plugin root.
Evidence Level: Source-validation maintainer guidance. A benchmark run becomes runtime evidence only when its run manifest names the installed plugin root or explicitly says that cache/runtime evidence is not claimed.
Safe to Share / Redaction Notes: Safe to share as-is; benchmark result files may contain local paths and Codex output and should be reviewed before sharing.

Groundwork benchmarks must separate the runtime kernel from the maintainer lab. The source checkout may contain docs, evals, artifacts, research, scripts, schemas, and historical baselines, but the plugin target measured by Plugin Eval should be the generated runtime package only.

> [!IMPORTANT]
> Do not run clean Plugin Eval benchmarks directly against the source checkout or a dirty target. Use a target whose basename is exactly `groundwork`, keep results outside that target, and rebuild the local marketplace after every package-boundary change.

## Clean Layout

Use the wrapper:

```bash
python3 scripts/run_plugin_eval_clean.py \
  --scenario to-prd \
  --source . \
  --run-root /private/tmp/groundwork-plugin-eval/smoke
```

The wrapper prepares this layout:

```text
/private/tmp/groundwork-plugin-eval/<run-id>/
  marketplace/
    .agents/plugins/marketplace.json
    plugins/groundwork/
  <scenario>/
    groundwork/
  results/
    run-manifest.json
    <scenario>/
      benchmark.json
      workspace-source/
      plugin-eval-analyze.json
```

If the run root already has a `results/` directory, the wrapper removes the whole results directory before writing the new run manifest and scenario outputs. This keeps stable smoke paths such as `/private/tmp/groundwork-plugin-eval/smoke` from mixing old benchmark output with a new `not_run` command-preparation pass.

The `marketplace/plugins/groundwork` package is built by `scripts/build_local_marketplace.py`. It should contain only:

```text
.codex-plugin/
skills/
hooks/hooks.json
scripts/codex-hooks/
README.md
LICENSE
```

It must not contain repo-only or maintainer-lab roots such as `.github/`, `AGENTS.md`, `CHANGELOG.md`, `PROJECT.md`, `docs/`, `evals/`, `artifacts/`, `examples/`, `research/`, or `schemas/`. The only packaged hook/script paths are the exact contract-listed `hooks/hooks.json` and `scripts/codex-hooks/` telemetry entrypoints; ordinary maintainer scripts remain source-only. `.codex-plugin/runtime-manifest.json` is generated during the build and binds the package to its metadata, package contract, README, and content inventory.

## Command Modes

Default mode prepares the clean target, builds the local marketplace, records metadata, runs static `plugin-eval analyze` when a Plugin Eval command is visible, and prints a copyable benchmark command. It does not run `codex exec`.

```bash
python3 scripts/run_plugin_eval_clean.py --scenario verify --source .
```

Use `--print-commands` when the current environment does not expose the official Plugin Eval CLI or when you only want a benchmark command plan. This still runs static `plugin-eval analyze` when a Plugin Eval command is visible; it skips benchmark execution and `codex exec`.

```bash
python3 scripts/run_plugin_eval_clean.py --scenario verify --source . --print-commands
```

Use `--execute` only when you intentionally want the wrapper to run Plugin Eval benchmark:

```bash
python3 scripts/run_plugin_eval_clean.py --scenario verify --source . --execute
```

If Plugin Eval writes `.plugin-eval` into the target during execution, the wrapper moves that directory into `results/<scenario>/target-plugin-eval-output/` and then refuses to finish unless the target is clean again.

The same target cleanup runs after static `plugin-eval analyze`, because analyze must not leave `.plugin-eval` inside the benchmark target either.

## Scenario Design

Clean benchmarks measure Groundwork runtime behavior on small user tasks, not the cost of recursively running Plugin Eval from inside a benchmarked scenario. The wrapper writes a minimal `results/<scenario>/workspace-source/` fixture and points `benchmark.json` at that fixture instead of the Groundwork source checkout.

> [!IMPORTANT]
> Scenario prompts must not ask the nested Codex run to run Plugin Eval, `scripts/run_plugin_eval_clean.py`, eval scripts, benchmark commands, or broad repository scans. They should ask for a realistic Groundwork output such as a compact PRD/spec, a scope-first verification report, or a Dispatch Package v2.

Scenario prompts are blind to the expected plugin read path: do not name the target `SKILL.md` or supporting reference files in the user prompt. The model must discover the minimum relevant guidance from the installed plugin. The harness may still enforce an expected-read allowlist, reject global-memory reads, or reject broad workspace scans after the run; those are evaluator-side assertions for the clean compact-default scenario, not production Groundwork prohibitions or prompt coaching. The runtime row carrying `dispatch_default_read_path` also disables the nested Codex `memories` feature for that ephemeral eval invocation so the host's normal memory policy cannot contaminate the isolated measurement.

The full source checkout is still used to build the local marketplace package and record source metadata. It is not the scenario workspace copied into the nested Codex run.

After execution, the wrapper reads only the nested Codex `codex.stdout.jsonl` command log under `results/<scenario>/target-plugin-eval-output/`. Missing raw command logs, nested Plugin Eval commands, `scripts/run_plugin_eval_clean.py`, benchmark-script commands under `scripts/` or `evals/`, or source-repo `docs/`, `evals/`, `artifacts/`, `scripts/`, or `research/` path scans are hard failures because they mean the scenario cannot prove clean non-recursive behavior or measured benchmark harness/source-repo exploration instead of Groundwork runtime read-path cost.

Allowlisted file discovery inside the temporary scenario workspace, such as `rg --files` for named task/evidence files and installed plugin entry files, is normally a reportable scan signal rather than an automatic hard failure. The Dispatch compact-default eval is stricter: its accepted task file is named up front, so any broad workspace scan or global-memory read fails that evaluator-side read-path check. Searching for words such as `benchmark`, `docs`, or `scripts` inside a named scenario task file is not a hard failure unless the command scans forbidden source-repo paths.

## Required Evidence

Every clean benchmark run must preserve `results/run-manifest.json`. The manifest records:

- source repo SHA and dirty status;
- builder packaged entries;
- marketplace root and package root;
- result root;
- installed cache root, or `null` when not visible;
- scenario name;
- Plugin Eval command;
- model turn count, command execution count, nested command matches, forbidden source scan matches, broad scan matches, and package files read when raw Codex logs are present;
- observed input/output/total tokens when Codex emits usage telemetry;
- static trigger, invoke, and deferred token budgets from `plugin-eval analyze` when available.

Observed usage is recorded only from JSONL entries with a valid usage payload. If Plugin Eval writes non-usage lines or malformed telemetry, the manifest records skipped or invalid line counts instead of turning them into zero-token samples.

Runtime/cache claims require an installed plugin root. If `installed_cache_root` is `null`, describe the run as clean source/package preparation and static analysis only, not installed-plugin runtime evidence.

## Comparison Rules

- Do not compare a clean run with a run whose target contains `.plugin-eval`.
- Do not compare runs where one target is named something other than `groundwork`; Plugin Eval may infer a fake marketplace plugin name from the basename.
- Do not use historical `evals/baselines/`, `artifacts/`, `research/`, or `examples/` as current evidence unless the prompt explicitly asks for historical, eval, or release-baseline context.
- Do not write benchmark results into the target. Results belong under `/private/tmp/groundwork-plugin-eval/<run-id>/results`.
- Rebuild the local marketplace after every package-boundary change before measuring.
- Use `--force` only for wrapper-owned run roots under `/private/tmp/groundwork-plugin-eval/<run-id>`. The helper rejects source checkouts, source parents, and forced deletion outside that temp run-root family.

## Token Budget Trend

Record token budget movement in `docs/plugin-token-budget-policy.md` whenever a runtime-package or public-entry change is benchmarked. At minimum, preserve:

- change scope;
- source gate result;
- static trigger, invoke, and deferred budget trend when `plugin-eval analyze` is available;
- observed input/output/total usage trend when benchmark execution emits usage telemetry;
- manifest or local evidence path.

The PR 6 source guardrail baseline adds this trend discipline without claiming a Plugin Eval static-budget replacement or installed-plugin runtime evidence.

Visible-output regression ceilings are enforced separately from input-token budgets: `to-prd` is capped at 3,200 characters / 28 non-empty lines / 6 sections, `verify` at 2,600 / 24 / 5, and the clean targeted Dispatch compact-default scenario at 2,800 / 26 / 6. These are post-response regression guards, not target lengths or truncation rules. Required fields and semantic completeness take precedence; Dispatch must return `needs_split` or use the prompt-material route-specific contract when a complete package cannot fit. Adapter-ready, clean-review fanout, complex separation, field-level validation, and explicitly requested full-schema outputs are outside the compact-default ceiling.

## Smoke Checks

Use these source-level checks before treating the wrapper/doc update as complete:

```bash
python3 scripts/check_runtime_package_boundary.py
python3 scripts/check_skill_entry_budget.py

python3 -m py_compile scripts/run_plugin_eval_clean.py

python3 scripts/run_plugin_eval_clean.py \
  --scenario to-prd \
  --source . \
  --run-root /private/tmp/groundwork-plugin-eval/smoke
```

For package-boundary checks, confirm the wrapper output names a package root under `marketplace/plugins/groundwork`, and confirm that root contains no `docs/`, `evals/`, or other maintainer-lab directories and no scripts outside the exact `scripts/codex-hooks/` allowlist.
