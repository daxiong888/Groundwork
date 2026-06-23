# PRD v0.5: Prototype-first Skill Expansion and Skill Quality System

Target Reader: Groundwork maintainers, future implementation agents, skill authors, and reviewers planning the v0.5 capability expansion.
Reader Action Needed: Review this PRD, decide whether to accept the v0.5 direction, and use the functional requirements and issue slices to implement the skill expansion in focused changes.
Decision Supported: Whether Groundwork should move from a fixed-small public skill surface to a quality-gated expansion model that adds new skills when they provide distinct routing, setup, grilling, decision mapping, prototype-first, or skill-audit value.
Artifact Type: product PRD.
Source of Truth: Maintainer directive in the current planning conversation; current Groundwork repository guidance and skill docs; current Matt Pocock skills repository, especially `grill-me`, `grilling`, `setup-matt-pocock-skills`, `writing-great-skills`, `prototype`, `domain-modeling`, `codebase-design`, `tdd`, and `diagnosing-bugs`; prior Groundwork iteration analysis uploaded as `Groundwork 迭代建议分析.txt`.
Scope: v0.5 product planning for public skill expansion, prototype-first workflows, model/reasoning decision policy, setup/configuration, decision mapping, visual handoff packets, and a writing-great-skills-style audit pass over existing Groundwork skills.
Out of Scope: Implementing the new skills in this PRD change; claiming runtime, marketplace, UAT, release, installed-plugin, cache-refresh, or customer readiness; creating PRs/issues automatically; changing plugin version metadata; mutating external trackers; running Codex App worktrees; adding MCP servers/hooks/task CRUD; copying Matt Pocock's repository wholesale.
Evidence Level: Planning evidence only. Repository source files and external skill references were inspected, but this PRD adds no runtime evidence, no installed-plugin evidence, no browser evidence, no release evidence, and no UAT evidence.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, raw traces, production data, or sensitive logs.
Status: Draft PRD for maintainer review.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-23.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Lifecycle Preflight

Intent: product capability expansion.
Suggested Workflow Mode: to-prd / roadmap PRD.
Locale: Chinese product discussion; English repository identifiers and durable artifact text.
Requirement State: draft for maintainer acceptance.
Artifact Promotion: required, because this PRD should become the source for v0.5 issue slicing and review.
Execution Topology: branch-local documentation artifact only.
Risk Gate: remote GitHub branch and docs-file write were explicitly requested by the maintainer.
Verification Strategy: documentation source review, post-write file fetch, branch diff comparison, and later implementation-specific evals.
Lifecycle State: not needed for this bounded planning artifact.
Stop Condition: v0.5 goals, non-goals, requirements, skill-surface decisions, issue slices, and evidence boundaries are clear enough for review and follow-up implementation.

---

## 2. Executive Summary

Groundwork v0.5 should promote the project from a PRD-first maintainer workflow to a decision-first workflow:

```text
raw intent
  -> setup / route / grill / decision-map / prototype-first as needed
  -> PRD / issue / implementation / verification / handoff
```

The previous small public skill surface remains a good default, but it must not become a product ceiling. Public skills should be added when they have a distinct invocation moment, a stable leading word, a checkable completion criterion, eval coverage, and a clear relationship to existing skills. The old constraint should become: **do not expand public skills without accepted product scope and quality gates**. This PRD is intended to provide that product scope.

v0.5 should add or evaluate these public skill candidates:

| Candidate | Public? | Why it earns a public surface |
| --- | --- | --- |
| `setup-groundwork` | Yes | One-time repo configuration for issue tracker, triage labels, domain docs, artifact roots, prototype defaults, and skill audit policy. This is a distinct setup event, not a normal workflow step. |
| `grill` | Yes | A standalone relentless interview for plans, designs, PRDs, prototypes, and architecture decisions. It should also remain callable by `to-prd`, `decision-map`, and `prototype`. |
| `decision-map` | Yes | A decision-structure skill for options, dependencies, tradeoffs, route choices, and explicit decision logs before PRD/prototype/implementation. |
| `skill-audit` | Yes | A writing-great-skills-style review and patch-proposal workflow for Groundwork's own skills. It is different from implementation conformance review because the subject is skill predictability and invocation quality. |
| `visual-handoff` | Not initially; branch under `prototype` / `handoff` | Worth adding later only if repeated use proves it needs direct invocation. v0.5.0 can ship it as a shared artifact pattern first. |
| `ask-groundwork` | Optional later router | Consider only if user-invoked skills multiply enough that cognitive load becomes a real problem. `decision-map` can cover the first routing need. |

v0.5 should also strengthen existing skills:

- `prototype` becomes Prototype Lab: UI variants, logic/state lab, visual packet, and decision capture.
- `to-prd` becomes prototype-aware and no longer owns every grilling case itself.
- `dispatch` and `implement` consume a shared cognitive budget policy, not only dispatch-local routing profiles.
- `handoff` and `verify` distinguish visual communication artifacts from runtime, browser, UAT, and release evidence.
- All existing skills receive a `writing-great-skills` audit pass before broad implementation.

---

## 3. Problem Statement

Groundwork has reached v0.4.2 as a hardened evidence-first workflow base, but the next bottleneck is not only evidence capture. The bottleneck is choosing the right first move.

The current practical failure modes are:

1. **PRD-first is too expensive for some ambiguous product work.** Complex UI, state, and workflow questions often become clearer through a prototype before a PRD is written.
2. **Prototype output is useful but not expressive enough yet.** Static screenshots, annotations, or generated images help only for simple visual feedback. More complex flows need runnable variants, state labs, and structured visual handoff packets.
3. **Pure text handoff is weak for frontend collaboration.** Complex frontend/backend handoffs need diagrams, state maps, API tables, variant decisions, and mock-vs-confirmed field boundaries in one artifact.
4. **Model and reasoning effort decisions are currently too dispatch-centric.** The same cost/latency/quality decision should inform PRD shaping, grilling, prototyping, implementation, review, and verification.
5. **Setup assumptions are implicit.** Groundwork needs a first-class way to declare where issues live, what labels mean, where domain docs live, where artifacts go, and which project conventions the skills must consume.
6. **The public skill surface rule can become an accidental blocker.** Keeping a small surface was useful earlier, but v0.5 needs explicit permission to add new public skills when they are productively distinct.
7. **Existing skill quality has not been systematically audited.** Groundwork skills have grown through hardening. v0.5 should review them for invocation clarity, duplication, no-op prose, progressive disclosure, leading words, completion criteria, and eval coverage.
8. **Decision mapping is missing as a named workflow.** Groundwork has routing, PRD shaping, and dispatch packages, but not a compact decision map that records options, dependencies, uncertainty, evidence, and the route chosen.

---

## 4. Goals

1. Establish a v0.5 product direction that permits new public skills when justified by accepted scope and quality gates.
2. Add a setup capability so Groundwork can learn per-repo issue, label, domain-doc, artifact, and prototype conventions before other skills rely on them.
3. Split standalone grilling from PRD writing without losing the existing grill-before-write behavior in `to-prd`.
4. Add decision mapping as a first-class workflow for option sets, tradeoffs, route decisions, and decision logs.
5. Upgrade prototype from throwaway static artifact to Prototype Lab: UI variants, logic/state lab, visual packet, and decision capture.
6. Add a skill-audit workflow based on writing-great-skills principles and apply it to every existing public skill and major shared guardrail.
7. Make cognitive budget policy shared across planning, prototype, implementation, verification, and dispatch.
8. Preserve Groundwork's evidence boundaries: visual packets, PRDs, docs, score schemas, and summaries are not runtime, browser, UAT, release, or customer-readiness evidence by themselves.
9. Add regression coverage so new skills improve route correctness without causing skill sprawl or over-triggering.

---

## 5. Non-goals

v0.5 must not:

- copy Matt Pocock's skills wholesale without Groundwork-specific boundaries;
- treat a previous README statement about a small public surface as a permanent product limit;
- add public skills without accepted scope, skill-quality review, and eval coverage;
- replace `to-prd`, `prototype`, `implement`, `verify`, `handoff`, or `dispatch` wholesale in one change;
- make every task go through setup, grill, decision-map, PRD, and prototype ceremony;
- claim that a visual packet, screenshot, generated image, PRD, or prototype is a confirmed backend/API contract without source evidence or explicit user confirmation;
- turn `dispatch` into an executor;
- spawn subagents, create worktrees, mutate remotes, open PRs/issues, publish packages, or schedule automations by default;
- modify plugin metadata or release versioning as part of this PRD-only branch;
- auto-apply skill-audit patch suggestions without maintainer approval.

---

## 6. Source Interpretation and Adoption Decisions

### 6.1 Groundwork current source interpretation

Groundwork's repository guidance currently treats the public skill surface as intentionally small and says not to add public skills unless an explicit issue requires it. For v0.5, the maintainer has explicitly clarified that this should not block ability expansion. This PRD interprets that clarification as product scope to add skills when they pass the v0.5 quality gate.

The implementation follow-up should update repository guidance from:

```text
Do not add public skills.
```

to:

```text
Do not add public skills unless an accepted PRD, issue, or maintainer directive explicitly expands the public surface and the new skill passes the skill-quality, routing, and eval gates.
```

### 6.2 Matt Pocock skill references

