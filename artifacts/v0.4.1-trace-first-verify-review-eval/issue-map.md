# v0.4.1 Trace-First Verify / Review Eval Issue Map

Target Reader: Groundwork maintainers implementing v0.4.1.
Reader Action Needed: Execute these issue slices in order and keep evidence boundaries explicit.
Decision Supported: How to split the v0.4.1 trace-first eval work into scoped repository changes and checks.
Artifact Type: issue map
Source of Truth: `docs/prd-v0.4.1-trace-first-verify-review-eval.md`.
Scope: Eval CSV, runner default wiring, and maintainer documentation for v0.4.1 trace-first verify/review coverage.
Out of Scope: Public skill expansion, runtime cache refresh, release baseline publication, remote issue mutation, and dependency changes.
Evidence Level: Local planning artifact derived from the v0.4.1 PRD and existing repository contracts.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, raw logs, or private payloads.

## Issues

### GW-041-1 Add trace-first verify/review eval suite

- Touches: `evals/prompts/trace-first-verify-review.csv`
- Acceptance:
  - Rows use trace-ready routing schema columns.
  - Verify rows require `output_contract=verify_scope_full` and relevant evidence tokens.
  - Dispatch rows preserve clean-review fan-out expectations without permitting risky writes.
- Verification:
  - CSV parser check succeeds.
  - Runner schema accepts the suite in dry local source validation.

### GW-041-2 Wire suite into default runtime selection

- Touches: `evals/run_runtime.py`
- Acceptance:
  - `trace-first-verify-review.csv` appears in `DEFAULT_SUITES`.
  - No new measurement token implementation is required.
- Verification:
  - Python syntax check succeeds.
  - Whitespace check succeeds.

### GW-041-3 Document maintainer usage and evidence limits

- Touches: `docs/nightly-harness.md`
- Acceptance:
  - The nightly harness suite list names the v0.4.1 trace-first suite.
  - The doc states that local CSV/source validation is not runtime/cache/release/UAT evidence.
- Verification:
  - Documentation diff is minimal and source-truth-bearing claims cite only existing local contracts.
