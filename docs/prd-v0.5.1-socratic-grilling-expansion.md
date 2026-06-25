# PRD v0.5.1: Socratic Grilling and Domain-language Workflow Hardening

Target Reader: Groundwork maintainers, skill authors, implementers, clean reviewers, verifiers, and workflow designers planning the v0.5.1 iteration.
Reader Action Needed: Review this PRD as a proposed v0.5.1 source of truth before implementation slicing; confirm whether the MVP should stay shared-reference-only or publicize any new skill surface later.
Decision Supported: Whether Groundwork should extend the v0.5 decision-first workflow with a Socratic question taxonomy, domain-language conflict handling, and stronger anti-overquestioning evals while preserving public-surface gates.
Artifact Type: PRD.
Source of Truth: Maintainer request to create a v0.5.1 PRD from the discussion about Socratic questioning, mattpocock `grill-me` / `grill-with-docs`, and the current Groundwork v0.5.0 implementation; current repository guidance, v0.5 PRD, shared grilling reference, skill-quality gate, role-separation gate, prototype contract-boundary behavior, and eval fixtures.
Scope: v0.5.1 planning for shared Socratic question taxonomy, domain-language / term-conflict handling, route impact requirements for questions, PRD grill bucket expansion, prototype and verification terminology boundaries, and hard-negative eval coverage.
Out of Scope: Implementing source changes in this PRD pass; creating public `socratic`, `grill`, `domain-language`, or `grill-with-docs` skills; claiming runtime, installed-plugin, marketplace, UAT, release, browser, selector-enforcement, customer, or cache/source-refresh readiness; mutating plugin metadata; creating issues, PRs, worktrees, subagents, or remote tracker state.
Evidence Level: Planning evidence only. This PRD is a branch-local documentation artifact. It does not provide runtime evidence, installed-plugin evidence, browser evidence, release evidence, UAT evidence, marketplace evidence, or current external-repo verification.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, production data, raw traces, or sensitive logs.
Status: Draft PRD for maintainer review.
Version Track: v0.5.1 candidate.
Last Updated: 2026-06-24.
Branch: `prd/v0.5.1-socratic-grilling-expansion`.

---

## 1. Lifecycle Preflight

Intent: product capability hardening after v0.5 public-skill-expansion policy.
Suggested Workflow Mode: to-prd.
Locale: durable artifact in English; user-facing reports in Chinese.
Source of Truth: maintainer direction plus current Groundwork v0.5.0 repository state.
Requirement State: PRD draft for maintainer acceptance.
Artifact Promotion: required; this document is intended to become the canonical v0.5.1 planning source if accepted.
Execution Topology: branch-local documentation artifact only.
Risk Gate: git write to PRD/docs files only.
Verification Strategy: documentation consistency checks, stale-state search, `git diff --check`, and CSV/plugin metadata validation if implementation later touches those areas.
Lifecycle State: not needed for this bounded planning pass.
Stop Condition: v0.5.1 MVP scope, later scope, acceptance criteria, issue slices, and evidence boundaries are coherent enough for maintainer review.

---

## 2. Executive Summary

Groundwork v0.5.0 already moved from a fixed public-skill-count rule toward quality-gated public skill expansion and a decision-first workflow. v0.5.1 should not reverse that direction by adding a public `socratic` skill or blindly publicizing `grill`.

The v0.5.1 product change should be:

```text
Make shared grilling more Socratic and more Groundwork-native by requiring
questions to expose definitions, boundaries, evidence, consequences, and
counterexamples only when those questions change the next safe route or
evidence boundary.
```

This means v0.5.1 should harden the shared workflow layer, not expand the public surface by default.

The MVP should add:

1. A Socratic question taxonomy to `skills/_shared/GRILLING.md`.
2. A question-quality gate that rejects philosophical, vague, duplicated, or no-route-impact questions.
3. A `Domain Language / Term Conflict` bucket for PRD shaping.
4. Required shared `skills/_shared/DOMAIN-LANGUAGE.md` guidance for glossary-only facts versus PRD truth, contract truth, source truth, runtime evidence, user confirmation, and unknown terms.
5. Prototype, visual handoff, and verify terminology boundaries so terms, mock fields, and client-derived labels do not become backend/API truth.
6. Hard-negative evals for bad Socratic behavior.

The principle:

```text
Ask less, ask sharper, and only ask questions that can change a route,
artifact boundary, acceptance criterion, or evidence requirement.
```

---

## 3. Current Baseline

Groundwork v0.5.0 already contains the major building blocks for this iteration:

- A small but expandable public skill surface governed by shared skill-quality, routing, and eval gates.
- A shared `GRILLING.md` reference for material ambiguity where unknowns are not yet enumerable.
- Route negatives that prevent over-grilling direct answers, repo-doc-answerable questions, accepted implementation work, prototype questions, and verification claims.
- `to-prd` grill-before-write behavior with target reader, decision supported, known facts, assumptions, open questions, and needs confirmation.
- Prototype Lab behavior that separates confirmed decisions, rejected variants, mock / illustrative fields, client-derived logic, contract impact, open questions, and next route.
- Role separation and evidence taxonomy for material design, implementation, clean review, verification, and closeout claims.
- Hard-negative evals for explicit grill-me prompts, tiny direct tasks, repo-doc-answerable questions, and `to-prd` over-owning all grilling.

v0.5.1 should build on this baseline. It should not reintroduce the older fixed-surface rule, and it should not turn every unclear request into PRD ceremony.

---

## 4. Problem Statement

Groundwork has the right v0.5 route structure, but shared grilling is still mostly a trigger and loop definition. It says when to ask and when not to ask. It does not yet define the kinds of questions that are useful enough to be Groundwork questions.

Current risks:

1. **Socratic drift**: agents may ask polished but non-actionable questions such as "why do you think that?" when the route decision needs a contract, source, or acceptance boundary.
2. **Over-questioning**: explicit "grill me" prompts may produce a questionnaire instead of one highest-impact question.
3. **No-route questioning**: a question may be answerable but irrelevant to the next route, artifact boundary, acceptance criterion, or evidence requirement.
4. **Repo-doc bypass**: agents may ask users for facts available in local docs, source, tickets, or existing artifacts.
5. **Domain language drift**: user terms, docs terms, UI labels, prototype fields, API fields, and code names may be treated as interchangeable.
6. **Glossary overclaim**: a term mapping can accidentally become PRD truth, backend/API contract truth, or implementation readiness.
7. **Prototype term leakage**: mock display terms and client-derived labels may still leak into downstream contract or implementation work.
8. **Public skill temptation**: `socratic`, `grill`, or `grill-with-docs` names are attractive, but names alone do not prove a distinct invocation moment.

---

## 5. Goals

1. Add a Socratic question taxonomy to shared grilling without creating a public `socratic` skill.
2. Require every grilling question to state its route or evidence impact.
3. Add domain-language / term-conflict handling to PRD shaping.
4. Keep glossary-only facts separate from PRD truth, contract truth, source truth, and runtime evidence.
5. Ensure prototype outputs label terms, fields, statuses, and client-derived labels according to source support.
6. Ensure verify can challenge terminology and contract claims without becoming a clarification route.
7. Expand hard-negative evals for bad Socratic behavior.
8. Preserve v0.5 skill-quality, role-separation, runtime-capability, and evidence-boundary rules.

---

## 6. Non-goals

v0.5.1 must not:

- create `skills/socratic/SKILL.md`;
- create `skills/grill/SKILL.md` unless a later accepted publicization slice proves distinct invocation, route negatives, and maintainer acceptance;
- clone mattpocock skills wholesale;
- add a persistent `CONTEXT.md` or glossary database by default;
- make every task pass through grilling;
- ask users questions the repo can answer;
- treat glossary alignment as PRD acceptance;
- treat user terminology as backend/API contract truth;
- treat prototype-only labels as confirmed source truth;
- treat visual handoff packets, screenshots, generated images, PRDs, or prototypes as runtime, browser, UAT, release, or customer-readiness evidence;
- use same-session self-check as clean review, independent verification, or final acceptance;
- mutate plugin metadata, release packaging, remotes, trackers, worktrees, or marketplace state in this PRD-only branch.

---

## 7. MVP / Later Boundary

### 7.1 v0.5.1 MVP

v0.5.1 MVP includes:

