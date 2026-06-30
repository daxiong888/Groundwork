# Lifecycle Preflight Contract

Target Reader: Groundwork skills that need to decide the next action before writing files, creating artifacts, mutating git state, or running verification.
Reader Action Needed: Classify the current request, choose the workflow mode, and apply the right gate before acting.
Decision Supported: Whether the next step is direct work, PRD/grill, issue splitting, implementation, verification, handoff, artifact promotion, git topology handling, or a stop condition.
Artifact Type: shared guardrail
Source of Truth: v0.3 lifecycle-state contract, task-state spine, routing reliability fixtures, shared mode-harness policy, and `skills/_shared/WORKFLOW-STATE-MACHINE.md`.
Scope: Transient pre-action routing, source-of-truth checks, locale inheritance, artifact promotion checks, git topology checks, verification strategy, and lifecycle-state promotion decisions.
Out of Scope: Public skills, task CRUD, tracker APIs, project task databases, `.planning`, `.gsd`, automatic state mutation, automatic commits, and replacing `artifacts/<workstream-slug>/STATE.md`.
Evidence Level: Derived from the v0.3 lifecycle-state contract, the task-state spine, and regression evidence from real Groundwork sessions.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.
Related Issues: #28, #29, #30, #31, #33.

## Core Rule

Lifecycle preflight is transient runtime decision state. It is computed before action and is not written by default.

`STATE.md` is durable recovery state. It is written only when lifecycle-state thresholds are met.

Preflight decides whether Groundwork may proceed. Lifecycle state records only the recoverable facts that a future session needs.

## Relationship to Lifecycle State

Use this split:

```text
Workflow Taxonomy / Task-State Spine
  -> choose the candidate workflow mode
Lifecycle Preflight
  -> decide whether the candidate action is safe and ready
Execution Gates
  -> stop irreversible or unsafe actions
Lifecycle State
  -> persist recoverable workstream facts only when thresholds are met
```

Do not copy the full preflight snapshot into `STATE.md`. Promote only fields that affect cross-session recovery, such as source truth, current workflow mode, active scope, verified evidence, open risks, current gap closure, next skill, and stop condition.

## Trigger Policy

Run lifecycle preflight before any non-trivial Groundwork action when at least one is true:

- the user introduces a new requirement, feature, workflow, version enhancement, or product decision;
- the user asks to split work into issues or tasks;
- the user asks for implementation, bug fixing, delivery, commit, push, PR, or issue closeout;
- the user asks for verification, UAT/SIT readiness, release readiness, or customer-safe evidence;
- the user asks for handoff, resume, pause, or cross-session continuation;
- the work would create or promote a durable artifact;
- the work may mutate git, a remote tracker, data, customer-visible state, runtime state, or shared project files;
- the prompt language could conflict with skill-template language;
- the host mode may be Plan Mode, read-only, chat-only, write-capable, or unknown and could affect durable writes, runtime claims, or remote mutation;
- the task might need `STATE.md` or `ROADMAP.md` under the lifecycle-state thresholds.

Skip preflight for small direct answers, trivial rewrites, simple explanations, and one-off edits where no artifact, git action, verification claim, or remote mutation is involved.

## Preflight Snapshot

Use this transient shape. It may be reasoned about silently, but high-risk fields should be surfaced before action.

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

## Workflow State Machine

Use `skills/_shared/WORKFLOW-STATE-MACHINE.md` as the canonical transition contract for:

- Requirement State meaning and owner;
- each public skill's accepted pre-states and produced states;
- each public skill's legal and forbidden next routes;
- transition gates, required evidence, stop conditions, and `expected_state_transition` tokens.

This file keeps the lightweight pre-action snapshot and mode interpretation. When the state machine and this explanatory layer appear to conflict, follow `WORKFLOW-STATE-MACHINE.md` for transition legality and use this file only to compute the transient preflight fields.

## Field Rules