| Matt source | v0.5 decision | Groundwork adaptation |
| --- | --- | --- |
| `grill-me` | Adopt concept | Add public `grill` as the standalone user-facing entry point. |
| `grilling` | Adopt behavior | Shared grilling loop: one question at a time, recommended answer, code/docs inspection before asking when possible. |
| `setup-matt-pocock-skills` | Adapt, not copy | Add `setup-groundwork` for issue tracker, triage labels, domain docs, artifact roots, prototype defaults, eval/runtime evidence policy, and skill-audit conventions. |
| `writing-great-skills` | Strongly adopt | Add `skill-audit` and a shared `SKILL-QUALITY.md` reference. Run it over all existing skills before or during v0.5 implementation. |
| `decision-mapping` | Source unconfirmed in current official repo listing | Treat as a user-named capability candidate. Groundwork should create `decision-map` as its own skill if accepted, based on option mapping, dependency resolution, tradeoff recording, and route decision evidence. |
| `prototype` UI/logic branches | Adopt and combine | Keep Groundwork contract-boundary rules, but add UI variants, logic/state lab, and decision capture. |
| `domain-modeling` | Adopt as shared reference | Use for setup, PRD, prototype, skill-audit, and implementation language consistency. |
| `codebase-design` | Adopt as shared reference | Use for implementation seams, architecture review, prototype-to-implementation decisions, and skill-audit of engineering guidance. |
| `tdd` / `diagnosing-bugs` | Strengthen existing implementation guidance | Feed shared cognitive budget and feedback-loop gates. |

---

## 7. Users and User Stories

### Maintainer

As a maintainer, I want public skill expansion to be possible but gated, so Groundwork can grow capabilities without becoming an unbounded skill bundle.

### Product planner

As a product planner, I want to decide whether to grill, prototype, decision-map, write PRD, or implement directly, so I can avoid premature PRDs and premature code.

### Prototype-driven builder

As a prototype-driven builder, I want UI variants and logic/state labs before PRD when the product shape is unclear, so decisions become visible before engineering work starts.

### Frontend collaborator

As a frontend collaborator, I want a visual handoff packet that shows states, flows, API fields, and mock-vs-confirmed boundaries, so I do not have to reverse-engineer complex behavior from plain text.

### Skill author

As a skill author, I want a writing-great-skills-style audit process, so every Groundwork skill has clear invocation, strong completion criteria, progressive disclosure, minimal duplication, and eval coverage.

### Implementation agent

As an implementation agent, I want setup, decision-map, cognitive budget, PRD, issue, and prototype artifacts to be explicit sources, so I can choose the lightest reliable execution path.

### Reviewer

As a reviewer, I want visual packets, prototypes, PRDs, and skill-audit reports to be labeled with evidence boundaries, so I do not mistake planning artifacts for runtime or release evidence.

---

## 8. Proposed Public Skill Surface

### 8.1 Existing public skills retained

The existing public skills remain valid and should be retained unless a later skill-audit issue proves a replacement is safer:

```text
to-prd
to-issues
triage
write-plan
prototype
implement
verify
handoff
dispatch
```

### 8.2 New public skill: `setup-groundwork`

Purpose:

Configure a repository for Groundwork before other skills rely on project conventions.

Should trigger:

- "setup Groundwork for this repo"
- "configure issue tracker / triage labels / artifact root"
- "where should Groundwork put PRDs and visual handoffs?"
- "set up domain docs and ADR location"
- first install or migration to a new repo

Required outputs:

```text
Setup Findings
Issue Tracker Policy
Triage Label Policy
Domain Docs Policy
Artifact Root Policy
Prototype Artifact Policy
Runtime / Evidence Claim Policy
Skill Audit Policy
Files To Update
Open Questions
Next Action
```

Default durable files, subject to maintainer approval:

```text
docs/agents/issue-tracker.md
docs/agents/triage-labels.md
docs/agents/domain.md
docs/agents/artifacts.md
docs/agents/prototype.md
docs/agents/runtime-evidence.md
```

Constraints:

- Inspect existing repo docs before writing.
- Present findings and decisions before writing config files.
- Do not create duplicate AGENTS/CLAUDE sections.
- Do not assume GitHub Issues if the repo has another source of task truth.

### 8.3 New public skill: `grill`

Purpose:

Relentlessly clarify a plan, design, PRD direction, prototype question, architecture direction, or product decision before downstream work.

Should trigger:

- "grill me"
- "challenge this plan"
- "stress-test this PRD"
- "ask the hard questions before we build"
- raw decisions where ambiguity is high and writing a full PRD would be premature

Required behavior:

- Ask one question at a time in interactive sessions.
- Provide a recommended answer for each question when evidence supports one.
- Walk the decision tree branch by branch.
- Inspect source/docs first when a question is answerable from the repo.
- Produce a compact decision capture when the grill loop stops.
- Route to `decision-map`, `prototype`, `to-prd`, or `write-plan` only after the unresolved decision shape is clear.

Required outputs:

```text
Grill Target
Decision Tree
Known Facts
Open Branch
Question
Recommended Answer
Impact If Different
Answered From Source
Decision Capture
Next Route
```

### 8.4 New public skill: `decision-map`

Purpose:

Map product, design, architecture, workflow, model/reasoning, or skill-surface decisions before choosing PRD/prototype/implementation route.

Should trigger:

- "decision mapping"
- "map the options"
- "which path should we take?"
- "prototype first or PRD first?"
- "do we add a skill or fold this into an existing skill?"
- "which model/thinking profile should this task use?"

Required behavior:

- Separate decision, options, criteria, dependencies, evidence, risks, reversibility, and next route.
- Show why options were rejected, not just the chosen answer.
- Use a cognitive budget block when the decision affects model/reasoning effort.
- Use prototype-first when visual/state uncertainty dominates.
- Use grill-first when the option set is incomplete.
- Use to-prd when acceptance and target reader can be stated.
- Use implement only when source truth is accepted or explicit bypass is present.

Required outputs:

```text
Decision Being Mapped
Options
Decision Criteria
Evidence Inspected
Dependencies
Tradeoffs
Reversibility
Risk Surface
Cognitive Budget
Recommended Decision
Rejected Options
Next Route
Decision Log Artifact Recommendation
```

### 8.5 New public skill: `skill-audit`

Purpose:

Review and improve Groundwork skills using writing-great-skills-style principles before adding or materially modifying public skills.

Should trigger:

- "run writing-great-skills over our skills"
- "audit this skill"
- "is this skill too broad / duplicated / unclear?"
- "prepare skill quality patch proposals"
- public skill addition, rename, split, merge, or major trigger edit

Required behavior:

- Inventory target skills and shared references.
- Classify invocation: model-invoked, user-invoked, shared reference, branch, or router.
- Check description trigger quality and context load.
- Identify no-op prose, duplication, sediment, sprawl, weak leading words, premature completion risk, and missing completion criteria.
- Check progressive disclosure and context pointers.
- Map every proposed change to an eval or fixture.
- Output patch proposals, not automatic broad rewrites.

Required outputs:

```text
Skill Audit Scope
Skill Inventory
Invocation Classification
Description Findings
Information Hierarchy Findings
Completion Criteria Findings
Duplication / No-op / Sprawl Findings
Progressive Disclosure Findings
Eval Coverage Findings
Patch Proposals
Risk / Rollback
Next Action
```

### 8.6 Public skill expansion quality gate

A new public skill may be added only when all of these are true:

1. It has a distinct invocation moment that users or model routing can recognize.
2. It has a leading word or name that is not merely a synonym for an existing skill.
3. It cannot be safely implemented as a branch or shared reference of an existing skill without overloading that skill.
4. It has a clear trigger contract and clear should-not-trigger cases.
5. It has checkable completion criteria.
6. It has a failure branch for likely misuse.
7. It declares evidence boundaries.
8. It has at least three positive and three negative eval fixtures before release.
9. It does not claim runtime, UAT, release, or remote-write evidence from docs alone.
10. It passes `skill-audit` before merge.

---

## 9. Existing Skill Changes

### 9.1 `to-prd`

Changes:

- Keep grill-before-write, but move reusable relentless-interview behavior into shared `grill` rules.
- Support prototype-first PRD derivation: PRD can be written from prototype decision capture when the source boundary is clear.
- Support decision-map-derived PRDs: accepted decisions and rejected options become source context.
- Continue to require audience-first headers and stable acceptance criteria IDs.
- Do not treat every raw idea as PRD-ready.

### 9.2 `prototype`

Changes:

- Add UI variants branch with multiple structurally different variants when visual design is the question.
- Add logic/state lab branch for state machines, reducers, business rules, and terminal/runnable decision aids.
- Add visual packet branch for complex frontend handoff and review.
- Add decision capture output that can feed PRD, contract, issue, or implementation.
- Keep contract boundary hard: mock fields and client-derived logic must not become confirmed backend contract.

### 9.3 `dispatch`

Changes:

- Keep package-only runtime routing.
- Consume shared cognitive budget policy for model profile, reasoning effort, cost/latency bias, and selector enforcement boundary.
- Route accepted task sets; do not become the general raw-intent router.
- Point raw decision questions to `decision-map`, not `dispatch`.

### 9.4 `implement`

Changes:

- Consume cognitive budget before high-risk implementation.
- Use decision-map outputs when implementation follows a tradeoff decision.
- Keep TDD-lite / diagnosis / QA-fix-QA gates.
- Use skill-audit when implementation modifies skills.

### 9.5 `verify`

Changes:

- Add verification lens for visual packet review.
- Add skill-audit report review lens when a skill-quality patch is being verified.
- Continue to require `Verification Scope` opening for readiness/evidence reports.
- Do not treat skill-audit, PRD, visual packet, or prototype artifacts as runtime evidence.

