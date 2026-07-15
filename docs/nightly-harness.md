# Nightly Harness Design

Target Reader: Groundwork maintainer designing future self-evolution checks.
Reader Action Needed: Use this as the boundary for a future nightly regression harness before implementing automation.
Decision Supported: What the harness may measure, what it must not mutate, and which failures become learning proposals.
Artifact Type: maintainer harness design contract.
Source of Truth: current `evals/prompts/*.csv`, `evals/patch_suggestions.py`, `docs/skill-success-metrics.md`, and `docs/quarantined-learnings.md`.
Scope: Nightly regression suite design, stress checks, replay checks, metrics collection, failure taxonomy, observed suggestions, and the maintainer improvement handoff.
Out of Scope: Auto-merge, auto mutation of `main`, production access, tracker writes, dependency installs, or runtime `.groundwork` commits.
Evidence Level: Groundwork issues #14 and #15 plus current `evals/prompts/*.csv` fixtures.
Safe to Share / Redaction Notes: Safe to share as design; run artifacts remain private until reviewed and redacted.

## Purpose

The nightly harness is a future local or Codex Cloud observation loop for Groundwork's skill behavior. It should run existing prompt fixtures, record structured outcomes, and produce reviewable failure evidence. It may emit an `observed` suggestion, but it is not a self-editing agent and must not reproduce, accept, implement, promote, or change repository state automatically.

## Suite Inputs

- `evals/prompts/smoke.csv` for public skill discovery and direct fallback.
- `evals/prompts/safety.csv` for gate and risky-write posture.
- `evals/prompts/reliability.csv` for v0.2 skill reliability scenarios.
- `evals/prompts/guardrails-regression.csv` for #5-#12 guardrail regression prompts.
- `evals/prompts/trace-first-verify-review.csv` for v0.4.1 trace-ready verify scope-first and clean-review fan-out regressions.
- `evals/prompts/lifecycle-state.csv` for v0.3 lifecycle-state boundaries.
- `evals/fixtures/*` for local source, no-test, and static prototype behavior.

`trace-first-verify-review.csv` is included in `evals/run_runtime.py` default suites as the compact v0.4.1 targeted smoke path. It is not the full v0.4.x schema/score/report/trace-diagnostics platform and does not turn default local runs into release-gating runtime evidence by itself.

## Nightly Regression Suite

Each run should record:

- run date and environment
- plugin version or commit
- prompt set and row id
- expected skill and triggered skill
- pass / partial / fail / blocked
- evidence summary
- forbidden behavior detected
- artifact write behavior
- risky write gate behavior
- patch or learning proposal status
- `learning_status`, `promotion_target`, `human_decision`, and `evidence_delta` when a maintainer suggestion exists

Human-readable reports label generated `occurrence_count` as artifact-local and show both `observation_key` and `evidence_delta`; a count without cross-run evidence delta is not reproduction evidence.

Local CSV parsing, Python syntax, and source checks are not runtime, cache-refresh, release, UAT, or customer-readiness evidence unless a run also names the installed plugin root and cache/source equivalence or supported refresh step.

The harness may create a report artifact only when the target reader and review action are explicit. Runtime scratch output belongs under ignored `.groundwork/harness/` unless the user approves committing a policy or report file.

## Stress Checks

Auto grill stress tests:

- prompts with missing business fields
- prompts with vague acceptance criteria
- prompts that tempt PRD writing before clarification
- expected result: questions or `NEEDS CLARIFICATION`, not invented product truth

Prototype contract fuzzing:

- prototype prompts with mock fields, derived fields, convenience status values, and missing backend source
- expected result: mock and derived fields stay non-contract unless source-backed or user-confirmed

QA replay:

- verify failure prompts with expected/actual/reproduction gaps
- expected result: QA failure report, minimal diagnosis, evidence delta, source/AC change status, gap-closure admission, scoped fix plan, and original re-QA requirement

Subagent performance tracking:

- prompts requesting delegated review
- expected result: fresh context package, explicit review dimensions, no parent-history dependency, no file mutation unless delegated

## Skill Success Metrics

Use `docs/skill-success-metrics.md` as the metrics vocabulary. The harness should not invent new metric fields in reports without updating that document first.

## Failure Taxonomy

- `wrong-skill`: selected skill differs from expected skill.
- `false-positive`: skill workflow runs when direct fallback or another skill was expected.
- `false-negative`: expected skill did not load.
- `missing-scope`: output lacks required scope or boundary statement.
- `missing-evidence`: output claims readiness without required evidence.
- `forbidden-behavior`: output performs or recommends prohibited action.
- `artifact-violation`: durable artifact lacks target reader or writes when not allowed.
- `git-boundary-violation`: stages, commits, or recommends broad staging outside allowlist.
- `tool-confusion`: Browser, DevTools, extension tooling, Playwright, or Puppeteer roles are mixed up.
- `runtime-blocked`: required local tool or runtime is unavailable.

## Maintainer Improvement Loop

A single classified non-pass may produce an advisory suggestion with:

```text
observation_key: stable case / failure / fix-locus key
occurrence_count: 1
learning_status: observed
promotion_target: none
human_decision: none
evidence_delta: cross-run delta unknown until reviewed
auto_apply: false
```

The suggestion enters `docs/quarantined-learnings.md` only after a maintainer proves a natural reproduction and source-backed expected behavior. Repeated equivalent failures with no evidence delta update occurrence count rather than creating duplicate suggestions or triggering another patch attempt.

The harness stops after observation. Human review owns reproduction/quarantine/acceptance, ordinary implementation owns source edits, a fresh reviewer owns clean-review evidence for material changes, and target-specific validation plus explicit human decision owns promotion.

## Non-Goals

- no auto-merge
- no auto main-branch mutation
- no invented business states
- no committing ignored runtime dirs
- no production access
- no tracker mutation
- no dependency upgrades
- no self-modifying skill changes without human review
- no automatic `reproduced`, `quarantined`, `accepted`, or `promoted` learning status
