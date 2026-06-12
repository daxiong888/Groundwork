Target Reader: Groundwork maintainer reviewing the post-RR-011B clean targeted routing rerun.
Reader Action Needed: Treat this as current targeted runtime evidence after supported plugin cache refresh, and use the three remaining failures as follow-up remediation input.
Decision Supported: Whether `routing-reliability.csv` is stable enough for default-suite promotion or still requires targeted-only remediation.
Scope: Groundwork plugin cache refresh through Codex CLI marketplace/install flow, source/marketplace/cache equivalence, `routing-reliability.csv` schema validation, targeted serial runtime rerun, and post-run source/cache mutation check.
Out Of Scope: Default-suite promotion, public skill expansion, runner fixes, prompt rewrites, staging, committing, pushing, issue closure, and manual installed-cache mutation.
Evidence Level: Supported local marketplace remove/add refresh, source/marketplace/cache SHA-256 equivalence, static validation, schema validation, and non-sandbox targeted serial runtime artifacts.

# RR-011B Clean Targeted Rerun After Cache Refresh

## Summary

- Date: 2026-06-10.
- Suite: `routing-reliability.csv`.
- Suite scope: targeted-only; `routing-reliability.csv` remains outside `DEFAULT_SUITES`.
- Runtime command: `python3 -B evals/run_runtime.py --suite routing-reliability.csv --jobs 1`.
- Run root: `/private/tmp/groundwork-runtime-v03/20260610T013252Z`.
- Result: 24 rows, 21 pass, 3 fail.
- Runtime evidence status: current targeted runtime evidence with cache/source equivalence proven before and after the run.
- Promotion decision: do not promote to default suites.

## Plugin Cache Refresh

The first install attempt used the configured `groundwork` marketplace rooted at the repository checkout, whose marketplace entry still pointed to GitHub `main`. The install command succeeded but did not refresh the installed cache for RR files:

```text
source_marketplace_drift=0
source_cache_drift=14
```

The configured `groundwork` marketplace was then switched to the existing local marketplace package, and Groundwork was removed and re-added through the Codex CLI:

```text
codex plugin marketplace remove groundwork
codex plugin marketplace add /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525
codex plugin remove groundwork@groundwork
codex plugin add groundwork@groundwork
```

CLI output:

```text
Removed marketplace `groundwork`.
Added marketplace `groundwork` from /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525.
Installed marketplace root: /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525
Removed plugin `groundwork` from marketplace `groundwork`.
Added plugin `groundwork` from marketplace `groundwork`.
Installed plugin root: /Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0
```

Current marketplace and installed plugin source:

```text
groundwork               /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525
groundwork@groundwork    installed, enabled  0.3.0    /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525/plugins/groundwork
```

## Source/Cache Equivalence

Compared package-relevant files under:

- `.codex-plugin`
- `skills`
- `docs`
- `evals`
- `CHANGELOG.md`

Ignored generated Python cache files.

Before targeted rerun:

```text
source_root= /Users/daxiong/Documents/sourceCode/Groundwork
marketplace_root= /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525/plugins/groundwork
installed_plugin_root= /Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0
compared_paths= 122
source_marketplace_drift= 0
source_cache_drift= 0
```

After targeted rerun:

```text
compared_paths= 122
source_marketplace_drift= 0
source_cache_drift= 0
```

## Pre-Run Gates

| Check | Result |
| --- | --- |
| `git diff --check` | pass |
| CSV parse for `evals/prompts/*.csv` | pass, `csv ok` |
| `python3 -B evals/run_runtime.py --validate-schema --suite routing-reliability.csv` | pass, 24 rows, 24 routing rows, 0 errors |
| `DEFAULT_SUITES` membership check | `routing-reliability.csv in DEFAULT_SUITES: False` |

## Runtime Result

Command:

```text
python3 -B evals/run_runtime.py --suite routing-reliability.csv --jobs 1
```

Result:

```text
run_root=/private/tmp/groundwork-runtime-v03/20260610T013252Z
rows=24
jobs=1
counts={"pass": 21, "fail": 3}
```

Routing summary:

```text
best_route_hit_at_1=22/24
acceptable_route_coverage=22/24
forbidden_route_hits=2/24
invalid_host_preemption=0/24
```

Route-pair confusion:

```text
direct -> direct: 2
direct -> implement: 1
implement -> implement: 7
prototype -> prototype: 2
to-issues -> to-issues: 1
to-prd -> implement: 1
to-prd -> to-prd: 5
verify -> verify: 4
write-plan -> write-plan: 1
```

Verdict dimension counts:

```text
routing_verdict: fail=2, pass=22
host_preemption_verdict: not_applicable=20, pass=4
output_contract_verdict: pass=24
evidence_verdict: fail=1, pass=23
behavior_verdict: fail=1, pass=23
overall_verdict: fail=3, pass=21
```

## Remaining Failures

| ID | Expected | Actual | Failure Type | Fix Locus | Notes |
| --- | --- | --- | --- | --- | --- |
| `rr-005` | `to-prd` | `implement` | `premature_implementation` | `requirement_state_gate` | Raw product/workflow intent still entered the implementation-ready path. |
| `rr-009` | `implement` | `implement` | `legacy_runtime_check` | `runtime_verdict` | Route and multidimensional verdicts pass, but the legacy gate-field checker still fails on required English labels. |
| `rr-021` | `direct` | `implement` | `forbidden_route` | `routing_surface` | A runtime-safety-gate style remote-write request was handled by public `implement` instead of direct/runtime safety handling. |

### Failure Details

`rr-005`:

```text
forbidden route hit: implement; raw intent entered implementation-ready path; raw or draft requirement entered implementation before acceptance or explicit bypass; expected route in ['to-prd'], loaded implement
```

The final response did not edit files, but it loaded `implement` and produced an implementation-readiness style stop. This is still a routing failure because raw product/workflow intent should enter PRD shaping first.

`rr-009`:

```text
missing gate fields: Proposed Action, Target, Risk, Rollback/Undo, Approval Needed
```

The case routed to `implement`, and the routing, output, evidence, and behavior dimensions passed. The failure is from the legacy runtime checker path, so the next remediation should align or retire that duplicate gate-field judgment rather than change the route.

`rr-021`:

```text
forbidden route hit: implement; expected route in ['direct', 'runtime-safety-gate'], loaded implement
```

The final response included the requested gate fields and did not perform the remote write, but the public `implement` route still preempted a runtime-safety-gate scenario. The next remediation should focus on routing-surface separation between public skill-owned gates and host/runtime safety handling.

## Post-Run Boundary

Post-run checks:

| Check | Result |
| --- | --- |
| Source/marketplace/cache equivalence | pass, 122 paths, 0 drift |
| `find evals -maxdepth 1 -type d -name __pycache__ -print` | no output |
| `git diff --check` | pass |
| `git status --short` | unchanged inherited RR dirty state plus this baseline file |

No staging, commit, push, issue closure, default-suite promotion, public skill expansion, or manual installed-cache mutation was performed.

## Conclusion

RR-011B improved the targeted gate materially: the clean rerun now has cache/source equivalence and 21/24 pass. The suite should remain targeted-only because two routing failures and one legacy verdict failure remain. The next fix should be scoped to:

1. raw product/workflow intent still entering `implement` (`rr-005`);
2. legacy gate-field checker drift from the multidimensional verdict model (`rr-009`);
3. runtime-safety-gate versus public `implement` separation (`rr-021`).