### 9.6 `handoff`

Changes:

- Add visual handoff packet as a handoff artifact type when text-only handoff is insufficient.
- Preserve current review-package boundaries.
- Reference existing PRD/prototype/contract artifacts instead of copying them.

### 9.7 `triage`, `to-issues`, and `write-plan`

Changes:

- `triage` consumes setup-groundwork label policy.
- `to-issues` consumes decision-map and prototype decision capture to slice vertical issues.
- `write-plan` remains for complex plans, but implementation keeps lightweight planning inline.

---

## 10. Prototype-first Workflow

### 10.1 Route decision

```text
raw intent
  -> decision-map when options/tradeoffs are unclear
  -> grill when the decision tree is under-specified
  -> prototype when visual/state/business-rule uncertainty dominates
  -> to-prd when target reader, acceptance, and source truth are clear enough
  -> implement only when accepted source truth or explicit bypass exists
```

### 10.2 Prototype Lab output

```text
Prototype Question
Decision Needed
Prototype Branch: ui-variants | logic-lab | visual-packet | contract-boundary-review
Host Surface
State Cases / Variants
Confirmed Contract Inputs
Mock / Illustrative Fields
Client-derived Logic
Runtime / Browser Evidence
Decision Capture
PRD Updates Suggested
Frontend Contract Updates Suggested
Cleanup Decision
Next Route
```

### 10.3 Prototype to PRD

A prototype may feed a PRD only through decision capture:

```text
prototype observations
  -> confirmed decisions
  -> unverified assumptions
  -> mock fields
  -> client-derived logic
  -> open confirmation questions
  -> PRD acceptance criteria
```

The PRD must not upgrade prototype-only mock fields into backend/API contract truth.

---

## 11. Visual Handoff Packet

A visual handoff packet is a structured communication artifact, not a readiness artifact.

Trigger when any of these are true:

- frontend handoff requires more than simple endpoint/field text;
- more than three UI states or branches must be explained;
- screenshots or generated images cannot capture the interaction logic;
- prototype variants need review or selection;
- backend contract and frontend behavior must be seen together;
- UAT paths, empty states, error states, and loading states need one shared reference.

Recommended artifact:

```text
artifacts/<feature-slug>/handoff/frontend-visual-packet.html
artifacts/<feature-slug>/handoff/frontend-contract.md
artifacts/<feature-slug>/handoff/evidence.md
```

Required sections:

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
- UAT/customer readiness: separate verify claim only.

---

## 12. Cognitive Budget Policy

v0.5 should add shared cognitive budget guidance under `skills/_shared/COGNITIVE-BUDGET.md` or equivalent.

Required fields:

```yaml
cognitive_budget:
  task_shape: tiny | normal | ambiguous | prototype_first | cross_cutting | high_risk | diagnosis | skill_change
  uncertainty: low | medium | high
  evidence_gap: none | source | runtime | browser | contract | domain | user_decision | skill_quality
  risk_surface:
    - customer_visible
    - public_api
    - schema
    - migration
    - security
    - data_correctness
    - frontend_contract
    - public_skill_surface
  recommended_profile:
    model_profile: fast | balanced | strongest | reviewer
    reasoning_effort: low | medium | high
    interaction_mode: direct | grill | decision_map | prototype | diagnose | review | dispatch
    stop_condition: ""
  selector_enforcement_boundary: tool_enforced | prompt_preference | unavailable | unknown
```

Rules:

- Do not expose private chain-of-thought; expose work mode and evidence needs.
- Do not claim selector enforcement unless a runtime or adapter proves it.
- Use high reasoning for public skill changes, schema/API/security/data correctness, weak validation, and cross-cutting workflow changes.
- Use low reasoning and direct mode for tiny bounded edits.
- Use prototype-first when visual/state uncertainty is higher than text-spec uncertainty.

---

## 13. Skill-audit Workflow

### 13.1 Audit scope

The first v0.5 skill-audit pass should cover:

```text
skills/to-prd/SKILL.md
skills/to-issues/SKILL.md
skills/triage/SKILL.md
skills/write-plan/SKILL.md
skills/prototype/SKILL.md
skills/implement/SKILL.md
skills/verify/SKILL.md
skills/handoff/SKILL.md
skills/dispatch/SKILL.md
skills/_shared/*.md that define cross-skill gates
```

### 13.2 Audit checks

For each skill:

1. Invocation class: public model-invoked, user-invoked, shared reference, branch, or router.
2. Description: leading word first, one trigger per branch, no duplicate synonyms, no body identity repeated.
3. Workflow: ordered steps with checkable completion criteria.
4. Information hierarchy: keep universal steps in `SKILL.md`; push branch-specific reference to linked files.
5. Context pointers: pointer wording must say when to load the reference, not just name the file.
6. Duplication: same rule should have one source of truth.
7. No-op prose: remove lines that do not change behavior.
8. Sediment: remove stale version-specific rules after migration.
9. Sprawl: split by branch or sequence when one skill hides too many different jobs.
10. Failure modes: include likely misuse branches.
11. Evidence boundary: state what the skill may and may not claim.
12. Eval coverage: positive, negative, hard-negative, and routing-conflict fixtures.

### 13.3 Initial audit hypotheses

These are hypotheses for the audit issue, not final verdicts:

| Skill | Likely audit focus |
| --- | --- |
| `to-prd` | May be carrying too much reusable grilling behavior; extract shared grill logic without weakening PRD gate. |
| `prototype` | Needs branch disclosure for UI variants, logic lab, visual packet, and contract-boundary review. |
| `dispatch` | Model/reasoning policy should become shared; dispatch should stay accepted-task package router. |
| `verify` | Strong opening contract is valuable; audit should avoid loosening it while pruning duplication. |
| `handoff` | Add visual packet branch without turning handoff into a general design artifact factory. |
| `implement` | Ensure skill-change tasks trigger skill-audit and high cognitive budget. |
| `to-issues` | Consume prototype/decision-map outputs without inventing accepted scope. |
| `triage` | Consume setup label policy and keep task readiness separate from release readiness. |
| `write-plan` | Keep for complex plans; avoid duplicating implement lightweight plan. |

---

## 14. Functional Requirements

### Public skill expansion

- FR-501: Groundwork must allow new public skills when an accepted PRD, issue, or maintainer directive explicitly expands the public skill surface.
- FR-502: Every new public skill must pass the v0.5 public skill expansion quality gate before merge.
- FR-503: README, AGENTS, and maintainer docs must describe the new policy as quality-gated expansion, not fixed-count restriction.
- FR-504: Public skill additions must include trigger fixtures, hard-negative fixtures, and at least one eval or smoke check.

### Setup

- FR-510: Add `setup-groundwork` as a public skill candidate.
- FR-511: Setup must inspect existing repository guidance before proposing edits.
- FR-512: Setup must capture issue tracker policy, triage label policy, domain docs policy, artifact root policy, prototype artifact policy, runtime evidence policy, and skill-audit policy.
- FR-513: Setup must not duplicate AGENTS/CLAUDE sections.

### Grilling

- FR-520: Add `grill` as a public skill candidate and shared grilling behavior.
- FR-521: Grill must ask one question at a time in interactive mode.
- FR-522: Grill must provide recommended answers and impact notes when evidence supports them.
- FR-523: Grill must inspect source/docs instead of asking when the answer can be found locally.
- FR-524: Grill must produce decision capture and route recommendation when stopped.

### Decision mapping

- FR-530: Add `decision-map` as a public skill candidate.
- FR-531: Decision-map must list options, criteria, dependencies, evidence, tradeoffs, reversibility, risks, and rejected options.
- FR-532: Decision-map must recommend the next route: grill, prototype, to-prd, to-issues, write-plan, implement, verify, handoff, dispatch, or blocked.
- FR-533: Decision-map must include cognitive budget when the decision affects model/reasoning profile.
- FR-534: Decision-map must avoid turning recommendations into accepted product truth.

### Prototype Lab

- FR-540: Upgrade `prototype` with UI variants, logic lab, visual packet, and decision capture branches.
- FR-541: UI variants must support structurally different alternatives and record the selected or rejected variants.
- FR-542: Logic lab must separate pure decision logic from throwaway shell code.
- FR-543: Prototype decision capture must separate confirmed facts, mock fields, client-derived logic, and unverified assumptions.
- FR-544: Prototype must keep cleanup decision: delete, absorb, or temporarily retain with review timing.

### Visual handoff

- FR-550: Add a shared visual handoff packet template.
- FR-551: Visual packets must include state/flow, UI surface map, API contract table, AC mapping, field status badges, open questions, and evidence boundary.
- FR-552: Visual packets must not replace frontend contract docs when API/contract claims exist.
- FR-553: Visual packets must not claim browser/runtime/UAT/release evidence unless that evidence is separately inspected and recorded.

### Skill audit

- FR-560: Add `skill-audit` as a public skill candidate.
- FR-561: Skill-audit must apply invocation, description, information hierarchy, completion criteria, no-op, duplication, progressive disclosure, leading word, failure mode, and eval coverage checks.
- FR-562: Skill-audit must produce patch proposals and risk/rollback notes before modifying skills.
- FR-563: Skill-audit must be required before adding, renaming, splitting, merging, or materially changing public skills.

### Cognitive budget

