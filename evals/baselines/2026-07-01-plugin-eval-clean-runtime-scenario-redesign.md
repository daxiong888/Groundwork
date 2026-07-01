# Clean Non-Recursive Targeted Runtime Baseline

Target Reader: Groundwork maintainer reviewing the accepted Plugin Eval runtime measurement baseline and the next optimization sequence.
Reader Action Needed: Use this baseline as the working runtime reference for follow-up skill read-path compression work.
Decision Supported: The clean non-recursive targeted runtime run replaces the earlier polluted benchmark run as the working baseline for Groundwork plugin optimization.
Artifact Type: baseline
Source of Truth: Local Groundwork checkout, Plugin Eval result JSON under `/private/tmp/groundwork-plugin-eval/groundwork-plugin-nonrecursive-runtime-20260701/results`, polluted comparison run under `/private/tmp/groundwork-plugin-eval/groundwork-plugin-runtime-snapshot-20260701-escalated/results`, and installed cache `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.5`.
Scope: Scenario prompt design, benchmark workspace isolation, runtime duration/token/tool-call measurements for `to-prd`, `verify`, and `dispatch`, cache/package equivalence, accepted interpretation, and the next optimization sequence.
Out of Scope: Full default eval suite, release readiness, UAT/customer readiness, marketplace publication, public skill behavior changes, and external Plugin Eval changes.
Evidence Level: Targeted local + installed-plugin-cache runtime evidence from real Codex CLI benchmark runs. Not release readiness.
Safe to Share / Redaction Notes: Safe to share as a maintainer evidence snapshot. Local absolute paths are retained because they are needed to locate reproducible evidence on this host; no secrets, credentials, private payloads, or production data are included.
Last Updated: 2026-07-01

## Accepted Baseline

The clean non-recursive targeted runtime run is accepted as the new working baseline for Groundwork runtime optimization. It replaces the earlier polluted runtime numbers for `to-prd`, `verify`, and `dispatch`.

The earlier high input numbers were materially caused by benchmark scenario design, not by the Groundwork runtime package alone and not by model-turn context explosion.

The earlier benchmark prompt asked nested Codex to "Run the Groundwork `<scenario>` benchmark scenario". That wording led the agent to inspect benchmark docs/scripts and, in multiple cases, invoke or prepare nested Plugin Eval commands. The redesigned benchmark now gives each scenario a minimal task workspace under `results/<scenario>/workspace-source/` and asks for realistic Groundwork outputs:

- `to-prd`: produce a compact PRD/spec from `TASK.md`;
- `verify`: produce a scope-first verification report from `CLAIM.md` and `EVIDENCE.md`;
- `dispatch`: produce a Dispatch Package v2 from `ACCEPTED-TASK.md`.

The clean run still measures a real installed Groundwork runtime package. It no longer measures the cost of recursively benchmarking the benchmark harness.

Acceptance rationale:

1. The benchmark target workspace is the minimal scenario workspace, not the Groundwork source tree.
2. The installed cache and local marketplace package were equivalent by `diff -qr`.
3. The installed cache top level contains only `.codex-plugin`, `LICENSE`, `README.md`, and `skills`.
4. Nested benchmark command matches dropped from 17 to 23 per polluted scenario to 0 in all clean scenarios.

Boundary: this is a targeted runtime baseline. It does not replace the full default eval suite and does not prove release readiness, UAT readiness, customer readiness, or marketplace publication readiness.

## Package And Cache Evidence

| Evidence | Result |
| --- | --- |
| Source root | `/Users/daxiong/Documents/sourceCode/Groundwork` |
| Installed cache root | `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.5` |
| Local marketplace package | `dist/groundwork-local-marketplace/plugins/groundwork` |
| Cache/package equivalence | `diff -qr dist/groundwork-local-marketplace/plugins/groundwork /Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.5` returned no output |
| Cache top-level entries | `.codex-plugin`, `LICENSE`, `README.md`, `skills` |
| Runtime package boundary check | `python3 scripts/check_runtime_package_boundary.py` passed |
| Skill entry budget check | `python3 scripts/check_skill_entry_budget.py` passed |

