# PRD v0.5: Prototype-first Skill Expansion and Runtime-aware Workflow Gates

Target Reader: Groundwork maintainers, implementation agents, reviewers, verifier roles, runtime adapter authors, and skill authors planning v0.5.
Reader Action Needed: Review this consolidated PRD as the single v0.5 source of truth; do not use the former addenda as parallel acceptance sources.
Decision Supported: Whether Groundwork should accept a prototype-first, role-separated, capability-aware, quality-gated skill expansion direction for v0.5, and which parts belong in MVP versus later releases.
Artifact Type: PRD.
Source of Truth: Maintainer request to fold review feedback into the v0.5 PRD; review feedback attachment supplied on 2026-06-23; follow-up review feedback supplied on 2026-06-24; the branch-local v0.5 PRD/addenda being consolidated; repo-local Groundwork guidance and shared artifact rules.
Scope: v0.5 planning for public skill expansion policy, skill quality gates, role separation, runtime capability discovery, model/runtime selector evidence boundaries, Prototype Lab shared references, visual handoff packet rules, skill-audit workflow requirements, and focused implementation slices.
Out of Scope: Implementing the skills in this PRD pass; claiming runtime, installed-plugin, marketplace, UAT, release, customer, browser, selector-enforcement, or cache/source-refresh readiness; changing plugin metadata; creating issues, PRs, worktrees, subagents, or remote tracker state.
Evidence Level: Planning evidence only. This PRD consolidates existing branch documents and maintainer review feedback. It does not add runtime evidence, installed-plugin evidence, browser evidence, release evidence, UAT evidence, marketplace evidence, or current official-doc verification.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, production data, raw traces, or sensitive logs.
Status: Accepted draft PRD baseline after review consolidation; implementation should not start until the issue-slice clarifications in this document are reflected in the issue map.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-24.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Lifecycle Preflight

Intent: product capability expansion and PRD consolidation.
Suggested Workflow Mode: to-prd.
Locale: durable artifact in English; user-facing reports in Chinese.
Source of Truth: mixed local artifact plus maintainer review feedback.
Requirement State: PRD draft for maintainer acceptance.
Artifact Promotion: required; this document is intended to be the canonical v0.5 planning source.
Execution Topology: branch-local documentation artifact only.
Risk Gate: git write to PRD/docs files only.
Verification Strategy: documentation consistency checks, stale-state search, `git diff --check`, and broad repository metadata/CSV validation if applicable.
Lifecycle State: not needed for this bounded planning pass.
Stop Condition: v0.5 MVP, later scope, role/runtime gates, acceptance criteria, and issue slices are coherent enough for maintainer review.

---

## 2. Executive Summary

Groundwork v0.5 should evolve from a mostly PRD-first workflow base into a decision-first workflow base:

```text
raw intent
  -> direct answer when bounded
  -> grill / decision-map / prototype when ambiguity is material
  -> PRD / issue map / implementation / verification / handoff when source truth is accepted
```

The direction is accepted as a product direction, but the original v0.5 branch was too broad for a directly implementable PRD. This document folds the prior PRD and five addenda into one source of truth and splits the work into:

- v0.5 MVP: policy and gates that make later skill expansion safe;
- v0.5 conditional scope: public skills that may land only after quality, routing, and hard-negative eval gates;
- v0.5.1 / v0.6 later scope: larger setup/router/model-characterization work that should not block the MVP.

The highest-priority product change is not "add many public skills." The highest-priority change is:

```text
public skill expansion is allowed only when explicitly scoped, quality-gated,
role-separated, capability-aware, and covered by positive plus hard-negative evals.
```

---

## 3. Review Consolidation Decision

The former branch shape had six parallel PRD/addendum documents. That was unsafe because implementation agents had to reconcile competing amendment order, especially around role separation, runtime capability, and Spark model routing.

The canonical document set is now:

```text
docs/prd-v0.5-prototype-first-skill-expansion.md
docs/capability-seeds/codex-model-menu-2026-06-23.md
docs/research/v0.5-codex-spark-signal-scan.md
```

The master PRD contains final product decisions. The capability seed records a dated user-observed Codex model menu input. The research scan records optional external signal and must not introduce requirements or acceptance gates by itself.

