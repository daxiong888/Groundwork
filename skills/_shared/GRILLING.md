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

For audit/debug or durable review artifacts, add known facts, why this is highest-impact, current route boundary, and evidence boundary.

## Evidence Boundary

Grilling output is self-check or clarification evidence only. Do not claim clean review, independent verification, runtime/browser/UAT/release/customer readiness, marketplace behavior, installed-plugin cache behavior, or selector enforcement from grilling.