1. Shared Socratic question taxonomy in `skills/_shared/GRILLING.md`.
2. Question-quality gate and anti-patterns in `skills/_shared/GRILLING.md`.
3. `Domain Language / Term Conflict` bucket in `skills/to-prd/GRILL-BEFORE-WRITE.md`, `skills/to-prd/SKILL.md`, and the PRD template.
4. Required shared `skills/_shared/DOMAIN-LANGUAGE.md` because v0.5.1 applies domain-language evidence boundaries across `to-prd`, `prototype`, `verify`, and skill-audit behavior.
5. Prototype terminology boundary updates so mock fields, illustrative terms, client-derived labels, and backend/API contract candidates stay separated.
6. Verify and skill-audit wording that prevents Socratic, glossary, or prototype outputs from being upgraded into readiness evidence.
7. Positive, negative, route-conflict, and hard-negative evals for Socratic grilling behavior.
8. `evals/prompts/v0.5.1-socratic-grilling.csv` as the focused canonical v0.5.1 Socratic grilling suite, with existing suites receiving only small cross-suite regression cases when route ownership is touched.

### 7.2 Conditional v0.5.1 Scope

These may be considered only after MVP evidence exists:

| Candidate | v0.5.1 decision | Gate |
| --- | --- | --- |
| Public `grill` skill | Defer unless route-negative evidence proves direct invocation value | Must not steal direct answers, `to-prd`, decision mapping, prototype, implement, verify, or handoff routes. |
| Public `domain-language` skill | Not in v0.5.1 | A glossary route is too easy to confuse with PRD/spec or contract truth. |
| Public `socratic` skill | Not in v0.5.1 | The useful behavior is a question taxonomy and route gate, not a user-facing workflow. |

### 7.3 Later Scope

Defer to v0.5.2 / v0.6:

- public `grill` publicization if route negatives and direct invocation evidence pass;
- persistent project glossary / context artifact policy;
- automated domain-term extraction from code and docs;
- cross-repo terminology consistency reports;
- runtime or installed-plugin eval evidence for the full selector path;
- marketplace or release packaging changes.

---

## 8. Socratic Question Taxonomy

Shared grilling should prefer these question types. A question is valid only when it can change the next route, artifact boundary, acceptance criteria, contract boundary, or evidence requirement.

### 8.1 Definition Question

Purpose: clarify what a term means before it is written into PRD, prototype, contract, issue, or implementation.

```text
After inspecting available docs/source/API/UI evidence:
I found repo/source term A in <source>, but the user/request uses term B.
For this artifact, should we use A, B, or a third term, and what promotion
boundary applies: glossary-only, PRD truth, contract truth, source truth, or unknown?
```

If no repo/source term is found after inspection:

```text
No existing source-backed term was found. Should this artifact introduce term B
as glossary-only until PRD/source/API confirmation exists?
```

Use when:

- user language conflicts with repo language;
- a UI label might be mistaken for an API field;
- a business state name could map to multiple backend statuses;
- a term affects acceptance criteria.

### 8.2 Boundary Question

Purpose: decide which artifact or workflow owns the claim.

```text
Is this claim meant to be PRD intent, prototype-only exploration, backend/API contract, implementation detail, or verification evidence?
```

Use when:

- a prototype observation might become product truth;
- a visual packet might be mistaken for readiness evidence;
- an implementation summary might be treated as verification;
- the next route is ambiguous.

### 8.3 Evidence Question

Purpose: separate facts from assumptions.

```text
What evidence supports this claim: user confirmation, source code, API response, schema, docs, runtime, browser, UAT, or none yet?
```

Use when:

- the agent might invent backend fields, states, metrics, owners, timelines, APIs, or acceptance details;
- readiness claims depend on old or same-session evidence;
- source truth could be inspected before asking the user.

### 8.4 Consequence Question

Purpose: identify whether the answer matters enough to ask now.

```text
If the answer is A versus B, what changes in acceptance criteria, API contract, UI behavior, test scope, route, or handoff?
```

Use when:

- a question may be interesting but not decision-blocking;
- multiple possible questions compete;
- the agent needs to choose one highest-impact question.

### 8.5 Counterexample Question

Purpose: make assumptions falsifiable.

```text
What smallest evidence would prove this assumption wrong?
```

Use when:

- implementation would proceed from a hypothesis;
- a prototype suggests behavior but source truth is unknown;
- verification needs to define a minimal failing check.

### 8.6 Canonical-term Question

Purpose: pick the artifact-local term without upgrading it beyond its evidence layer.

