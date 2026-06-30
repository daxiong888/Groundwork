# Plugin Token Budget Policy

Target Reader: Groundwork maintainers changing runtime package contents, public skill entries, or Plugin Eval benchmark workflows.
Reader Action Needed: Keep token discipline as a source-validation quality gate before claiming runtime-package or benchmark readiness.
Decision Supported: Whether a change preserves the lightweight runtime boundary and public skill entry budget.
Artifact Type: maintainer policy
Source of Truth: `scripts/build_local_marketplace.py`, `scripts/check_runtime_package_boundary.py`, `scripts/check_skill_entry_budget.py`, `README.runtime.md`, and `docs/plugin-eval-clean-workflow.md`.
Scope: Runtime package boundary, SKILL.md entry-file budget checks, benchmark trend recording, and source-validation CI gates.
Out of Scope: Official tokenizer parity, Plugin Eval static budget replacement, release approval, marketplace publication, installed-cache refresh, UAT, or customer readiness.
Evidence Level: Source-validation policy and local static checks only. Runtime evidence still requires installed-plugin/cache evidence named by the run.
Safe to Share / Redaction Notes: Safe to share as-is; benchmark run outputs may contain local paths and should be reviewed before sharing.

Groundwork treats token discipline as part of product quality. Public entry files must stay small enough to route the user to the right lazy-loaded contract, and the runtime package must stay separate from the maintainer repository.

## Policy

1. Runtime package is not the repository.

The runtime package contains only `.codex-plugin/`, `skills/`, `README.md`, and `LICENSE`. Repository-only roots such as `.github/`, `docs/`, `evals/`, `artifacts/`, `schemas/`, and `scripts/` must not enter the packaged plugin.

2. Evidence-first means claim-scoped evidence, not repository-wide search.

A Groundwork answer should inspect the source needed for the claim being made. It should not front-load broad repository scans, historical baselines, or maintainer docs unless the user request, risk, or evidence boundary requires them.

3. Strict gates are lazy-loaded by risk and explicit scope.

Public `SKILL.md` entry files should route to shared gates or branch references. They should not inline long examples, full package schemas, or low-frequency closeout templates unless the strict gate is always required for that skill's invocation.

## Source Gates

`scripts/check_runtime_package_boundary.py` builds a fresh local marketplace package and fails when:

- the package has top-level roots outside the allowed runtime set;
- forbidden repo-only roots are present;
- `README.md` differs from `README.runtime.md`;
- `.codex-plugin/plugin.json` is missing;
- `skills/` is missing.

`scripts/check_skill_entry_budget.py` applies the current approximate budget:

| Entry file | Max lines |
| --- | ---: |
| `skills/verify/SKILL.md` | 140 |
| `skills/implement/SKILL.md` | 140 |
| `skills/dispatch/SKILL.md` | 130 |
| `skills/handoff/SKILL.md` | 120 |

It also fails any public `SKILL.md` with a fenced inline example longer than 40 lines, and it blocks YAML schema-like blocks unless the file carries an explicit `token-budget: allow-full-yaml-schema` exemption.

These checks are approximate. They are intended to stop regressions now and can later be replaced or supplemented by official Plugin Eval static budget checks.

## Benchmark Trend

Record static and observed token budget movement whenever a package-boundary or public-entry change is benchmarked. Use `docs/plugin-eval-clean-workflow.md` for the clean benchmark procedure and preserve the run manifest path.

| Date | Change scope | Source gate | Static budget trend | Observed usage trend | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-07-01 | PR 6 token budget guardrail source gates | `check_runtime_package_boundary.py`, `check_skill_entry_budget.py` | Baseline static budget trend recording added; no Plugin Eval replacement claimed | Not run in this source-validation change | Local source checks only |