---

## 4. Problem Statement

Groundwork has a strong evidence-first foundation, but v0.5 needs better first-move selection and stronger evidence separation.

Current failure modes:

1. PRD-first is too expensive when the real uncertainty is visual, stateful, or option-heavy.
2. Prototype artifacts can clarify decisions, but they can also be mistaken for backend/API contract truth.
3. Public skill expansion is currently blocked by a small-surface rule rather than governed by an explicit quality gate.
4. Review and verification can be overclaimed when the same role designs, implements, self-checks, and closes out a material change.
5. Runtime/model routing can be overclaimed when a prompt requests a model, subagent, child thread, or reasoning level but the runtime did not enforce it.
6. Model menu facts, official-doc references, local UI observations, and community research can blur into a single evidence layer.
7. v0.5 implementation slices were too large, especially Prototype Lab plus visual handoff plus verification.

---

## 5. Goals

1. Replace fixed public-skill-count thinking with quality-gated public skill expansion.
2. Add a role separation hard gate for material design, implementation, clean review, verification, and closeout claims.
3. Add lazy runtime capability discovery so Groundwork does not invent model, selector, subagent, or child-thread availability.
4. Upgrade `prototype` toward Prototype Lab through shared references for decision capture, contract-boundary review, UI variants, logic/state labs, and visual handoff packets.
5. Define when `grill`, `decision-map`, `skill-audit`, `setup-groundwork`, and `visual-handoff` should be public skills, shared references, or later work.
6. Make cognitive/model routing profile recommendations visible without claiming selector enforcement.
7. Preserve evidence boundaries for PRDs, prototypes, visual packets, self-checks, clean reviews, runtime evidence, browser evidence, UAT, and release readiness.
8. Add positive, negative, and hard-negative eval coverage for every material v0.5 workflow gate.

---

## 6. Non-goals

v0.5 must not:

- copy external skills wholesale;
- add public skills merely because their names are attractive;
- make every task go through setup, grill, decision-map, PRD, and prototype ceremony;
- treat prototype-only mock fields as confirmed backend/API contract truth;
- treat visual packets, screenshots, generated images, PRDs, or prototypes as browser/runtime/UAT/release evidence;
- use implementation self-checks as independent clean review or final readiness evidence;
- silently substitute subagents for child threads, child threads for subagents, or prompt preferences for selector enforcement;
- hardcode a permanent global model list as runtime truth;
- claim current official OpenAI/Codex behavior from unrefreshed local planning notes;
- mutate plugin metadata, release packaging, remotes, trackers, worktrees, or marketplace state in this PRD-only branch.

---

## 7. MVP / Later Boundary

### 7.1 v0.5 MVP

v0.5 MVP includes:

1. Public skill expansion policy plus shared `SKILL-QUALITY.md`.
2. Role separation hard gate for material changes.
3. Lazy runtime capability and selector-enforcement boundary.
4. Prototype Lab shared references for decision capture and contract-boundary handling.
5. Visual handoff packet as a shared artifact pattern used by `prototype`, `handoff`, and `verify`.
6. Skill-audit workflow as a required quality lens for public skill changes; public exposure is conditional.
7. Regression coverage for hard negatives: self-verification, prototype mock promotion, visual packet readiness overclaim, selector enforcement overclaim, and runtime fallback mismatch.

### 7.2 Conditional v0.5 Scope

These may become public skills in v0.5 only after routing and hard-negative evals pass:

| Candidate | v0.5 decision | Gate |
| --- | --- | --- |
| `grill` | Public candidate | Must prove distinct invocation from `to-prd` and avoid over-questioning small work. |
| `decision-map` | Conditional public candidate | Must pass route-conflict negatives against `to-prd`, `write-plan`, `dispatch`, and direct answers. |
| `skill-audit` | Required workflow/reference first; public candidate only if direct invocation is proven | Must not let authors approve their own skill changes. |
| `setup-groundwork` | Guide/reference first; public skill later unless setup event frequency and trigger clarity are proven | Must avoid becoming a large one-time questionnaire or duplicate docs generator. |
| `visual-handoff` | Shared branch under `prototype` / `handoff` | Public skill deferred until repeated direct invocation is proven. |

