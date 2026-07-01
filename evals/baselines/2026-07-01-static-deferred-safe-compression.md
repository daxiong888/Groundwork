# Static Deferred Safe Compression Baseline

Target Reader: Groundwork maintainers reviewing static plugin-eval budget work.
Reader Action Needed: Use this as repo-only evidence for the first static deferred cleanup pass and for deciding whether the next pass should keep compressing references or introduce an advanced/runtime package split.
Decision Supported: Whether active static budget is under the next target and which deferred references remain the largest safe contracts.
Artifact Type: static budget evidence snapshot
Source of Truth: Local `plugin-eval analyze` runs against a freshly built local runtime package on 2026-07-01.
Scope: Static estimated token budgets only: trigger, invoke, deferred, active, and top deferred file classification.
Out of Scope: Runtime token usage, installed cache equivalence, release readiness, UAT readiness, customer readiness, or full Plugin Eval benchmark behavior.
Evidence Level: Source/local-package static estimate. Not runtime execution evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Summary

This pass achieved the active static target without cutting high-risk verify release/runtime/cache boundaries.

| Metric | Before | After | Target | Status |
| --- | ---: | ---: | ---: | --- |
| `trigger_cost_tokens` | 759 | 759 | no change expected | unchanged |
| `invoke_cost_tokens` | 13,184 | 11,240 | active <= 12,000 with trigger | improved |
| `active_static_tokens` | 13,943 | 11,999 | <= 12,000 | pass |
| `deferred_cost_tokens` | 138,083 | 114,678 | <= 90,000 first target | partial |

## Compression Applied

- Compressed active entry files for `to-prd`, `dispatch`, `wiki`, `prototype`, `to-issues`, and `triage`.
- Compressed dispatch examples and adapter templates by replacing full YAML specimens with compact field matrices and hard-negative lists.
- Compressed shared references `WORKFLOW-STATE-MACHINE.md`, `GRILLING.md`, `LLM-WIKI.md`, and `LIFECYCLE-PREFLIGHT.md`.
- Kept verify release/runtime/cache references and core role/evidence/non-executor boundaries intact.

## Top Deferred Classification After Pass

| File | Tokens | Classification | Rationale |
| --- | ---: | --- | --- |
| `skills/dispatch/DISPATCH-PACKAGE-DETAILS.md` | 3,281 | keep-runtime-reference / compress-later | Adapter-ready package field validation and managed-worktree admissibility. |
| `skills/dispatch/adapters/codex_app_managed_worktree_thread/DISPATCH-PACKAGE-CONTRACT.md` | 2,514 | keep-runtime-reference | Runtime adapter contract. Do not move without an advanced package split. |
| `skills/dispatch/adapters/codex_app_managed_worktree_thread/MERGE-BACK-PROTOCOL.md` | 2,387 | keep-runtime-reference | Merge-back safety contract and closeout boundary. |
| `skills/_shared/RUNTIME-CAPABILITY.md` | 2,339 | keep-runtime-reference | Runtime/tool enforcement evidence boundary. |
| `skills/_shared/LLM-WIKI.md` | 2,278 | compress-later | Useful runtime contract, already compressed once; more reduction possible. |
| `skills/_shared/EVIDENCE-BOUNDARY.md` | 2,243 | keep-runtime-reference | Central evidence hierarchy; high-risk to over-compress. |
| `skills/dispatch/COMPLEX-WORK-SEPARATION.md` | 2,146 | keep-runtime-reference / compress-later | Role separation and managed-worktree closeout boundary. |
| `skills/_shared/WORKFLOW-STATE-MACHINE.md` | 2,098 | compress-later | Canonical routing/eval token contract; already compressed once. |
| `skills/_shared/LIFECYCLE-STATE.md` | 2,082 | compress-later | Durable recovery state contract. |
| `skills/dispatch/adapters/codex_app_managed_worktree_thread/REVIEW-PACKAGE-TEMPLATE.md` | 1,934 | compress-later | Template content can likely be reduced further. |
| `skills/_shared/tools/lint_goal_contract.py` | 1,931 | keep-runtime-reference | Installed runtime references this linter path in Goal Contract docs. |
| `skills/_shared/REVIEW-LOOP.md` | 1,861 | keep-runtime-reference | Clean-review/remediation loop boundary. |
| `skills/_shared/SKILL-QUALITY.md` | 1,850 | compress-later | Public-skill quality contract; likely table-compressible. |
| `skills/_shared/SKILL-AUDIT.md` | 1,842 | compress-later | Audit rubric; not on targeted runtime path. |
| `skills/dispatch/adapters/codex_app_managed_worktree_thread/ADAPTER.md` | 1,842 | keep-runtime-reference | Core runtime adapter contract. |

## Interpretation

The safe compression pass reduced deferred by 23,405 tokens, but not to the 90k target. The remaining top deferred files are mostly safety contracts: adapter contract, merge-back, runtime capability, evidence hierarchy, role separation, lifecycle state, review loop, and Goal Contract linting.

Further deferred reduction should be split into one of two paths:

1. Continue low-risk compression of `REVIEW-PACKAGE-TEMPLATE.md`, `SKILL-QUALITY.md`, `SKILL-AUDIT.md`, `LIFECYCLE-STATE.md`, and `COMPLEX-WORK-SEPARATION.md`.
2. If plugin-eval static score still treats deferred as a release blocker after another safe pass, design an advanced package split that keeps the default runtime package small while preserving high-risk references in an explicit advanced/maintainer package.

## Verification Command

```bash
tmp=$(mktemp -d /private/tmp/gw-static-after.XXXXXX)
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
{'trigger_cost_tokens': 759, 'invoke_cost_tokens': 11240, 'deferred_cost_tokens': 114678}
active 11999
```
