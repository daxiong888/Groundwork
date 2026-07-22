# Optional Runtime Eval Gate

Target Reader: Groundwork maintainers deciding whether to run real Codex runtime evals after the schema/source CI gate.
Reader Action Needed: Use this as the checklist for opt-in runtime eval evidence, artifact handling, and non-readiness boundaries.
Decision Supported: Whether a maintainer-run Codex runtime eval has enough named evidence to support a scoped review claim.
Artifact Type: maintainer doc
Source of Truth: `docs/prd-v0.4.x-trace-first-eval-platform-roadmap.md`, `artifacts/v0.4.x-trace-first-eval-platform-roadmap/issue-map.md`, `docs/eval-trace-artifacts.md`, and `.github/workflows/evals.yml`.
Scope: Optional Codex runtime eval execution guidance, required evidence fields, scratch/promotion boundaries, redaction requirements, and example commands for V045-002.
Out of Scope: Default CI runtime execution, secrets provisioning, Codex CLI installation, plugin cache refresh automation, report promotion automation, release approval, UAT approval, customer readiness, PR creation, tracker writes, or artifact auto-commit.
Evidence Level: Documentation and policy only. This file defines the optional runtime evidence path; it does not execute runtime evals or prove installed plugin behavior.
Safe to Share / Redaction Notes: Safe to share as maintainer documentation. It contains command templates and policy text only; no secrets, credentials, PII, raw traces, runtime logs, or private payloads.

## Core Boundary

The default eval CI gate is schema/source-only. It compiles Python files, parses prompt CSVs, runs dependency-free unit tests, validates schema-shaped fixtures, and runs fixture CLIs. Prompt headers, canonical row IDs, required trace-ready columns, and non-empty row sets are validated before row normalization, and `--validate-schema --all-prompts` checks targeted-only and fixture-only rows before the runtime-only execution filter. It does not run Codex runtime, does not require secrets, and does not prove installed plugin behavior.

Runtime eval is opt-in maintainer evidence. A maintainer may run it locally or in a managed environment when they have an explicit reason to inspect real Codex behavior. Runtime eval output is not a release, UAT, cache, marketplace, or customer-readiness claim by itself.

## Required Evidence Fields

Any runtime eval claim must name:

- `installed_plugin_root`: the installed Groundwork plugin root used by Codex runtime;
- `source_root`: the repository source root or commit under evaluation;
- `source_cache_equivalence`: the refresh command, install method, or equivalence check connecting source to installed plugin cache;
- `run_scope`: suites, rows, case filters, retries, timeout policy, and whether the run is targeted or broad;
- `commands_or_trials`: exact commands or trials executed; use `suite:<registered-suite.csv>`, `group:<exact-group>`, `case_id:<exact-id>`, or `prompt_file:<canonical-absolute-path>` for Groundwork runtime selectors, and preserve the exact case ID when reviewing the runner's reversibly encoded per-case artifact path;
- `limitations`: known missing coverage, unstable environment details, skipped suites, and non-deterministic factors;
- `missing_evidence`: evidence not collected and why it matters;
- `redaction_status`: `not_needed`, `applied`, `failed`, or `not_reviewed`;
- `redaction_reviewer`: `human`, `tool`, or `unknown`.

If any required field is missing, keep the claim scoped as incomplete runtime evidence.

## Scratch And Promotion

Runtime output belongs in ignored scratch space by default:

```text
.groundwork/harness/<run-id>/
```

Do not commit raw traces, raw command output, browser logs, model transcripts, private paths, cookies, tokens, credentials, PII, production payloads, or unreviewed final responses.

Promotion into `artifacts/evals/<run-id>/` is optional and must follow `docs/eval-trace-artifacts.md`. Promoted artifacts must be redacted, reviewable, and explicit about target reader, reader action, source, run scope, redaction status, limitations, and missing evidence.

## Example Commands

These examples are not release gates. Adjust suite, timeout, plugin root, source root, and scratch path for the maintained environment.

Source/schema gate, no runtime:

```bash
python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv
```

Optional runtime eval in a maintainer-managed environment:

```bash
GROUNDWORK_RUNTIME_ROOT=".groundwork/harness" \
python evals/run_runtime.py --suite trace-first-verify-review.csv --case-timeout 360
```

When documenting a Codex CLI-backed runtime run, state:

```text
Requires maintainer-managed Codex CLI environment and credentials.
Do not commit raw logs or traces.
Do not claim installed plugin behavior unless source/cache equivalence is documented.
```

## Evidence Record Template

```yaml
runtime_eval_evidence:
  installed_plugin_root: ""
  source_root: ""
  source_ref: ""
  source_cache_equivalence: ""
  run_scope:
    suites: []
    cases: []
    retries: 0
    timeout_seconds: null
    targeted_or_broad: targeted
  commands_or_trials: []
  scratch_root: ".groundwork/harness/<run-id>"
  promoted_artifacts: []
  redaction:
    status: not_reviewed
    reviewer: unknown
    notes: []
  limitations: []
  missing_evidence: []
  readiness_claims:
    runtime_behavior: scoped_only
    release: not_claimed
    uat: not_claimed
    customer: not_claimed
```

## Promotion Checklist

Before promoting runtime eval evidence:

- confirm raw traces stay in `.groundwork/harness/` unless redacted;
- confirm every promoted trace file is marked `.redacted.jsonl`;
- confirm `report.md` cites source artifacts and limitations;
- confirm `patch-suggestions.json` is advisory and has `auto_apply: false`;
- confirm redaction status is not `failed`;
- confirm `not_reviewed` artifacts contain only non-sensitive metadata;
- confirm the final claim does not exceed the named evidence.

## Non-Goals

- no default CI runtime eval;
- no required secrets in CI;
- no `codex exec` in source/schema gate;
- no automatic artifact commit;
- no automatic PR, issue, tracker, release, or UAT mutation;
- no release readiness from local runtime output alone;
- no customer readiness from report, score, trace, or patch suggestion artifacts alone.