### 7.3 Later Scope

Defer to v0.5.1 / v0.6:

- full public `setup-groundwork`;
- full public `decision-map` if v0.5 keeps it reference-only;
- full Spark characterization suite and local A/B evals;
- refreshed community signal scan;
- public `visual-handoff`;
- broad model/router automation beyond lazy capability discovery;
- plugin metadata/version/release changes.

---

## 8. Public Skill Expansion Policy

A new public skill may be added only when all are true:

1. It has a distinct invocation moment.
2. It has a leading word or name that is not merely a synonym for an existing skill.
3. It cannot be safely implemented as a branch or shared reference of an existing skill.
4. It has a clear trigger contract and clear should-not-trigger cases.
5. It has checkable completion criteria.
6. It has failure branches for likely misuse.
7. It declares evidence boundaries.
8. It has at least three positive and three negative eval fixtures before release.
9. It has hard-negative fixtures for its most dangerous overclaims.
10. It passes skill-quality review before merge.

The repo guidance should change from "do not add public skills" to:

```text
Do not add public skills unless an accepted PRD, issue, or maintainer directive explicitly expands the public surface and the new skill passes the skill-quality, routing, and eval gates.
```

---

## 9. Role Separation Hard Gate

Groundwork v0.5 must enforce this rule:

```text
The same AI role/session that designs or implements a material change must not be the authority that clean-reviews, verifies, or accepts that same change.
```

Self-checks are useful implementation hygiene. They are not independent review.

```text
self-check evidence != clean review evidence
self-run tests != independent verification
implementation summary != acceptance evidence
same-session review != independent review
same-session design -> implementation -> verification != allowed closeout
```

### 9.1 Materiality Threshold

Role separation is required when the change affects:

- public skill surface;
- shared guardrails;
- runtime/router/selector policy;
- release, UAT, customer, runtime, browser, or marketplace readiness claims;
- schema, API, security, permissions, data correctness, or migrations;
- broad eval behavior;
- frontend/backend contract truth;
- cross-module workflow behavior.

Non-material bounded edits may proceed in the same session after source truth is accepted, but final reports must label evidence as self-check only and must not claim independent readiness.

### 9.2 Role Authority

Designer/planner may produce PRDs, decision maps, prototypes, architecture options, or skill designs. It may implement only after maintainer acceptance or an independent accepted source package exists, and it still cannot clean-review or independently verify its own material change.

Implementer may inspect, edit, run tests/checks, self-review, and report evidence. It must not act as clean reviewer or final verifier for its own change.

Clean reviewer must be read-only unless explicitly reassigned to a separate follow-up implementation task. If reassigned to fix, a new clean reviewer is required afterward.

Verifier must begin with explicit scope and separate covered/not-covered evidence. It must block or mark unverified when independent evidence is absent for material readiness claims.

Coordinator may synthesize evidence but must not claim evidence it did not receive.

---

## 10. Runtime Capability and Model Policy

Groundwork v0.5 must enforce this rule:

```text
Groundwork must not assume that a model, reasoning effort, subagent runtime,
child-thread runtime, worktree runtime, or selector enforcement mechanism is
available merely because a prompt requests it.
```

### 10.1 Lazy Capability Discovery

Always record the minimal capability boundary when runtime/model selection is material:

```yaml
capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
```

Only ask or inspect detailed model, reasoning, subagent, and worktree fields when:

- runtime routing is material to the task;
- the user requested a concrete runtime or model;
- a dispatch package claims runtime/model selection;
- a final report might claim selector enforcement;
- missing runtime capability would change the route or stop condition.

### 10.2 Evidence Layers

Keep these layers separate:

| Evidence layer | What it can support | What it cannot support |
| --- | --- | --- |
| Official docs reference | dated product guidance | user-specific availability or selector enforcement |
| User-observed model menu seed | current user-supplied visible labels | every Codex surface, runtime execution, reasoning support |
| Runtime adapter/tool report | stronger capability and enforcement evidence | product truth outside the reported runtime |
| Prompt/package preference | desired model/runtime | actual execution or enforcement |
| Local characterization eval | Groundwork-specific fit | universal benchmark or release readiness |
| Community/third-party scan | supporting signal | mandatory acceptance gate or representative consensus |

