# Lifecycle Preflight Contract

Target Reader: Groundwork skills deciding the next action before file writes, artifacts, git mutation, or verification.
Reader Action Needed: Classify request, choose workflow mode, and apply the right gate before acting.
Decision Supported: Whether the next step is direct work, PRD/grill, issue split, implementation, verification, handoff, artifact promotion, git topology handling, or stop.
Artifact Type: shared guardrail
Source of Truth: v0.3 lifecycle-state contract, task-state spine, routing reliability fixtures, mode-harness policy, and `skills/_shared/WORKFLOW-STATE-MACHINE.md`.
Scope: Transient pre-action routing, source-of-truth checks, locale inheritance, artifact promotion, git topology, verification strategy, and lifecycle-state promotion.
Out of Scope: Public skills, task CRUD, tracker APIs, project task databases, `.planning`, `.gsd`, automatic state mutation, automatic commits, or replacing `artifacts/<workstream-slug>/STATE.md`.
Evidence Level: Derived from v0.3 lifecycle-state contract, task-state spine, and Groundwork regression evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Core Rule

Lifecycle preflight is transient decision state, computed before action and not written by default. `STATE.md` is durable recovery state and is written only when lifecycle-state thresholds are met.

```text
Workflow Taxonomy / Task-State Spine -> candidate workflow
Lifecycle Preflight -> safe/ready decision
Execution Gates -> stop irreversible or unsafe actions
Lifecycle State -> persist recoverable workstream facts only when thresholds are met
```

Promote only cross-session recovery facts: source truth, current mode, scope, verified evidence, risks, gap closure, next skill, and stop condition.

## Trigger Policy

Run preflight before non-trivial actions involving new requirements, issue/task splitting, implementation/delivery/commit/push/PR/closeout, verification/UAT/release/customer-safe evidence, handoff/resume, durable artifacts, git/remote/data/customer/runtime/shared-file mutation, locale conflicts, host-mode ambiguity, or possible `STATE.md`/`ROADMAP.md` need.

Skip for small direct answers, trivial rewrites, simple explanations, and one-off edits with no artifact, git action, verification claim, or remote mutation.

## Preflight Snapshot

```md
# Lifecycle Preflight
Intent:
Suggested Workflow Mode:
Host Mode:
Locale:
Source of Truth:
Requirement State:
Artifact Promotion:
Execution Topology:
Risk Gate:
Verification Strategy:
Lifecycle State:
Stop Condition:
```

Use `WORKFLOW-STATE-MACHINE.md` for transition legality and `expected_state_transition` tokens; this file only computes transient preflight fields.

## Field Rules

| Field | Allowed Values | Rule |
| --- | --- | --- |
| `Intent` | `direct`, `new_requirement`, `clarify`, `issue_split`, `plan`, `prototype`, `implement`, `verify`, `handoff`, `delivery`, `remote_mutation` | Strong new requirements default to `to-prd` / grill-before-write unless explicitly bypassed. |
| `Suggested Workflow Mode` | `direct`, `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, `wiki`, `blocked` | Routes only; durable terminal states belong to lifecycle state. |
| `Host Mode` | `plan_mode`, `read_only`, `write_capable`, `chat_only`, `unknown` | Use `MODE-HARNESS.md` when host mode affects durable writes, runtime execution, reviewer closeout, or artifact promotion. |
| `Locale` | session locale | Use `LOCALE-GUARD.md`; skill-file language does not override user-visible locale. |
| `Source of Truth` | `conversation`, `accepted_prd`, `local_artifact`, `external_issue`, `pull_request`, `source_code`, `test_evidence`, `runtime_evidence`, `state_md`, `mixed`, `unknown` | Source truth beats lifecycle state; stale state must not override code/tests/runtime/PRD/accepted issue/user confirmation. |
| `Requirement State` | `raw`, `grilled`, `prd_draft`, `prd_accepted`, `issue_ready`, `implementation_ready`, `verified`, `blocked` | Raw cannot split/implement without explicit bypass; draft is not accepted; issue/implementation readiness require scope, ACs, source, verification, and topology as applicable. |
| `Artifact Promotion` | `none`, `recommended`, `required`, `external_source_of_truth` | Use `ARTIFACT-PROMOTION.md` before durable downstream issue/implementation/verification/UAT/release/PR/handoff use. |
| `Execution Topology` | `read_only`, `conversation_only`, `artifact_only`, `current_branch_ok`, `branch_required`, `worktree_required`, `blocked` | Use `GIT-TOPOLOGY-GATE.md` for implementation, delivery, commit, push, PR, or issue closeout. |
| `Risk Gate` | `none`, `git_write`, `remote_write`, `destructive`, `customer_visible`, `data_write`, `secrets_or_pii`, `blocked` | If not `none`, surface target, effect, recovery, and approval need before action. |
| `Verification Strategy` | `none`, `smoke`, `scoped`, `full`, `serial`, `bounded_parallel`, `blocked` | Scope-first; parallel scheduling is not evidence. |
| `Lifecycle State` | `not_needed`, `read_existing`, `recommend_update`, `must_update_before_handoff`, `stale` | Use only for pause/resume, recovery, gap closure, UAT/release reuse, multi-artifact/milestone work, or pending human decision. |
| `Stop Condition` | concrete blocker | Missing PRD/source truth/artifact promotion/safe topology/remote scope/verification evidence or stale required state. |

## Mode Rules

These interpret the state machine; they do not replace it.

- `to-prd`: new requirement starts with grill-before-write; do not implement before `prd_accepted` or explicit bypass.
- `to-issues`: require `prd_accepted`, `issue_ready`, or external accepted task source; do not split raw requirements.
- `triage`: classify readiness, blocker, source state, lifecycle need, and next owner only.
- `write-plan`: accepted-enough scope only; produce sequence/checkpoints, not issue split/runtime dispatch/implementation.
- `prototype`: throwaway question-answering artifact; do not promote mock/prototype fields into backend/API truth.
- `implement`: run git topology gate before writes; PR-bound work on `main`/`master`/`trunk`, empty branch, or detached HEAD needs branch/worktree decision.
- `verify`: final report begins with `Verification Scope`; lifecycle updates come after scope body.
- `handoff`: reference existing state when present; create/update only when thresholds are met.
- `dispatch`: accepted ready tasks only; package-only routing, no execution/validation/clean-review claims without evidence.
- `wiki`: durable wiki maintenance only; wiki synthesis is not source truth, implementation authority, verification, runtime, release, or UAT/customer readiness.

## Forbidden Behavior

Do not treat preflight as a public skill, write snapshots by default, use `STATE.md` as PRD/issue/plan/diff/log/project board/chat transcript, let English templates override Chinese sessions, start PR-bound implementation on unsafe topology without decision, or push `main`/close remote issues as a substitute for missed PR flow.
