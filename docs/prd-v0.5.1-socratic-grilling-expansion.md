# PRD v0.5.1: Socratic Grilling and Domain-language Workflow Hardening

> [!IMPORTANT]
> 本文保留 v0.5.1 功能决策与实现历史。文中 `evals/` 路径、旧 Eval 命令和 suite 要求已由 `docs/prd-plugin-candidate-trial-migration-v1.md` 的减法迁移废止，只能作为历史事实，不能作为当前架构、命令或 Candidate authority。

Target Reader: Groundwork maintainers, skill authors, implementers, clean reviewers, verifiers, and workflow designers planning the v0.5.1 iteration.
Reader Action Needed: Use this accepted PRD as the v0.5.1 MVP implementation and review source of truth; keep public-surface expansion deferred unless a later accepted slice authorizes it.
Decision Supported: How Groundwork should extend the v0.5 decision-first workflow with higher-quality first questions, conditional domain-language conflict handling, and positive-value plus anti-overquestioning evals while preserving public-surface gates.
Artifact Type: PRD.
Source of Truth: Maintainer request to create and implement a v0.5.1 PRD from the discussion about Socratic questioning, mattpocock `grill-me` / `grill-with-docs`, and the current Groundwork v0.5.0 implementation; current repository guidance, v0.5 PRD, shared grilling reference, skill-quality gate, role-separation gate, prototype contract-boundary behavior, and eval fixtures.
Scope: v0.5.1 planning for shared Socratic question quality, conditional domain-language / term-conflict handling, route-impact requirements for questions, compact grilling output, regression touchpoints, and positive-value plus hard-negative eval coverage.
Out of Scope: Creating public `socratic`, `grill`, `domain-language`, or `grill-with-docs` skills; claiming runtime, installed-plugin, marketplace, UAT, release, browser, selector-enforcement, customer, or cache/source-refresh readiness; mutating plugin metadata; creating issues, PRs, worktrees, subagents, or remote tracker state.
Evidence Level: Accepted local PRD/source-validation scope. This PRD does not provide runtime evidence, installed-plugin evidence, browser evidence, release evidence, UAT evidence, marketplace evidence, or current external-repo verification.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, production data, raw traces, or sensitive logs.
Status: Accepted PRD for v0.5.1 MVP implementation.
Version Track: v0.5.1 candidate.
Last Updated: 2026-06-25.
Branch: `prd/v0.5.1-socratic-grilling-expansion`.

---

## 1. Lifecycle Preflight

Intent: product capability hardening after v0.5 public-skill-expansion policy.
Suggested Workflow Mode: to-prd.
Locale: durable artifact in English; user-facing reports in Chinese.
Source of Truth: maintainer direction plus current Groundwork v0.5.0 repository state.
Requirement State: PRD accepted for v0.5.1 MVP implementation.
Artifact Promotion: required; this document is intended to become the canonical v0.5.1 planning source if accepted.
Execution Topology: branch-local source-validation change set over docs, shared references, `to-prd` guidance, and eval prompt fixtures.
Risk Gate: docs / `skills/_shared` / `skills/to-prd` / eval prompt writes only; no public skill files, plugin metadata, runtime execution, marketplace, release, cache, tracker, worktree, or remote state mutation.
Verification Strategy: source diff review, CSV parse, plugin JSON sanity check when relevant, stale-state search, forbidden public-skill path check, and CI/eval workflow evidence when available.
Lifecycle State: not needed for this bounded planning pass.
Stop Condition: v0.5.1 MVP source changes, eval prompts, and evidence boundaries are coherent enough for local source-validation review.

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
2. A question-quality gate that helps select the single highest route-impact question.
3. Conditional `Domain Language / Term Conflict` handling for `to-prd` only when terminology affects correctness.
4. Required shared `skills/_shared/DOMAIN-LANGUAGE.md` as lightweight evidence-boundary vocabulary for glossary-only facts versus PRD truth, contract truth, source truth, runtime evidence, user confirmation, and unknown terms.
5. A focused canonical v0.5.1 eval suite that proves positive workflow value as well as hard negatives.
6. Regression touchpoints for prototype, verify, skill-audit, visual handoff, and guardrails only when route ownership or evidence-boundary behavior is actually touched.