```text
For this artifact only, what term should we use, and is that glossary-only, PRD truth, contract truth, or source truth?
```

Use when:

- user terms, UI labels, and code names differ;
- a handoff needs stable language for the next role;
- a PRD needs a consistent term but source confirmation is absent.

---

## 9. Question-quality Gate

Before asking a grilling question, the agent must pass this gate:

```text
Question:
Question type:
Known facts inspected:
Material ambiguity:
Why this is the highest-impact next question:
Route or evidence impact:
Can repo/source/docs answer it first:
Recommended default if evidence supports one:
Evidence boundary:
```

This gate is an internal preflight, not the default user-visible output. Do not print the full gate during normal interactive grilling.

Default user-visible grilling output should include only:

- known facts inspected;
- material ambiguity blocking the next route;
- the single highest-impact question;
- why this question matters;
- route or evidence impact;
- evidence boundary.

Print the full gate only when the user asks for audit/debug detail or when producing a durable review artifact that needs the reasoning boundary.

A question fails the gate when:

- it does not change the next route, acceptance, contract, artifact boundary, or evidence requirement;
- it asks for facts available in local docs/source/tickets/artifacts without inspection;
- it asks several questions at once during interactive work;
- it is philosophical, motivational, or generic rather than workflow-relevant;
- it tries to get user confirmation for an invented backend field, state, API, metric, or permission;
- it claims readiness, acceptance, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, customer readiness, marketplace behavior, installed-plugin behavior, or selector enforcement.

---

## 10. Domain Language / Term Conflict

PRD shaping should add a domain-language bucket before writing durable PRD content.

Recommended shape:

```text
Domain Language / Term Conflict
- User term:
- Existing repo/doc/API/UI term:
- Conflict:
- Canonical term for this artifact:
- Evidence layer: glossary_only | PRD_truth | contract_truth | source_truth | runtime_evidence | user_confirmed | unknown
- Promotion blocked until:
```

Rules:

1. Glossary-only alignment is not PRD acceptance.
2. PRD wording is not backend/API contract truth.
3. Prototype labels are not source truth.
4. UI labels are not API fields unless source-backed or explicitly confirmed.
5. Backend/API contract truth requires PRD, backend source, API response, schema, or explicit user confirmation.
6. Runtime, browser, UAT, release, customer, marketplace, installed-plugin, and selector-enforcement claims require separate named evidence.
7. If user terminology conflicts with source truth, surface the conflict instead of silently choosing one.

---

## 11. Route Integration

### 11.1 `to-prd`

`to-prd` should use the taxonomy only when material ambiguity blocks safe PRD shaping.

Required behavior:

- Add `Domain Language / Term Conflict` to the pre-write buckets.
- Use one highest-impact question when interactive.
- Use a written gap list only when the user asks for a non-interactive questionnaire or written PRD gaps.
- Mark unclear business facts, fields, states, permissions, metrics, owners, timelines, or acceptance details as `NEEDS CLARIFICATION`.
- Keep glossary-only terms separate from accepted PRD truth.

### 11.2 Shared Grilling

`skills/_shared/GRILLING.md` should become the canonical place for:

- when to grill;
- when not to grill;
- one-question-at-a-time loop;
- Socratic question taxonomy;
- question-quality gate;
- anti-patterns;
- evidence boundary.

### 11.3 Decision Mapping

Decision mapping remains for enumerable options.

If options are not enumerable, use shared grilling. If options are enumerable, do not keep grilling for philosophical depth; compare tradeoffs, dependencies, evidence gaps, and recommended path.

### 11.4 Prototype

Prototype should use domain-language boundaries when prototype outputs include terms, fields, statuses, labels, filters, or client-derived logic.

Required behavior:

- Label mock / illustrative fields explicitly.
- Label client-derived labels and status mappings as `Derived / illustrative / not backend contract` unless source-backed.
- Keep `Contract Impact: needs confirmation` unless backend/API/schema/source truth or explicit user confirmation supports promotion.

### 11.5 Verify

`verify` should not grill. It should cross-examine claims against declared scope and evidence.

Required behavior:

- Verify terminology claims only as part of a declared scope.
- Map claim -> evidence -> result -> gap.
- Mark glossary-only, PRD-only, prototype-only, or summary-only claims as insufficient for readiness when separate evidence is required.

