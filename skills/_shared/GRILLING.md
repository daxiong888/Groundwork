# Shared Grilling Reference

Target Reader: Groundwork skill authors, routers, implementers, clean reviewers, and verifiers deciding whether ambiguity needs clarification before PRD, prototype, decision mapping, or implementation.
Reader Action Needed: Use this reference to run the shared grilling loop only when material ambiguity blocks a safe next route.
Decision Supported: Whether to ask a single clarification question, answer directly, route to `to-prd`, route to decision mapping, route to `prototype`, or stop before implementation readiness claims.
Artifact Type: shared workflow reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-540, AC-A3, AC-D1, and V050-003A in `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md`.
Scope: Shared grilling behavior, one-question-at-a-time clarification, route boundaries, route negatives, and evidence boundaries.
Out of Scope: Creating a public `grill` skill, accepting PRDs, approving implementation readiness, replacing decision mapping, replacing prototype exploration, or claiming runtime/browser/UAT/release evidence.
Evidence Level: Source-validation policy. This file is local shared guidance only until separately reviewed and verified.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, private payloads, or personal data.

## Public Surface Boundary

`grill` is a public candidate only after shared route negatives prove a distinct invocation moment and hard negatives against over-questioning pass.

Do not create `skills/grill/SKILL.md` or treat this shared reference as a public skill. Public exposure belongs to the later V050-003B slice and requires maintainer acceptance, route-negative evidence, and independent skill-quality review.

## Core Definition

Grilling is the shared clarification route for material ambiguity where the unknowns are not yet enumerable.

Use grilling when the next safe action depends on discovering the right question before drafting, comparing, prototyping, or implementing. Grilling produces clarification only. It does not produce PRD acceptance, task readiness, implementation readiness, clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, or customer readiness.

## Trigger Conditions

Use the shared grilling loop when at least one condition is true:

- The user explicitly asks to be grilled, challenged, questioned, or clarified before proceeding.
- Raw product, workflow, skill-selection, runtime, marketplace, plugin, prototype, or implementation intent has material ambiguity and the missing unknowns are not yet enumerable.
- A requested PRD, prototype, or decision artifact would invent product truth without first discovering the highest-impact unknown.
- The user wants planning help but the decision space is still too unclear to map options or write acceptance criteria.

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

After the answer, either ask the next single highest-impact question or route to the narrowest appropriate workflow: direct answer, `to-prd`, decision mapping, `prototype`, `to-issues`, `implement`, `verify`, `handoff`, or blocked.

## Output Requirements

When using grilling, state:

- Known facts inspected.
- Material ambiguity blocking the next route.
- The single clarification question.
- Why this question is the highest-impact next question.
- Current route boundary, including what route may become appropriate after the answer.
- Evidence boundary: clarification only, not acceptance or implementation readiness.

## Evidence Boundary

Grilling output is Self-check or clarification evidence only. It may prepare PRD, prototype, decision mapping, issue slicing, implementation planning, or verification routes, but it cannot mark any downstream artifact accepted or ready.

Do not claim clean review, independent verification, runtime evidence, browser evidence, UAT evidence, release evidence, customer readiness, marketplace behavior, installed-plugin cache behavior, or selector enforcement from grilling.