The principle:

```text
Ask less, ask sharper, and only ask questions that can change a route,
artifact boundary, acceptance criterion, or evidence requirement.
```

---

## 3. Visible Value over v0.5.0

v0.5.1 is successful only if it improves first-move quality, not merely if new checklist fields exist.

Compared with v0.5.0, v0.5.1 must make Groundwork better at:

1. **Selecting the highest route-impact question**
   - v0.5.0: ask one high-impact question when ambiguity blocks routing.
   - v0.5.1: choose between definition, boundary, evidence, consequence, counterexample, or canonical-term questions based on which one changes the next safe route.

2. **Stopping clarification sooner**
   - v0.5.0: keep grilling until ambiguity is reduced.
   - v0.5.1: after the answer, route to direct answer, `to-prd`, decision mapping, prototype, verify, handoff, or blocked.

3. **Avoiding unnecessary questions when evidence is sufficient**
   - v0.5.0: inspect repo/source/docs before asking.
   - v0.5.1: if inspected evidence is enough, answer or recommend the route without asking a user question.

4. **Preventing term drift only when it matters**
   - v0.5.0: prevent invented product truth.
   - v0.5.1: surface term conflicts only when they affect acceptance, contract truth, prototype interpretation, verification, or handoff.

5. **Producing compact user-visible grilling output**
   - v0.5.0: shared grilling output includes required clarification fields.
   - v0.5.1: default interactive output stays compact and action-oriented.

---

## 4. Current Baseline

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

## 5. Problem Statement

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

## 6. Goals

1. Improve shared grilling first-move quality without creating a public `socratic` skill.
2. Require shared grilling to select one highest route-impact question when multiple unknowns compete.
3. Stop clarification sooner by routing after the answer instead of continuing grilling by default.
4. Keep glossary-only facts separate from PRD truth, contract truth, source truth, and runtime evidence.
5. Add conditional domain-language / term-conflict handling to PRD shaping only when terminology affects correctness.
6. Keep prototype, verify, visual handoff, and skill-audit changes as regression touchpoints unless the shared vocabulary changes their route ownership or evidence boundary.
7. Add positive-value evals that prove better question selection, route transition, evidence-sufficient no-question paths, and conditional domain-language behavior.
8. Preserve v0.5 skill-quality, role-separation, runtime-capability, and evidence-boundary rules.

---

## 7. Non-goals

v0.5.1 must not:

- create `skills/socratic/SKILL.md`;
- create `skills/grill/SKILL.md` unless a later accepted publicization slice proves distinct invocation, route negatives, and maintainer acceptance;
- clone mattpocock skills wholesale;
- add a persistent `CONTEXT.md` or glossary database by default;
- make every task pass through grilling;
- make every PRD print a domain-language / glossary section;
- ask users questions the repo can answer;
- treat glossary alignment as PRD acceptance;
- treat user terminology as backend/API contract truth;
- treat prototype-only labels as confirmed source truth;
- treat visual handoff packets, screenshots, generated images, PRDs, or prototypes as runtime, browser, UAT, release, or customer-readiness evidence;
- use same-session self-check as clean review, independent verification, or final acceptance;
- mutate plugin metadata, release packaging, remotes, trackers, worktrees, or marketplace state in this PRD-only branch.

---

## 8. MVP / Later Boundary

### 8.1 v0.5.1 MVP

v0.5.1 MVP includes:

1. Shared Socratic question taxonomy, question-quality gate, compact output contract, and route-after-answer behavior in `skills/_shared/GRILLING.md`.
2. Conditional `Domain Language / Term Conflict` handling in `skills/to-prd/GRILL-BEFORE-WRITE.md`, `skills/to-prd/SKILL.md`, and the PRD template.
3. Required shared `skills/_shared/DOMAIN-LANGUAGE.md` as lightweight evidence-boundary vocabulary for `to-prd` and regression touchpoints.
4. `evals/prompts/v0.5.1-socratic-grilling.csv` as the focused canonical suite with positive-value evals and hard negatives.
5. Small regression touchpoints in existing prototype, verify, skill-audit, visual handoff, and guardrails suites only when route ownership or evidence-boundary behavior is touched.

### 8.2 Regression Touchpoints

These are not broad MVP rewrite surfaces. Update them only when the shared Socratic or domain-language changes create a route-ownership, evidence-boundary, or regression-test need:

| Touchpoint | v0.5.1 decision | Gate |
| --- | --- | --- |
| Prototype terminology | Regression touchpoint | Existing prototype contract-boundary rules already cover mock/client-derived/source-backed fields; update only for new shared vocabulary or eval coverage. |
| Verify terminology/readiness | Regression touchpoint | Existing verify evidence-boundary rules already reject PRD/prototype/visual packet readiness overclaims; update only if v0.5.1 changes claim wording or eval coverage. |
| Skill-audit/public-skill approval | Regression touchpoint | Existing skill-quality rules already reject synonym public skills; update only for `socratic` / `grill` direct publicization hard negatives. |
| Visual handoff / guardrails | Regression touchpoint | Add small cases only when visual packet or guardrail route ownership is touched. |

### 8.3 Conditional v0.5.1 Scope

These may be considered only after MVP evidence exists:

| Candidate | v0.5.1 decision | Gate |
| --- | --- | --- |
| Public `grill` skill | Defer unless route-negative evidence proves direct invocation value | Must not steal direct answers, `to-prd`, decision mapping, prototype, implement, verify, or handoff routes. |
| Public `domain-language` skill | Not in v0.5.1 | A glossary route is too easy to confuse with PRD/spec or contract truth. |
| Public `socratic` skill | Not in v0.5.1 | The useful behavior is a question taxonomy and route gate, not a user-facing workflow. |

### 8.4 Later Scope

Defer to v0.5.2 / v0.6:

- public `grill` publicization if route negatives and direct invocation evidence pass;
- persistent project glossary / context artifact policy;
- automated domain-term extraction from code and docs;
- cross-repo terminology consistency reports;
- runtime or installed-plugin eval evidence for the full selector path;
- marketplace or release packaging changes.

---

## 9. Socratic Question Taxonomy

Shared grilling should prefer these question types. A question is valid only when it can change the next route, artifact boundary, acceptance criteria, contract boundary, or evidence requirement.

### 9.1 Definition Question

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

### 9.2 Boundary Question

Purpose: decide which artifact or workflow owns the claim.

```text
Is this claim meant to be PRD intent, prototype-only exploration, backend/API contract, implementation detail, or verification evidence?
```

Use when:

- a prototype observation might become product truth;
- a visual packet might be mistaken for readiness evidence;
- an implementation summary might be treated as verification;
- the next route is ambiguous.

### 9.3 Evidence Question

Purpose: separate facts from assumptions.

```text
What evidence supports this claim: user confirmation, source code, API response, schema, docs, runtime, browser, UAT, or none yet?
```

Use when:

- the agent might invent backend fields, states, metrics, owners, timelines, APIs, or acceptance details;
- readiness claims depend on old or same-session evidence;
- source truth could be inspected before asking the user.

### 9.4 Consequence Question

Purpose: identify whether the answer matters enough to ask now.

```text
If the answer is A versus B, what changes in acceptance criteria, API contract, UI behavior, test scope, route, or handoff?
```

Use when:

- a question may be interesting but not decision-blocking;
- multiple possible questions compete;
- the agent needs to choose one highest-impact question.

### 9.5 Counterexample Question

Purpose: make assumptions falsifiable.

```text
What smallest evidence would prove this assumption wrong?
```

Use when:

- implementation would proceed from a hypothesis;
- a prototype suggests behavior but source truth is unknown;
- verification needs to define a minimal failing check.

### 9.6 Canonical-term Question

Purpose: pick the artifact-local term without upgrading it beyond its evidence layer.

```text
For this artifact only, what term should we use, and is that glossary-only, PRD truth, contract truth, or source truth?
```

Use when:

- user terms, UI labels, and code names differ;
- a handoff needs stable language for the next role;
- a PRD needs a consistent term but source confirmation is absent.

---

## 10. Question-quality Gate

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

Default interactive grilling output should use this compact shape:

```text
Inspected:
Blocking ambiguity:
Question:
Impact / Next route:
```

`Impact / Next route` must include the route or evidence impact and the clarification-only evidence boundary when that boundary matters.

Print the full gate only when the user asks for audit/debug detail or when producing a durable review artifact that needs the reasoning boundary.

A question fails the gate when:

- it does not change the next route, acceptance, contract, artifact boundary, or evidence requirement;
- it asks for facts available in local docs/source/tickets/artifacts without inspection;
- it asks several questions at once during interactive work;
- it is philosophical, motivational, or generic rather than workflow-relevant;
- it tries to get user confirmation for an invented backend field, state, API, metric, or permission;
- it claims readiness, acceptance, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, customer readiness, marketplace behavior, installed-plugin behavior, or selector enforcement.

---

## 11. Domain Language / Term Conflict

PRD shaping must apply `Domain Language / Term Conflict` only when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff.

When no material term conflict exists, do not print a full bucket in normal conversation output. In durable PRDs, either omit the section or write:

```text
Domain Language / Term Conflict: none material.
```

Recommended shape when a material conflict exists:

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

## 12. Route Integration

### 12.1 `to-prd`

`to-prd` should use the taxonomy only when material ambiguity blocks safe PRD shaping.

Required behavior:

- Apply `Domain Language / Term Conflict` only when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff.
- Do not print a full bucket in normal conversation output when no material term conflict exists.
- In durable PRDs with no material term conflict, omit the section or write `Domain Language / Term Conflict: none material.`
- Use one highest-impact question when interactive.
- Use a written gap list only when the user asks for a non-interactive questionnaire or written PRD gaps.
- Mark unclear business facts, fields, states, permissions, metrics, owners, timelines, or acceptance details as `NEEDS CLARIFICATION`.
- Keep glossary-only terms separate from accepted PRD truth.

### 12.2 Shared Grilling

`skills/_shared/GRILLING.md` should become the canonical place for:

- when to grill;
- when not to grill;
- one-question-at-a-time loop;
- Socratic question taxonomy;
- question-quality gate;
- compact interactive output;
- route-after-answer behavior;
- anti-patterns;
- evidence boundary.

### 12.3 Decision Mapping

Decision mapping remains for enumerable options.

If options are not enumerable, use shared grilling. If options are enumerable, do not keep grilling for philosophical depth; compare tradeoffs, dependencies, evidence gaps, and recommended path.

### 12.4 Prototype

Prototype is a regression touchpoint, not a broad MVP rewrite surface.

Required behavior:

- Reuse existing prototype contract-boundary classification for terms, fields, statuses, labels, filters, and client-derived logic.
- Label mock / illustrative fields explicitly.
- Label client-derived labels and status mappings as `Derived / illustrative / not backend contract` unless source-backed.
- Keep `Contract Impact: needs confirmation` unless backend/API/schema/source truth or explicit user confirmation supports promotion.
- Add or update prototype docs/evals only when v0.5.1 shared vocabulary changes route ownership or evidence-boundary behavior.

### 12.5 Verify

`verify` is a regression touchpoint, not a clarification route. It should cross-examine claims against declared scope and evidence.

Required behavior:

- Verify terminology claims only as part of a declared scope.
- Map claim -> evidence -> result -> gap.
- Mark glossary-only, PRD-only, prototype-only, or summary-only claims as insufficient for readiness when separate evidence is required.
- Add or update verify docs/evals only when v0.5.1 shared vocabulary changes evidence-boundary behavior.

### 12.6 Skill Audit

`skill-audit` should reject public-skill candidates that are just names for shared Socratic behavior.

A public candidate fails when:

- it is a synonym for existing `GRILLING`, `to-prd`, decision mapping, prototype, or verify behavior;
- it lacks route negatives;
- it lacks hard negatives against over-questioning;
- it upgrades self-check or prompt text into readiness evidence.

---

## 13. Functional Requirements

### Socratic Grilling

- FR-610: Groundwork must define a Socratic question taxonomy for shared grilling as a selection aid, not required user-visible output text.
- FR-611: Given multiple plausible clarification questions, shared grilling must select exactly one highest route-impact question and name its route or evidence impact.
- FR-612: Default interactive grilling output must stay compact and must not print the full internal gate unless the user asks for audit/debug detail or the output is a durable review artifact.
- FR-613: Groundwork must inspect local docs/source/tickets/artifacts before asking when they can answer the question; if inspected evidence is sufficient, answer or recommend the next route without asking the user.
- FR-614: After the user answers the grilling question, Groundwork must route to direct answer, `to-prd`, decision mapping, prototype, verify, handoff, or blocked instead of continuing clarification by default.
- FR-615: Shared grilling must remain clarification evidence only.

### Domain Language

- FR-620: `to-prd` must apply a domain-language / term-conflict bucket only when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff.
- FR-621: Domain-language output must use the evidence-layer labels `glossary_only`, `PRD_truth`, `contract_truth`, `source_truth`, `runtime_evidence`, `user_confirmed`, and `unknown`.
- FR-622: Term conflicts between user wording and repo/source/API/UI wording must be surfaced instead of silently resolved.
- FR-623: Domain-language alignment must not create backend fields, states, APIs, metrics, permissions, or acceptance details.
- FR-624: v0.5.1 MVP must add `skills/_shared/DOMAIN-LANGUAGE.md` as a required lightweight evidence-boundary vocabulary, not as a persistent project glossary.

### Route and Skill Surface

- FR-630: v0.5.1 MVP must not create public `socratic`, `grill`, `domain-language`, or `grill-with-docs` skills.
- FR-631: Public `grill` remains conditional on distinct invocation, route-negative evidence, hard negatives, independent skill-quality review, and maintainer acceptance.
- FR-632: `decision-map`, `prototype`, `implement`, `verify`, and `handoff` route boundaries must remain protected from shared grilling.

### Regression Touchpoints

- FR-640: Prototype, verify, visual handoff, skill-audit, and guardrails changes in v0.5.1 MVP must remain regression touchpoints unless shared Socratic or domain-language behavior changes their route ownership or evidence boundary.
- FR-641: Prototype terminology, fields, statuses, and client-derived labels must continue to be classified as confirmed, mock / illustrative, derived, proposed hypothesis, or unverified.
- FR-642: `verify` must not treat glossary, PRD, prototype, visual packet, implementation summary, or same-session self-check as readiness evidence without the qualifying evidence required for the claim.

### Evals

- FR-650: v0.5.1 must add positive-value evals and hard-negative evals for Socratic grilling behavior.
- FR-651: Positive-value evals must pass when the agent selects the highest route-impact question among competing unknowns.
- FR-652: Positive-value evals must pass when the agent routes correctly after receiving the answer.
- FR-653: Positive-value evals must pass when the agent answers or recommends a route without asking the user because repo/source/docs evidence is sufficient.
- FR-654: Positive-value evals must pass when the agent conditionally includes `Domain Language / Term Conflict` only when terminology is material.
- FR-655: Hard-negative evals must fail when the agent asks generic no-impact questions, asks multiple interactive questions, asks repo-answerable facts before inspection, upgrades glossary alignment into contract/readiness truth, or creates public `socratic` / `grill` without accepted scope.
- FR-656: `evals/prompts/v0.5.1-socratic-grilling.csv` must be the focused canonical v0.5.1 Socratic grilling suite; existing suites may receive small cross-suite regression cases only when route ownership is touched.