### 10.3 Canonical Model Profiles

Groundwork routes by profile first and maps to concrete model only when capability evidence exists:

| Profile | Default use | Boundary |
| --- | --- | --- |
| `fast_scan` | quick classification, fixture linting, low-risk summarization | not final readiness or high-risk review |
| `balanced_work` | normal PRD/doc work, scoped implementation with accepted AC, ordinary verification with current evidence | not high-risk final authority |
| `strong_reasoning` | ambiguous product decisions, prototype-first routing, public skill design, cross-cutting plans | not a substitute for role separation |
| `exhaustive_review` | independent clean review, skill-audit, architecture/security/privacy/schema/data correctness review | still needs evidence and role separation |
| `spark_iteration` | bounded fast coding iteration with fast feedback loop | not final clean review, final verification, public skill approval, release/UAT/customer authority |

The dated model menu seed for 2026-06-23 lives in `docs/capability-seeds/codex-model-menu-2026-06-23.md`.

### 10.4 Codex UI Thinking Normalization

The user-observed Codex UI thinking labels are:

```text
Low
Medium
High
Extra high
```

Groundwork normalizes them internally as:

```text
low
medium
high
xhigh
```

API reasoning effort values and Codex UI thinking labels are different evidence layers. Groundwork must not treat the Codex UI observation as a universal API fact, and must not treat API docs as proof of current Codex UI selector enforcement.

### 10.5 Subagent vs Child Thread Boundary

Groundwork must not silently substitute runtime types:

```text
Requested runtime:
Available runtime:
Runtime mismatch: yes | no | unknown
Fallback proposed:
User approval required: yes | no
```

If the user explicitly asks for a child thread / managed worktree thread, a subagent is a mismatch unless the user approves fallback. If the user explicitly asks for subagents, a managed worktree child thread is a mismatch unless the user approves fallback.

---

## 11. Prototype Lab and Visual Handoff

`prototype` should evolve through shared references before new public skill expansion:

1. Decision capture: confirmed decisions, rejected variants, unverified assumptions, mock fields, client-derived logic, open questions, and next route.
2. Contract-boundary review: prototype-only fields must not become backend/API truth without source evidence or explicit user confirmation.
3. UI variants: structurally different alternatives when visual design is the question.
4. Logic/state lab: runnable or inspectable state-machine/business-rule exploration when behavior is unclear.
5. Visual handoff packet: structured communication artifact for frontend/backend collaboration.

Visual handoff packet required sections:

```text
Overview
State / Flow Diagram
UI Surface Map
Selected Variant or Variant Switcher
API Contract Table
Error / Empty / Loading States
AC -> UI Behavior -> API Evidence Mapping
Mock vs Confirmed Field Badges
Open Questions
Do Not Implement / Do Not Assume
Evidence Boundary
```

Evidence rule:

- HTML packet: communication and review artifact.
- Browser run: browser evidence only if actually run and recorded.
- API/schema/source inspection: source truth only if inspected and named.
- UAT/customer readiness: separate verification claim only.

---

## 12. Skill-audit Workflow

`skill-audit` is required as a workflow/reference for public skill additions and material skill changes. It may become a public skill only after direct invocation and routing negatives prove it is worth the surface area.

Audit checks:

1. Invocation class: public model-invoked, user-invoked, shared reference, branch, or router.
2. Trigger description: leading word first, stable trigger, no duplicate synonym routing.
3. Workflow: ordered steps and checkable completion.
4. Information hierarchy: universal rules in `SKILL.md`, branch detail in references.
5. Progressive disclosure: references loaded only when the branch requires them.
6. Duplication and no-op prose removal.
7. Failure branches for likely misuse.
8. Evidence boundary and stop condition.
9. Positive, negative, and hard-negative eval coverage.

A skill author must not be the final authority that approves its own material skill-quality change.

---

## 13. Functional Requirements

### Policy and Quality

- FR-501: Groundwork must allow public skill expansion only under accepted scope and quality gates.
- FR-502: Groundwork must define a shared skill-quality checklist before adding public skills.
- FR-503: Repo guidance must describe public skill expansion as quality-gated, not fixed-count.
- FR-504: Public skill additions must include trigger, should-not-trigger, and hard-negative eval fixtures.

