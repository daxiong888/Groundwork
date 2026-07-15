---
name: prototype
description: Throwaway logic/state/UI/static-HTML prototype for a specific interaction, visual, or business-rule question. Not production code, backend/API truth, readiness, durable docs, or handoff.
---

# prototype

## Trigger Contract

Use when a bounded throwaway artifact can answer a product, state, interaction, visual, or business-rule question faster than implementation.

Route away:

- PRD wording or unclear requirement shaping -> `to-prd`.
- Production code edits -> `implement`.
- Source/API/frontend contract or readiness proof -> `verify`.
- Handoff or durable continuation -> `handoff`.
- No concrete prototype question -> use `skills/_shared/GRILLING.md` or answer directly.

## Required Evidence

Name the prototype question first. Inspect source, PRD, task, data shape, existing prototype, screenshot, or UI notes only as needed. Static HTML/visual claims need browser/runtime evidence; otherwise mark `unverified`.

Prototype evidence can classify backend candidates, mock fields, and client-derived logic, but cannot confirm backend/API/source truth without source, schema/API, runtime evidence, or explicit confirmation.

Load one branch extension: `LOGIC.md`, `LOGIC-LAB.md`, `UI.md`, or `UI-VARIANTS.md`. Add `CONTRACT-BOUNDARY.md` for mock/backend separation, `DECISION-CAPTURE.md` for promoted decisions or any iterative prototype-learning pass, `skills/_shared/VISUAL-HANDOFF-PACKET.md` for visual packets, and `skills/_shared/REVIEW-LOOP.md` only when downstream ownership matters.

## Workflow

State question, decision, contract sources, and unavailable evidence; grill only if ambiguity blocks scope; pick one branch; keep artifact throwaway; separate confirmed/rejected decisions, mock/client-derived fields, assumptions, and backend candidates; run browser/runtime checks for visual/interaction correctness; draft findings as proposed feedback unless source truth supports promotion; decide cleanup.

For iterative work, run the conditional Prototype Learning Loop from `DECISION-CAPTURE.md`: one falsifiable hypothesis, one minimum probe, one observation, and one evidence/decision delta at a time. Another iteration requires new evidence or a changed hypothesis; it is not an automatic retry.

## Hard Stops

- Stop before treating any prototype field, state, enum, payload, or rule as confirmed backend contract without qualifying evidence.
- Stop before handing prototype findings to PRD, issue, implementation, or contract notes unless contract sources, confirmed fields, mock fields, client-derived logic, and assumptions are separated.
- Stop before promoting a prototype into durable source truth unless `Contract Impact: confirmed update`.
- Stop before treating static HTML, screenshots, generated images, UI variants, or logic lab output as browser/runtime/UAT/release/customer evidence without the actual evidence named.
- Do not let prototype polish imply production capability.
- Do not use prototype instead of `verify` for backend/API/source truth or readiness claims.

## Failure Handling

Mark missing backend/state/rule evidence as `mock`, `illustrative`, `proposed hypothesis`, `unverified assumption`, or `client-derived logic`. If prototype conflicts with API/schema/source, name the conflict and route proof to `verify`. If browser/runtime evidence is unavailable, mark visual/interaction evidence `unverified`.

## Output Shape

Default to prototype question, answer/decision, evidence boundary, states or interactions explored, material gaps, and cleanup/next action. Add contract sources, confirmed/rejected decisions, mock/client-derived fields, assumptions, contract impact, browser/runtime evidence, coverage, or downstream feedback only when the prototype actually exercised them.

For an explicitly requested visual handoff packet, include the required sections from `skills/_shared/VISUAL-HANDOFF-PACKET.md`; do not emit an empty packet or `not applicable` placeholders for ordinary prototypes.

## Stop Condition

Stop when the prototype question is answered, remaining gap is explicit, evidence level is bounded, and cleanup or absorption is decided. Also stop when an iteration produces no evidence delta, needs source/API/runtime proof, requires a product/authority decision, or would turn throwaway work into production implementation.

## Artifact Rule

Create prototype files only for a concrete question. Delete/absorb after use unless temporary retention has reason. Follow artifact policy for durable artifacts and redact sensitive data.