The wrapper script changes are not part of the installed plugin package. They affect benchmark setup only. The nested Codex runs used the installed local package provisioned by Plugin Eval.

## Scenario Design Change

Implemented in `scripts/run_plugin_eval_clean.py`:

- create minimal per-scenario workspaces in `results/<scenario>/workspace-source/`;
- point `benchmark.json` at that minimal workspace instead of the Groundwork source checkout;
- replace recursive benchmark prompts with small realistic Groundwork tasks;
- add success checklist language forbidding nested Plugin Eval, `scripts/run_plugin_eval_clean.py`, eval scripts, benchmark commands, and broad repository scans;
- preserve installed-plugin evidence and observed usage collection;
- compute observed `total_tokens` as `input_tokens + output_tokens` when Plugin Eval usage JSONL omits `total_tokens`.

Covered by `evals/test_plugin_eval_clean.py`:

- `dispatch` config uses `workspace-source/` and asks for Dispatch Package v2;
- default/custom config does not contain "benchmark scenario";
- observed usage totals are calculated when total is missing.
- raw command-log parser counts model turns, command executions, package files read, nested commands, and broad scans;
- missing raw command logs fail executed benchmarks because clean non-recursive status cannot be proven;
- nested Plugin Eval, wrapper, or benchmark-script commands fail the benchmark;
- source-repo harness scans fail based on path operands, while scenario-file content searches such as `rg -n "scripts" TASK.md` remain allowed.

## Runtime Results

Clean run command:

```sh
python3 scripts/run_plugin_eval_clean.py --scenario to-prd --scenario verify --scenario dispatch --source . --run-root /private/tmp/groundwork-plugin-eval/groundwork-plugin-nonrecursive-runtime-20260701 --force --execute
```

Comparison run root:

```text
/private/tmp/groundwork-plugin-eval/groundwork-plugin-runtime-snapshot-20260701-escalated/results
```

Clean run root:

```text
/private/tmp/groundwork-plugin-eval/groundwork-plugin-nonrecursive-runtime-20260701/results
```

| Scenario | Status | Model turns | Tool calls | Duration | Input tokens | Output tokens | Total tokens | Previous input | Previous duration | Nested benchmark commands |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `to-prd` | completed | 1 | 10 | 100.1s | 135,477 | 3,456 | 138,933 | 453,864 | 213.0s | 0 |
| `verify` | completed | 1 | 7 | 56.5s | 56,793 | 2,442 | 59,235 | 582,855 | 233.0s | 0 |
| `dispatch` | completed | 1 | 11 | 101.1s | 80,028 | 5,641 | 85,669 | 809,348 | 327.3s | 0 |

Total observed input improved from `1,846,067` tokens in the polluted comparison run to `272,298` tokens in the clean run, an approximately `85.3%` reduction.

Observed reductions from the polluted comparison run:

| Scenario | Input reduction | Duration reduction | Command reduction |
| --- | ---: | ---: | ---: |
| `to-prd` | 70.2% | 53.0% | 30 commands to 10 commands |
| `verify` | 90.3% | 75.7% | 27 commands to 7 commands |
| `dispatch` | 90.1% | 69.1% | 32 commands to 11 commands |

## Raw Runtime Observations

The raw `codex.stdout.jsonl` files show one model turn per scenario in both the polluted and clean runs. The prior "about 31 rounds" interpretation should be corrected: it was command/tool execution count, not model-turn count.

| Run | Scenario | Model turns | Command executions | Nested command matches | Broad scan matches |
| --- | --- | ---: | ---: | ---: | ---: |
| polluted | `to-prd` | 1 | 30 | 21 | 2 |
| polluted | `verify` | 1 | 27 | 17 | 2 |
| polluted | `dispatch` | 1 | 32 | 23 | 1 |
| clean | `to-prd` | 1 | 10 | 0 | 0 |
| clean | `verify` | 1 | 7 | 0 | 1 |
| clean | `dispatch` | 1 | 11 | 0 | 0 |