### Role Separation

- FR-510: Groundwork must define designer/planner, implementer, clean reviewer, verifier, and coordinator roles.
- FR-511: Groundwork must apply role separation to material changes according to the materiality threshold.
- FR-512: Implementer self-checks must be labeled separately from clean review and independent verification.
- FR-513: `verify` must block or mark unverified material readiness claims when the only evidence is same-session self-check.
- FR-514: Dispatch/handoff/closeout packages must report independent review and independent verification status separately.

### Runtime Capability

- FR-520: Groundwork must define lazy runtime capability discovery and selector-enforcement statuses.
- FR-521: Groundwork must route by model profile before mapping to concrete models.
- FR-522: Groundwork must separate model profile, concrete model, thinking/reasoning preference, runtime selection, and selector enforcement.
- FR-523: Groundwork must prevent silent fallback between subagents and child-thread/worktree runtimes.
- FR-524: Result/final reports must not claim model/runtime execution or selector enforcement without tool/runtime evidence.

### Prototype Lab

- FR-530: `prototype` must support decision capture and contract-boundary review without promoting mock fields to contract truth.
- FR-531: UI variants and logic/state labs must be added as focused references or branches before a public `visual-handoff` skill is considered.
- FR-532: Visual packets must include evidence boundaries and must not replace source/API contract docs.

### Skill Candidates

- FR-540: `grill` may become public only if it has distinct routing from `to-prd` and hard negatives against over-questioning.
- FR-541: `decision-map` may become public only if it has distinct routing from `write-plan`, `dispatch`, `to-prd`, and direct answers.
- FR-542: `skill-audit` must exist as a required workflow/reference before it is considered public.
- FR-543: `setup-groundwork` must start as a guide/reference unless setup trigger clarity and frequency justify public exposure.

### Evals

- FR-550: v0.5 must add hard-negative evals for self-verification, self-approval, prototype mock promotion, visual packet readiness overclaim, selector enforcement overclaim, runtime mismatch, and Spark final-authority misuse.
- FR-551: v0.5 issue slices must map each material acceptance criterion to a source change and a focused check.

---

## 14. Acceptance Criteria

### AC-A: Policy Accepted

- AC-A1: The accepted PRD states a single public skill expansion policy and removes addendum ordering ambiguity.
- AC-A2: MVP and later scope are explicit.
- AC-A3: Candidate skills are classified as public candidate, conditional public candidate, shared workflow/reference, or later scope.

### AC-B: Source Files Changed

- AC-B1: A shared skill-quality reference exists before any public skill is added.
- AC-B2: A shared role separation reference exists and is referenced by affected skills when implemented.
- AC-B3: A shared runtime capability / selector boundary reference exists and is referenced by affected skills when implemented.
- AC-B4: Prototype Lab references are split into focused branches, including decision capture and contract-boundary review.
- AC-B5: Visual handoff packet rules exist as shared communication artifact guidance, not readiness evidence.

### AC-C: Evals / Hard Negatives Added

- AC-C1: Hard-negative evals fail if same-session self-check is treated as independent readiness.
- AC-C2: Hard-negative evals fail if a reviewer fixes its own finding and declares clean review passed.
- AC-C3: Hard-negative evals fail if prototype mock fields become confirmed backend/API contract.
- AC-C4: Hard-negative evals fail if visual packet output is treated as browser/runtime/UAT/release evidence.
- AC-C5: Hard-negative evals fail if `tool_enforced` is claimed from prompt text alone.
- AC-C6: Hard-negative evals fail if child-thread and subagent runtimes are silently substituted.
- AC-C7: Hard-negative evals fail if Spark is used as final clean reviewer, final verifier, public skill approver, or release/UAT authority.

### AC-D: Evidence Boundary Preserved

- AC-D1: Implementation final reports distinguish self-check, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, and release evidence.
- AC-D2: Runtime/cache claims name installed plugin root and cache/source refresh or equivalence evidence, or explicitly state that runtime evidence was not refreshed.
- AC-D3: No plugin version bump, package release claim, marketplace claim, installed-plugin cache claim, UAT claim, or customer readiness claim is made by this PRD-only branch.

---

