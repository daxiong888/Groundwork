# Workflow State Machine

Target Reader: Groundwork public skills, eval authors, reviewers, and maintainers who need one canonical workflow transition contract.
Reader Action Needed: Validate whether a skill may accept the current requirement state, which state it may produce, which route may run next, and which gate must stop unsafe promotion.
Decision Supported: Whether a Groundwork route transition is legal, blocked, explicitly bypassed, or only recommendation-level.
Artifact Type: shared guardrail
Source of Truth: `skills/_shared/LIFECYCLE-PREFLIGHT.md`, public skill trigger contracts, routing reliability schema, and current eval prompt fields.
Scope: Public Groundwork route transitions for `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, and `wiki`, plus direct/blocked boundary behavior.
Out of Scope: Runtime adapter internal lifecycle states, external tracker status mutation, automatic task CRUD, automatic `STATE.md` writes, release approval, UAT approval, or replacing source-specific skill contracts.
Evidence Level: Source-derived canonical contract for prompt routing and eval review; runtime behavior still requires installed-plugin/cache evidence when claimed.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.
Related Issues: FRAME-001.

## Core Rule

Groundwork workflow state is a transition contract, not a transcript. A route may act only when the current requirement state satisfies its accepted pre-state gate or when a documented exception below explicitly allows a narrower action.

`expected_state_transition` in routing eval rows must use the canonical tokens in this file. The token records the expected transition action, not proof that the stronger produced state was actually verified.

## Canonical Tokens

Requirement state tokens:

```text
raw
grilled
prd_draft
prd_accepted
issue_ready
implementation_ready
verified
blocked
```

Expected state transition tokens:

```text
none
clarify
draft
accept
split
plan
implement
verify
handoff
block
close
```

Route tokens for `expected_best`, `acceptable_routes`, and `forbidden_routes`:

```text
direct
to-prd
to-issues
triage
write-plan
prototype
implement
verify
handoff
dispatch
wiki
```

Outcome, produced-state, and stop-condition token:

```text
blocked
```

## Requirement State

| Requirement State | Meaning | Owner |
|---|---|---|
| `raw` | New, ambiguous, draft-only, or conversation-only intent without accepted source truth. | `to-prd` by default; `direct` only for tiny answers; `blocked` when action would be unsafe. |
| `grilled` | Clarified enough to draft but not accepted as product truth. | `to-prd`; may return to `direct` for narrow answers or `blocked` for unresolved material gaps. |
| `prd_draft` | Draft PRD/spec exists but is not accepted by maintainer, user, or canonical source. | `to-prd`; `verify` may review consistency without promoting acceptance. |
| `prd_accepted` | Accepted PRD/spec/plan or named source truth is ready to slice or plan. | `to-issues`, `write-plan`, `triage`; `to-prd` only for scoped PRD updates. |
| `issue_ready` | A vertical slice has clear scope, acceptance criteria, blocker status, and verification expectation. | `triage` owns final readiness; `write-plan` may plan; `dispatch` may route only after accepted readiness is evidenced. |
| `implementation_ready` | Source truth, scoped files/modules, acceptance criteria, verification expectation, and git topology decision are sufficient for implementation. | `implement`; `dispatch` for accepted ready tasks; `triage` when readiness is disputed. |
| `verified` | Verification route or accepted evidence has covered the claimed scope and named gaps. | `verify` owns the evidence claim; `triage`, `handoff`, `wiki`, or `dispatch` may consume it within their boundaries. |
| `blocked` | Required source truth, approval, evidence, topology, permission, or safe next action is missing. | Owning route reports the stop condition; `triage` may classify unblock path. |

## Skill State Contract

`accepted_pre_states` are the default legal inputs. Exceptions must be named in the transition gate table and surfaced in output when they matter.

| Skill | accepted_pre_states | produced_states |
|---|---|---|
| `to-prd` | `raw`, `grilled`, `prd_draft`, `blocked` | `grilled`, `prd_draft`, `prd_accepted`, `blocked` |
| `to-issues` | `prd_accepted`, `issue_ready` | `issue_ready`, `blocked` |
| `triage` | `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | `raw`, `prd_draft`, `issue_ready`, `implementation_ready`, `verified`, `blocked` |
| `write-plan` | `prd_accepted`, `issue_ready`, `implementation_ready` | `implementation_ready`, `blocked` |
| `prototype` | `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready` | `raw`, `grilled`, `prd_draft`, `blocked` |
| `implement` | `implementation_ready` | `implementation_ready`, `blocked` |
| `verify` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified` | `verified`, `blocked` |
| `handoff` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` |
| `dispatch` | `issue_ready`, `implementation_ready`, `verified` | `issue_ready`, `implementation_ready`, `blocked` |
| `wiki` | `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` |