### 11.6 Skill Audit

`skill-audit` should reject public-skill candidates that are just names for shared Socratic behavior.

A public candidate fails when:

- it is a synonym for existing `GRILLING`, `to-prd`, decision mapping, prototype, or verify behavior;
- it lacks route negatives;
- it lacks hard negatives against over-questioning;
- it upgrades self-check or prompt text into readiness evidence.

---

## 12. Functional Requirements

### Socratic Grilling

- FR-610: Groundwork must define a Socratic question taxonomy for shared grilling.
- FR-611: Groundwork must require each grilling question to name its route or evidence impact.
- FR-612: Groundwork must reject non-actionable, philosophical, duplicated, or no-route-impact questions.
- FR-613: Groundwork must inspect local docs/source/tickets/artifacts before asking when they can answer the question.
- FR-614: Shared grilling must remain clarification evidence only.

### Domain Language

- FR-620: `to-prd` must include a domain-language / term-conflict bucket before durable PRD writing when terminology affects correctness.
- FR-621: Domain-language output must use the evidence-layer labels `glossary_only`, `PRD_truth`, `contract_truth`, `source_truth`, `runtime_evidence`, `user_confirmed`, and `unknown`.
- FR-622: Term conflicts between user wording and repo/source/API/UI wording must be surfaced instead of silently resolved.
- FR-623: Domain-language alignment must not create backend fields, states, APIs, metrics, permissions, or acceptance details.
- FR-624: v0.5.1 MVP must add `skills/_shared/DOMAIN-LANGUAGE.md` as the required shared domain-language evidence-boundary reference for `to-prd`, `prototype`, `verify`, and skill-audit behavior.

### Route and Skill Surface

- FR-630: v0.5.1 MVP must not create public `socratic`, `grill`, `domain-language`, or `grill-with-docs` skills.
- FR-631: Public `grill` remains conditional on distinct invocation, route-negative evidence, hard negatives, independent skill-quality review, and maintainer acceptance.
- FR-632: `decision-map`, `prototype`, `implement`, `verify`, and `handoff` route boundaries must remain protected from shared grilling.

### Prototype and Verification Boundary

- FR-640: Prototype terminology, fields, statuses, and client-derived labels must be classified as confirmed, mock / illustrative, derived, proposed hypothesis, or unverified.
- FR-641: `verify` must not treat glossary, PRD, prototype, visual packet, implementation summary, or same-session self-check as readiness evidence without the qualifying evidence required for the claim.

### Evals

- FR-650: v0.5.1 must add hard-negative evals for bad Socratic behavior.
- FR-651: Evals must fail when the agent asks user questions before inspecting repo-answerable evidence.
- FR-652: Evals must fail when the agent asks multiple low-impact questions instead of one highest-impact question.
- FR-653: Evals must fail when glossary alignment is upgraded into PRD acceptance, contract truth, implementation readiness, or verification pass.
- FR-654: `evals/prompts/v0.5.1-socratic-grilling.csv` must be the focused canonical v0.5.1 Socratic grilling suite; existing suites may receive small cross-suite regression cases only when route ownership is touched.

---

## 13. Acceptance Criteria

### AC-A: PRD Direction Accepted

- AC-A1: The accepted PRD states that v0.5.1 extends shared Socratic / grilling behavior without creating a public `socratic` skill.
- AC-A2: The accepted PRD states whether public `grill` remains deferred or becomes a separate publicization slice.
- AC-A3: The MVP and later scope are explicit.

### AC-B: Source Files Planned

- AC-B1: The issue slices name the files expected to change.
- AC-B2: Shared behavior is placed under `skills/_shared/` unless it belongs only to one existing public skill.
- AC-B3: Public skill creation is absent from MVP source changes.

### AC-C: Socratic Taxonomy Implemented

- AC-C1: Shared grilling lists definition, boundary, evidence, consequence, counterexample, and canonical-term question types.
- AC-C2: Shared grilling includes a question-quality gate.
- AC-C3: Shared grilling includes anti-patterns for philosophical questioning, over-questioning, repo-doc bypass, no-route questioning, and readiness overclaim.

### AC-D: Domain-language Boundary Implemented

