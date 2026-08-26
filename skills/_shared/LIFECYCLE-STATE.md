# Lifecycle State Contract

Target Reader: Groundwork skills that need resumable workstream state.
Reader Action Needed: decide when to create, update, reference, or ignore lifecycle artifacts.
Decision Supported: whether a task needs workstream-scoped `STATE.md` or optional `ROADMAP.md` without becoming project management.
Scope: lifecycle artifact paths, triggers, fields, stale-state handling, multi-session behavior, and skill boundaries.
Out of Scope: public skills, CLI/hooks/task CRUD, project task DB, tracker integration, `.planning`, `.gsd`, and automatic mutation.
Evidence Level: grounded in `docs/prd-v0.3-lifecycle-state.md` and public skill contracts.

## Core Rule

Lifecycle state is opt-in, workstream-scoped recovery state for resuming decisions, evidence, gaps, risks, and next action. Do not use it for one-off work, direct answers, or global project tracking.

Default paths:

```text
artifacts/<workstream-slug>/STATE.md
artifacts/<workstream-slug>/ROADMAP.md
```

Forbidden defaults: `STATE.md`, `PROJECT-STATE.md`, `artifacts/STATE.md`, `.groundwork/STATE.md`, `.groundwork/tasks/<task-id>/STATE.md`, `.planning/*`, `.gsd/*`.

`.groundwork/runs/`, `.groundwork/harness/`, and `.groundwork/tmp/` are runtime scratch, not lifecycle artifact locations.

## Workstream Slug

Use a stable lowercase kebab-case slug for one independently resumable workstream. Prefer existing issue/PRD/feature/release/bug-fix slugs. Do not use spaces, slashes, traversal, shell metacharacters, or global names such as `project`, `all`, `global`, `current`.

## `STATE.md`

```md
# STATE.md

Target Reader:
Reader Action Needed:
Decision Supported:
Scope:
Out of Scope:
Evidence Level:
Last Updated:
Canonical Sources:

Current Workflow Mode:
Current Milestone:
Last Confirmed Decision:
Active Scope:
Verified Evidence:
Unverified Claims:
Open Risks:
Current Gap Closure:
Next Skill:
Stop Condition:
```

Field rules:

- `Last Updated`: exact timestamp with timezone, preferably ISO 8601.
- `Canonical Sources`: true fact sources; source truth beats lifecycle state.
- `Current Workflow Mode`: Groundwork route/state, not GSD phase. Allowed: `direct`, `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `dispatch`, `wiki`, `paused`, `blocked`, `done`.
- `paused` and `done` are lifecycle states, not preflight suggested routes.
- `Current Milestone`: `none` unless true multi-milestone work.
- `Current Gap Closure`: unresolved verify/QA gap or `none`.
- `Next Skill`: next Groundwork skill or direct action.
- `Stop Condition`: where the next session stops.

Keep `STATE.md` under 100 lines; body fields default to 1-3 lines. Cite artifacts/checks/commands instead of copying logs. Keep only current facts and close/replace stale gaps after re-verify.

Never include full chat history, full PRDs/issues/plans/diffs/logs, diaries, all-task lists, project-wide task registries, secrets, credentials, PII, sensitive rows, unredacted screenshots/payloads, private reasoning, or guesses as facts.

## `ROADMAP.md`

```md
# ROADMAP.md

Target Reader:
Reader Action Needed:
Decision Supported:
Scope:
Out of Scope:
Evidence Level:
Last Updated:
Canonical Sources:

Initiative:
Milestones:
Current Milestone:
Dependencies:
Workstreams:
Decision Gates:
Verification Gates:
Release / UAT Gates:
Stop Conditions:
```

Create/update `ROADMAP.md` only for multiple milestones, sequenced workstreams, UAT/SIT/release stage gates, explicit roadmap requests, or progression too large for one `STATE.md`. It is not a task entrypoint, project board, task DB, GSD runtime, or duplicate `STATE.md`.

## Trigger Policy

Create, update, or recommend `STATE.md` only when a hard condition is true:

1. User asks to pause, resume, switch sessions, save state, or continue later.
2. Cross-session recovery cost exceeds writing state.
3. Verify gap / QA failure / fix -> re-verify chain remains open.
4. UAT/SIT/release state must be reused.
5. Multi-artifact workstream will continue.
6. Multi-milestone work needs current milestone and next gate.
7. Human decision is pending and next session needs evidence/options/risks.

Do not use `STATE.md` for small edits, one-off explanations, rewrites, simple title changes, low-risk answers, one-shot verification with no gap, existing issue/PR that owns state, or sufficient handoff. Weak signals like artifact count, complexity, tidiness, framework habit, or GSD mimicry are not enough.

## Skill Boundaries

- `handoff`: check/reference existing state for cross-session transfer; recommend state only when threshold is met; never copy full state or become long-term owner.
- `verify`: update/recommend state for surviving verification gaps; after re-verify, close/update `Current Gap Closure`; never put lifecycle notes before `Verification Scope`.
- `triage`: decide if state is justified; keep small tasks direct; do not equate `ready-for-agent` with needing state; do not create task DB.
- `write-plan`: read existing state/roadmap for multi-stage work; check canonical sources; recommend roadmap only for true multi-milestone work.
- `to-prd`, `to-issues`, `prototype`, `implement`: no lifecycle-specific behavior unless durable artifact policy already applies.

## Multi-Session Rules

Separate workstreams can have separate state files; do not create project-global lifecycle state by default.

When sessions share a workstream: read `STATE.md`, check canonical sources, mark stale conflicts, update `Last Updated` on changes, close gaps only with re-verify evidence, and use git/PR/issue/branch/worktree coordination for real concurrency. Groundwork does not provide locks.

Explicit project-global summaries stay conversation-only by default, or become non-lifecycle artifacts with target reader, action, scope, and evidence level.

## Validation

Behavior evidence should cover: small tasks reject lifecycle state; pause/resume references state; verify gaps recover; re-verify closes stale gaps; roadmap only for multi-milestone contexts; `.planning`, `.gsd`, and project-global lifecycle state are rejected; handoff references state without owning it; state never overrides canonical source truth.
