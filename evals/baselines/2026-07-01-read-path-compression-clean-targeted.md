# Read-Path Compression Clean Targeted Baseline

Target Reader: Groundwork maintainer reviewing the post-compression clean targeted Plugin Eval baseline.
Reader Action Needed: Use this artifact and `scripts/check_plugin_eval_clean_regression.py` as the working regression gate for `to-prd`, `verify`, and `dispatch` read-path cost.
Decision Supported: The first runtime read-path compression pass is accepted as the current targeted clean baseline, with loose thresholds for future regression checks.
Artifact Type: repo-only baseline and regression gate definition
Source of Truth: Local checkout at `8b904ef47b8c4f291696dcf8355ec1afa038deae`, installed cache `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.5`, local marketplace package `dist/groundwork-local-marketplace/plugins/groundwork`, and Plugin Eval run roots under `/private/tmp/groundwork-plugin-eval/2026-07-01-after-read-path-compression-*`.
Scope: Clean targeted Plugin Eval scenarios `to-prd`, `verify`, and `dispatch`; observed token usage; model turns; command executions; package read paths; nested command and source-scan guardrails; source/cache equivalence.
Out of Scope: Full default eval suite, release readiness, UAT/customer readiness, public marketplace readiness, customer acceptance, and new top-level Codex product thread isolation.
Evidence Level: Targeted local installed-plugin runtime evidence from real Plugin Eval-spawned Codex CLI benchmark threads. Not release evidence.
Safe to Share / Redaction Notes: Safe for maintainer review. Local absolute paths and thread ids are retained for reproducibility on this host. No secrets or production data are included.
Last Updated: 2026-07-01

## Acceptance Summary

This baseline supersedes the earlier clean non-recursive runtime baseline for ongoing read-path regression tracking.

The earlier clean baseline remains useful as proof that benchmark recursion was removed. This artifact records the next accepted state: clean targeted runtime after the first skill/reference read-path compression pass.

Observed total input:

| Run | Total input |
| --- | ---: |
| Polluted benchmark run | `1,846,067` |
| Clean non-recursive targeted baseline | `272,298` |
| Post-compression clean targeted baseline | `100,528` |

Post-compression improvement:

- `63.1%` input reduction from the clean non-recursive targeted baseline.
- `94.6%` input reduction from the earlier polluted benchmark run.

## Commit And Cache Evidence

| Evidence | Result |
| --- | --- |
| Source commit | `8b904ef47b8c4f291696dcf8355ec1afa038deae` |
| Commit subject | `Tighten clean plugin eval runtime paths` |
| Branch | `main` |
| Remote check | `origin/main` pointed at `8b904ef47b8c4f291696dcf8355ec1afa038deae` after push |
| Source dirty status during valid runs | clean |
| Local marketplace package | `dist/groundwork-local-marketplace/plugins/groundwork` |
| Installed cache root | `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.5` |
| Cache refresh method | `codex plugin add groundwork@groundwork --json` |
| Cache/package equivalence command | `diff -qr dist/groundwork-local-marketplace/plugins/groundwork /Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.5.5` |
| Cache/package equivalence result | no output |
| Runtime package boundary check | `python3 scripts/check_runtime_package_boundary.py` passed |
| Skill entry budget check | `python3 scripts/check_skill_entry_budget.py` passed |

Runtime package top-level entries:

- `.codex-plugin`
- `LICENSE`
- `README.md`
- `skills`

## Valid Scenario Runs

These runs were started from the current shell through Plugin Eval/Codex CLI, not from a separate top-level Codex product conversation. They were not subagents. Each scenario ran in a fresh Plugin Eval-spawned Codex runtime thread and did not receive this maintainer chat transcript as its prompt.

| Scenario | Run root | Thread id | Duration |
| --- | --- | --- | ---: |
| `to-prd` | `/private/tmp/groundwork-plugin-eval/2026-07-01-after-read-path-compression-to-prd` | `019f1c58-92d8-7400-90a5-76e6453ccc4b` | `78,748 ms` |
| `verify` | `/private/tmp/groundwork-plugin-eval/2026-07-01-after-read-path-compression-verify` | `019f1c5a-1467-70d0-ae2a-40f38aeed420` | `98,838 ms` |
| `dispatch` | `/private/tmp/groundwork-plugin-eval/2026-07-01-after-read-path-compression-dispatch` | `019f1c5b-df6b-7720-b30d-0b33330698e5` | `172,370 ms` |

## Runtime Metrics