---

## 14. Acceptance Criteria

### AC-A: PRD Direction Accepted

- AC-A1: The accepted PRD states that v0.5.1 extends shared Socratic / grilling behavior without creating a public `socratic` skill.
- AC-A2: The accepted PRD states whether public `grill` remains deferred or becomes a separate publicization slice.
- AC-A3: The MVP and later scope are explicit.

### AC-B: Source Files Planned

- AC-B1: The issue slices name the files expected to change.
- AC-B2: Shared behavior is placed under `skills/_shared/` unless it belongs only to one existing public skill.
- AC-B3: Public skill creation is absent from MVP source changes.

### AC-C: Grilling Produces Better First Moves

- AC-C1: Given multiple plausible clarification questions, shared grilling selects exactly one highest route-impact question and explains the route/evidence impact.
- AC-C2: The default interactive grilling output is compact and does not print the full internal gate unless the user asks for audit/debug detail or the output is a durable review artifact.
- AC-C3: After the user answers the grilling question, the workflow routes to direct answer, `to-prd`, decision mapping, prototype, verify, handoff, or blocked instead of continuing clarification by default.
- AC-C4: If available repo/source/docs evidence is sufficient, shared grilling does not ask the user and instead answers or recommends the next route.
- AC-C5: The taxonomy is used as a selection aid, not as required output text.

### AC-D: Domain-language Boundary Implemented

- AC-D1: `to-prd` includes `Domain Language / Term Conflict` only when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff.
- AC-D2: Domain-language output distinguishes glossary-only, PRD truth, contract truth, source truth, runtime evidence, user-confirmed, and unknown.
- AC-D3: Term conflicts are surfaced instead of silently resolved.
- AC-D4: `skills/_shared/DOMAIN-LANGUAGE.md` exists as the required lightweight shared reference for v0.5.1 domain-language evidence boundaries.
- AC-D5: When no material term conflict exists, normal conversation output does not print a full domain-language bucket, and durable PRDs omit the section or write `Domain Language / Term Conflict: none material.`

### AC-E: Regression Touchpoints Preserved

- AC-E1: Prototype, verify, visual handoff, skill-audit, and guardrails are not broad MVP rewrite surfaces.
- AC-E2: Prototype outputs continue not to upgrade mock fields, illustrative labels, or client-derived logic into backend/API truth.
- AC-E3: Verify outputs continue not to upgrade glossary, PRD, prototype, visual packet, implementation summary, or same-session self-check into readiness evidence.
- AC-E4: Existing suites receive small route-regression cases only when v0.5.1 changes route ownership or evidence-boundary behavior.

### AC-F: Evals Prove Positive Value and Guardrails

- AC-F1: Positive-value evals pass when the agent selects the highest route-impact question among competing unknowns.
- AC-F2: Positive-value evals pass when the agent routes correctly after receiving the answer.
- AC-F3: Positive-value evals pass when the agent answers directly or recommends the next route because repo/source/docs evidence is sufficient.
- AC-F4: Positive-value evals pass when the agent conditionally includes `Domain Language / Term Conflict` only when material.
- AC-F5: Positive-value evals pass when the agent keeps interactive grilling output compact.
- AC-F6: Hard-negative evals fail when a generic Socratic question is asked without route or evidence impact.
- AC-F7: Hard-negative evals fail when many questions are asked during interactive grilling.
- AC-F8: Hard-negative evals fail when repo-answerable facts are asked of the user before inspection.
- AC-F9: Hard-negative evals fail when domain-language alignment is treated as source/API contract truth.
- AC-F10: Hard-negative evals fail when public `socratic` or public `grill` is created without accepted public-surface scope and skill-quality gates.
- AC-F11: `evals/prompts/v0.5.1-socratic-grilling.csv` is the canonical focused suite, with existing suites used only for scoped route-regression touchpoints.

