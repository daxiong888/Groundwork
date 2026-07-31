Target Reader: Groundwork maintainers, clean reviewers, and verifiers reviewing the frozen GPT-5.6 skill-contract hardening PRD.
Reader Action Needed: Verify that each Phase 0 correction was committed and passed on a clean state before any Phase 1 candidate was applied.
Decision Supported: Whether the Phase 0 validation baseline satisfies the frozen PRD ordering and evidence requirements.
Artifact Type: baseline validation report
Source of Truth: `docs/prd-gpt-5.6-skill-contract-hardening.md`, commit `e070e1c`, and the listed local commits and deterministic command results.
Scope: G56-BASE-001, G56-BASE-002, and G56-BASE-003 source/deterministic validation before Phase 1.
Out of Scope: Installed plugin cache, model/runtime execution, clean review, release, UAT, marketplace, and customer readiness.
Evidence Level: Local source and deterministic self-check evidence captured from clean sequential commits; not independent review evidence.
Safe to Share / Redaction Notes: Safe to share as-is; no credentials, private payloads, PII, or sensitive logs are included.

# GPT-5.6 Phase 0 Validation Baseline

Frozen source base: `e070e1cdb75e649b651471ef53f2ade22bb7a8db`

Tracked PRD commit: `893ad60`

## G56-BASE-001 — `to-issues` active-suite sanitation

Correction commit: `5b2e661da263079e7fba1b5391ec691e4ac96cf2`

Candidate isolation: `git diff HEAD^ HEAD` contained only the four authorized prompt CSV files. No `skills/` file or Phase 1 candidate was present.

| Check | Result |
| --- | --- |
| Parse every `evals/prompts/*.csv` with `csv.DictReader` | `csv ok` |
| `python3 -B evals/run_runtime.py --validate-schema --suite to-issues.csv --suite routing-reliability.csv --suite smoke.csv --suite lifecycle-preflight-regressions.csv` | Pass; 4 suites, 80 rows, 0 errors |
| `python3 -B -m unittest evals.test_coverage_manifest` | Pass; 9 tests |
| Exact changed-row allowlist check | Pass; only `to-issues-001`–`003`, `006`–`008`, `013`–`018`, `rr-003`, `rr-planmode-accepted-001`, `sx-002`, `life-023`, and `life-024` changed |
| Read-only invariants | Pass; `life-018` and `life-022` unchanged; `to-issues-013`–`018` absent; `Verification Evidence Needed` absent; `skills/` unchanged |

## G56-BASE-002 — `to-prd` progressive-disclosure oracle

Correction commit: `68ec82472bc1bc97100705b6845e6067c16632e3`

Candidate isolation: `git diff HEAD^ HEAD` contained only `evals/test_progressive_disclosure.py`. `skills/to-prd/*` still matched `e070e1c`, and the Phase 1C durable-mode test was absent.

| Check | Result |
| --- | --- |
| `python3 -B -m unittest evals.test_progressive_disclosure.ProgressiveDisclosureTests.test_to_prd_has_prompt_provided_compact_fast_path` | Pass; 1 test |
| Correction scope check | Pass; one test file only; no `skills/to-prd/*` diff |
| Candidate-oracle exclusion check | Pass; no Phase 1C durable-mode test or candidate-only sentence |

## G56-BASE-003 — Dispatch package-only oracle

Correction commit: `5b802f57d6a93872a40fddddc14db5e3091dd0d3`

Candidate isolation: `git diff HEAD^ HEAD` contained only `evals/prompts/dispatch.csv::dispatch-009`. `skills/dispatch/*` was unchanged and `dispatch-022` was absent.

| Check | Result |
| --- | --- |
| `python3 -B evals/run_runtime.py --validate-schema --suite dispatch.csv` as part of the cumulative Phase 0 schema run | Pass; dispatch suite contained 21 rows |
| Correction scope check | Pass; one CSV file and only `dispatch-009` changed |
| Package-only oracle check | Pass; execution remains with the owning runtime/operator even when explicitly requested and tools are available |

## Completed Phase 0 Validation Baseline

The cumulative clean state after G56-BASE-003 contained the tracked PRD, the three isolated corrections, and the first two evidence updates, with no Phase 1 candidate.

| Check | Result |
| --- | --- |
| Parse every `evals/prompts/*.csv` with `csv.DictReader` | `csv ok` |
| Schema validation for `dispatch.csv`, `to-issues.csv`, `routing-reliability.csv`, `smoke.csv`, and `lifecycle-preflight-regressions.csv` | Pass; 5 suites, 101 rows, 0 errors |
| Coverage manifest plus corrected BASE-002 target unittest | Pass; 10 tests |
| Phase 1 exclusion | Pass; no `skills/` diff from `e070e1c`, no `dispatch-022`, and no Phase 1A/1B/1C focused test methods |

The commit that finalizes this report is the Phase 0 validation baseline parent for Phase 1. Later Phase 1 checks must start from that commit and must not be presented as Phase 0 evidence.
