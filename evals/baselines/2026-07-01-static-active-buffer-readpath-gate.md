# Static Active Buffer And Read-Path Gate Baseline

Target Reader: Groundwork maintainers reviewing static-budget and clean targeted read-path guardrail work.
Reader Action Needed: Use this repo-only checkpoint as the accepted baseline after commit `09676f3b55e335eb7d5bf406231b6c6bd70122d3`.
Decision Supported: Whether the active static budget now has usable buffer and whether clean targeted runtime read paths are guarded by exact package read allowlists.
Artifact Type: static budget and source-validation evidence snapshot.
Source of Truth: Local `plugin-eval analyze` against a freshly built local runtime package, local unit/eval checks, and commit `09676f3b55e335eb7d5bf406231b6c6bd70122d3`.
Scope: Static estimated token budgets, clean targeted regression gate shape, detector coverage, and line-budget guardrails.
Out of Scope: Runtime token usage, installed cache equivalence, clean targeted benchmark rerun behavior, release readiness, UAT readiness, customer readiness, or full Plugin Eval suite behavior.
Evidence Level: Source/local-package static estimate plus local validation. Not runtime execution evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Summary

Commit: `09676f3b55e335eb7d5bf406231b6c6bd70122d3`

This checkpoint is accepted as the current static/read-path guardrail baseline. The active static budget is now below the stage target with usable buffer, and the clean targeted read-path regression gate uses exact package read allowlists instead of a small blacklist.

| Metric | Value | Target | Status |
| --- | ---: | ---: | --- |
| `trigger_cost_tokens` | 587 | no hard target | pass |
| `invoke_cost_tokens` | 10,653 | no hard target | pass |
| `active_static_tokens` | 11,240 | <= 11,500 | pass |
| `deferred_cost_tokens` | 111,421 | <= 105,000 | partial |

## Guardrail Changes

- `scripts/check_plugin_eval_clean_regression.py` replaced package-read blacklist checks with `EXPECTED_PACKAGE_READS`.
- `to-prd` clean targeted package reads are limited to `plugins/groundwork/skills/to-prd/SKILL.md`.
- `verify` clean targeted package reads are limited to:
  - `plugins/groundwork/skills/verify/SKILL.md`
  - `plugins/groundwork/skills/verify/VERIFY-SCOPE.md`
  - `plugins/groundwork/skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`
- `dispatch` clean targeted package reads are limited to:
  - `plugins/groundwork/skills/dispatch/SKILL.md`
  - `plugins/groundwork/skills/dispatch/DISPATCH-PACKAGE.md`
- Unexpected package reads fail the regression gate as `unexpected package reads`.
- `extract_package_file_reads()` now detects common read commands including `python3`, `head`, `tail`, `grep`, `rg`, `perl`, and `node`.
- All public `SKILL.md` files are covered by `scripts/check_skill_entry_budget.py` line budgets.

## Compression Applied

- Public skill descriptions and active entries were shortened to create active-budget buffer.
- Low-risk deferred references were compressed into checklist/table form:
  - `skills/_shared/LIFECYCLE-STATE.md`
  - `skills/_shared/LLM-WIKI.md`
  - `skills/_shared/SKILL-AUDIT.md`
  - `skills/_shared/SKILL-QUALITY.md`
  - `skills/_shared/WORKFLOW-STATE-MACHINE.md`
  - `skills/dispatch/COMPLEX-WORK-SEPARATION.md`
  - `skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md`

## Deferred Stop Reason

The deferred target was not pushed to `<= 105,000` in this pass. The remaining deferred weight is concentrated in safety contracts such as dispatch full package details, managed-worktree adapter contracts, merge-back protocol, runtime capability, evidence boundary, review loop, role separation, and related package templates.

Further compression should not hard-cut these contracts inside the same default runtime package. If deferred remains a blocker, use one of these routes:

1. Rerun clean targeted runtime benchmark first to confirm behavior remains stable.
2. Design an advanced/runtime split that moves advanced or maintainer-only references out of the default runtime package while preserving safety contracts.

## Verification

Checks run locally before commit `09676f3b55e335eb7d5bf406231b6c6bd70122d3`:

```text
python3 -m unittest evals.test_plugin_eval_clean evals.test_progressive_disclosure
python3 -m unittest discover evals
python3 scripts/check_skill_entry_budget.py
python3 scripts/check_runtime_package_boundary.py
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
git diff --check
```

Static estimate command:

```bash
tmp=$(mktemp -d /private/tmp/gw-static-final.XXXXXX)
python3 scripts/build_local_marketplace.py --output "$tmp/marketplace" >/dev/null
node /Users/daxiong/.codex/plugins/cache/openai-curated-remote/plugin-eval/0.1.2/scripts/plugin-eval.js analyze "$tmp/marketplace/plugins/groundwork" --format json --output "$tmp/analyze.json" >/dev/null
python3 - <<'PY' "$tmp/analyze.json"
import json, sys
b = json.load(open(sys.argv[1]))["budgets"]
vals = {k: b[k]["value"] for k in ["trigger_cost_tokens", "invoke_cost_tokens", "deferred_cost_tokens"]}
print(vals)
print("active", vals["trigger_cost_tokens"] + vals["invoke_cost_tokens"])
PY
```

Observed output:

```text
{'trigger_cost_tokens': 587, 'invoke_cost_tokens': 10653, 'deferred_cost_tokens': 111421}
active 11240
```

## Current Recommendation

Do not continue small deferred text-compression passes as the default next step. The next validation step should be a clean targeted runtime benchmark rerun against the refreshed package/cache path, using the exact read-path gate:

```text
to-prd <= 35k
verify <= 55k
dispatch <= 50k
total <= 140k
model turns per scenario == 1
unexpected package reads == 0
forbidden scans == 0
nested commands == 0
```

If that runtime benchmark remains stable, close this optimization stage and open a separate advanced/runtime split design if deferred static cost remains strategically important.
