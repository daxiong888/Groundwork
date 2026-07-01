# Workflow State Machine

Target Reader: Groundwork public skills, eval authors, reviewers, and maintainers who need one canonical workflow transition contract.
Reader Action Needed: Validate accepted pre-state, produced state, legal next route, and stop gate.
Decision Supported: Whether a route transition is legal, blocked, explicitly bypassed, or recommendation-level.
Artifact Type: shared guardrail
Source of Truth: `skills/_shared/LIFECYCLE-PREFLIGHT.md`, public skill trigger contracts, routing reliability schema, and eval prompt fields.
Scope: Public route transitions for `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, `wiki`, plus direct/blocked behavior.
Out of Scope: Runtime adapter internal lifecycle, tracker mutation, automatic task CRUD, automatic state writes, release/UAT approval, or replacing source-specific skill contracts.
Evidence Level: Source-derived routing/eval contract; runtime behavior still requires installed-plugin/cache evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Core Rule

Workflow state is a transition contract, not a transcript. A route may act only when current requirement state satisfies its accepted pre-state gate or a named exception applies. `expected_state_transition` records expected transition action, not proof that a stronger produced state was verified.

## Canonical Tokens

Requirement states: `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked`.

Expected transitions: `none`, `clarify`, `draft`, `accept`, `split`, `plan`, `implement`, `verify`, `handoff`, `block`, `close`.

Route tokens: `direct`, `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, `wiki`.

Use `blocked` as verdict/produced state/stop condition; use `block` only as `expected_state_transition`.

## Requirement State

| State | Meaning | Owner |
| --- | --- | --- |
| `raw` | New, ambiguous, draft-only, or conversation-only intent without accepted source truth. | `to-prd`; `direct` only for tiny safe answers. |
| `grilled` | Clarified enough to draft but not accepted as product truth. | `to-prd` or `direct` for narrow answers. |
| `prd_draft` | Draft PRD/spec not accepted by maintainer, user, or canonical source. | `to-prd`; `verify` may review consistency only. |
| `prd_accepted` | Accepted PRD/spec/plan or named source truth is ready to slice/plan. | `to-issues`, `write-plan`, `triage`. |
| `issue_ready` | Vertical slice has scope, ACs, blocker status, and verification expectation. | `triage` final readiness; `write-plan` may plan. |
| `implementation_ready` | Source truth, scope, ACs, verification, and git topology are sufficient for implementation. | `implement`; `dispatch` for accepted ready tasks. |
| `verified` | Verification or accepted evidence covered declared scope and gaps. | `verify`; consumers keep scope boundary. |
| `blocked` | Source truth, approval, evidence, topology, permission, or safe next action is missing. | Owning route reports stop condition; `triage` may classify. |

## Skill State Contract

| Skill | accepted_pre_states | produced_states |
| --- | --- | --- |
| `to-prd` | `raw`, `grilled`, `prd_draft`, `blocked` | `grilled`, `prd_draft`, `prd_accepted`, `blocked` |
| `to-issues` | `prd_accepted`, `issue_ready` | `issue_ready`, `blocked` |
| `triage` | any requirement state | `raw`, `prd_draft`, `issue_ready`, `implementation_ready`, `verified`, `blocked` |
| `write-plan` | `prd_accepted`, `issue_ready`, `implementation_ready` | `implementation_ready`, `blocked` |
| `prototype` | `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready` | `raw`, `grilled`, `prd_draft`, `blocked` |
| `implement` | `implementation_ready` | `implementation_ready`, `blocked` |
| `verify` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified` | `verified`, `blocked` |
| `handoff` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | same state or `blocked` |
| `dispatch` | `issue_ready`, `implementation_ready`, `verified` | `issue_ready`, `implementation_ready`, `blocked` |
| `wiki` | `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | same state or `blocked` |

## Transition Gates

| Transition | Required Gate | Stop Condition |
| --- | --- | --- |
| `raw` -> `to-prd` | User intent/source context needs requirement shaping. | Ask clarification when target reader, decision, facts, or material unknowns are missing. |
| `raw` -> `to-issues` | Accepted PRD/spec/plan, named external task source, or maintainer acceptance. | `require_prd_acceptance`; do not fake precision. |
| `raw` -> `implement` | Explicit bypass plus source truth, clear ACs, scoped change, safe git topology. | `require_gate` or PRD acceptance. |
| `prd_draft` -> `to-issues`/`implement` | Accepted source truth or owner confirmation. | `require_prd_acceptance`; draft-only cannot drive downstream work. |
| `prd_accepted` -> `to-issues` | ACs, scope, blocker status, and verification expectation. | Artifact promotion or clarification when source is conversation-only/underspecified. |
| `issue_ready` -> `write-plan` | Accepted slice, dependencies, stop conditions, verification checkpoints. | Clarify materially unknown implementation/dependency path. |
| `issue_ready` -> `dispatch` | Accepted ready-for-agent evidence, blocker status, verification expectation, package inputs. | `blocked`; dispatch cannot accept raw/grilled/prd_draft. |
| `issue_ready` -> `implement` | Source truth, scoped files/modules, ACs, verification, git topology promote it to `implementation_ready`. | `require_gate`; route to `triage` if disputed. |
| `implementation_ready` -> `implement` | Diff/status, branch/worktree decision, touched files, ACs, verification plan. | Gate unsafe topology, destructive/remote/data write, secrets/PII, customer risk. |
| `implement` -> `verified` | `verify` pass or scoped evidence report beginning with `Verification Scope`. | Implement self-check is not verification by default. |
| `implementation_ready` -> `verify` | In-scope claim, out-of-scope limits, expected evidence, gap handling. | Block when required evidence is unavailable. |
| `verified` -> `triage` | Scope, covered/not-covered evidence, remaining gaps, closeout criteria. | Block when scope/risk is unclear. |
| `implementation_ready`/`verified` -> `dispatch` | Accepted ready task or verified follow-up package needing package-only routing. | Block unproven runtime execution or clean-review implications. |
| any -> `handoff` | Current state, sources, evidence, gaps, next owner, do-not-assume boundaries. | Block long raw copies or evidence upgrades. |
| any -> `wiki` | Explicit wiki maintenance intent, storage mode, citations, evidence layers. | Block synthesis promotion beyond cited source truth. |
| any -> `direct` | Small bounded answer/trivial edit with no artifact, git mutation, verification claim, remote mutation, or durable state impact. | Route into workflow when readiness/source-truth claims appear. |

## Next Route Negatives

- `to-prd` output that remains `raw`, `grilled`, or `prd_draft` must not route to `implement` or `dispatch`.
- `to-issues` slices missing scope, ACs, blockers, or verification expectation must not route to implementation/dispatch.
- `implement` must not produce verified state; use `verify`.
- `dispatch` accepts only accepted ready tasks or verified follow-up packages and must not claim runtime execution.
- `prototype`, `handoff`, and `wiki` may preserve/explain state but must not upgrade mock observations, summaries, or synthesis into source truth, clean review, verification, runtime, release, or UAT evidence.

## Eval Usage

Map rows to canonical expected transition tokens:

| Scenario | expected_state_transition |
| --- | --- |
| No promotion | `none` |
| Clarification/grilling | `clarify` |
| PRD/spec draft | `draft` |
| Acceptance recognized | `accept` |
| Accepted source split | `split` |
| Implementation plan | `plan` |
| Code/doc implementation route | `implement` |
| Verification route | `verify` |
| Continuation package | `handoff` |
| Gate blocks progress | `block` |
| Closeout/no further action | `close` |