## Route Transition Contract

`legal_next_routes` are possible next owners after the skill finishes. They are not automatic readiness claims. `forbidden_next_routes` name hard-negative transitions unless a documented gate exception applies.

| Skill | legal_next_routes | forbidden_next_routes |
|---|---|---|
| `to-prd` | `to-prd`, `to-issues`, `triage`, `prototype`, `verify`, `wiki` | `implement`, `dispatch` when output is only `raw`, `grilled`, or `prd_draft`; `handoff` that presents draft truth as accepted |
| `to-issues` | `triage`, `write-plan`, `implement`, `dispatch`, `verify`, `handoff`, `wiki` | `implement` or `dispatch` when slices are missing scope, ACs, blocker status, or verification expectation; `verify` that claims readiness without implementation/evidence |
| `triage` | `to-prd`, `to-issues`, `write-plan`, `implement`, `verify`, `handoff`, `dispatch`, `wiki` | Any route that contradicts the classified blocker/readiness state; `dispatch` from raw or draft state |
| `write-plan` | `implement`, `dispatch`, `verify`, `handoff`, `triage` | `to-issues` without accepted source change; `implement` when the plan records unresolved source truth or unsafe git topology |
| `prototype` | `to-prd`, `triage`, `write-plan`, `verify`, `handoff`, `wiki` | `implement` or `dispatch` from prototype-only truth; `verify` that treats mock/prototype observations as backend/API/source truth |
| `implement` | `verify`, `triage`, `handoff`, `dispatch`, `wiki` | Direct transition to `verified` state; `dispatch` as if implementation self-check were clean review or runtime evidence |
| `verify` | `triage`, `handoff`, `dispatch`, `wiki` | `implement` unless verify found scoped remediation; `dispatch` when readiness remains unverified or blocked |
| `handoff` | `to-prd`, `to-issues`, `triage`, `write-plan`, `implement`, `verify`, `dispatch`, `wiki` | Any route that upgrades handoff summary into source truth, clean review, independent verification, runtime evidence, release evidence, or UAT evidence |
| `dispatch` | `verify`, `triage`, `handoff`, `wiki` | `to-prd`/`to-issues` as a substitute for missing source acceptance; runtime execution claims without execution evidence |
| `wiki` | `to-prd`, `to-issues`, `triage`, `write-plan`, `implement`, `verify`, `dispatch`, `handoff` | Treating wiki synthesis as source/API truth, implementation readiness, verification, runtime evidence, release evidence, or UAT/customer readiness without cited authoritative sources |

## Transition Gates

