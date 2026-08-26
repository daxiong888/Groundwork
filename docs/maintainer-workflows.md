# Maintainer Workflows

Target Reader: Open-source maintainers and reviewers evaluating how Groundwork supports real Codex-assisted maintenance.
Reader Action Needed: Decide when to use the full Groundwork loop, when to use a smaller path, and how to preserve evidence without adding ceremony.
Decision Supported: Whether Groundwork fits maintainer workflows such as PR clarification, implementation, verification, review transfer, and release evidence.
Artifact Type: maintainer workflow guide.
Source of Truth: `docs/plugin-architecture.md`, `docs/product-principles.md`, public skill contracts, and repo-local `AGENTS.md`.
Scope: Maintainer-facing use of the public Groundwork skills, especially `to-prd`, `implement`, `verify`, and `handoff`.
Out of Scope: Replacing GitHub issues, CI, human code review, release ownership, security review, or Codex host approval enforcement.
Evidence Level: Current maintainer guidance derived from canonical source contracts. Historical PRDs, changelog entries, and eval baselines are supporting snapshots only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, or personal data.

Groundwork helps maintainers run evidence-first coding loops with Codex. It is optimized for situations where correctness depends on more than a code diff: PRD/spec clarity, source-code truth, runtime evidence, integration contracts, UAT behavior, and handoff quality.

It does not replace repository workflow. GitHub issues remain the collaboration record, CI remains automated verification, and maintainers still own review and merge decisions. Groundwork adds a small layer of workflow discipline around Codex so that requests, edits, evidence, and continuation context stay connected.

## Default Loop

```text
to-prd -> implement -> verify -> handoff
```

Use the full loop when a change affects product behavior, public API/contract, documentation, release readiness, UAT, security-sensitive behavior, cross-session work, or reviewer handoff.

Use a smaller path when the request is mechanical, local, and low risk. A typo fix, title rewrite, or direct explanation should stay conversation-first. Groundwork should add structure only when ambiguity, risk, reuse, or evidence needs justify it.

For complex bugs, material workflow changes, or readiness-adjacent claims, maintainers can apply the shared loop:

```text
Construct -> Attack -> Narrow -> Verify
```

Construct with [`FIRST-PRINCIPLES.md`](../skills/_shared/FIRST-PRINCIPLES.md): primitive facts, constraints, causal mechanism, root cause or core need, minimal solution, and falsifiable signal. Attack with [`ADVERSARIAL-REVIEW.md`](../skills/_shared/ADVERSARIAL-REVIEW.md): strongest counterexample, missing evidence, hidden assumptions, edge states, scope creep, and claim boundaries. Then narrow unsupported work and verify through the owning Groundwork route. This loop is a shared reference, not a new public skill surface.

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

## Artifact Discipline

Groundwork is conversation-first by default. Write durable artifacts only when they support review, reuse, execution, verification, UAT, release, or handoff.

Every durable artifact should carry the audience-first header fields defined in `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: target reader, reader action, decision supported, artifact type, source of truth, scope, out-of-scope boundary, evidence level, and safe-to-share or redaction notes. Sensitive data, credentials, private request payloads, long logs, and unredacted personal data must not be copied into artifacts.

## Historical Governance Baseline

v0.3.4 introduced much of the governance vocabulary still used by the current surface, including layered `AGENTS.md`, artifact headers, prototype contract boundaries, implement planning/TDD-lite, verify scope, git boundaries, and handoff review packages. The version label is historical evidence, not the current architecture owner.

It is not a new runtime, plugin split, automation layer, task database, or subagent spawning system. Runtime evidence still requires installed plugin cache/source equivalence or a supported marketplace refresh before it can be treated as release-gating evidence.

## Public Skill Expansion Boundary

Groundwork no longer treats the public skill surface as fixed-count by default. It treats expansion as a quality-gated maintainer decision: accepted scope must explicitly authorize the new public skill, and the candidate must pass the shared [`SKILL-QUALITY.md`](../skills/_shared/SKILL-QUALITY.md) checklist, routing review, and positive, negative, and hard-negative behavior expectations before merge.

Maintainers should first classify new behavior as one of five surfaces: public skill, shared reference, branch/workflow lens, router behavior, or one-off guide. Use the smallest surface that preserves a clear trigger contract and evidence boundary. A candidate that lacks a distinct invocation moment, conflicts with an existing route, or cannot state should-not-trigger cases should stay out of `skills/<name>/SKILL.md`.

## Setup Guidance Reference

`setup-groundwork` is guide/reference first. Groundwork should not require a setup pass before ordinary use, and maintainers should not create `skills/setup-groundwork/SKILL.md` unless a later accepted scope proves a repeated setup trigger, clear should/should-not routing, and the public skill-quality gate.

Use lightweight setup notes only when they help a maintainer choose local evidence sources, runtime boundaries, or repository conventions before a task starts. Prefer existing canonical docs, repo-local `AGENTS.md`, shared guardrails, and small references over a generated questionnaire or duplicate onboarding artifact.

Capability seeds belong in [`capability-seeds/`](capability-seeds/) as dated evidence inputs. A seed may record a user-observed menu, screenshot summary, stated environment fact, or docs reference, but it is not runtime/tool enforcement evidence. When model or runtime selection matters, pair the seed with the status language from [`RUNTIME-CAPABILITY.md`](../skills/_shared/RUNTIME-CAPABILITY.md) and keep `selector_enforcement` as `unknown` or `prompt_preference` unless a tool/runtime report proves enforcement for the specific run.

## Maintainer Boundary

Groundwork should help maintainers reduce review and coding load without hiding responsibility. The maintainer still decides what qualifies, what merges, what releases, what gets security review, and what evidence is sufficient for the repository.
