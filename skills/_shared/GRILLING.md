# Shared Grilling Reference

Target Reader: Groundwork skill authors, routers, implementers, clean reviewers, and verifiers deciding whether ambiguity needs clarification before PRD, prototype, decision mapping, or implementation.
Reader Action Needed: Run the shared grilling loop only when material ambiguity blocks a safe next route.
Decision Supported: Whether to ask one clarification, answer directly, route to `to-prd`, decision mapping, `prototype`, or stop before readiness claims.
Artifact Type: shared workflow reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-540/AC-A3/AC-D1 and `docs/prd-v0.5.1-socratic-grilling-expansion.md`.
Scope: Shared grilling behavior, question-quality gate, route-after-answer behavior, route negatives, and evidence boundaries.
Out of Scope: Public `grill` skill creation, PRD acceptance, implementation readiness, decision mapping replacement, prototype replacement, or runtime/browser/UAT/release evidence.
Evidence Level: Source-validation policy only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, or personal data.

## Public Surface Boundary

Do not create public `grill`, `socratic`, `domain-language`, or `grill-with-docs` skills for this behavior. Socratic questioning is a shared selection aid until a later accepted publicization scope passes route-negative evidence, skill-quality review, and maintainer acceptance.

## Core Definition

Grilling is clarification for material ambiguity where unknowns are not yet enumerable. It can prepare PRD, prototype, decision mapping, issue slicing, implementation planning, or verification routes, but cannot create PRD acceptance, task readiness, implementation readiness, clean review, verification, runtime/browser/UAT/release evidence, or customer readiness.

Rule: ask less, ask sharper, and ask only questions that can change route, artifact boundary, AC, contract boundary, or evidence requirement.

## Trigger And Route Negatives

Use grilling when the user asks to be challenged/clarified, raw product/workflow/skill/runtime/plugin/prototype/implementation intent has material ambiguity, requested artifacts would invent product truth, or planning space is too unclear to map options.

Do not grill when a narrower route can safely proceed:

- direct answer/edit for tiny factual or mechanical work;
- inspect repo docs/source first when they can answer;
- `to-prd` when target reader, decision, facts, and open questions are clear enough;
- decision mapping when options are enumerable;
- `prototype` when a throwaway artifact can answer faster;
- `implement` when accepted source, scope, git gates, and verification gates are ready;
- `verify` for readiness/evidence sufficiency.

For explicit grill/challenge/clarify prompts, use Plan Mode when exposed to choose the narrowest route. Plan Mode may shape boundary or ask one question, but must not write durable artifacts or claim tool-enforced Plan Mode without host evidence.

## Clarification Modes

Interactive default: ask one highest-impact question; ask another only after the answer exposes a new blocker.

Non-interactive gap list: at most five questions, only when the user explicitly asks for a questionnaire/checklist/gap list or a written artifact. Each question must state impact and a recommended default when evidence supports one.

## Spec Convergence Loop

Use this small loop for raw or ambiguous specification work when one material decision still blocks the next route. It runs one user-controlled turn at a time inside the owning route; it does not auto-run skills, create a public `loop` route, or require a workflow artifact.

1. Inspect available facts and the current canonical draft before asking.
2. Select one decision that can change route, AC, contract, artifact boundary, checkpoint, or evidence requirement.
3. Ask one question with a recommended answer and consequence when evidence supports a recommendation.
4. After the answer, record the decision delta, update the canonical facts/assumptions/open questions, and remove the resolved or contradicted stale state.
5. Route or ask one new question only if a new material blocker remains. Another question requires a new decision delta; repeated reframing of the same unresolved question is not progress.

The loop is done when the next route's material decisions are resolved or explicitly gated, not when every possible unknown has disappeared. Stop or pause when repo/source evidence can answer instead; the user lacks authority; the answer would authorize risky work; no decision delta exists; or the remaining unknown can safely stay as `NEEDS CLARIFICATION` for the next owner.

After a material answer, use this compact write-back when the canonical update is not already obvious in a durable PRD:

```text
Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta:
- Canonical Update Status: updated
- Canonical Update:
- Resolved / Removed:
- Next Route or Question: route
- Next Route: to-prd
```

`Decision Delta Status` must be exactly `changed`, and `Canonical Update Status` must be exactly `updated`. These tokens assert that the answer materially changed the current decision and that the canonical state was rewritten; prose synonyms do not replace them, and the detail fields must not negate the token with claims such as nothing changed, unchanged, kept as-is, or deferred. If either assertion is not true, do not emit a convergence checkpoint: stop or pause and name the missing evidence, decision, or authority instead.

Use exactly one of three finite states and only its companion fields:

- `route`: include exactly one public `Next Route` from `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, or `wiki`; do not include `Question`, `Impact / Next route`, or `Stop Reason`.
- `question`: include exactly one `Question` and one `Impact / Next route`; do not include `Next Route` or `Stop Reason`.
- `stop`: include exactly one `Stop Reason`; do not include `Next Route`, `Question`, or `Impact / Next route`.

All reserved checkpoint and companion fields must remain inside the single `Spec Convergence Checkpoint`; a later section cannot reintroduce or override them.

For example, the question and stop alternatives are:

```text
Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta:
- Canonical Update Status: updated
- Canonical Update:
- Resolved / Removed:
- Next Route or Question: question
- Question:
- Impact / Next route:
```

```text
Spec Convergence Checkpoint
- Decision Delta Status: changed
- Decision Delta:
- Canonical Update Status: updated
- Canonical Update:
- Resolved / Removed:
- Next Route or Question: stop
- Stop Reason:
```

Do not emit this checkpoint for the initial one-question prompt or for a clear spec that does not need iterative clarification.

For a recurring workflow, conditionally apply this loop lens only where it changes the spec:

- recurring unit and any parent loop;
- trigger (`event`, `schedule`, or explicit manual action);
- owner, input, output, and falsifiable success evidence;
- human checkpoint, decision, and decision-ready brief;
- bounded retry, stop/pause condition, and next route.

Do not turn the lens into a mandatory checklist. Prepare safe, reversible analysis before a checkpoint when useful, but never "push right" past source acceptance, destructive/remote/data/production/shared-skill approval, secrets/PII review, or customer-visible authority.

When an answer would authorize a data write, stop before action and emit this exact checkpoint once. The seven control values are fixed tokens; the four decision details must be non-empty and decision-ready:

```text
Risky Action Checkpoint
- Proposed Action:
- Action Kind: data_mutation
- Target:
- Target Kind: data_store
- Risk:
- Rollback/Undo:
- Approval Needed: yes
- Risk Gate: data_write
- Approval Status: pending
- Action State: blocked
- Checkpoint Position: before_action
```

The complete checkpoint is exactly the heading plus these eleven structured field lines. Do not add prose, sections, duplicate fields, wrappers, or notes before, inside, or after the card. The four decision-detail fields describe intended, potential, or contingent work only; none may contain timing, present/past execution, or completion claims such as `now`, `immediately`, `before approval`, `already`, `executed`, `finished`, `ran successfully`, `went live`, or `was changed`. Do not claim or imply that the data write can proceed while `Approval Status` is `pending` and `Action State` is `blocked`.

## Question-quality Gate

Before asking, inspect available context/source when it can answer the question. A valid question is necessary for the next route, answerable by the user, more useful than several lower-impact questions, grounded in known facts/assumptions, and paired with a default/consequence only when evidence supports it.

Internal gate:

```text
Question:
Question type:
Known facts inspected:
Material ambiguity:
Why highest-impact:
Route or evidence impact:
Can repo/source/docs answer it first:
Recommended default:
Evidence boundary:
```

A question fails when it does not affect route/acceptance/contract/artifact/evidence, asks for facts local evidence can answer, batches questions in interactive mode, exceeds five gap-list questions, invents backend fields/states/APIs/metrics/owners/timelines, or claims readiness/evidence beyond clarification.

## Question Types

Use only as selection aids:

- Definition: clarify a term before PRD/prototype/contract/issue/implementation.
- Boundary: decide artifact/workflow ownership of a claim.
- Evidence: separate facts from assumptions and name required source.
- Consequence: confirm whether an answer changes route, AC, API, UI, test, or handoff.
- Counterexample: make assumptions falsifiable.
- Canonical term: pick artifact-local language without upgrading evidence layer.

Priority: Boundary/Evidence first when route, truth layer, or verification changes; Counterexample when assumptions would drive implementation; Consequence when multiple questions compete; Definition/Canonical-term when terms block acceptance or source alignment.

## Output

Interactive default:

```text
Inspected:
Blocking ambiguity:
Question:
Impact / Next route:
```

`Impact / Next route` is required and must state the route, acceptance, contract, artifact, or evidence consequence of the answer. Deterministic output checks validate the one-question shape and this explicit impact field; the question-quality gate above remains responsible for judging whether that claimed consequence is actually material and source-grounded.

For audit/debug or durable review artifacts, add known facts, why this is highest-impact, current route boundary, and evidence boundary.

After an answered question, add `Decision Delta` and `Remaining Blocking Ambiguity` only when they materially explain why the route changed or why one more question is needed. Do not print empty convergence scaffolding.

## Evidence Boundary

Grilling output is self-check or clarification evidence only. Do not claim clean review, independent verification, runtime/browser/UAT/release/customer readiness, marketplace behavior, installed-plugin cache behavior, or selector enforcement from grilling.
