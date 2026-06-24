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