## 15. Proposed Issue Slices

Issue slices must preserve the MVP rule that conditional public skills start as shared references or workflow lenses. Creating `skills/<candidate>/SKILL.md` is a public skill surface change because `skills/` holds public skill contracts. Public candidate files may be created only in the explicit publicization slice after the reference-first slice and route negatives pass.

### V050-001: Public Skill Expansion Policy and Skill-quality Gate

Goal: Update repo guidance and add shared skill-quality policy.

Primary files:

```text
AGENTS.md
README.md
docs/maintainer-workflows.md
skills/_shared/SKILL-QUALITY.md
```

Dependencies: PRD acceptance.

### V050-001A: Role Separation Hard Gate

Goal: Add role identity, materiality threshold, self-check evidence taxonomy, and blocked readiness rules.

Primary files:

```text
skills/_shared/ROLE-SEPARATION.md
skills/implement/SKILL.md
skills/verify/SKILL.md
skills/dispatch/SKILL.md
skills/handoff/SKILL.md
skills/prototype/SKILL.md
evals/prompts/v0.5-role-separation.csv
```

Dependencies: V050-001.

### V050-001B: Lazy Runtime Capability and Selector Boundary

Goal: Add capability discovery, selector-enforcement statuses, model profiles, runtime mismatch fields, and subagent-vs-child-thread fallback rules.

Primary files:

```text
skills/_shared/RUNTIME-CAPABILITY.md
skills/_shared/COGNITIVE-BUDGET.md
skills/_shared/SUBAGENT-DELEGATION.md
skills/dispatch/SKILL.md
skills/implement/SKILL.md
skills/verify/SKILL.md
evals/prompts/v0.5-runtime-capability.csv
```

Dependencies: V050-001 and V050-001A.

### V050-002: Setup Guidance and Capability Seed Handling

Goal: Add setup guidance and capability seed handling without creating a public `setup-groundwork` skill.

Primary files:

```text
docs/maintainer-workflows.md
docs/capability-seeds/README.md
docs/capability-seeds/codex-model-menu-2026-06-23.md
skills/_shared/RUNTIME-CAPABILITY.md
```

Dependencies: V050-001B.

### V050-003A: Shared Grilling Loop and Route Negatives

Goal: Add shared grilling behavior and route negatives without creating a public `grill` skill.

Primary files:

```text
skills/_shared/GRILLING.md
skills/to-prd/SKILL.md
skills/prototype/SKILL.md
evals/prompts/v0.5-grill.csv
```

Dependencies: V050-001 and V050-001A.

### V050-003B: Public `grill` Skill

Goal: Create the public `grill` skill only after V050-003A demonstrates distinct routing and hard negatives pass.

Primary files:

```text
skills/grill/SKILL.md
evals/prompts/v0.5-grill.csv
```

Dependencies: V050-003A and maintainer acceptance of public exposure.

### V050-004A: Shared Decision Mapping Reference

Goal: Add decision mapping as a shared reference and route-conflict evals without creating a public `decision-map` skill.

Primary files:

```text
skills/_shared/DECISION-MAPPING.md
skills/_shared/COGNITIVE-BUDGET.md
skills/to-prd/SKILL.md
skills/write-plan/SKILL.md
skills/dispatch/SKILL.md
evals/prompts/v0.5-decision-map.csv
```

Dependencies: V050-001B.

### V050-004B: Public `decision-map` Skill

Goal: Create the public `decision-map` skill only after V050-004A proves it is not duplicating `write-plan`, `to-prd`, `dispatch`, or direct answers.

Primary files:

```text
skills/decision-map/SKILL.md
skills/decision-map/DECISION-MAP-TEMPLATE.md
evals/prompts/v0.5-decision-map.csv
```

Dependencies: V050-004A and maintainer acceptance of public exposure.

### V050-005A: Prototype Decision Capture and Contract Boundary

Goal: Split prototype output into confirmed decisions, unverified assumptions, mock fields, client-derived logic, open questions, and next route.

Primary files:

```text
skills/prototype/DECISION-CAPTURE.md
skills/prototype/CONTRACT-BOUNDARY.md
skills/prototype/SKILL.md
evals/prompts/prototype.csv
```

Dependencies: V050-001A.