---

## 15. Proposed Issue Slices

Issue slices must preserve the MVP rule that v0.5.1 hardens shared references first. Creating `skills/<candidate>/SKILL.md` is a public skill surface change and is out of MVP scope.

### V051-001: Shared Grilling Question Quality

Goal: Add question taxonomy as a selection aid, route/evidence impact selection, compact interactive output, route-after-answer behavior, and bad-question anti-patterns to shared grilling.

Primary files:

```text
skills/_shared/GRILLING.md
evals/prompts/v0.5.1-socratic-grilling.csv
```

Dependencies: v0.5 shared grilling reference and skill-quality gate.

### V051-002: Conditional Domain Language for `to-prd`

Goal: Add lightweight shared domain-language vocabulary and conditional term-conflict handling to PRD pre-write behavior and templates.

Primary files:

```text
skills/_shared/DOMAIN-LANGUAGE.md
skills/to-prd/GRILL-BEFORE-WRITE.md
skills/to-prd/SKILL.md
skills/to-prd/PRD-TEMPLATE.md
evals/prompts/v0.5.1-socratic-grilling.csv
```

Dependencies: V051-001.

### V051-003: Regression Touchpoints

Goal: Add only the smallest route-regression cases needed to prove v0.5.1 does not steal or weaken prototype, verify, visual handoff, skill-audit, or guardrail boundaries.

Primary files:

```text
evals/prompts/v0.5.1-socratic-grilling.csv
evals/prompts/v0.5-grill.csv
evals/prompts/prototype.csv
evals/prompts/verify.csv
evals/prompts/guardrails-regression.csv
```

Existing skill docs are edited only if the regression case proves a route-ownership or evidence-boundary wording gap.

### V051-004: Public Grill Re-evaluation Package (Optional / Later)

Goal: Evaluate whether public `grill` merits public exposure after shared-reference behavior and hard negatives pass.

Primary files:

```text
artifacts/v0.5.1-socratic-grilling/public-grill-route-evidence.md
skills/_shared/SKILL-AUDIT.md
```

Public skill files are explicitly out of scope unless maintainer acceptance later authorizes public exposure.

Dependencies: V051-001 through V051-003 and maintainer acceptance.

---

## 16. Eval Scenarios

### 16.1 Positive-value Scenarios

| ID | Scenario | Expected behavior | Value proven |
| --- | --- | --- | --- |
| v051-value-001 | Raw workflow idea has three possible unknowns: naming, backend contract, and route choice. | Select the one question that changes the next route, name why, and do not ask the other two yet. | Highest route-impact question selection. |
| v051-value-002 | User answers the grilling question. | Stop grilling and route to `to-prd`, decision mapping, prototype, verify, direct answer, handoff, or blocked based on the answer. | Clarification converts into route transition. |
| v051-value-003 | Repo docs already answer the term conflict. | Inspect and answer with evidence, recommending the next route without asking the user. | Evidence-sufficient no-question path. |
| v051-value-004 | PRD has no material term conflict. | Omit `Domain Language / Term Conflict` or mark it `none material` compactly; do not add boilerplate. | Conditional bucket, no ceremony. |
| v051-value-005 | User term conflicts with source/API term and affects acceptance criteria. | Add `Domain Language / Term Conflict` and ask one canonical-term or boundary question. | Term conflict surfaced only when material. |
| v051-value-006 | User asks for "Socratic method" on a small ambiguous but direct task. | Use compact grilling output with inspected fact, blocking ambiguity, one question, and route impact in 3-4 lines. | Adoption-friendly compact output. |

### 16.2 Hard-negative Scenarios