| Transition | required_gate | required_evidence | stop_condition |
|---|---|---|---|
| `raw` -> `to-prd` | Clarification/PRD shaping gate | User intent or source context that needs requirement shaping. | `ask_clarification` when target reader, decision, known facts, or material unknowns are missing. |
| `raw` -> `to-issues` | PRD acceptance gate | Accepted PRD/spec/plan, named external task source, or explicit maintainer acceptance. | `require_prd_acceptance`; do not split raw intent into fake-precise issues. |
| `raw` -> `implement` | Explicit bypass gate plus implementation readiness gate | User explicitly bypasses PRD/spec shaping, source truth is adequate for the scoped change, acceptance criteria are clear, and git topology is safe. | `require_gate` or `require_prd_acceptance`; raw implementation is illegal without explicit bypass. |
| `prd_draft` -> `to-issues` | Acceptance/source-truth promotion gate | Maintainer/user acceptance or another canonical source that owns acceptance. | `require_prd_acceptance`; draft-only PRDs are not accepted truth. |
| `prd_draft` -> `implement` | Accepted source truth gate plus implementation readiness gate | Accepted source truth, scoped files/modules, acceptance criteria, verification expectation, and git topology decision. | `require_prd_acceptance` or `require_gate`; draft-only PRDs cannot drive implementation by default. |
| `prd_accepted` -> `to-issues` | Slice readiness gate | Acceptance criteria, scope, blocker status, and verification expectation sufficient to create vertical slices. | `require_artifact_promotion` or `ask_clarification` when source is conversation-only or underspecified. |
| `issue_ready` -> `write-plan` | Plan readiness gate | Accepted slice, dependency context, stop conditions, and verification checkpoints. | `ask_clarification` when implementation path or dependencies are materially unknown. |
| `issue_ready` -> `dispatch` | Accepted ready-for-agent dispatch gate | Accepted ready task or issue slice, ready-for-agent evidence, blocker status, verification expectation, and package-only dispatch inputs when needed. | `blocked`; dispatch cannot accept `raw`, `grilled`, or `prd_draft`. |
| `issue_ready` -> `implement` | Implementation readiness promotion gate | Source truth, scoped files/modules, ACs, verification expectation, and git topology decision must first promote the task to `implementation_ready`. | `require_gate`; route to `triage` when readiness is disputed. |
| `implementation_ready` -> `implement` | Git topology and risk gate | Current diff/status, branch/worktree decision, touched files, ACs, and focused verification plan. | `require_gate` for unsafe git topology, destructive action, remote write, data write, secrets/PII, or customer-visible risk. |
| `implement` -> `verified` | Verification route gate | A `verify` pass or explicitly scoped evidence report beginning with `Verification Scope`. | `require_gate`; implement may report self-check, but must not produce `verified` by default. |
| `implementation_ready` -> `verify` | Scope-first verification gate | In-scope claim, out-of-scope limits, source/test/runtime evidence expected, and gap handling. | `blocked` when required evidence is unavailable; do not claim readiness from code diff alone. |
| `verified` -> `triage` | Closeout/classification gate | Verification scope, covered/not covered evidence, remaining gaps, and closeout criteria. | `blocked` when verification scope or remaining risk is unclear. |
| `implementation_ready` -> `dispatch` | Accepted implementation-ready dispatch gate | Accepted ready task, readiness source, Goal Contract/runtime package inputs when needed, and verification expectation. | `blocked`; dispatch cannot accept `raw`, `grilled`, or `prd_draft`. |
| `verified` -> `dispatch` | Post-verification runtime routing gate | Verified scope plus accepted ready follow-up task or clean-review package that needs runtime routing. | `blocked` when dispatch would imply unproven runtime execution or clean review. |
| any -> `handoff` | Continuation-state gate | Current state, canonical sources, evidence, gaps, next owner, and do-not-assume boundaries. | `blocked` when handoff would copy raw logs/full PRDs/long diffs or upgrade evidence. |
| any -> `wiki` | Wiki source/citation gate | Explicit durable wiki maintenance intent, wiki root/storage mode, source citations, and evidence-layer labels. | `blocked` when wiki work would promote synthesis beyond cited source truth. |
| any -> `blocked` | Stop-condition gate | The missing source truth, approval, evidence, permission, topology, or safe next action. | `blocked`; name the owning unblock route or human decision. |
| any -> `direct` | Direct-answer gate | Small bounded answer or trivial edit with no artifact, git mutation, verification claim, remote mutation, or durable state impact. | `direct_answer`; route into workflow when the answer would make readiness/source-truth claims. |

## Eval Usage

Routing eval rows should map state expectations as follows:

| Scenario | expected_state_transition |
|---|---|
| No workflow state promotion expected | `none` |
| Clarification/grilling only | `clarify` |
| PRD/spec draft produced | `draft` |
| PRD/spec accepted or acceptance recognized | `accept` |
| Accepted source split into issues | `split` |
| Implementation plan produced | `plan` |
| Code/document implementation route expected | `implement` |
| Verification route expected | `verify` |
| Handoff/continuation package expected | `handoff` |
| Required gate blocks progress | `block` |
| Triage closeout/no further action expected | `close` |

`blocked` is not a route-list token. Use `blocked` as `expected_stop_condition`, verdict, or produced state; use `block` as `expected_state_transition`.

## Hard Negatives

- `raw` -> `implement` is illegal unless the user explicitly bypasses PRD/spec shaping and the implementation readiness gate passes.
- `prd_draft` -> `to-issues` or `implement` is illegal by default unless an accepted source truth or owner confirmation exists.
- `implement` must not produce `verified` by default; use `verify` or explicitly state that verified state is not being claimed.
- `dispatch` accepts only accepted ready tasks or verified follow-up packages. It may accept `issue_ready` only when ready-for-agent evidence and verification expectation are present. It must not accept `raw`, `grilled`, or `prd_draft` as executable dispatch input.
- `prototype`, `handoff`, and `wiki` may preserve or explain state, but must not upgrade mock observations, summaries, or synthesis into source truth, clean review, verification, runtime evidence, release evidence, or UAT/customer readiness.