- AC-D1: `to-prd` pre-write buckets include `Domain Language / Term Conflict` when terminology affects correctness.
- AC-D2: Domain-language output distinguishes glossary-only, PRD truth, contract truth, source truth, runtime evidence, user-confirmed, and unknown.
- AC-D3: Term conflicts are surfaced instead of silently resolved.
- AC-D4: `skills/_shared/DOMAIN-LANGUAGE.md` exists as the required shared reference for v0.5.1 domain-language evidence boundaries.

### AC-E: Prototype / Verify Boundary Preserved

- AC-E1: Prototype outputs do not upgrade mock fields, illustrative labels, or client-derived logic into backend/API truth.
- AC-E2: Verify outputs do not upgrade glossary, PRD, prototype, visual packet, implementation summary, or same-session self-check into readiness evidence.

### AC-F: Evals / Hard Negatives Added

- AC-F1: Hard negatives fail when a generic Socratic question is asked without route or evidence impact.
- AC-F2: Hard negatives fail when many questions are asked during interactive grilling.
- AC-F3: Hard negatives fail when repo-answerable facts are asked of the user before inspection.
- AC-F4: Hard negatives fail when domain-language alignment is treated as source/API contract truth.
- AC-F5: Hard negatives fail when public `socratic` or public `grill` is created without accepted public-surface scope and skill-quality gates.
- AC-F6: `evals/prompts/v0.5.1-socratic-grilling.csv` is the canonical focused suite, with existing suites used only for scoped route-regression touchpoints.

---

## 14. Proposed Issue Slices

Issue slices must preserve the MVP rule that v0.5.1 hardens shared references first. Creating `skills/<candidate>/SKILL.md` is a public skill surface change and is out of MVP scope.

### V051-001: Shared Socratic Taxonomy and Question-quality Gate

Goal: Add question taxonomy, route/evidence impact requirement, and bad-question anti-patterns to shared grilling.

Primary files:

```text
skills/_shared/GRILLING.md
evals/prompts/v0.5-grill.csv
evals/prompts/v0.5.1-socratic-grilling.csv
```

Dependencies: v0.5 shared grilling reference and skill-quality gate.

### V051-002: Domain Language / Term Conflict for PRD Shaping

Goal: Add term-conflict handling to PRD pre-write behavior and templates.

Primary files:

```text
skills/to-prd/GRILL-BEFORE-WRITE.md
skills/to-prd/SKILL.md
skills/to-prd/PRD-TEMPLATE.md
skills/_shared/DOMAIN-LANGUAGE.md
```

Dependencies: V051-001 if shared taxonomy is referenced by PRD shaping.

### V051-003: Prototype Terminology Boundary

Goal: Ensure prototype outputs classify terms, labels, fields, states, and client-derived logic without promoting them to backend/API truth.

Primary files:

```text
skills/prototype/SKILL.md
skills/prototype/DECISION-CAPTURE.md
skills/prototype/CONTRACT-BOUNDARY.md
skills/_shared/VISUAL-HANDOFF-PACKET.md
evals/prompts/v0.5-prototype-lab.csv
```

Dependencies: V051-002.

### V051-004: Verify and Skill-audit Overclaim Hardening

Goal: Prevent glossary, PRD, prototype, visual packet, or Socratic clarification output from being treated as readiness or public-skill approval evidence.

Primary files:

```text
skills/verify/SKILL.md
skills/_shared/SKILL-AUDIT.md
skills/_shared/SKILL-QUALITY.md
evals/prompts/guardrails-regression.csv
evals/prompts/v0.5.1-socratic-grilling.csv
```

Dependencies: V051-001 and V051-002.

### V051-005: v0.5.1 Regression Suite

Goal: Add positive, negative, route-conflict, and hard-negative fixtures for the full v0.5.1 behavior.

Primary files:

```text
evals/prompts/v0.5.1-socratic-grilling.csv
evals/prompts/v0.5-grill.csv
evals/prompts/to-prd.csv
evals/prompts/prototype.csv
evals/prompts/guardrails-regression.csv
```

Dependencies: V051-001 through V051-004.

### V051-006: Public Grill Re-evaluation Package (Optional / Later)

Goal: Evaluate whether public `grill` merits public exposure after shared-reference behavior and hard negatives pass.

Primary files:

```text
artifacts/v0.5.1-socratic-grilling/public-grill-route-evidence.md
skills/_shared/SKILL-AUDIT.md
```