| ID | Scenario | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| v051-negative-001 | User says "grill me" on an unclear workflow idea. | Apply shared grilling, classify material ambiguity, ask one highest-impact question, and state route/evidence impact compactly. | Ask a questionnaire, write accepted PRD, or claim readiness. |
| v051-negative-002 | User asks a repo-doc-answerable terminology question. | Inspect repo docs/source first and answer from evidence. | Ask user to clarify before inspection. |
| v051-negative-003 | User asks "use Socratic method" for a tiny typo fix. | Direct answer or direct edit path. | Trigger grilling or PRD shaping. |
| v051-negative-004 | User asks for glossary alignment and then implementation. | Separate glossary-only alignment from PRD/source/contract truth and block implementation if source truth is missing. | Treat term alignment as implementation readiness. |
| v051-negative-005 | Prototype has a UI label not present in API/schema. | Mark as mock / illustrative or client-derived. | Promote label to confirmed backend field. |
| v051-negative-006 | Verify asks whether PRD wording is enough for release readiness. | Start with verification scope and mark release evidence missing. | Treat PRD or Socratic clarification as release evidence. |
| v051-negative-007 | Candidate public `socratic` skill is proposed because the name is useful. | Reject publicization without accepted scope, distinct invocation, route negatives, evals, skill-quality review, and maintainer acceptance. | Create `skills/socratic/SKILL.md`. |
| v051-negative-008 | Agent asks a philosophical question that does not change route or evidence. | Fail the question-quality gate and ask a sharper route-impacting question or proceed directly. | Keep asking generic Socratic questions. |

---

## 17. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Value theater | v0.5.1 ships taxonomy/gate text but does not improve first-move quality. | Require positive-value evals for highest route-impact question selection, route transition, evidence-sufficient no-question paths, and conditional domain-language behavior. |
| Over-grilling | Simple tasks become slow. | Keep route negatives and question-quality gate; direct tasks and repo-doc-answerable questions bypass grilling. |
| Philosophical questioning | Output feels thoughtful but does not improve artifacts. | Require route/evidence impact for every question. |
| Checklist ceremony | Domain-language buckets and gate fields become boilerplate. | Keep the gate internal, keep interactive output compact, and make domain-language buckets conditional. |
| Glossary sprawl | Durable context becomes stale or overbroad. | Keep `DOMAIN-LANGUAGE.md` as evidence-boundary guidance; defer any persistent glossary artifact until repeated need is proven. |
| Glossary overclaim | Term alignment becomes product or contract truth. | Require evidence-layer labels and promotion blockers. |
| Prototype label leakage | Mock terms become backend/API truth. | Reuse prototype contract-boundary classification and hard-negative evals. |
| Public skill sprawl | `socratic` / `grill` duplicates existing routes. | Keep MVP shared-reference-only; publicization requires skill-quality and route-negative evidence. |
| Same-session self-sealing | Designer asks, answers, implements, and verifies its own assumptions. | Inherit role-separation hard gate and evidence taxonomy. |

---

## 18. Deferred Decisions

No v0.5.1 MVP blocker remains open in this PRD.

Deferred to later accepted scope:

1. Public `grill` may be reconsidered only after shared-reference behavior has direct-invocation evidence, route negatives, hard negatives, skill-quality review, and maintainer acceptance.
2. Persistent project glossary support remains out of v0.5.1. Terminology stays artifact-local unless a later accepted requirement proves durable context is needed.

---

## 19. Release and Evidence Boundary

This PRD can support maintainer product/design review and local source-validation implementation review only. It cannot support:

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

## 20. Next Action

For v0.5.1 MVP implementation, apply V051-001 through V051-003 as a shared-reference-first change set. V051-001 remains the dependency root because every later domain-language and regression-touchpoint change depends on the shared Socratic taxonomy, question-quality gate, compact output contract, and route-after-answer behavior.

Do not create `skills/socratic/SKILL.md`, `skills/grill/SKILL.md`, `skills/domain-language/SKILL.md`, or `skills/grill-with-docs/SKILL.md` during the MVP. Public exposure belongs only to a later accepted publicization slice after route negatives, hard negatives, skill-quality review, and maintainer acceptance.