- FR-570: Add shared cognitive budget policy.
- FR-571: Cognitive budget must include task shape, uncertainty, evidence gap, risk surface, recommended model profile, reasoning effort, interaction mode, stop condition, and selector enforcement boundary.
- FR-572: Cognitive budget must not expose private reasoning; it exposes work mode and evidence needs only.
- FR-573: Selector enforcement must not be claimed without runtime/adapter evidence.

### Evals and regression coverage

- FR-580: Add eval fixtures for setup, grill, decision-map, prototype-first, visual-handoff, cognitive-budget, public-skill-expansion, and skill-audit.
- FR-581: Add hard-negative cases for over-triggering, skill duplication, unsupported contract promotion, visual-packet-as-readiness, and selector enforcement overclaim.
- FR-582: Existing v0.4.x source-validation evidence boundaries must remain intact.

---

## 15. Acceptance Criteria

- AC-1: The accepted v0.5 implementation updates repo guidance so public skill expansion is allowed when explicitly scoped and quality-gated.
- AC-2: `setup-groundwork` has a `SKILL.md`, setup templates, trigger fixtures, and should-not-trigger fixtures.
- AC-3: `grill` has a `SKILL.md`, shared grilling reference, one-question interactive rule, code/docs-before-ask rule, and decision-capture output.
- AC-4: `decision-map` has a `SKILL.md`, decision-map template, cognitive budget block, rejected-options section, and route recommendation rules.
- AC-5: `skill-audit` has a `SKILL.md`, skill-quality checklist, patch proposal template, and eval coverage requirements.
- AC-6: `prototype` supports UI variants, logic lab, visual packet, and decision capture without weakening contract-boundary rules.
- AC-7: `handoff` and `prototype` share visual packet rules and both state that the packet is communication/review evidence, not runtime/UAT/release evidence.
- AC-8: `dispatch`, `implement`, `prototype`, `to-prd`, and `verify` can reference shared cognitive budget policy.
- AC-9: `to-prd` can consume prototype decision capture and decision-map outputs without inventing product truth.
- AC-10: `verify` can review visual packet and skill-audit outputs without claiming readiness from docs alone.
- AC-11: `to-issues` can slice accepted prototype/decision-map-derived PRDs into vertical issues with contract impact.
- AC-12: Eval fixtures include positive and negative cases for all new public skill candidates.
- AC-13: Hard-negative evals fail if a prototype mock field is promoted to confirmed backend contract.
- AC-14: Hard-negative evals fail if a visual packet is treated as browser/runtime/UAT/release evidence.
- AC-15: Hard-negative evals fail if selector enforcement is claimed without runtime or adapter evidence.
- AC-16: Skill-audit output identifies at least one improvement opportunity or explicitly records no material finding for every existing public skill.
- AC-17: Public docs explain when to add a public skill versus shared reference versus branch.
- AC-18: All durable new artifacts include audience-first header fields.
- AC-19: Implementation final report separates source-validation evidence from runtime/release/UAT evidence.
- AC-20: No plugin version bump, package release claim, marketplace claim, or installed-plugin cache claim is made by the v0.5 PRD-only or source-validation changes.

---

## 16. Proposed Issue Slices

### V050-001: Public skill expansion policy and shared quality gate

Goal: Update repo guidance and shared policy so public skills can be added under accepted scope and skill-quality gates.

Primary files:

```text
AGENTS.md
README.md
docs/maintainer-workflows.md
skills/_shared/SKILL-QUALITY.md
```

Verification:

```bash
git diff --check
```

Dependencies: PRD acceptance.

### V050-002: `setup-groundwork`

Goal: Add setup skill and templates for repo-level Groundwork conventions.

Primary files:

```text
skills/setup-groundwork/SKILL.md
skills/setup-groundwork/*.md
evals/prompts/*setup*.csv or equivalent fixtures
```

Dependencies: V050-001.

### V050-003: `grill` and shared grilling loop

Goal: Add standalone grill skill and shared grilling reference used by PRD, prototype, decision-map, and architecture planning.

Primary files:

```text
skills/grill/SKILL.md
skills/_shared/GRILLING.md
skills/to-prd/SKILL.md
skills/prototype/SKILL.md
```

Dependencies: V050-001.

### V050-004: `decision-map`

Goal: Add decision mapping as a route-choice and tradeoff artifact skill.

Primary files:

```text
skills/decision-map/SKILL.md
skills/decision-map/DECISION-MAP-TEMPLATE.md
skills/_shared/COGNITIVE-BUDGET.md
```

Dependencies: V050-001, can run parallel with V050-003 if shared cognitive budget contract is agreed.

### V050-005: Prototype Lab and visual packet

Goal: Upgrade prototype and handoff artifacts to support UI variants, logic lab, visual packet, and prototype-to-PRD decision capture.

Primary files:

```text
skills/prototype/UI-VARIANTS.md
skills/prototype/LOGIC-LAB.md
skills/prototype/DECISION-CAPTURE.md
skills/_shared/VISUAL-HANDOFF-PACKET.md
skills/handoff/SKILL.md
skills/verify/SKILL.md
```

Dependencies: V050-003 and V050-004 preferred, but contract-boundary work can proceed independently.

### V050-006: `skill-audit` and first audit pass

Goal: Add skill-audit and use it to produce patch proposals for existing skills.

Primary files:

```text
skills/skill-audit/SKILL.md
skills/skill-audit/SKILL-AUDIT-TEMPLATE.md
artifacts/v0.5-skill-audit/initial-audit.md
```

Dependencies: V050-001.

### V050-007: v0.5 regression suite

Goal: Add regression coverage for setup, grill, decision-map, prototype-first, visual handoff, cognitive budget, and skill-audit routing.

Primary files:

```text
evals/prompts/v0.5-skill-expansion.csv
evals/scenarios/v050-*.md
evals/checks/* as needed
```

Dependencies: V050-002 through V050-006.

---

## 17. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Skill sprawl | More public skills can confuse users and increase routing conflicts. | Require distinct invocation, skill-audit, eval fixtures, and should-not-trigger cases. Add `ask-groundwork` only if user-invoked cognitive load becomes real. |
| Over-grilling | Too many questions slow simple work. | `grill` should trigger on ambiguity or explicit request; direct small tasks remain direct. |
| Decision-map becomes bureaucracy | Users may get an artifact when they needed a direct answer. | Use decision-map only when there are real options, dependencies, or tradeoffs. |
| Setup writes unwanted config | Repo setup can create clutter. | Inspect first, present draft, and ask before writing setup docs. |
| Visual packet mistaken for readiness | Reviewers may think a polished HTML packet proves behavior. | Every packet must include evidence boundary and verify must reject readiness without runtime/browser/UAT evidence. |
| Skill-audit over-edits skills | Broad rewrites can introduce regressions. | Patch proposals first; small implementation slices; eval before merge. |
| Cognitive budget leaks reasoning | Work mode might be confused with chain-of-thought. | Only expose task shape, uncertainty, evidence gaps, risk, recommended profile, and stop condition. |
| Matt source drift | External skill repo can change. | Record source paths and dates in implementation artifacts; avoid wholesale copy; adapt to Groundwork contracts. |

---

## 18. Success Metrics

- Route evals correctly choose `grill`, `decision-map`, `prototype`, `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` for v0.5 fixtures.
- Hard-negative evals catch visual-packet-as-readiness and prototype-mock-as-contract failures.
- Skill-audit produces actionable findings for all existing public skills or explicitly records no material finding.
- At least one complex UI/frontend handoff scenario produces a visual packet recommendation instead of a plain text-only handoff.
- At least one prototype-first scenario flows to PRD without promoting mock fields to backend truth.
- Model/reasoning profile outputs include selector enforcement boundary and do not overclaim `tool_enforced`.
- Public docs no longer describe public skill count as fixed; they describe quality-gated expansion.

---

## 19. Release and Evidence Boundary

This PRD and its source-validation implementation slices can support product/design review only. They cannot support:

- installed plugin runtime readiness;
- marketplace readiness;
- release readiness;
- UAT readiness;
- customer readiness;
- browser behavior claims;
- Codex App worktree or handoff execution claims;
- selector enforcement claims.

Any future release claim must include installed plugin root, source root, cache/source refresh or equivalence evidence, run scope, commands/trials, limitations, and explicit evidence status.

---

## 20. Open Questions

1. Should the public skill name be `grill`, `grill-me`, or `grilling`? Recommended default: `grill`, because Groundwork public skill names are action-oriented and concise.
2. Should the public skill name be `decision-map` or `decision-mapping`? Recommended default: `decision-map`, because it names the artifact and action compactly.
3. Should `skill-audit` be user-invoked only, model-invoked for skill edits, or both? Recommended default: model-invoked for public skill edits and user-invoked by name.
4. Should `setup-groundwork` write `docs/agents/*` files by default? Recommended default: present draft first, then write after maintainer confirmation.
5. Should `visual-handoff` become a public skill in v0.5.0? Recommended default: no; start as a shared packet used by `prototype` and `handoff`.
6. Should `ask-groundwork` be added as a router? Recommended default: defer until after v0.5 fixtures show user-invoked cognitive load.
7. Should v0.5 update plugin metadata immediately? Recommended default: no, not until source-validation and runtime/plugin evidence are separately available.

---

## 21. Next Action

Review this PRD for acceptance. If accepted, create an issue map for V050-001 through V050-007 and implement in small branches. The first implementation branch should update repository guidance and add `skills/_shared/SKILL-QUALITY.md`, because every later public skill addition depends on the quality gate.
