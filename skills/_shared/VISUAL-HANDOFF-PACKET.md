Target Reader: Codex running `prototype`, `handoff`, or `verify` when visual handoff material could be mistaken for implementation or readiness evidence.
Reader Action Needed: Structure visual packets for review while preserving source, runtime, browser, UAT, and release evidence boundaries.
Decision Supported: Whether a visual packet is only a communication artifact, what it may communicate, and which claims require separate evidence.
Artifact Type: shared visual handoff packet contract
Source of Truth: docs/prd-v0.5-prototype-first-skill-expansion.md FR-532, AC-B5, AC-C4, AC-D1 and artifacts/v0.5-prototype-first-skill-expansion/issue-map.md V050-005C.
Scope: Visual handoff packet sections, mock-vs-confirmed field marking, API contract mapping, open questions, do-not-assume guidance, and evidence boundaries.
Out of Scope: Public `visual-handoff` skill creation, browser automation, runtime proof, source/API verification, UAT, release, customer readiness, UI variants, and logic/state lab mechanics.
Evidence Level: Source-validation guidance only; visual packets are communication/review artifacts unless separate source, browser, runtime, UAT, or release evidence is produced and named.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, screenshots, or private payloads.

# Visual Handoff Packet

## Core Rule

A visual handoff packet is a communication artifact for frontend/backend/product review. It can organize state, flow, UI, API mapping, mock fields, and open questions, but it must not replace source/API contract docs or become readiness evidence by itself.

HTML packets, screenshots, generated images, static prototypes, prototype output, diagrams, and visual artifacts remain communication/review artifacts unless the packet names the separate browser run, runtime run, API/schema/source inspection, UAT evidence, or release evidence that supports the specific claim.

## Required Sections

Every visual handoff packet must include these sections or explicitly mark them `not applicable` with a reason:

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

Minimum section intent:

- `Overview`: the review goal, audience, and scope.
- `State / Flow Diagram`: states, transitions, entry/exit points, and unknowns.
- `UI Surface Map`: screens, panels, controls, messages, and visible states.
- `Selected Variant or Variant Switcher`: selected UI option, variant comparison, or why variants are out of scope.
- `API Contract Table`: endpoint, field, owner, evidence source, and status for each API/schema claim.
- `Error / Empty / Loading States`: visible user-facing states and whether each is confirmed or proposed.
- `AC -> UI Behavior -> API Evidence Mapping`: acceptance criterion, UI behavior, source/API evidence, and gap.
- `Mock vs Confirmed Field Badges`: each field marked as confirmed, proposed, mock, or client-derived.
- `Open Questions`: smallest unresolved decisions before implementation or contract promotion.
- `Do Not Implement / Do Not Assume`: explicit non-contract fields, visual-only conveniences, unsupported API/schema assumptions, and readiness claims that are not proven.
- `Evidence Boundary`: the exact evidence layer available and missing for source/API, browser, runtime, UAT, release, and customer readiness.

## Mock vs Confirmed Fields

Use these badges consistently:

| Badge | Meaning | May Become Contract Truth? |
| --- | --- | --- |
| `confirmed source/API` | Backed by named PRD, source code, API response, schema, runtime evidence, or explicit user confirmation. | Yes, only for the named evidence scope. |
| `proposed contract hypothesis` | Needed by the visual flow but source/API evidence has not been inspected or confirmed. | No, requires separate source/API/user confirmation. |
| `mock / illustrative / not backend contract` | Added only to explain a state, screen, payload, screenshot, or prototype. | No. |
| `Derived / illustrative / not backend contract` | Computed, formatted, aggregated, inferred, or display-only client logic. | No. |

Mock fields in a visual packet must not be copied into API/schema/source truth, PRD acceptance, or implementation guidance as confirmed fields. If a visual packet needs a field that is not source-backed, place it under `Open Questions` and `Do Not Implement / Do Not Assume`.

## Evidence Boundary

Use this boundary table when visual packet evidence could be overclaimed:

| Claim Type | What Qualifies | What Does Not Qualify |
| --- | --- | --- |
| Source/API/schema truth | Named PRD, source file, API response, schema, runtime evidence, or explicit user confirmation. | Static HTML, screenshot, generated image, visual packet, prototype-only fixture, or client-derived label. |
| Browser evidence | Actual browser/UI run with tool, URL/context, action, observation, and limitation. | HTML file existence, visual packet text, screenshot without recorded browser context, or generated mock. |
| Runtime evidence | Actual command, adapter, or runtime execution with scope, output, and limitation. | Prompt text, packet summary, static artifact, or implementation summary. |
| UAT evidence | User/customer/UAT environment evidence for the specific UAT claim. | Local visual packet, internal review, self-check, or prototype artifact. |
| Release evidence | Release-gate evidence for the specific release claim. | Local source diff, visual handoff packet, clean-looking UI, or self-check. |

## Skill Integration

- `prototype`: may create or review visual packets as prototype/communication output. It must classify mock, proposed, confirmed, and client-derived fields using `skills/prototype/CONTRACT-BOUNDARY.md`.
- `handoff`: may cite or package visual packets for continuation. It must keep packet claims under `Do-Not-Assume` unless source/API, browser, runtime, UAT, or release evidence is separately named.
- `verify`: may verify whether a packet is evidence-sufficient for a readiness claim. It must block or mark unverified any browser, runtime, UAT, release, customer-readiness, or API/schema truth claim based only on packet output.

## Hard Stops

- Stop before treating a visual handoff packet as browser evidence unless an actual browser run is performed and recorded.
- Stop before treating a visual handoff packet as runtime, UAT, release, customer-readiness, or installed-plugin evidence unless the specific qualifying evidence exists and is named.
- Stop before treating mock, illustrative, or client-derived fields as confirmed API/schema/source truth.
- Stop before creating a public `visual-handoff` skill from this shared reference.

## Output Reminder

When reporting visual packet work, keep role evidence separate:

```text
Self-check Evidence:
Clean Review Evidence:
Independent Verification Evidence:
Runtime Evidence:
Browser Evidence:
UAT Evidence:
Release Evidence:
Readiness Boundary:
Required Next Independent Role:
```
