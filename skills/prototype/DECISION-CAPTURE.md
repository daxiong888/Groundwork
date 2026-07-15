Target Reader: Codex running the `prototype` skill for decision-oriented prototype work.
Reader Action Needed: Capture what the prototype decided, what it rejected, and what still needs confirmation.
Decision Supported: Whether prototype findings can become proposed feedback, require verification, or should route to another Groundwork skill.
Artifact Type: prototype decision-capture reference
Source of Truth: docs/prd-v0.5-prototype-first-skill-expansion.md FR-530 and artifacts/v0.5-prototype-first-skill-expansion/issue-map.md V050-005A.
Scope: Prototype decisions, rejected variants, assumptions, mock fields, client-derived logic, contract impact, open questions, and next route.
Out of Scope: Public visual-handoff skill creation, UI variant mechanics, logic/state lab mechanics, backend/API verification, runtime execution, browser QA, UAT, release, or customer readiness.
Evidence Level: Source-validation guidance only; prototype outputs are not backend/API, browser, runtime, UAT, release, or acceptance evidence by themselves.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, or private payloads.

# Prototype Decision Capture

Use this reference whenever a prototype is used to choose, reject, or narrow product behavior before PRD, issue, implementation, verification, or handoff work.

## Core Rule

Prototype output must name the decision boundary instead of implying product or backend truth.

Capture what was decided for the prototype question, what was rejected, what remains unverified, and what should happen next. Do not treat prototype-only mock fields, visual labels, sample payloads, or client-derived logic as backend/API contract truth unless source evidence or explicit user confirmation is present.

## Prototype Learning Loop

Use this small loop only while one bounded prototype question still has a falsifiable uncertainty. It is a conditional behavior inside `prototype`, not a new public route, durable state machine, automatic retry policy, or requirement-state upgrade.

One iteration records:

```text
Iteration Checkpoint
- Current Hypothesis:
- Probe:
- Observation:
- Evidence Delta Status: changed
- Evidence Delta:
- Decision Delta Status: changed
- Decision Delta:
- Next Probe or Stop: propose_probe
- Proposed Probe:
```

Use the alternative stop shape when no further probe is proposed:

```text
Iteration Checkpoint
- Current Hypothesis:
- Probe:
- Observation:
- Evidence Delta Status: none
- Evidence Delta:
- Decision Delta Status: none
- Decision Delta:
- Next Probe or Stop: stop
- Stop Reason:
```

Rules:

1. Test one material hypothesis with the smallest disposable probe that can distinguish outcomes.
2. Record observation separately from interpretation. Name browser/runtime/tool evidence when used; otherwise keep the claim at prototype evidence level.
3. `Evidence Delta Status` accepts only `changed` or `none`. `Evidence Delta` names what is newly observed since the previous iteration; the first probe may use `first probe`, while a repeated probe and result uses status `none` and describes the repetition in the detail field. The detail must not contradict its status by pairing `changed` with an identical/unchanged result or `none` with a new/first/localized observation.
4. `Decision Delta Status` accepts only `changed` or `none`. `Decision Delta` states what current decision, rejected variant, assumption, contract impact, or next route changed; use status `none` when no decision changed. The detail must not contradict the status by pairing `changed` with no decision change or `none` with an accepted/rejected decision or new route.
5. If either delta status is `none`, `Next Probe or Stop` must be `stop`. Prose synonyms for changed or unchanged do not replace the status tokens.
6. `Next Probe or Stop` accepts only `propose_probe` or `stop`. `propose_probe` requires both delta statuses to be `changed`, exactly one non-empty `Proposed Probe`, and no `Stop Reason`; `stop` requires exactly one non-empty `Stop Reason` and forbids `Proposed Probe`. All reserved checkpoint and companion fields must remain inside the single `Iteration Checkpoint`; a later section cannot reintroduce them.
7. Continue only when the same prototype question remains open and a new probe can add evidence or falsify a changed hypothesis. `propose_probe` is a proposal, not execution; each next iteration requires an explicit continuation and is never auto-run.
8. Update the current decision fields below as canonical state. Move disproved options to `Rejected Variants` and remove resolved items from `Open Questions`; do not preserve stale intermediate assumptions as current truth.

