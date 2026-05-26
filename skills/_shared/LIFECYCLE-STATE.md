# Lifecycle State Contract

Target Reader: Groundwork skills that need resumable workstream state.
Reader Action Needed: Decide when to create, update, reference, or ignore lifecycle artifacts.
Decision Supported: Whether a task needs workstream-scoped `STATE.md` or optional `ROADMAP.md` without becoming project management.
Scope: Lifecycle artifact paths, triggers, field rules, stale-state handling, multi-session behavior, and skill boundaries.
Out of Scope: Public skills, CLI, hooks, task CRUD, project task database, tracker integration, `.planning`, `.gsd`, and automatic state mutation.
Evidence Level: Grounded in `docs/prd-v0.3-lifecycle-state.md` and the existing Groundwork artifact, handoff, verify, triage, and write-plan contracts.

## Core Rule

Lifecycle state is opt-in, workstream-scoped recovery state.

Use it when a future session must resume a specific workstream without rediscovering decisions, evidence, gaps, risks, and next action. Do not use it for small one-off work, ordinary direct answers, or global project tracking.

Default paths:

```text
artifacts/<workstream-slug>/STATE.md
artifacts/<workstream-slug>/ROADMAP.md
```

Forbidden default paths:

```text
STATE.md
PROJECT-STATE.md
artifacts/STATE.md
.groundwork/STATE.md
.groundwork/tasks/<task-id>/STATE.md
.planning/*
.gsd/*
```

`.groundwork/runs/`, `.groundwork/harness/`, and `.groundwork/tmp/` remain runtime scratch. They are not lifecycle artifact locations.

## Workstream Slug

`<workstream-slug>` is a stable lowercase kebab-case identifier for one independently resumable workstream.

Rules:

- use short business or engineering words, such as `admin-user-filter` or `release-v0-3`;
- do not use spaces, slashes, backslashes, path traversal, shell metacharacters, or project-global names such as `project`, `all`, `global`, or `current`;
- prefer an existing issue, PRD, feature, release, or bug-fix slug when one exists;
- rename only when the old slug is misleading and references can be updated.

## `STATE.md` Template

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

- `Last Updated` uses an exact timestamp with timezone, preferably ISO 8601 such as `2026-05-26T18:30:00+08:00`; author or session metadata is optional.
- `Canonical Sources` links the true sources of facts. Source truth beats lifecycle state when they conflict.
- `Current Workflow Mode` records the Groundwork route or state, not a GSD phase. `direct` is allowed as a route value, not as a public skill or project lifecycle mode.
- Allowed route/state values: `direct`, `to-prd`, `to-issues`, `triage`, `write-plan`, `prototype`, `implement`, `verify`, `handoff`, `paused`, `blocked`, `done`.
- `Current Milestone` is `none` unless there is real multi-milestone work.
- `Current Gap Closure` records the current unresolved verify/QA gap. If no active gap exists, write `none`.
- `Next Skill` recommends the next Groundwork skill or direct action.
- `Stop Condition` tells the next session when to stop.

Keep `STATE.md` under 100 lines. Default each body field to 1-3 lines, cite artifacts/checks/commands instead of copying logs, keep only current facts, and close or replace stale gap closure after re-verify.

`STATE.md` must not contain full chat history, full PRDs, full issue bodies, full plans, full diffs, command transcripts, full logs, daily diary entries, all-task lists, project-wide task registries, secrets, tokens, cookies, private keys, credentials, customer PII, sensitive rows, unredacted screenshots, unredacted request payloads, private reasoning, or guesses presented as facts.

## `ROADMAP.md` Template

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

Create or update `ROADMAP.md` only when at least one is true:

- the initiative has multiple milestones;
- multiple workstreams have sequencing dependencies;
- UAT/SIT/release requires stage-level gates;
- the user explicitly requests a multi-stage roadmap;
- one `STATE.md` cannot express progression clearly.

`ROADMAP.md` is not an ordinary task entrypoint, project board, task database, GSD phase runtime, or duplicate `STATE.md`.

## Trigger Policy

Create, update, or recommend `STATE.md` only when at least one hard condition is true:

1. User explicitly asks to pause, resume, switch sessions, save state, or continue later.
2. Work crosses sessions and recovery cost is higher than writing state.
3. A verify gap / QA failure / fix -> re-verify chain remains open.
4. UAT/SIT/release state needs to be reused.
5. Multi-artifact workstream will continue after the current session.
6. Multi-milestone work needs current milestone and next gate.
7. Human decision is pending and the next session needs evidence/options/risks.

Do not create or recommend `STATE.md` for a small edit, one-off explanation, small rewrite, simple title change, low-risk direct answer, one-shot verification with no remaining gap, existing issue/PR that fully owns state, or handoff response that is sufficient.

Weak signals are not enough: several artifacts exist, task looks complex, output looks professional, the agent wants tidiness, framework habit, or desire to mimic GSD.

## Skill Boundaries

`handoff`:

- check whether a workstream `STATE.md` exists when cross-session transfer is requested;
- reference existing `STATE.md` when present;
- recommend creating or updating `STATE.md` when the threshold is met;
- never copy full state or make handoff the long-term state owner.

`verify`:

- if a verification gap must survive the session, update or recommend `STATE.md`;
- after re-verify, close or update `Current Gap Closure`;
- if no state threshold is met, do not write state;
- never put lifecycle notes before the required `Verification Scope` block.

`triage`:

- decide whether lifecycle state is justified;
- keep small tasks direct;
- do not equate `ready-for-agent` with needing state;
- do not create a task database.

`write-plan`:

- read existing `STATE.md` / `ROADMAP.md` for multi-stage work;
- check canonical sources before trusting state;
- do not create lifecycle files for ordinary plans;
- recommend `ROADMAP.md` only for true multi-milestone work.

`to-prd`, `to-issues`, `prototype`, and `implement` do not require lifecycle-specific behavior unless a durable artifact is created under the normal artifact policy.

## Multi-Session Rules

Different workstreams can have separate state files. Groundwork must not create project-global lifecycle state by default.

When multiple sessions touch the same workstream:

1. Read existing `STATE.md` first.
2. Check canonical sources before trusting state.
3. Mark stale state when source truth differs.
4. Update `Last Updated` when changing state.
5. Do not close another session's gap unless re-verify evidence supports closure.
6. Use git, PR, issue, branch, or worktree coordination for real concurrency; Groundwork does not provide locks.

If a user explicitly requests a project-global summary, do not create project-global lifecycle `STATE.md`. Keep it conversation-only by default, or create a separate non-lifecycle artifact only when it has target reader, action, scope, and evidence level.

## Validation

Lifecycle evals should cover:

- small tasks do not suggest lifecycle state;
- pause/resume suggests or references lifecycle state;
- verify gap closure is recoverable;
- re-verify closes stale gap;
- roadmap appears only for multi-milestone contexts;
- `.planning`, `.gsd`, and project-global lifecycle state are rejected;
- handoff references state without owning it;
- state never overrides canonical source truth.