The single broad scan in clean `verify` was:

```sh
rg --files -g 'CLAIM.md' -g 'EVIDENCE.md' -g 'plugin.json' -g 'SKILL.md' .
```

That command only enumerated the temporary scenario workspace and installed plugin entry files. It was not a recursive benchmark or source-repo exploration.

## Answers To The Earlier Instrumentation Questions

1. Scenario model turns are available from raw `codex.stdout.jsonl` by counting `turn.started`. In the clean run, all three scenarios used 1 model turn.
2. Scenario tool calls are available from raw `codex.stdout.jsonl` by counting completed `command_execution` events. In the clean run: `to-prd` 10, `verify` 7, `dispatch` 11.
3. Runtime package reads are visible from command execution logs. In the clean run:
   - `to-prd` read `TASK.md`, `plugins/groundwork/README.md`, `.codex-plugin/plugin.json`, `skills/to-prd/*`, and shared lifecycle/evidence files.
   - `verify` read `CLAIM.md`, `EVIDENCE.md`, `skills/verify/SKILL.md`, `VERIFY-SCOPE.md`, and `SCOPE-EVIDENCE-TEMPLATE.md`; it listed `plugin.json` and `SKILL.md` files but did not read plugin README.
   - `dispatch` read `ACCEPTED-TASK.md`, listed plugin files, and read `skills/dispatch/SKILL.md`, `RESULT-PACKAGE.md`, `DISPATCH-PACKAGE.md`, `RUNTIME-ADAPTERS.md`, `ROUTING-PROFILES.md`, and `EXAMPLES.md`; it did not read plugin README or `.codex-plugin/plugin.json`.
4. `dispatch` reached 327.3s in the polluted run because the prompt induced benchmark-recursion behavior. Raw command logs show 32 command executions, 23 of which matched benchmark/plugin-eval/run-harness terms. The clean dispatch run is 101.1s with 11 command executions and 0 nested command matches.
5. The main inducing prompt text was: "Run the Groundwork `<scenario>` benchmark scenario and finish with a concise evidence report." For `dispatch`, this led to searches across `docs`, `skills`, `evals`, `scripts`, and `.codex-plugin`, reads of `docs/plugin-eval-clean-workflow.md` and `scripts/run_plugin_eval_clean.py`, and Plugin Eval command discovery. The clean prompt now asks for a Dispatch Package v2 from `ACCEPTED-TASK.md` and explicitly prohibits benchmark commands.

## Current Interpretation

The benchmark scenario design fix is accepted. It cleanly separates two concerns:

- benchmark harness measurement: no longer polluted by recursive Plugin Eval execution;
- Groundwork skill runtime payload cost: still high enough to optimize, especially `to-prd` and `dispatch`.

Static Plugin Eval budgets did not materially change because the installed plugin runtime package content did not change in this pass. The static budget remains driven by public skill descriptions, invocation cost, and deferred supporting references.

Current priority interpretation:

- `to-prd` is now the highest clean observed input scenario at `135,477` input tokens. It should be the first runtime read-path compression target.
- `dispatch` is second priority at `80,028` input tokens because its reference split is clear and likely to improve both runtime reads and static deferred cost later.
- `verify` is comparatively healthy at `56,793` input tokens and should receive only light-touch scan/read-path policy fixes in this phase.

## Accepted Next Plan

### Step 0: Solidify The Baseline And Guardrails

Goal: keep future measurements from regressing into polluted benchmark recursion.

Changes:

- keep this accepted baseline as the maintainer evidence artifact;
- keep scenario workspaces under `results/<scenario>/workspace-source/`;
- ensure benchmark prompts do not contain "benchmark scenario" or ask Codex to run a Groundwork benchmark;
- treat nested Plugin Eval, wrapper, or benchmark-script command matches in raw command logs as hard failures;
- treat missing raw command logs as failed executed benchmarks because nested-command absence cannot be proven;
- calculate observed `total_tokens` as `input_tokens + output_tokens` when Plugin Eval usage JSONL omits total.