### `Intent`

Allowed values:

```text
direct
new_requirement
clarify
issue_split
plan
prototype
implement
verify
handoff
delivery
remote_mutation
```

Strong `new_requirement` triggers include:

```text
新需求
版本增强
产品增强
v0.3.x 强化
新增能力
设计一个流程
这个产品应该支持
new requirement
feature request
product enhancement
```

A strong `new_requirement` defaults to `to-prd` / grill-before-write unless the user explicitly says to bypass PRD and implement directly.

### `Suggested Workflow Mode`

Allowed values match Groundwork routes:

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
blocked
```

Route examples:

- raw product or workflow request -> `to-prd`;
- accepted PRD or task split request -> `to-issues`, after source-of-truth check;
- readiness, blocker, state transition, or closeout -> `triage`;
- multi-step implementation design -> `write-plan`;
- throwaway question-answering UI or logic artifact -> `prototype`;
- scoped code change -> `implement`, after git topology gate;
- tests/runtime/UAT/release/customer-safe evidence -> `verify`;
- pause/resume/cross-session transfer -> `handoff`;
- accepted ready-task runtime routing or package-only execution matrix -> `dispatch`;
- durable project wiki query, ingest, audit, repair, or update request -> `wiki`.

Preflight suggested modes are actionable routes plus `blocked`. Durable terminal or holding states such as `paused` and `done` belong to lifecycle state, not to preflight suggested routes.

### `Host Mode`

Use `skills/_shared/MODE-HARNESS.md` when host mode affects trust, durable writes, runtime execution, reviewer closeout, or artifact promotion.

Allowed values:

```text
plan_mode
read_only
write_capable
chat_only
unknown
```

Rules:

- Plan Mode can shape route, scope, evidence, artifact boundary, conversation drafts, and highest-impact questions, but must not write durable files or claim write completion.
- Read-only and chat-only contexts may produce reports, packages, route decisions, and recommendations, but must not claim file edits, runtime execution, git mutation, or remote mutation.
- Write-capable context still requires source truth, artifact promotion, git topology, and risk gates before edits.
- Unknown host mode takes the safer branch for durable writes and runtime claims.

### `Locale`

Use `skills/_shared/LOCALE-GUARD.md`.

The session locale controls user-visible prose, headings, issue titles, issue bodies, and artifact prose. Skill-file language and examples do not override it.

### `Source of Truth`

Allowed values:

```text
conversation
accepted_prd
local_artifact
external_issue
pull_request
source_code
test_evidence
runtime_evidence
state_md
mixed
unknown
```

Source truth beats lifecycle state. If `STATE.md` conflicts with code, tests, runtime evidence, PRD, accepted issue, or user-confirmed decision, mark state as stale and follow the canonical source.

### `Requirement State`

Allowed values:

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

Rules:

- `raw` cannot proceed directly to `to-issues` or `implement` unless the user explicitly requests a bypass.
- `prd_draft` cannot be treated as accepted unless the user confirms it or another canonical source owns the decision.
- `issue_ready` requires clear scope, acceptance criteria, missing-field status, and verification expectation.
- `implementation_ready` requires source truth, scoped files or modules, acceptance criteria, and a git topology decision.
- See `skills/_shared/WORKFLOW-STATE-MACHINE.md` for state owners, accepted pre-states, produced states, next routes, forbidden routes, and eval transition tokens.

### `Artifact Promotion`

Allowed values:

```text
none
recommended
required
external_source_of_truth
```

Use `skills/_shared/ARTIFACT-PROMOTION.md` when conversation output is about to become a durable source for issue splitting, implementation, verification, UAT, release, PR, or handoff.

### `Execution Topology`

Allowed values:

```text
read_only
conversation_only
artifact_only
current_branch_ok
branch_required
worktree_required
blocked
```

Use `skills/_shared/GIT-TOPOLOGY-GATE.md` when implementation, delivery, commit, push, PR, or issue closeout is in scope.

### `Risk Gate`

Allowed values:

```text
none
git_write
remote_write
destructive
customer_visible
data_write
secrets_or_pii
blocked
```

If the gate is not `none`, surface the risk before action with target, expected effect, rollback or recovery path, and explicit approval need.

### `Verification Strategy`

Allowed values:

```text
none
smoke
scoped
full
serial
bounded_parallel
blocked
```

Verification must stay scope-first. Parallel execution is a scheduling decision, not an evidence shortcut.

### `Lifecycle State`

Allowed values:

```text
not_needed
read_existing
recommend_update
must_update_before_handoff
stale
```

Do not force every issue into `STATE.md`. Use lifecycle state only when the v0.3 threshold is met: pause/resume, cross-session recovery, open gap closure, UAT/release reuse, multi-artifact continuation, multi-milestone work, or pending human decision.

### `Stop Condition`

Use a concrete stop condition when any of these is true:

- PRD acceptance is missing;
- source truth is unknown or conflicting;
- artifact promotion is required but not possible;
- current git topology is unsafe;
- remote mutation scope is unclear;
- verification evidence is unavailable;
- lifecycle state is stale and must not be trusted.

## Required Behavior by Mode

These mode rules are an interpretation layer over `skills/_shared/WORKFLOW-STATE-MACHINE.md`. They explain how to apply the state machine during preflight; they do not replace the canonical state transition tables.

### `to-prd`

If `Intent = new_requirement`, start with grill-before-write. Do not implement before the requirement state is at least `prd_accepted` or explicitly bypassed.

### `to-issues`

If `Requirement State` is not `prd_accepted`, `issue_ready`, or owned by an external task source, stop and request acceptance or source-of-truth promotion. Do not split raw requirements into fake-precise issues.

### `triage`

Classify readiness, blockers, source state, lifecycle-state need, and next owner. Do not turn a readiness decision into implementation, verification, or remote closeout without the owning route and evidence gate.

### `write-plan`

Use only after scope is accepted enough to plan implementation. Produce dependencies, sequence, stop conditions, and verification checkpoints; do not invent PRD truth, split issues, dispatch runtimes, or implement the plan.

### `prototype`

Keep the output throwaway and question-answering. State the artifact boundary clearly, and do not promote prototype fields, UI observations, or mock data into backend/API contract truth without source evidence.

### `implement`

Before writing files, run git topology gate. If current branch is `main` / `master` / `trunk`, the branch name is empty, or `HEAD` is detached and the work is PR-bound, choose a branch or worktree first.

### `verify`

Begin the final report with `Verification Scope`. If a gap must survive the session, recommend or update lifecycle state after the verification body, not before scope.

### `handoff`

Reference existing `STATE.md` when present. Recommend creating or updating state only when lifecycle thresholds are met. Do not turn handoff into a full lifecycle database.

### `dispatch`

Route only accepted, ready tasks to runtime/package choices. Dispatch may generate package-only routing, execution matrixes, and Result Package expectations; it is not an executor and must not claim runtime execution, validation, or clean review happened.

### `wiki`

Use for durable project wiki query, ingest, audit, repair, or update work. Wiki pages can orient work and preserve project knowledge, but wiki synthesis must not become source truth, implementation authority, verification evidence, runtime evidence, release evidence, or UAT/customer readiness without cited authoritative sources.

## Forbidden Behavior

- Do not treat preflight as a public skill.
- Do not write preflight snapshots by default.
- Do not use `STATE.md` as a full PRD, full issue body, full plan, full diff, full log, project board, or chat transcript.
- Do not let English skill templates override a Chinese session.
- Do not start PR-bound implementation on `main` / `master` / `trunk`, an empty branch name, or detached `HEAD` without topology decision.
- Do not push `main` or close remote issues as a substitute for a missed PR flow.
