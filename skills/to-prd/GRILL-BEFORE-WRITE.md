# GRILL-BEFORE-WRITE

Target Reader: Codex running the Groundwork `to-prd` skill.
Reader Action Needed: Check full durable PRD content inputs after the Durable Write Gate passes.
Decision Supported: Whether full durable PRD content drafting can proceed or must stop for evidence-first clarification.
Artifact Type: branch-specific full-durable PRD content gate
Source of Truth: Groundwork PRD shaping contract, shared grilling reference, and domain-language promotion guardrails.
Scope: Full durable PRD pre-write buckets, evidence-first clarification, question-count mode, domain-language conflict handling, and content gate.
Out of Scope: Accepting PRDs, implementing requirements, verifying readiness, runtime execution, release approval, or replacing downstream issue slicing.
Evidence Level: Source-validation policy only. This gate does not prove implementation readiness, runtime behavior, UAT readiness, release readiness, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

Use this content gate only for `full durable` mode, after the owning `SKILL.md` Durable Write Gate passes. Do not load or apply it for `compact conversation` or `compact durable` output. Explicit interactive grilling in conversation uses `skills/_shared/GRILLING.md` and does not activate this durable-only gate.

## Mandatory pre-write check

Do not write PRD content until all six buckets are explicitly listed:

1. **Target Reader** (who must review or decide next)
2. **Decision Supported** (the decision or action the PRD must enable)
3. **Known Facts** (verified from user input or cited evidence)
4. **Assumptions** (inferences not yet verified)
5. **Open Questions** (decision-blocking unknowns)
6. **Needs Confirmation** (unknown business facts, fields, states, permissions, user behaviors, or acceptance details that must not be invented)

If any bucket is missing, stop and add it first.

Apply **Domain Language / Term Conflict** only when terminology materially affects acceptance, contract truth, source truth, prototype interpretation, verification, or handoff. Use `skills/_shared/DOMAIN-LANGUAGE.md` for evidence-layer labels and promotion blockers.

When no material term conflict exists, do not print a full domain-language bucket in normal conversation output. In durable PRDs, omit the section or write `Domain Language / Term Conflict: none material.`

## Evidence-first clarification

- Inspect local code, docs, tickets, data, or prototype notes first when they can answer a question without user input.
- Ask the user only for unknowns that remain after available evidence has been checked.
- Follow `skills/_shared/GRILLING.md` clarification modes: interactive work asks one highest-impact question at a time; non-interactive questionnaire or written PRD gap-list mode may ask at most 5 high-impact questions only when explicitly requested.
- Include a recommended answer or default decision and the impact of the answer for each clarification question when evidence supports one.
- Use `skills/_shared/GRILLING.md` to select the single highest route-impact question when competing unknowns are not yet enumerable.
- For iterative clarification, use the shared Spec Convergence Loop. After each answer, write the confirmed decision into `Known Facts` or the appropriate PRD section, update affected ACs/constraints, remove the resolved item from `Open Questions` / `Needs Confirmation`, and delete contradicted assumptions. Do not append the answer as a conversation-history note while leaving stale canonical state in place.

## Clarification hardening

- Never invent backend fields, business states, policy, metrics, owner, timeline, field values, or unsupported abilities.
- Any unknown backend field, business state, unsupported ability, or missing acceptance detail must be labeled **NEEDS CLARIFICATION**.
- If a required acceptance detail is unknown, mark it **NEEDS CLARIFICATION** instead of guessing.
- Do not mutate product truth based on prototype-only mock data.
- Do not treat glossary-only alignment as PRD acceptance, backend/API contract truth, source truth, or implementation readiness.
- If user terminology conflicts with repo/source/API/UI terminology and affects correctness, surface the conflict instead of silently resolving it.

## Full-durable content gate

After the Durable Write Gate passes, full durable PRD content drafting may proceed only when:

- the six buckets are present,
- assumptions are clearly separated from facts,
- remaining questions are limited to the highest-impact unknowns,
- each listed question has a recommended answer or default and impact when possible,
- unknown business details are tagged **NEEDS CLARIFICATION**,
- material term conflicts include an evidence layer and a promotion blocker.

Convergence does not require zero unknowns. It requires that the next route's material decisions are resolved or explicitly gated, remaining unknowns are accurately labeled, and no stale assumption or resolved question still contradicts the current draft.