| Scenario | Input | Output | Total | Turns | Commands | Nested commands | Forbidden scans | Broad scans |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `to-prd` | `24,493` | `3,306` | `27,799` | `1` | `2` | `0` | `0` | `0` |
| `verify` | `39,702` | `4,335` | `44,037` | `1` | `7` | `0` | `0` | `1` |
| `dispatch` | `36,333` | `3,177` | `39,510` | `1` | `4` | `0` | `0` | `0` |
| **Total** | `100,528` | `10,818` | `111,346` | n/a | `13` | `0` | `0` | `1` |

## Package Read Paths

| Scenario | Package files read |
| --- | --- |
| `to-prd` | `plugins/groundwork/skills/to-prd/SKILL.md` |
| `verify` | `plugins/groundwork/skills/verify/SKILL.md`; `plugins/groundwork/skills/verify/VERIFY-SCOPE.md`; `plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md` |
| `dispatch` | `plugins/groundwork/skills/dispatch/SKILL.md`; `plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md` |

Read-path interpretation:

- `to-prd` did not read plugin README, `.codex-plugin/plugin.json`, plugin manifests, package internals, PRD template, grilling reference, lifecycle reference, or evidence reference.
- `dispatch` did not read `DISPATCH-PACKAGE-DETAILS.md`, `RESULT-PACKAGE.md`, `RUNTIME-ADAPTERS.md`, `ROUTING-PROFILES.md`, or `EXAMPLES.md`.
- `verify` read only its expected scope files. The one broad scan was an allowlisted `rg --files` discovery command, not a forbidden source-repo scan.

## Discarded Run

One earlier attempt from the current shell without network escalation is explicitly discarded.

Reason:

- nested Codex runtime hit DNS/network errors while contacting `https://chatgpt.com/backend-api/codex/responses`;
- `benchmark-result.json` marked the scenario as failed;
- usage was `0`;
- raw event log contained reconnect errors and no completed final response.

Classification under the fixed wrapper:

```text
status = invalid-run
valid_for_usage_regression = false
evidence_category = discarded_runs
invalid_run_class = invalid_transport_failure
```

This run is infrastructure/transport failure evidence only. It is not plugin behavior evidence and must not be used for token regression.

## Wrapper Caveat

The valid runs above were produced before `scripts/run_plugin_eval_clean.py` was hardened to propagate `benchmark-result.json` scenario failures. They were manually checked against `benchmark-result.json` and raw traces.

Follow-up wrapper behavior now required for unattended gates:

- `benchmark-result.json` must exist;
- scenario status must be `completed`;
- observed usage must be loaded from the same reported run root;
- input tokens must be positive;
- final assistant message must exist;
- terminal transport failure must not be present;
- nested benchmark commands and forbidden source scans must be zero;
- invalid transport failures must be classified as discarded runs, not plugin failures and not completed zero-usage runs.

## Regression Gate

Executable gate:

```sh
python3 scripts/check_plugin_eval_clean_regression.py \
  /private/tmp/groundwork-plugin-eval/<run-id>/results/run-manifest.json
```

The script also accepts multiple single-scenario manifests:

```sh
python3 scripts/check_plugin_eval_clean_regression.py \
  /private/tmp/groundwork-plugin-eval/<run-id-to-prd>/results/run-manifest.json \
  /private/tmp/groundwork-plugin-eval/<run-id-verify>/results/run-manifest.json \
  /private/tmp/groundwork-plugin-eval/<run-id-dispatch>/results/run-manifest.json
```

Thresholds are intentionally loose relative to this baseline:

| Gate | Threshold |
| --- | ---: |
| `to-prd` input | `<= 35,000` |
| `verify` input | `<= 55,000` |
| `dispatch` input | `<= 50,000` |
| total input | `<= 140,000` |
| model turns per scenario | `== 1` |
| nested benchmark commands | `== 0` |
| forbidden source scans | `== 0` |

Read-path gates:

- `dispatch` must not read `DISPATCH-PACKAGE-DETAILS.md` by default.
- `to-prd` must not read plugin README or `.codex-plugin/plugin.json` by default.

These thresholds leave roughly 35% to 40% operational slack from the current measurements, so small runner/model/prompt variation should not cause noise while meaningful regressions still fail.

## Recommended Next Step

Use this baseline for targeted runtime regression only. Next maintainer work should run:

```sh
python3 scripts/run_plugin_eval_clean.py \
  --scenario to-prd \
  --scenario verify \
  --scenario dispatch \
  --source . \
  --run-root /private/tmp/groundwork-plugin-eval/<run-id> \
  --force \
  --execute

python3 scripts/check_plugin_eval_clean_regression.py \
  /private/tmp/groundwork-plugin-eval/<run-id>/results/run-manifest.json
```

This remains targeted local runtime evidence. It does not replace full default evals and does not prove release readiness, UAT readiness, customer readiness, or public marketplace readiness.
