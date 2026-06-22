# Release Evidence Claim Boundary

Target Reader: Groundwork maintainers, release reviewers, CI gate authors, runtime eval operators, and clean-review coordinators.
Reader Action Needed: Use this template before saying an eval platform change is runtime-verified, release-ready, UAT-ready, customer-ready, cache-equivalent, or marketplace-ready.
Decision Supported: Whether a readiness claim is source-only, runtime-verified, release-ready, UAT/customer-ready, unsupported, or intentionally not claimed.
Artifact Type: maintainer doc
Source of Truth: `docs/prd-v0.4.x-trace-first-eval-platform-roadmap.md`, `artifacts/v0.4.x-trace-first-eval-platform-roadmap/issue-map.md`, `docs/optional-runtime-eval-gate.md`, `docs/eval-trace-artifacts.md`, and the v0.4.0 release evidence plan.
Scope: Release evidence claim vocabulary, required fields, source/runtime/release/UAT boundaries, and minimal v0.4.x eval release claim examples for V045-003.
Out of Scope: Running CI, running Codex runtime evals, refreshing plugin cache, proving cache/source equivalence, publishing releases, approving UAT, customer acceptance, marketplace publishing, or committing runtime artifacts.
Evidence Level: Documentation and template only. This file defines the claim shape and review boundary; it does not verify runtime behavior or release readiness.
Safe to Share / Redaction Notes: Safe to share as maintainer documentation. It contains templates and examples only; no secrets, credentials, PII, raw traces, private URLs, runtime logs, or customer payloads.

## Core Boundary

Docs, schema files, unit tests, prompt CSV parsing, source-only CI, report generation, and patch suggestion generation are `source_validation` evidence. They can support implementation conformance and review confidence, but they are not runtime verification and cannot by themselves prove release, UAT, customer, marketplace, or cache readiness.

Runtime verification requires a named runtime environment and evidence that the runtime used the intended source or installed plugin cache. Release readiness requires a broader maintainer decision over source, runtime, cache/source equivalence, open risks, limitations, and missing evidence. UAT and customer readiness require separate UAT/customer evidence.

## Claim Types

Use one of these `claim_type` values:

- `source_validation`: source, schema, CSV, unit test, static fixture, report, or documentation evidence only.
- `runtime`: real Codex runtime behavior was exercised.
- `cache`: installed plugin cache state or source/cache equivalence was checked.
- `release`: maintainer release-readiness decision.
- `uat`: UAT-readiness or UAT result claim.
- `customer`: customer-readiness or customer-acceptance claim.
- `marketplace`: marketplace package or install-path readiness claim.
- `cache_refresh`: supported plugin cache refresh action.
- `not_applicable`: readiness is intentionally not claimed.

Use one of these `evidence_status` values:

- `verified`: the required evidence for this claim type is present and named.
- `partial`: some evidence exists, but required fields or checks are missing.
- `unverified`: the claim is being discussed but lacks required evidence.
- `not_applicable`: the claim is intentionally out of scope.

## Required Template

Every runtime, cache, release, UAT, customer, marketplace, or cache-refresh claim must use this shape. Source-only claims should also use it when there is a risk of being mistaken for runtime or release evidence.

```yaml
release_evidence_claim:
  claim_type: source_validation | runtime | cache | release | uat | customer | marketplace | cache_refresh | not_applicable
  claim: ""
  evidence_status: verified | partial | unverified | not_applicable
  installed_plugin_root: ""
  source_root: ""
  source_ref: ""
  refresh_or_equivalence:
    method: refresh_step | source_cache_equivalence | tracked_commit_equivalence | not_run | not_applicable
    evidence: ""
  run_scope:
    kind: targeted | full | smoke | not_run | not_applicable
    suites: []
    cases: []
    commands_or_trials: []
  redaction:
    status: not_needed | applied | failed | not_reviewed | not_applicable
    reviewer: human | tool | unknown | not_applicable
    notes: []
  limitations: []
  missing_evidence: []
  readiness_claims:
    runtime: not_claimed | source_only | verified
    cache: not_claimed | partial | verified
    release: not_claimed | partial | verified
    uat: not_claimed | partial | verified
    customer: not_claimed | partial | verified
```

Required fields:

- `claim_type`
- `evidence_status`
- `installed_plugin_root`
- `source_root`
- `refresh_or_equivalence.method`
- `refresh_or_equivalence.evidence`
- `run_scope.kind`
- `run_scope.commands_or_trials`
- `limitations`
- `missing_evidence`

If a required field is not applicable, write `not_applicable` and explain why in `limitations` or `missing_evidence`.

## Evidence Status Rules

`source_validation` may be `verified` from commands such as:

- Python syntax checks;
- prompt CSV parsing;
- schema validation;
- unit tests;
- fixture CLI runs;
- `git diff --check` over the relevant diff.

`source_validation` must not be rewritten as `runtime`, `release`, `uat`, or `customer` unless the corresponding evidence fields are present.

`runtime` cannot be `verified` unless:

- `installed_plugin_root` is named;
- `source_root` and `source_ref` are named;
- refresh or source/cache equivalence is documented;
- run scope and exact commands/trials are named;
- limitations and missing evidence are explicit;
- raw traces or logs are kept in scratch or redacted before promotion.

`release` cannot be `verified` unless:

- source validation is complete for the release scope;
- runtime/cache evidence required by the release decision is named or explicitly marked not required;
- open P1/P2 risks are resolved or accepted by a maintainer;
- missing evidence is documented;
- release-specific limitations are explicit.