Stop the loop when the question is answered; the observation creates no evidence delta; a source/API/runtime/browser truth claim requires `verify`; a product/acceptance decision requires `to-prd`; accepted production work requires `implement`; approval or authority is missing; or another pass would only add cosmetic polish. Prototype iteration count, artifact polish, and repeated self-check do not prove convergence.

## Required Decision Fields

Every decision-oriented prototype output must include:

- `Confirmed Decisions`: decisions supported by the user's instruction, PRD/task source, inspected source/API/schema evidence, or explicit user confirmation.
- `Rejected Variants`: alternatives discarded by the prototype result or user decision, with the reason and evidence level.
- `Unverified Assumptions`: assumptions still missing PRD, backend source, API response, schema, runtime, browser, or user-confirmation evidence.
- `Mock / Illustrative Fields`: fields used only to explain a screen, state, payload, example, or fixture; label as `mock / illustrative / not backend contract`.
- `Client-derived Logic`: computed, formatted, inferred, aggregated, or display-only logic; label as `Derived / illustrative / not backend contract`.
- `Contract Impact`: `none`, `needs confirmation`, or `confirmed update`.
- `Open Questions`: the smallest confirmation questions needed before PRD/API/implementation promotion.
- `Next Route`: `to-prd`, `to-issues`, `implement`, `verify`, `handoff`, `dispatch`, `cleanup`, or `no follow-up`.

Add the `Iteration Checkpoint` only when a prior probe exists or another prototype iteration is actually being considered. Ordinary one-shot prototypes keep the default decision fields without empty loop scaffolding.

## Decision Status Rules

Use these statuses:

| Status | Meaning | Allowed Next Step |
| --- | --- | --- |
| `confirmed for prototype` | Enough evidence exists to answer the prototype question only. | Proposed feedback, cleanup, or further design iteration. |
| `needs source confirmation` | The decision may affect backend/API/schema/PRD truth but source evidence was not inspected. | Route to `verify` or ask the backend/source confirmation question. |
| `confirmed contract update` | PRD, backend source, API response, schema, runtime evidence, or explicit user confirmation supports the contract claim. | Proposed PRD/issue/implementation update with named evidence. |
| `rejected` | The prototype or user decision ruled out a variant. | Keep as rejected variant; do not implement unless reopened. |

## Next Route Rules

- Use `to-prd` when the prototype resolves product wording, acceptance criteria, or business-rule intent.
- Use `to-issues` when the accepted PRD or decision needs task slicing.
- Use `implement` only when production change scope and acceptance criteria are already accepted.
- Use `verify` when the user asks whether prototype behavior matches backend/API/source truth, browser behavior, runtime behavior, UAT, release, or readiness.
- Use `handoff` when the prototype must be preserved for another session and the handoff threshold is met.
- Use `cleanup` when the prototype was temporary and no downstream source artifact should keep it.

## Hard Stops

Stop promotion and record an open question when:

- a prototype mock field is being copied into backend/API contract without source evidence or user confirmation;
- client-side derivation is being described as server-side behavior without source evidence;
- a screenshot, generated image, HTML artifact, or static prototype is being used as browser/runtime/UAT/release evidence without an actual run and recorded evidence;
- same-session prototype self-check is being treated as clean review, independent verification, or final readiness.

## Output Template

```text
Confirmed Decisions
- ...
Rejected Variants
- ...
Unverified Assumptions
- ...
Mock / Illustrative Fields
- ... (`mock / illustrative / not backend contract`)
Client-derived Logic
- ... (`Derived / illustrative / not backend contract`)
Contract Impact: none / needs confirmation / confirmed update
Open Questions
- ...
Next Route: to-prd / to-issues / implement / verify / handoff / dispatch / cleanup / no follow-up
```