Success signal:

- `python3 -m unittest evals.test_plugin_eval_clean` passes;
- clean benchmark scenarios report `nested_command_matches == 0`;
- target workspace is not the source checkout;
- observed usage total fallback remains covered by test.

### Step 1: Compress `to-prd` Runtime Reads

Goal: reduce `to-prd` clean runtime input from `135,477` to roughly `60k` to `75k`, or at least by `35%`.

Likely edits:

- add a hard fast path in `skills/to-prd/SKILL.md` for prompt-provided compact PRD/spec tasks;
- for `TASK.md -> compact PRD/spec`, read only the named task artifact and the active `to-prd` contract;
- avoid plugin README, `.codex-plugin/plugin.json`, unrelated skill files, lifecycle refs, wiki refs, evidence-boundary refs, grilling refs, and full PRD template refs unless the request asks for durable PRD output, source-backed product truth, wiki-backed context, or material ambiguity blocks drafting;
- split compact conversation PRD/spec behavior from durable PRD artifact behavior.

Success signal:

- no plugin README read;
- no plugin manifest read;
- no unrelated shared lifecycle/evidence refs read for the compact fixture;
- output remains a complete compact PRD/spec;
- tool calls drop from 10 toward 4 to 6;
- nested benchmark commands remain 0 and broad scans remain 0.

Follow-up runtime result after the `to-prd` fast-path and active-contract scenario boundary:

| Metric | Clean baseline | Follow-up run | Result |
| --- | ---: | ---: | --- |
| Input tokens | 135,477 | 39,704 | 70.7% reduction |
| Duration | 100.1s | 56.0s | 44.0% reduction |
| Command executions | 10 | 4 | target met |
| Model turns | 1 | 1 | unchanged |
| Nested command matches | 0 | 0 | clean |
| Forbidden source scans | 0 | 0 | clean |
| Broad scan matches | 0 | 0 | clean |

Follow-up run root:

```text
/private/tmp/groundwork-plugin-eval/groundwork-to-prd-fastpath-runtime2-20260701/results
```

The follow-up raw command log read only:

```text
TASK.md
plugins/groundwork/skills/to-prd/SKILL.md
```

It did not read plugin README, `.codex-plugin/plugin.json`, `PRD-TEMPLATE.md`, `GRILL-BEFORE-WRITE.md`, or shared lifecycle/evidence references. This is targeted runtime evidence for the `to-prd` fast-path scenario only; it is not full-suite or release readiness evidence.

### Step 2: Compress `dispatch` Reference Path

Goal: reduce `dispatch` clean runtime input from `80,028` to roughly `45k` to `55k`, or at least by `25%`, without weakening package-only non-execution behavior.

Likely edits:

- make `skills/dispatch/SKILL.md` a smaller router and package contract entry;
- split `DISPATCH-PACKAGE.md` into a compact required contract and a details file;
- make `EXAMPLES.md` conditional and out of the default read path;
- make `RUNTIME-ADAPTERS.md` conditional on runtime capability or adapter behavior scope;
- make `ROUTING-PROFILES.md` conditional on material model/profile selection;
- make `RESULT-PACKAGE.md` conditional unless the prompt asks for returned evidence/result package expectations.

Success signal:

- `EXAMPLES.md` is not read by the default clean fixture;
- `RUNTIME-ADAPTERS.md` and `ROUTING-PROFILES.md` are not read unless the fixture asks for them;
- package-only "do not execute" behavior remains visible in the final answer.

Follow-up runtime result after the dispatch physical reference split and compact active-contract scenario boundary:

| Metric | Clean baseline | Follow-up run | Result |
| --- | ---: | ---: | --- |
| Input tokens | 80,028 | 25,267 | 68.4% reduction |
| Duration | 101.1s | 65.1s | 35.6% reduction |
| Command executions | 11 | 3 | target met |
| Model turns | 1 | 1 | unchanged |
| Nested command matches | 0 | 0 | clean |
| Forbidden source scans | 0 | 0 | clean |
| Broad scan matches | 0 | 0 | clean |

Follow-up run root:

```text
/private/tmp/groundwork-plugin-eval/groundwork-dispatch-split-runtime2-20260701/results
```

The follow-up raw command log read only:

```text
ACCEPTED-TASK.md
plugins/groundwork/skills/dispatch/SKILL.md
plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md
```

It did not read plugin README, `.codex-plugin/plugin.json`, `DISPATCH-PACKAGE-DETAILS.md`, `RESULT-PACKAGE.md`, `RUNTIME-ADAPTERS.md`, `ROUTING-PROFILES.md`, or `EXAMPLES.md`. This is targeted runtime evidence for the compact dispatch package scenario only; it is not full-suite or release readiness evidence.

### Step 3: Light-Touch `verify` Scan Policy

Goal: reduce `verify` clean runtime input from `56,793` toward `45k` to `50k` without weakening verification safety boundaries.

Likely edits:

- keep nested Plugin Eval, wrapper, or benchmark-script commands as hard failures;
- keep source repo docs/evals/artifacts/scripts/research path scans as hard failures;
- treat allowlisted `rg --files` in the temporary scenario workspace as a warning, not a hard failure;
- avoid plugin internals unless the claim explicitly evaluates Groundwork plugin packaging or runtime internals.

Success signal:

- `verify` keeps CLAIM/EVIDENCE and verify-scope reads;
- plugin package discovery does not expand into unrelated internals;
- safety/evidence-boundary behavior remains intact.

Follow-up runtime result after the `verify` named-evidence default path and active-contract scenario boundary:

| Metric | Clean baseline | Follow-up run | Result |
| --- | ---: | ---: | --- |
| Input tokens | 56,793 | 43,221 | 23.9% reduction |
| Duration | 56.5s | 70.3s | slower by 24.4% |
| Command executions | 7 | 7 | unchanged |
| Model turns | 1 | 1 | unchanged |
| Nested command matches | 0 | 0 | clean |
| Forbidden source scans | 0 | 0 | clean |
| Broad scan matches | 1 | 0 | removed |

Follow-up run root:

```text
/private/tmp/groundwork-plugin-eval/groundwork-verify-fastpath-runtime3-20260701/results
```

The follow-up raw command log read only:

```text
CLAIM.md
EVIDENCE.md
plugins/groundwork/skills/verify/SKILL.md
plugins/groundwork/skills/verify/VERIFY-SCOPE.md
plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md
```

It did not read plugin README, `.codex-plugin/plugin.json`, other skill `SKILL.md` files, unrelated package internals, or repository docs/source. This is targeted runtime evidence for the named-evidence `verify` scenario only; it is not full-suite, release readiness, UAT readiness, or customer readiness evidence.

### Step 4: Static Entry Compression

Goal: reduce static active budget only after the real runtime read paths are less noisy.

Targets:

- first static active target: `<= 16k` and met by PR5 follow-up (`13,184`);
- later target: `<= 12k`;
- do not force an immediate `8k` target if that would remove safety boundaries.

Boundary:

Static compression should be a separate PR after runtime read-path compression. The real clean runtime logs should decide which deferred refs matter most.

Follow-up result after static entry compression:

| Static Budget | Before PR5 | After PR5 | Result |
| --- | ---: | ---: | --- |
| Trigger tokens | 815 | 759 | 6.9% reduction |
| Invoke / active tokens | 25,407 | 13,184 | 48.1% reduction; target met |
| Deferred tokens | 138,083 | 138,083 | unchanged |

Follow-up static analyze roots:

```text
/private/tmp/groundwork-plugin-eval/groundwork-static-compression-20260701/results
/private/tmp/groundwork-plugin-eval/groundwork-static-compression-maincheck-20260701/results
```

