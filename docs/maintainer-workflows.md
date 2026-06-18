# Maintainer Workflows

Target Reader: Open-source maintainers and reviewers evaluating how Groundwork supports real Codex-assisted maintenance.
Reader Action Needed: Decide when to use the full Groundwork loop, when to use a smaller path, and how to preserve evidence without adding ceremony.
Decision Supported: Whether Groundwork fits maintainer workflows such as PR clarification, implementation, verification, review transfer, and release evidence.
Scope: Maintainer-facing use of the public Groundwork skills, especially `to-prd`, `implement`, `verify`, and `handoff`.
Out of Scope: Replacing GitHub issues, CI, human code review, release ownership, security review, or Codex host approval enforcement.
Evidence Level: Grounded in `docs/prd.md`, `docs/product-principles.md`, the public skill surface, v0.2.x/v0.3 changelog entries, and runtime baseline reports under `evals/baselines/`.

Groundwork helps maintainers run evidence-first coding loops with Codex. It is optimized for situations where correctness depends on more than a code diff: PRD/spec clarity, source-code truth, runtime evidence, integration contracts, UAT behavior, and handoff quality.

It does not replace repository workflow. GitHub issues remain the collaboration record, CI remains automated verification, and maintainers still own review and merge decisions. Groundwork adds a small layer of workflow discipline around Codex so that requests, edits, evidence, and continuation context stay connected.

## Default Loop

```text
to-prd -> implement -> verify -> handoff
```

Use the full loop when a change affects product behavior, public API/contract, documentation, release readiness, UAT, security-sensitive behavior, cross-session work, or reviewer handoff.

Use a smaller path when the request is mechanical, local, and low risk. A typo fix, title rewrite, or direct explanation should stay conversation-first. Groundwork should add structure only when ambiguity, risk, reuse, or evidence needs justify it.

## 1. Clarify With `to-prd`

Use `to-prd` when the request is ambiguous, product-facing, cross-layer, or likely to create downstream implementation risk.

Expected output:

- target reader and decision supported
- known facts and source-truth references
- assumptions separated from verified facts
- unresolved decisions that block acceptance
- acceptance criteria with stable IDs
- non-goals and scope boundaries

Groundwork must not invent product truth. Business states, backend fields, user actions, metrics, owners, timelines, APIs, or acceptance details need support from user confirmation, source code, API/schema evidence, existing docs, or accepted project context.

## 2. Implement With Boundaries

Use `implement` when the PRD, issue, or task is ready enough to change code or project artifacts.

Expected output:

- scope and stop condition
- current git boundary and relevant dirty state
- files inspected before edits
- minimal change summary
- tests or checks run
- remaining gaps or no-test justification

Implementation should stay narrow. It should not mix unrelated refactors, dependency upgrades, formatting sweeps, speculative abstractions, or unrelated documentation cleanup into the same change.

## 3. Verify With Evidence

Use `verify` when someone asks whether a change is correct, supported, ready for review, ready for UAT, releaseable, aligned with a contract, or backed by enough evidence.

Expected output:

- explicit in-scope and out-of-scope boundaries
- covered and not-covered evidence areas
- evidence sources
- user-visible claim being checked
- claim or acceptance-criteria mapping to evidence
- verdict of `pass`, `partial`, `fail`, or `blocked`
- unverified claims and next action

A diff summary alone is not readiness evidence. Missing tests, runtime/browser checks, data readiness, environment readiness, UAT evidence, and customer validation must stay explicit when they were not checked.

## 4. Handoff As A Review Package

Use `handoff` when another maintainer, reviewer, agent, or future session needs to continue the work.

Expected output:

- current state
- source artifacts and their roles
- decisions made
- code, test, runtime, UAT, contract, and git-boundary evidence when available
- risks and gaps
- allowed and disallowed files when file boundary matters
- do-not-assume notes
- next action
- redaction note

Handoff should reference canonical artifacts instead of copying full PRDs, issue bodies, plans, diffs, logs, or transcripts. It is a transfer package, not a replacement for the source of truth.

## Auxiliary Paths

`to-issues` turns an accepted PRD/spec or plan into tracker-neutral vertical work units. It should not split raw intent that still lacks acceptance.

`triage` classifies readiness, severity, blockers, state transition, and whether local lifecycle state is justified.

`write-plan` sequences accepted work before edits when dependencies, contracts, or checks need a more explicit implementation plan.

`prototype` answers a product, interaction, state, visual, or business-rule question with a throwaway artifact. Prototype output is not backend contract unless source-backed or explicitly confirmed.

## Case Studies

See [`../examples/`](../examples/) for real Groundwork maintenance examples:

- [`01-scope-first-verification`](../examples/01-scope-first-verification/) shows how readiness checks start with explicit scope and evidence.
- [`02-prototype-contract-boundary`](../examples/02-prototype-contract-boundary/) shows how prototype output stays separate from backend contract truth.

## Artifact Discipline

Groundwork is conversation-first by default. Write durable artifacts only when they support review, reuse, execution, verification, UAT, release, or handoff.

Every durable artifact should carry the audience-first header fields defined in `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: target reader, reader action, decision supported, artifact type, source of truth, scope, out-of-scope boundary, evidence level, and safe-to-share or redaction notes. Sensitive data, credentials, private request payloads, long logs, and unredacted personal data must not be copied into artifacts.

## v0.3.4 Governance Baseline Boundary

v0.3.4 is a main-chain governance baseline for the current nine public skills, including package-only `dispatch`. It strengthens layered `AGENTS.md`, artifact headers, grill-before-write, prototype contract boundaries, implement planning/TDD-lite, verify scope/lenses, QA-fix-QA, git boundary, handoff review packages, and the shared done definition inherited by `dispatch`.

It is not a new runtime, plugin split, automation layer, task database, or subagent spawning system. Runtime evidence still requires installed plugin cache/source equivalence or a supported marketplace refresh before it can be treated as release-gating evidence.

## Maintainer Boundary

Groundwork should help maintainers reduce review and coding load without hiding responsibility. The maintainer still decides what qualifies, what merges, what releases, what gets security review, and what evidence is sufficient for the repository.
