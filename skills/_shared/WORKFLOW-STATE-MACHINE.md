# Workflow State Machine

Target Reader: public skills, eval authors, reviewers, and maintainers needing one route-transition contract.
Reader Action Needed: validate accepted pre-state, produced state, legal next route, and stop gate.
Decision Supported: whether a transition is legal, blocked, explicitly bypassed, or recommendation-level.
Artifact Type: shared guardrail.
Source of Truth: `scripts/codex-hooks/groundwork_route_registry.json`; this document, public skill trigger contracts, and eval prompt fields must validate against it.
Scope: transitions for `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, `wiki`, plus direct/blocked behavior.
Out of Scope: runtime adapter lifecycle, tracker mutation, task CRUD, automatic state writes, release/UAT approval, or replacing skill-specific contracts.
Evidence Level: source-derived routing/eval contract; runtime behavior requires installed-plugin/cache evidence.

## Core Rule

Workflow state is a transition contract, not a transcript. A route may act only when the current requirement state satisfies its accepted pre-state gate or a named exception applies. `expected_state_transition` records expected transition action, not proof that a stronger produced state was verified.

Tokens:

- Requirement states: `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked`.
- Expected transitions: `none`, `clarify`, `draft`, `accept`, `split`, `plan`, `implement`, `verify`, `handoff`, `block`, `close`.
- Route tokens: `direct`, `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, `wiki`.
- Use `blocked` as verdict/produced state/stop condition; use `block` only as `expected_state_transition`.

## Requirement States

| State | Meaning | Owner |
| --- | --- | --- |
| `raw` | ambiguous/draft/conversation-only intent without accepted source truth | `to-prd`; `direct` for tiny safe answers |
| `grilled` | clarified enough to draft, not accepted as product truth | `to-prd` or narrow `direct` |
| `prd_draft` | draft PRD/spec not accepted by owner/source | `to-prd`; `verify` consistency only |
| `prd_accepted` | accepted PRD/spec/plan or named source truth ready to slice/plan | `to-issues`, `write-plan`, `triage` |
| `issue_ready` | vertical slice has scope, ACs, blocker status, verification expectation | `triage`; `write-plan` may plan |
| `implementation_ready` | source truth, scope, ACs, verification, git topology are enough | `implement`; `dispatch` for accepted ready tasks |
| `verified` | verification/evidence covered declared scope and gaps | `verify`; consumers keep scope boundary |
| `blocked` | source truth, approval, evidence, topology, permission, or safe action missing | owning route stops; `triage` may classify |

## Skill State Contract

| Skill | accepted_pre_states | produced_states |
| --- | --- | --- |
| `to-prd` | `raw`, `grilled`, `prd_draft`, `blocked` | `grilled`, `prd_draft`, `prd_accepted`, `blocked` |
| `to-issues` | `prd_accepted`, `issue_ready` | `issue_ready`, `blocked` |
| `triage` | any | `raw`, `prd_draft`, `issue_ready`, `implementation_ready`, `verified`, `blocked` |
| `write-plan` | `prd_accepted`, `issue_ready`, `implementation_ready` | `implementation_ready`, `blocked` |
| `prototype` | `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready` | `raw`, `grilled`, `prd_draft`, `blocked` |
| `implement` | `implementation_ready` | `implementation_ready`, `blocked` |
| `verify` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified` | `verified`, `blocked` |
| `handoff` | `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | same or `blocked` |
| `dispatch` | `issue_ready`, `implementation_ready`, `verified` | `issue_ready`, `implementation_ready`, `blocked` |
| `wiki` | `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | same or `blocked` |

## Transition Gates

| Transition | Required Gate | Stop Condition |
| --- | --- | --- |
| `raw` -> `to-prd` | user intent/source needs shaping | ask when target reader, decision, facts, or material unknowns are missing |
| `raw` -> `to-issues` | accepted PRD/spec/plan, named accepted task source, or maintainer acceptance | `require_prd_acceptance` |
| `raw` -> `implement` | explicit bypass plus source truth, clear ACs, scoped change, safe topology | `require_gate` or PRD acceptance |
| `prd_draft` -> downstream | accepted source truth or owner confirmation | `require_prd_acceptance` |
| `prd_accepted` -> `to-issues` | ACs, scope, blockers, verification expectation | artifact promotion or clarification |
| `issue_ready` -> `write-plan` | accepted slice, dependencies, stops, verification checkpoints | clarify material dependency/path unknowns |
| `issue_ready` -> `dispatch` | ready-for-agent evidence, blockers, verification expectation, package inputs | `blocked`; dispatch cannot accept raw/grilled/draft |
| `issue_ready` -> `implement` | source truth, scoped files/modules, ACs, verification, topology promote it | `require_gate`; route to `triage` if disputed |
| `implementation_ready` -> `implement` | diff/status, branch/worktree decision, touched files, ACs, verification plan | gate unsafe topology, destructive/remote/data writes, secrets/PII, customer risk |
| `implement` -> `verified` | `verify` pass or scoped `Verification Scope` report | implement self-check is not verification |
| `implementation_ready` -> `verify` | in-scope claim, out-of-scope limits, expected evidence, gap handling | block unavailable required evidence |
| `verified` -> `triage` | scope, covered/not-covered evidence, gaps, closeout criteria | block unclear scope/risk |
| `implementation_ready`/`verified` -> `dispatch` | accepted ready task or verified follow-up needing package-only routing | block runtime/clean-review overclaims |
| any -> `handoff` | state, sources, evidence, gaps, next owner, do-not-assume boundaries | block long raw copies/evidence upgrades |
| any -> `wiki` | explicit wiki maintenance, storage mode, citations, evidence layers | block synthesis promotion |
| any -> `direct` | small bounded answer, trivial edit, or ordinary audit performed in the current context without artifact/git/verification/remote/durable-state impact | route when readiness/source-truth claims or explicit route/package/fan-out/delegation requests appear |

## Next Route Negatives

- `to-prd` output that remains `raw`, `grilled`, or `prd_draft` must not route to `implement` or `dispatch`.
- `to-issues` slices missing scope, ACs, blockers, or verification expectation must not route to implementation/dispatch.
- `implement` must not produce verified state; use `verify`.
- `dispatch` accepts only accepted ready tasks or verified follow-up packages and must not claim runtime execution.
- `prototype`, `handoff`, and `wiki` may preserve/explain state but must not upgrade mock observations, summaries, or synthesis into source truth, clean review, verification, runtime, release, or UAT evidence.

## Eval Usage

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