`uat` and `customer` cannot be `verified` from source validation, runtime eval, score JSON, reports, traces, or patch suggestions alone. They require separate UAT/customer evidence from the relevant environment, data, reviewer, or customer acceptance process.

## Minimal v0.4.x Eval Examples

Schema/source-only CI evidence:

```yaml
release_evidence_claim:
  claim_type: source_validation
  claim: "v0.4.x trace-first eval schema/source gate passed locally or in CI."
  evidence_status: verified
  installed_plugin_root: not_applicable
  source_root: "$SOURCE_ROOT"
  source_ref: "$COMMIT_SHA"
  refresh_or_equivalence:
    method: not_applicable
    evidence: "No installed plugin cache is used by the schema/source gate."
  run_scope:
    kind: targeted
    suites:
      - trace-first-verify-review.csv
    cases: []
    commands_or_trials:
      - "python evals/run_runtime.py --validate-schema --suite trace-first-verify-review.csv"
      - "python -m unittest evals.test_schema_validation evals.test_scoring evals.test_checks evals.test_trace_diagnostics evals.test_report evals.test_patch_suggestions"
      - "PYTHONPATH=evals python -m unittest evals.test_run_runtime_scheduler"
      - "python evals/report.py --run-dir evals/fixtures/report"
      - "python evals/patch_suggestions.py --run-dir evals/fixtures/patch-suggestions"
  redaction:
    status: not_applicable
    reviewer: not_applicable
    notes:
      - "No raw runtime trace or private payload is produced by this source-only gate."
  limitations:
    - "This does not run Codex runtime."
    - "This does not prove installed plugin cache behavior."
    - "This does not claim release, UAT, or customer readiness."
  missing_evidence:
    - "installed plugin root"
    - "source/cache equivalence"
    - "real runtime eval output"
    - "release approval"
    - "UAT/customer evidence"
  readiness_claims:
    runtime: source_only
    cache: not_claimed
    release: not_claimed
    uat: not_claimed
    customer: not_claimed
```

Optional runtime evidence after a maintainer-managed run:

```yaml
release_evidence_claim:
  claim_type: runtime
  claim: "Targeted trace-first verify/review runtime behavior was exercised for a maintained environment."
  evidence_status: partial
  installed_plugin_root: "$INSTALLED_PLUGIN_ROOT"
  source_root: "$SOURCE_ROOT"
  source_ref: "$COMMIT_SHA"
  refresh_or_equivalence:
    method: source_cache_equivalence
    evidence: "Record the exact refresh command or equivalence check here."
  run_scope:
    kind: targeted
    suites:
      - trace-first-verify-review.csv
    cases: []
    commands_or_trials:
      - "GROUNDWORK_REPO=\"$PWD\" GROUNDWORK_RUNTIME_ROOT=\".groundwork/harness\" python evals/run_runtime.py --suite trace-first-verify-review.csv --case-timeout 360"
  redaction:
    status: not_reviewed
    reviewer: unknown
    notes:
      - "Raw runtime output remains in `.groundwork/harness/` until redaction review."
  limitations:
    - "This is targeted runtime evidence only."
    - "Release readiness still requires maintainer decision and missing-evidence review."
  missing_evidence:
    - "redacted promoted report"
    - "release approval"
    - "UAT/customer evidence"
  readiness_claims:
    runtime: verified
    cache: partial
    release: not_claimed
    uat: not_claimed
    customer: not_claimed
```

Unsupported release claim:

```yaml
release_evidence_claim:
  claim_type: release
  claim: "v0.4.x eval platform is release-ready."
  evidence_status: unverified
  installed_plugin_root: ""
  source_root: "$SOURCE_ROOT"
  source_ref: "$COMMIT_SHA"
  refresh_or_equivalence:
    method: not_run
    evidence: "Only source/schema checks were run."
  run_scope:
    kind: not_run
    suites: []
    cases: []
    commands_or_trials: []
  redaction:
    status: not_applicable
    reviewer: not_applicable
    notes: []
  limitations:
    - "Source/schema checks alone are not release evidence."
  missing_evidence:
    - "installed plugin root"
    - "source/cache equivalence or supported refresh"
    - "runtime eval evidence if required by release scope"
    - "maintainer release decision"
    - "UAT/customer evidence if claimed"
  readiness_claims:
    runtime: source_only
    cache: not_claimed
    release: not_claimed
    uat: not_claimed
    customer: not_claimed
```

## Review Checklist

- The claim has a `release_evidence_claim` object.
- `claim_type` and `evidence_status` match the actual evidence.
- Source-only evidence is not labeled `runtime_verified`.
- CI pass is not treated as release readiness.
- Runtime eval pass is not treated as UAT or customer readiness.
- Installed plugin root is named for runtime/cache/plugin claims.
- Source root and source ref are named.
- Refresh or source/cache equivalence is named, or explicitly not applicable.
- Run scope and exact commands/trials are listed.
- Limitations and missing evidence are non-empty for partial or unverified claims.
- Raw traces/logs are scratch-only or redacted before promotion.
- UAT/customer readiness has separate environment, data, reviewer, or customer evidence.

## Non-Goals

- no automatic release approval;
- no automatic UAT/customer acceptance;
- no runtime eval execution from this template;
- no plugin cache mutation;
- no raw trace or runtime log commits;
- no readiness promotion from score JSON, report, or patch suggestions alone.
