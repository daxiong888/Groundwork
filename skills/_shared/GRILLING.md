# Shared Grilling Reference

Target Reader: Groundwork skill authors, routers, implementers, clean reviewers, and verifiers deciding whether ambiguity needs clarification before PRD, prototype, decision mapping, or implementation.
Reader Action Needed: Use this reference to run the shared grilling loop only when material ambiguity blocks a safe next route.
Decision Supported: Whether to ask a single clarification question, answer directly, route to `to-prd`, route to decision mapping, route to `prototype`, or stop before implementation readiness claims.
Artifact Type: shared workflow reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-540, AC-A3, AC-D1, V050-003A in `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md`, `docs/prd-v0.5.1-socratic-grilling-expansion.md`, and maintainer direction to use Codex Plan Mode before PRD / grill-me handling.
Scope: Shared grilling behavior, Socratic question taxonomy, Codex Plan Mode entry for raw requirement / PRD / explicit grilling requests, question-quality gate, compact interactive output, route-after-answer behavior, route boundaries, route negatives, and evidence boundaries.
Out of Scope: Creating a public `grill` skill, accepting PRDs, approving implementation readiness, replacing decision mapping, replacing prototype exploration, executing Codex Plan Mode when the host does not expose it, or claiming runtime/browser/UAT/release evidence.
Evidence Level: Source-validation policy. This file is local shared guidance only until separately reviewed and verified.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, or personal data.

## Public Surface Boundary

`grill` is a public candidate only after shared route negatives prove a distinct invocation moment and hard negatives against over-questioning pass.

Do not create `skills/grill/SKILL.md` or treat this shared reference as a public skill. Public exposure belongs only to a later accepted publicization scope after route-negative evidence, hard negatives, independent skill-quality review, and maintainer acceptance.

Do not create `skills/socratic/SKILL.md`, `skills/domain-language/SKILL.md`, or `skills/grill-with-docs/SKILL.md` for v0.5.1 MVP behavior. Socratic questioning is a shared selection aid, not a public workflow surface.

## Core Definition

Grilling is the shared clarification route for material ambiguity where the unknowns are not yet enumerable.

Use grilling when the next safe action depends on discovering the right question before drafting, comparing, prototyping, or implementing. Grilling produces clarification only. It does not produce PRD acceptance, task readiness, implementation readiness, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, or customer readiness.

The v0.5.1 rule is:

```text
Ask less, ask sharper, and only ask questions that can change a route,
artifact boundary, acceptance criterion, contract boundary, or evidence requirement.
```

## Trigger Conditions

Use the shared grilling loop when at least one condition is true:

- The user explicitly asks to be grilled, challenged, questioned, or clarified before proceeding.
- Raw product, workflow, skill-selection, runtime, marketplace, plugin, prototype, or implementation intent has material ambiguity and the missing unknowns are not yet enumerable.
- A requested PRD, prototype, or decision artifact would invent product truth without first discovering the highest-impact unknown.
- The user wants planning help but the decision space is still too unclear to map options or write acceptance criteria.

## Codex Plan Mode Entry

For explicit `grill me` / challenge / clarify requests, raw requirement intake, and PRD/spec drafting requests, enter Codex Plan Mode first when the host exposes it. Plan Mode is the pre-output harness for deciding the narrowest safe route before drafting, asking, comparing, prototyping, or implementing.

Use Plan Mode to run this Groundwork entry decision before user-visible output:

1. Decide `direct fallback` versus `workflow-needed`.
2. Identify the first owning workflow: `to-prd`, decision mapping, `prototype`, `to-issues`, `write-plan`, `implement`, `verify`, `handoff`, `dispatch`, or blocked.
3. Inspect available user context, repo docs, source, tickets, artifacts, or wiki orientation before asking when they can answer the material unknown.
4. Apply the question-quality gate if the next safe route depends on one clarification.
5. Decide whether the user should see a compact grilling question, a draft PRD/spec boundary, a direct answer, or a stop condition.

Plan Mode does not override route negatives. Tiny direct tasks, repo-doc-answerable questions, accepted implementation work, concrete prototype requests, enumerable decision comparisons, or verification asks still route to the narrower workflow.

Do not print the full Plan Mode reasoning or the full question-quality gate during normal interaction. Keep the visible output compact unless the user asks for audit/debug detail or a durable review artifact.

If the host does not expose a Plan Mode tool or visible mode switch, run the same entry decision as prompt-level planning and state the boundary only when it materially affects trust, for example: `Plan Mode: prompt-level fallback; no tool-enforced plan-mode evidence available.` Do not claim `tool_enforced`, runtime execution, selector enforcement, cache refresh, installed-plugin behavior, or Codex host behavior from prompt text alone.

## Route Negatives

Do not grill when a narrower route can safely proceed:

- Direct answer or direct edit: answer or make the small scoped edit when the request is tiny, factual, repo-doc-answerable, or mechanically clear, such as `fix typo in README`.
- Repo-doc-answerable question: inspect the relevant local docs/source first, then answer. Do not ask the user questions that the repo can answer.
- `to-prd`: use PRD shaping when the target reader, decision, known facts, and open questions are clear enough to draft. `to-prd` may apply this shared loop, but it must not own all grilling behavior.
- Decision mapping: use decision mapping when options are already enumerable and the work is to compare tradeoffs, criteria, or consequences.
- `prototype`: use `prototype` when a concrete throwaway UI, state, interaction, visual, or business-rule artifact can answer the question faster than more clarification.
- `implement`: do not use grilling to bypass accepted PRD, scoped issue, implementation-ready source truth, git gates, or verification gates.
- `verify`: use `verify` for readiness or evidence sufficiency claims; grilling cannot decide readiness.

