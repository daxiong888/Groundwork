Target Reader: Codex running the `prototype` skill when state, reducer, validation, data-transform, or business-rule uncertainty needs bounded exploration before PRD, issue, implementation, or verification work.
Reader Action Needed: Decide whether to run a logic/state lab, capture explored rules and cases, and preserve contract and evidence boundaries.
Decision Supported: Whether logic/state lab output answered a prototype question, what remains unverified, and what must not be treated as server truth or runtime readiness.
Artifact Type: prototype logic/state-lab reference
Source of Truth: docs/prd-v0.5-prototype-first-skill-expansion.md FR-531 and artifacts/v0.5-prototype-first-skill-expansion/issue-map.md V050-005B.
Scope: State machine, reducer, data transform, validation, and business-rule exploration triggers; should-not-trigger cases; lab outputs; mock/source classification; runtime/browser/UAT evidence boundaries.
Out of Scope: Production implementation, backend/API source-truth verification, public `visual-handoff` skill creation, runtime tooling, browser QA, UAT, release, customer readiness, or server truth without source evidence.
Evidence Level: Source-validation guidance only; logic/state lab artifacts are exploratory prototype output and are not backend/API, browser, runtime, UAT, release, acceptance, or final implementation evidence by themselves.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, screenshots, or private payloads.

# Logic/state Lab

Use a Logic/state lab when the prototype question is about behavior: state transitions, reducer logic, validation branches, data transforms, business rules, edge cases, or decision tables.

Logic/state lab output is exploratory. It may clarify a proposed behavior or expose contradictions, but it does not prove server truth, backend/API contract truth, runtime behavior, browser behavior, UAT readiness, release readiness, or production implementation correctness by itself.

## Trigger Boundary

Logic/state lab should trigger when at least one is true:

- A state machine, transition graph, reducer, or stateful workflow is unclear.
- A data transform, sort/filter/grouping rule, derived label, or validation branch needs deterministic exploration.
- A business rule has edge cases that can be represented with cases, tables, or small throwaway code.
- The output will feed PRD wording, issue slicing, implementation planning, or source-truth verification questions.

Logic/state lab should not trigger when:

- The user asks whether behavior matches real backend/API/source truth; route that claim to `verify`.
- The user asks for production implementation; route to `implement`.
- The user asks for runtime, browser, UAT, release, customer-readiness, marketplace, or installed-plugin evidence.
- The requested conclusion would treat lab assumptions as server truth without PRD, source code, API response, schema, runtime evidence, or explicit user confirmation.
- A direct source/API inspection is required before any exploratory model would be useful.

## Required Output

```text
Prototype Question
Decision Needed
Model / Rule Under Test
Inputs
States / Transitions
Cases Covered
Observed Result
Contract Sources
Confirmed Backend Fields
Mock / Illustrative Fields
Client-derived Logic
Unverified Assumptions
Contract Impact: none / needs confirmation / confirmed update
Open Questions
Next Route: to-prd / to-issues / implement / verify / handoff / dispatch / cleanup / no follow-up
Runtime / Browser Evidence
Evidence Boundary
Cleanup Decision
```

## Lab Rules

- Keep the lab small, deterministic, and disposable.
- Prefer explicit cases, tables, or minimal code over narrative-only reasoning when behavior needs repeatability.
- Separate observed prototype behavior from accepted product, backend, or server behavior.
- Mark mocked inputs, fields, states, and payloads as `mock / illustrative / not backend contract`.
- Mark client-computed transforms, display labels, counters, filters, sort order, and derived state as `Derived / illustrative / not backend contract`.
- Use `DECISION-CAPTURE.md` for confirmed decisions, rejected variants, unverified assumptions, `Contract Impact`, open questions, and next route.
- Use `CONTRACT-BOUNDARY.md` before any PRD, issue, contract, visual handoff, or implementation feedback.
- If lab findings contradict PRD/task/source evidence, stop promotion and route the conflict to `verify` or source-owner confirmation.

## Evidence Boundary

- Logic/state lab output may support `confirmed for prototype` behavior decisions and proposed feedback only.
- Server truth requires named PRD, backend source, API response, schema, runtime evidence, or explicit user confirmation.
- Source/API/schema truth cannot be inferred from reducer code, fixtures, mocked payloads, decision tables, or terminal output created only for the lab.
- Runtime evidence requires an actual command/tool execution with scope, output, and limitation. A lab artifact is not runtime evidence unless that execution is separately run and recorded for the claim.
- Browser evidence requires an actual browser run with tool, URL/context, action, observation, and limitation.
- UAT and release evidence require separate verification packages for those claims.
- Production implementation correctness requires accepted implementation scope, production code, and relevant checks.

## Hard Stops

- Stop before treating Logic/state lab output as server truth without source evidence.
- Stop before treating lab assumptions, mocked schema, fixture fields, state names, reducers, or derived calculations as confirmed backend/API/schema contract.
- Stop before treating a lab artifact as runtime/browser/UAT/release evidence without the qualifying run and recorded evidence.
- Stop before turning throwaway lab code into production implementation guidance unless accepted implementation scope and source-truth evidence exist.
