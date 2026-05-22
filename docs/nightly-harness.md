# Nightly Harness Design

Target Reader: Groundwork maintainer designing future self-evolution checks.
Reader Action Needed: Use this as the boundary for a future nightly regression harness before implementing automation.
Decision Supported: What the harness may measure, what it must not mutate, and which failures become learning proposals.
Scope: Nightly regression suite design, stress checks, replay checks, metrics collection, failure taxonomy, and quarantined learning proposal flow.
Out of Scope: Auto-merge, auto mutation of `main`, production access, tracker writes, dependency installs, or runtime `.groundwork` commits.
Evidence Level: Groundwork issues #14 and #15 plus current `evals/prompts/*.csv` fixtures.

## Purpose

The nightly harness is a future local or Codex Cloud evaluation loop for Groundwork's skill behavior. It should run existing prompt fixtures, record structured outcomes, and produce reviewable failure evidence. It is not a self-editing agent and it must not change repository state without a human-reviewed patch.

## Suite Inputs

- `evals/prompts/smoke.csv` for public skill discovery and direct fallback.
- `evals/prompts/safety.csv` for gate and risky-write posture.
- `evals/prompts/reliability.csv` for v0.2 skill reliability scenarios.
- `evals/prompts/guardrails-regression.csv` for #5-#12 guardrail regression prompts.
- `evals/fixtures/*` for local source, no-test, and static prototype behavior.

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
- expected result: QA failure report, minimal diagnosis, scoped fix plan, and re-QA requirement

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

## Quarantined Learning Proposals

Repeated failures may produce a quarantined learning proposal. The harness may suggest a patch, but human review decides whether to accept, reject, or promote it. See `docs/quarantined-learnings.md` for the proposal format and promotion boundary.

## Non-Goals

- no auto-merge
- no auto main-branch mutation
- no invented business states
- no committing ignored runtime dirs
- no production access
- no tracker mutation
- no dependency upgrades
- no self-modifying skill changes without human review
