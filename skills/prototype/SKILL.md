---
name: prototype
description: Use a throwaway logic/state/UI/static-HTML prototype to answer a specific interaction, visual, or business-rule question before PRD or implementation. Not for production code, backend/API truth, readiness verification, durable docs, or handoff.
---

# prototype

## Trigger Contract

Use when a bounded throwaway artifact can answer a product, state, interaction, visual, or business-rule question faster than full implementation.

Route away:

- PRD wording or unclear requirement shaping -> `to-prd`.
- Production code edits -> `implement`.
- Source/API/frontend contract or readiness proof -> `verify`.
- Handoff or durable continuation -> `handoff`.
- No concrete prototype question -> use `skills/_shared/GRILLING.md` or answer directly.

## Required Evidence

Name the prototype question first. Inspect source, PRD, task, data shape, existing prototype, screenshot, or UI notes only as needed to answer it. Static HTML/visual claims need browser/runtime evidence; otherwise mark them `unverified`.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Core boundaries:

- Prototype evidence may classify backend contract candidates, mock fields, and client-derived logic, but cannot confirm backend/API/source truth without PRD, backend source, API/schema, runtime evidence, or explicit user confirmation.
- Use `DECISION-CAPTURE.md` for confirmed decisions, rejected variants, assumptions, open questions, contract impact, and next route.
- Use `CONTRACT-BOUNDARY.md` for backend contract candidates, mock/illustrative fields, and client-derived logic.
- Use `LOGIC.md`, `LOGIC-LAB.md`, `UI.md`, or `UI-VARIANTS.md` as the single branch extension.
- Use `skills/_shared/VISUAL-HANDOFF-PACKET.md` only for visual/backend/frontend review packets.
- Use `skills/_shared/ROLE-SEPARATION.md` only when prototype output materially affects design, public skill behavior, contract truth, or downstream implementation.

## Workflow

1. State Prototype Question, Decision Needed, Contract Sources, and unavailable evidence.
2. If ambiguity blocks the question, apply shared grilling instead of inventing scope.
3. Pick one branch: simple logic, logic lab, UI/static HTML, or UI variants.
4. Keep artifact throwaway and narrow.
5. Separate confirmed decisions, rejected variants, mock fields, client-derived logic, unverified assumptions, and backend contract candidates.
6. Run browser/runtime checks when visual or interaction correctness matters; if unavailable, still provide contract-boundary output and name the smallest follow-up check.
7. Draft findings as proposed PRD/issue/contract/implementation feedback unless source truth or user confirmation already supports promotion.
8. Decide cleanup: delete, absorb, or keep temporarily with reason and expiry.

## Hard Stops

- Stop before treating any prototype field, state, enum, payload, or rule as confirmed backend contract without qualifying evidence.
- Stop before handing prototype findings to PRD, issue, implementation, or contract notes unless contract sources, confirmed fields, mock fields, client-derived logic, and assumptions are separated.
- Stop before promoting a prototype into durable source truth unless `Contract Impact: confirmed update`.
- Stop before treating static HTML, screenshots, generated images, UI variants, or logic lab output as browser/runtime/UAT/release/customer evidence without the actual evidence named.
- Do not let prototype polish imply production capability.
- Do not use prototype instead of `verify` for backend/API/source truth or readiness claims.

## Failure Handling

- Missing backend source -> mark `mock / illustrative / proposed hypothesis`.
- Missing state/rule source -> mark `unverified assumption` or `client-derived logic`.
- Prototype conflicts with API/schema/source -> name conflict and route source-truth proof to `verify`.
- Browser/runtime evidence unavailable -> mark visual/interaction evidence `unverified` and name the smallest check.

## Output Shape

```text
Prototype Question
Decision Needed
Contract Sources
Contract Status
Confirmed Decisions
Rejected Variants
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
Open Questions
Next Route: to-prd / to-issues / implement / verify / handoff / dispatch / cleanup / no follow-up
States Explored
Interactions Explored
Browser / Runtime Evidence
Coverage Evidence Status: prototype_only / browser_verified / runtime_verified / unverified
Visual Handoff Packet
Role-separation Evidence
Known Gaps
Implementation Implications
Proposed PRD / Issue / Contract Feedback
Cleanup Decision
Next Action
Artifact Recommendation
```

For visual handoff packets, include the required sections from `skills/_shared/VISUAL-HANDOFF-PACKET.md` or mark them `not applicable`.

## Stop Condition

Stop when the prototype question is answered, remaining gap is explicit, evidence level is bounded, and cleanup or absorption is decided.

## Artifact Rule

Create prototype files only when they answer a concrete question. Delete or absorb them after use unless temporary retention has a clear reason. Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md` for durable artifacts. Redact secrets, credentials, PII, sensitive logs, screenshots, private payloads, and database rows.