Post-compression invoke contributors:

| Component | Tokens |
| --- | ---: |
| `plugin-manifest` | 404 |
| `dispatch-skill-file` | 1,261 |
| `handoff-skill-file` | 901 |
| `implement-skill-file` | 909 |
| `prototype-skill-file` | 1,364 |
| `to-issues-skill-file` | 1,369 |
| `to-prd-skill-file` | 1,908 |
| `triage-skill-file` | 1,244 |
| `verify-skill-file` | 1,388 |
| `wiki-skill-file` | 1,510 |
| `write-plan-skill-file` | 926 |

Because PR5 changed `skills/to-prd/SKILL.md`, a targeted `to-prd` runtime smoke check was run:

| Metric | PR2 follow-up | PR5 smoke run | Result |
| --- | ---: | ---: | --- |
| Input tokens | 39,704 | 36,308 | 8.6% reduction |
| Duration | 56.0s | 45.9s | 18.0% reduction |
| Command executions | 4 | 4 | unchanged |
| Model turns | 1 | 1 | unchanged |
| Nested command matches | 0 | 0 | clean |
| Forbidden source scans | 0 | 0 | clean |
| Broad scan matches | 0 | 1 | allowlisted discovery warning |

Follow-up runtime root:

```text
/private/tmp/groundwork-plugin-eval/groundwork-static-compression-toprd-runtime-20260701/results
```

The PR5 `to-prd` smoke run read only:

```text
TASK.md
plugins/groundwork/skills/to-prd/SKILL.md
```

It did not read plugin README, `.codex-plugin/plugin.json`, `PRD-TEMPLATE.md`, `GRILL-BEFORE-WRITE.md`, shared lifecycle/evidence references, or unrelated package internals. The one broad scan match was:

```text
rg --files -g 'TASK.md' -g 'plugins/groundwork/skills/to-prd/SKILL.md'
```

This is treated as an allowlisted scenario-workspace discovery warning, not a hard failure or benchmark recursion signal.

## Review Decisions

| Question | Decision |
| --- | --- |
| Should the clean non-recursive run become the working baseline? | Yes. It is accepted as the targeted clean runtime baseline, not as full-suite or release readiness evidence. |
| Should the next implementation pass target `dispatch` first? | No. Target `to-prd` first for maximum clean input ROI; target `dispatch` second for clear reference splitting. |
| Should broad scans be warnings or hard failures? | Nested Plugin Eval/wrapper/benchmark-script commands and source repo harness path scans are hard failures. Allowlisted scenario-workspace file discovery is a warning. |
| Should static budget reduction be in the same PR? | No. Keep it in the same optimization stage but split into a later PR after runtime read-path compression. |

## Verification Commands

Focused source checks run after the scenario redesign, PR2 `to-prd` fast-path update, PR3 `dispatch` reference split, PR4 `verify` named-evidence update, PR5 static entry compression, and report preparation:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest evals.test_plugin_eval_clean
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest evals.test_progressive_disclosure
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile scripts/run_plugin_eval_clean.py evals/test_plugin_eval_clean.py evals/test_progressive_disclosure.py
python3 scripts/check_runtime_package_boundary.py
python3 scripts/check_skill_entry_budget.py
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
git diff --check
```

Results:

- baseline guardrail unit tests passed, 10 tests;
- progressive disclosure unit tests passed, 7 tests;
- combined focused source tests passed, 17 tests;
- Python compile passed;
- runtime package boundary passed;
- skill entry budget check passed;
- plugin JSON parse passed;
- eval prompt CSV parse passed;
- whitespace/conflict marker check passed.

Installed-cache equivalence belongs to the original accepted clean baseline evidence. The PR2, PR3, PR4, and PR5 follow-up runtime/static runs used a local marketplace package built from the current dirty source state and should not be read as global installed-cache refresh or installed-cache/source equivalence evidence.