### V050-005B: UI Variants and Logic Lab

Goal: Add UI-variant and logic/state-lab references without creating backend contract truth.

Primary files:

```text
skills/prototype/UI-VARIANTS.md
skills/prototype/LOGIC-LAB.md
skills/prototype/SKILL.md
```

Dependencies: V050-005A.

### V050-005C: Visual Handoff Packet and Verify Lens

Goal: Add visual handoff packet rules and verification lens while preserving readiness boundaries.

Primary files:

```text
skills/_shared/VISUAL-HANDOFF-PACKET.md
skills/handoff/SKILL.md
skills/verify/SKILL.md
skills/prototype/SKILL.md
```

Dependencies: V050-005A.

### V050-006A: Shared Skill-audit Workflow / Reference

Goal: Add skill-audit as a required workflow/reference without creating a public `skill-audit` skill.

Primary files:

```text
skills/_shared/SKILL-QUALITY.md
skills/_shared/SKILL-AUDIT.md
evals/prompts/v0.5-skill-audit.csv
```

Dependencies: V050-001 and V050-001A.

### V050-006B: Public `skill-audit` Skill

Goal: Create the public `skill-audit` skill only if direct invocation and routing negatives prove it merits public exposure.

Primary files:

```text
skills/skill-audit/SKILL.md
skills/skill-audit/SKILL-AUDIT-TEMPLATE.md
evals/prompts/v0.5-skill-audit.csv
```

Dependencies: V050-006A and maintainer acceptance of public exposure.

### V050-007: v0.5 Regression Suite

Goal: Add cross-suite positive, negative, and hard-negative fixtures for v0.5 routes and evidence boundaries. This slice aggregates and broadens coverage; it must not be the only place where V050-001A or V050-001B hard-negative evals land.

Primary files:

```text
evals/prompts/v0.5-skill-expansion.csv
evals/prompts/v0.5-runtime-capability.csv
evals/prompts/v0.5-role-separation.csv
evals/prompts/v0.5-prototype-lab.csv
```

Dependencies:

- V050-001, V050-001A, V050-001B, V050-002.
- V050-003A, V050-004A, V050-005A, V050-005B, V050-005C, V050-006A.
- Any publicization slices that are accepted into v0.5.

---

## 16. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Skill sprawl | More public skills increase routing conflicts. | Require distinct invocation, skill-quality gate, positive/negative evals, and hard-negative fixtures. |
| Over-grilling | Simple tasks become slow. | `grill` triggers only on explicit request or material ambiguity. |
| Decision-map bureaucracy | Users get ceremony instead of a direct answer. | Route only when options, dependencies, or tradeoffs are real. |
| Setup questionnaire sprawl | One-time setup becomes heavy and stale. | Keep `setup-groundwork` as guide/reference first; inspect existing docs before asking. |
| Self-sealing loop | Same role accepts its own material work. | Role separation gate and final-report evidence taxonomy. |
| Runtime overclaim | Prompt preference is reported as actual model/runtime execution. | Lazy capability discovery and selector-enforcement statuses. |
| Visual packet mistaken for readiness | Frontend handoff artifact becomes release evidence. | Evidence boundary in packet and verify lens. |
| Spark overuse | Fast model becomes final authority. | `spark_iteration` is bounded to fast coding loops and never final clean review/readiness authority. |

---

## 17. Open Questions

These are genuinely unresolved and should be answered during issue slicing or implementation:

1. Should `grill` ship as public in v0.5, or should it first land as shared behavior behind `to-prd` and `prototype`?
2. Does `decision-map` pass enough route-conflict negatives to justify a public skill in v0.5?
3. Should `skill-audit` be public in v0.5, or required only as a shared workflow/reference?
4. Which local Spark characterization evals are required before any Spark-specific implementation routing is more than provisional?

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

If this PRD direction is accepted, slice V050-001 through V050-007 into focused tasks. The first implementation slice should be V050-001 because every later skill addition depends on the shared skill-quality gate and updated public skill expansion policy. Do not create `skills/grill/SKILL.md`, `skills/decision-map/SKILL.md`, or `skills/skill-audit/SKILL.md` until their shared-reference slice has passed route negatives and the maintainer accepts public exposure.