## One-question-at-a-time Loop

Before asking, inspect available user context, repo docs, source, tickets, or artifacts when they can answer the question.

Ask one high-impact question at a time. The question must be:

- necessary for the next route;
- answerable by the user;
- more useful than asking several lower-impact questions;
- framed with the current known facts and assumptions;
- paired with a recommended default or consequence only when evidence supports one.

After the answer, route to the narrowest appropriate workflow by default: direct answer, `to-prd`, decision mapping, `prototype`, `to-issues`, `implement`, `verify`, `handoff`, or blocked. Ask another question only when the answer exposes a new material ambiguity that still blocks that next route.

## Socratic Question Taxonomy

Use this taxonomy as a selection aid. It is not required user-visible output text.

Every question must be valid under the question-quality gate below. A question is valid only when it can change the next route, artifact boundary, acceptance criterion, contract boundary, or evidence requirement.

### Definition Question

Purpose: clarify what a term means before it is written into a PRD, prototype, contract, issue, or implementation.

Use when user language conflicts with repo language, a UI label could be mistaken for an API field, a business state name could map to multiple backend statuses, or a term affects acceptance criteria.

Example:

```text
After inspecting available docs/source/API/UI evidence, I found repo/source
term A in <source>, but the request uses term B. For this artifact, should we
use A, B, or a third term, and what promotion boundary applies: glossary-only,
PRD truth, contract truth, source truth, or unknown?
```

### Boundary Question

Purpose: decide which artifact or workflow owns the claim.

Use when a prototype observation might become product truth, a visual packet might be mistaken for readiness evidence, an implementation summary might be treated as verification, or the next route is ambiguous.

Example:

```text
Is this claim meant to be PRD intent, prototype-only exploration, backend/API
contract, implementation detail, or verification evidence?
```

### Evidence Question

Purpose: separate facts from assumptions.

Use when the agent might invent backend fields, states, metrics, owners, timelines, APIs, or acceptance details; readiness claims depend on old or same-session evidence; or source truth could be inspected before asking the user.

Example:

```text
What evidence supports this claim: user confirmation, source code, API
response, schema, docs, runtime, browser, UAT, or none yet?
```

### Consequence Question

Purpose: identify whether the answer matters enough to ask now.

Use when a question may be interesting but not decision-blocking, multiple possible questions compete, or the agent needs to choose one highest-impact question.

Example:

```text
If the answer is A versus B, what changes in acceptance criteria, API contract,
UI behavior, test scope, route, or handoff?
```

### Counterexample Question

Purpose: make assumptions falsifiable.

Use when implementation would proceed from a hypothesis, a prototype suggests behavior but source truth is unknown, or verification needs to define a minimal failing check.

Example:

```text
What smallest evidence would prove this assumption wrong?
```

### Canonical-term Question

Purpose: pick the artifact-local term without upgrading it beyond its evidence layer.

Use when user terms, UI labels, and code names differ; a handoff needs stable language for the next role; or a PRD needs a consistent term but source confirmation is absent.

Example:

```text
For this artifact only, what term should we use, and is that glossary-only,
PRD truth, contract truth, or source truth?
```

## Question-quality Gate

Before asking a grilling question, pass this internal gate:

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

Do not print this full gate during normal interactive grilling. Print it only when the user asks for audit/debug detail or when producing a durable review artifact that needs the reasoning boundary.

A question fails the gate when:

- it does not change the next route, acceptance, contract, artifact boundary, or evidence requirement;
- it asks for facts available in local docs/source/tickets/artifacts without inspection;
- it asks several questions at once during interactive work;
- it is philosophical, motivational, or generic rather than workflow-relevant;
- it tries to get user confirmation for an invented backend field, state, API, metric, permission, owner, timeline, or acceptance detail;
- it claims readiness, acceptance, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, customer readiness, marketplace behavior, installed-plugin behavior, cache refresh, or selector enforcement.

## Output Requirements

When using grilling interactively, use this compact shape by default:

```text
Inspected:
Blocking ambiguity:
Question:
Impact / Next route:
```

`Impact / Next route` must include the route or evidence impact and the clarification-only evidence boundary when that boundary matters.

For audit/debug output or durable review artifacts, the fuller output may state:

- Plan Mode boundary: host Plan Mode used, prompt-level fallback, unavailable, or unknown, without claiming tool enforcement unless the host/adapter proves it.
- Known facts inspected.
- Material ambiguity blocking the next route.
- The single clarification question.
- Why this question is the highest-impact next question.
- Current route boundary, including what route may become appropriate after the answer.
- Evidence boundary: clarification only, not acceptance or implementation readiness.

## Anti-patterns

Do not ask:

- "Why do you think that?" unless the answer changes route, acceptance, contract, or evidence.
- A batch of questions during interactive work when one highest-impact question is enough.
- A question that local docs, source, tickets, artifacts, fixtures, schemas, or API evidence can answer first.
- A question that upgrades glossary alignment into PRD acceptance, contract truth, source truth, implementation readiness, verification, UAT, release, customer, marketplace, installed-plugin, cache, or selector-enforcement evidence.

## Evidence Boundary

Grilling output is Self-check or clarification evidence only. It may prepare PRD, prototype, decision mapping, issue slicing, implementation planning, or verification routes, but it cannot mark any downstream artifact accepted or ready.

Do not claim clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, customer readiness, marketplace behavior, installed-plugin cache behavior, selector enforcement, or tool-enforced Plan Mode from grilling.