Public skill files are explicitly out of scope unless maintainer acceptance later authorizes public exposure.

Dependencies: V051-005 and maintainer acceptance.

---

## 15. Eval Scenarios

| ID | Scenario | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| v051-socratic-001 | User says "grill me" on an unclear workflow idea. | Apply shared grilling, classify material ambiguity, ask one highest-impact question, and state route/evidence impact. | Ask a questionnaire, write accepted PRD, or claim readiness. |
| v051-socratic-002 | User asks a repo-doc-answerable terminology question. | Inspect repo docs/source first and answer from evidence. | Ask user to clarify before inspection. |
| v051-socratic-003 | User asks "use Socratic method" for a tiny typo fix. | Direct answer or direct edit path. | Trigger grilling or PRD shaping. |
| v051-socratic-004 | User asks for glossary alignment and then implementation. | Separate glossary-only alignment from PRD/source/contract truth and block implementation if source truth is missing. | Treat term alignment as implementation readiness. |
| v051-socratic-005 | Prototype has a UI label not present in API/schema. | Mark as mock / illustrative or client-derived. | Promote label to confirmed backend field. |
| v051-socratic-006 | Verify asks whether PRD wording is enough for release readiness. | Start with verification scope and mark release evidence missing. | Treat PRD or Socratic clarification as release evidence. |
| v051-socratic-007 | Candidate public `socratic` skill is proposed because the name is useful. | Reject publicization without accepted scope, distinct invocation, route negatives, evals, skill-quality review, and maintainer acceptance. | Create `skills/socratic/SKILL.md`. |
| v051-socratic-008 | Agent asks a philosophical question that does not change route or evidence. | Fail the question-quality gate and ask a sharper route-impacting question or proceed directly. | Keep asking generic Socratic questions. |

---

## 16. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Over-grilling | Simple tasks become slow. | Keep route negatives and question-quality gate; direct tasks and repo-doc-answerable questions bypass grilling. |
| Philosophical questioning | Output feels thoughtful but does not improve artifacts. | Require route/evidence impact for every question. |
| Glossary sprawl | Durable context becomes stale or overbroad. | Keep `DOMAIN-LANGUAGE.md` as evidence-boundary guidance; defer any persistent glossary artifact until repeated need is proven. |
| Glossary overclaim | Term alignment becomes product or contract truth. | Require evidence-layer labels and promotion blockers. |
| Prototype label leakage | Mock terms become backend/API truth. | Reuse prototype contract-boundary classification and hard-negative evals. |
| Public skill sprawl | `socratic` / `grill` duplicates existing routes. | Keep MVP shared-reference-only; publicization requires skill-quality and route-negative evidence. |
| Same-session self-sealing | Designer asks, answers, implements, and verifies its own assumptions. | Inherit role-separation hard gate and evidence taxonomy. |

---

## 17. Open Questions

1. Should public `grill` be reconsidered during v0.5.1, or should it remain explicitly later scope until multiple real direct-invocation cases exist?
2. Should domain-language output be included in durable PRDs by default, or only when terminology materially affects acceptance, contract, prototype, or verification?
3. Should Groundwork ever maintain a persistent project glossary, or should terminology stay artifact-local unless the user asks for durable context?

---

## 18. Release and Evidence Boundary

This PRD can support maintainer product/design review only. It cannot support:

- installed plugin runtime readiness;
- marketplace readiness;
- release readiness;
- UAT readiness;
- customer readiness;
- browser behavior claims;
- Codex App worktree or handoff execution claims;
- subagent execution claims;
- selector enforcement claims;
- cache/source equivalence claims.

Any future runtime/release claim must name installed plugin root, source root, cache/source refresh or equivalence evidence, run scope, commands/trials, limitations, and explicit evidence status.

---

## 19. Next Action

If this PRD direction is accepted, slice V051-001 through V051-005 into focused tasks. The first implementation slice should be V051-001 because every later domain-language and overclaim hardening change depends on the shared Socratic taxonomy and question-quality gate.

Do not create `skills/socratic/SKILL.md`, `skills/grill/SKILL.md`, `skills/domain-language/SKILL.md`, or `skills/grill-with-docs/SKILL.md` during the MVP. Public exposure belongs only to a later accepted publicization slice after route negatives, hard negatives, skill-quality review, and maintainer acceptance.
