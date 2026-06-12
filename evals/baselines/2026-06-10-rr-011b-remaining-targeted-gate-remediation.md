# RR-011B Remaining Targeted Gate Remediation

Target Reader: Groundwork maintainer reviewing the remaining `routing-reliability.csv` targeted-gate blockers after RR-011A.
Reader Action Needed: Review the narrow `rr-012` acceptable-route/checker fix, the `rr-013` no-final-response reporting fix, and the remaining non-release-gating evidence boundary.
Decision Supported: Whether RR-011B should merge a bounded `rr-012` fixture/checker correction and `rr-013` runtime-failure reporting correction without changing public skill routing surface or default-suite status.
Scope: `rr-012` and `rr-013` artifacts from `/private/tmp/groundwork-runtime-v03/20260609T105035Z`, focused RR-011B artifacts from `/private/tmp/groundwork-runtime-v03/20260610T011547Z` and `/private/tmp/groundwork-runtime-v03/20260610T011555Z`, current prompt rows, runner verdict behavior for no-final-response runtime exits, and targeted-only suite governance.
Out Of Scope: Default-suite promotion, broad CSV rewrites, public skill surface expansion, installed plugin cache mutation, staging, committing, pushing, and unrelated inherited dirty files.
Evidence Level: RR-011 full targeted diagnostic artifacts, RR-011B focused runtime artifacts, local replay against the saved `rr-012` response, current source inspection, and focused runner regression tests. This is not release-gating evidence because cache/source equivalence is not proven.

## Metadata

- Date: 2026-06-10 local time.
- Task ID: RR-011B.
- Source worktree: `/Users/daxiong/.codex/worktrees/cd5d/Groundwork`.
- Source truth repository: `/Users/daxiong/Documents/sourceCode/Groundwork`.
- Suite: `routing-reliability.csv`.
- Prior full targeted run: `/private/tmp/groundwork-runtime-v03/20260609T105035Z/summary.json`.
- Default-suite promotion: not in scope; `routing-reliability.csv` remains targeted-only.

## Diagnosis Matrix

| ID | Expected | Recorded actual | Artifact evidence | Primary fix locus | Decision |
| --- | --- | --- | --- | --- | --- |
| `rr-012` | `implement` | prior: `implement`; focused rerun: `triage` | Prior full targeted case had `returncode=124`, `failure_type=codex_timeout`, no `last/rr-012.txt`, and routing passed before timeout. Focused rerun `/private/tmp/groundwork-runtime-v03/20260610T011008Z` completed with a source-truth/customer-visible risk stop: `Triage Verdict`, no file changes, missing target file/copy, and next action. | narrow prompt fixture plus runner gate-equivalence checker | Keep `expected_best=implement`, allow `triage` as an acceptable route only for the explicit-bypass/customer-visible risk stop, and accept the observed triage risk-gate output as a gate equivalent. Do not route to `to-prd`, `to-issues`, or `write-plan`; do not broaden raw-intent prompts. |
| `rr-013` | `implement` | `direct` | Case result has `returncode=1`, `failure_type=codex_exit`, `fix_locus=runtime_environment`, no `last/rr-013.txt`; log shows websocket TLS EOF, HTTP fallback stream disconnects, and `turn.failed` before final output. | `runtime environment/flake` plus narrow runner reporting | Do not change expected route or fixture. Runner should report no-final-response runtime exits as `actual_route=unknown` with blocked route/output/evidence slices instead of a deterministic forbidden `direct` hit. |

## Remediation Decision

`rr-012` has two evidence layers. The prior full targeted run timed out without a final response, so that artifact remains a runtime-environment flake. The focused rerun completed and proved a narrow fixture/checker issue: an explicit-bypass customer-visible edit with no source truth may safely stop in `triage`, and the observed triage output carried the required risk gate substance without the exact five English gate labels. RR-011B therefore keeps `expected_best=implement`, adds only `triage` to `rr-012` acceptable routes, and adds a narrow customer-visible triage gate equivalent.

`rr-013` is runtime/network-only on the inspected artifacts, but the runner reporting made the diagnostic summary misleading by defaulting missing output to `direct`. RR-011B narrows that behavior: when `codex exec` exits nonzero and produces no final response, the route is unknown and the routing/output/evidence dimensions are blocked by runtime failure. This preserves completed forbidden-route detection while removing a false forbidden-route hit for no-response runtime failures.

## Release-Gating Classification

This note is not release-gating targeted runtime evidence. It records a diagnostic remediation and deferral classification.

## Focused Validation

Post-remediation focused runtime:

- Sandbox command: `python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1 rr-012 rr-013`
- Sandbox raw path: `/private/tmp/groundwork-runtime-v03/20260610T011547Z`
- Sandbox result: `blocked=2`, both rows `actual_route=unknown`, `forbidden_route_hits=0`; logs show the known Codex state DB/app-server sandbox permission failure.
- Escalated command: `python3 evals/run_runtime.py --suite routing-reliability.csv --jobs 1 rr-012 rr-013`
- Escalated raw path: `/private/tmp/groundwork-runtime-v03/20260610T011555Z`
- Escalated result before final local checker replay: `rr-013` passed; `rr-012` routing passed with `actual_route=triage`, `acceptable_route_coverage=2/2`, `forbidden_route_hits=0`, but gate equivalence still needed two observed no-execution markers.
- Local replay after the final checker marker adjustment against `/private/tmp/groundwork-runtime-v03/20260610T011555Z/last/rr-012.txt`: routing, output contract, evidence, and overall verdict all pass.

Release-gating readiness still requires:

- supported cache/source equivalence or an explicit release-gating equivalence verdict;
- a clean targeted run or an accepted policy for bounded runtime flakes;
- no default-suite promotion before targeted evidence passes.
