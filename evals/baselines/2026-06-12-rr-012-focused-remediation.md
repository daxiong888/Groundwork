# RR-012 Focused Remediation Evidence

Target Reader: Groundwork maintainer reviewing the post-RR-012 routing reliability remediation.
Reader Action Needed: Use this note to decide whether the bounded RR-012 checker and routing-surface fixes have enough focused evidence to merge without a full targeted rerun.
Decision Supported: Whether the remaining `rr-005` and `rr-019` failures are closed by focused evidence while `routing-reliability.csv` stays targeted-only.
Scope: Final main-source plugin reinstall, source/marketplace/cache equivalence, focused runtime for `rr-005` and `rr-019`, and local validation after the RR-012 checker fixes.
Out of Scope: Full 24-row targeted rerun, default-suite promotion, public skill expansion, push, PR creation, issue closure, and manual installed-cache mutation.
Evidence Level: Supported `codex plugin add groundwork@groundwork`, package-relevant SHA-256 equivalence, focused runtime artifacts, schema validation, CSV parse, static diff check, and focused runner tests.

## Summary

- Date: 2026-06-12.
- Suite: `routing-reliability.csv`.
- Suite scope: targeted-only; `routing-reliability.csv` remains outside `DEFAULT_SUITES`.
- Installed plugin root: `/Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0`.
- Source root: `/Users/daxiong/Documents/sourceCode/Groundwork`.
- Marketplace source: `/Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525/plugins/groundwork`.
- Full targeted rerun: intentionally not run after the final bounded checker fixes.

## Cache/Source Equivalence

The installed cache was refreshed through the supported CLI path:

```text
codex plugin add groundwork@groundwork
```

The final package-relevant equivalence check compared:

- `.codex-plugin`
- `skills`
- `docs`
- `evals`
- `CHANGELOG.md`

Generated Python cache files were ignored.

Final result:

```text
source: /Users/daxiong/Documents/sourceCode/Groundwork
marketplace: /Users/daxiong/.codex/plugins/groundwork-local-marketplace-20260525/plugins/groundwork -> /Users/daxiong/Documents/sourceCode/Groundwork
cache: /Users/daxiong/.codex/plugins/cache/groundwork/groundwork/0.3.0
counts: source=123 marketplace=123 cache=123
same: 123
different: 0
```

## Focused Runtime Evidence

### rr-005

Command:

```text
python3 -B evals/run_runtime.py --suite routing-reliability.csv --jobs 1 rr-005
```

Run root:

```text
/private/tmp/groundwork-runtime-v03/20260612T061609Z
```

Result:

```text
id=rr-005
expected=to-prd
actual=to-prd
verdict=pass
best_route_hit_at_1=1/1
acceptable_route_coverage=1/1
forbidden_route_hits=0/1
invalid_host_preemption=0/1
routing_verdict=pass
output_contract_verdict=pass
evidence_verdict=pass
behavior_verdict=pass
overall_verdict=pass
```

Interpretation:

- The route now stays in `to-prd`.
- Draft PRD/spec artifacts such as `README.md`, `docs/*.md`, and `artifacts/*/prd.md` are treated as requirement-shaping artifacts, not implementation, when the actual route is `to-prd` and the response marks the work as draft/spec/acceptance shaping.
- Code implementation remains forbidden for raw or draft requirement rows.

### rr-019

Command:

```text
python3 -B evals/run_runtime.py --suite routing-reliability.csv --jobs 1 rr-019
```

Run root:

```text
/private/tmp/groundwork-runtime-v03/20260612T071314Z
```

Result:

```text
id=rr-019
expected=prototype
actual=prototype
verdict=pass
best_route_hit_at_1=1/1
acceptable_route_coverage=1/1
forbidden_route_hits=0/1
invalid_host_preemption=0/1
routing_verdict=pass
output_contract_verdict=pass
evidence_verdict=pass
behavior_verdict=pass
overall_verdict=pass
```

Interpretation:

- The route stays in `prototype`.
- Throwaway prototype artifacts such as root `index.html`, `prototype.html`, and `artifacts/*prototype*/index.html` are excluded from `no_file_changes` production-source evidence when `artifact_allowed=true` and the actual route is `prototype`.
- The exemption is not a general source-change waiver; it applies only to prototype artifacts under the prototype route.

## Local Validation

Commands:

```text
git diff --check
python3 -B test_run_runtime_scheduler.py
python3 -B evals/run_runtime.py --validate-schema --suite routing-reliability.csv
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
python3 -c "import evals.run_runtime as r; print('routing-reliability.csv' in r.DEFAULT_SUITES, r.DEFAULT_SUITES)"
```

Results:

```text
git diff --check: pass
test_run_runtime_scheduler.py: Ran 64 tests ... OK
schema validation: pass, 24 rows, 24 routing rows, 0 errors
plugin JSON parse: pass
CSV parse: csv ok
DEFAULT_SUITES membership: False
```

## Full Rerun Decision

No full 24-row targeted rerun was performed after the final bounded checker fixes.

Rationale:

- The final changes were narrow deterministic checker changes for already-identified row artifacts.
- `rr-005` and `rr-019` both have focused runtime pass evidence after cache/source equivalence.
- Prior focused runs showed `rr-020`, `rr-021`, `rr-022`, `rr-023`, and `rr-024` passing after the same cache/source equivalence path.
- A full rerun would spend substantial runtime without materially increasing confidence for these bounded checker changes.

Classification:

```text
focused_remediation_evidence_complete
full_targeted_release_gate_not_claimed
default_suite_promotion_not_supported
```

## Remaining Boundary

`routing-reliability.csv` remains targeted-only. A future full targeted rerun may be useful before default-suite promotion, but it is not required for this bounded RR-012 remediation closeout.
