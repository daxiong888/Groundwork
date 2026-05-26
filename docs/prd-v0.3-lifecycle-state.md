# Groundwork v0.3 PRD: GSD-lite Lifecycle State Contract

Target Reader: Groundwork maintainer implementing and reviewing v0.3.
Reader Action Needed: Decide whether to add a narrow lifecycle-state contract and use this PRD as the implementation source of truth.
Decision Supported: Whether v0.3 should add workstream-scoped `STATE.md` / optional `ROADMAP.md` without adding runtime, CLI, hooks, task DB, or new public skills.
Scope: Shared lifecycle state contract, minimal skill references, docs updates, eval coverage, automation boundaries, and release acceptance for v0.3.
Out of Scope: Public skill expansion, GSD clone, project-wide task database, `.planning` / `.gsd` directory model, installed hooks, user-facing CLI, statusline, MCP server, tracker integration, runtime orchestration, and automatic GitHub commits.
Evidence Level: Grounded in current Groundwork v0.2.3 repository contracts, artifact policy, handoff/verify/triage/write-plan behavior, prior framework research, and current product boundary decisions.

## 1. Executive Summary

Groundwork v0.3 adds a narrow **GSD-lite lifecycle state contract** for resumable R&D work. It does not add a public skill, CLI, hook, runtime, task database, statusline, MCP server, `.planning`, `.gsd`, or GSD command loop.

The product problem is not “how Groundwork manages every task in a project.” The product problem is:

> When a real project has multiple Codex sessions and multiple workstreams, how can each individual workstream be safely resumed without turning Groundwork into a project management system?

v0.3 solves this by adding one shared reference:

```text
skills/_shared/LIFECYCLE-STATE.md
```

That shared reference defines two optional durable artifacts:

```text
artifacts/<workstream-slug>/STATE.md
artifacts/<workstream-slug>/ROADMAP.md
```

`STATE.md` is **workstream-scoped**, not project-global. It preserves the current recoverable facts for one feature, task, bug fix, UAT/release checkpoint, or contract-review stream.

`ROADMAP.md` is **narrow and optional**. It exists only for multi-milestone or multi-stage initiatives where sequencing cannot be captured in a single state summary.

`handoff` remains a **session transfer package**. It may reference `STATE.md`, but it does not own long-term lifecycle state.

`verify` may update or recommend lifecycle state only when a gap closure needs to survive beyond the current response or session.

`triage` may decide whether lifecycle state is justified, but it must not create a task database.

`write-plan` may read `STATE.md` / `ROADMAP.md` for multi-stage planning, but it must not create lifecycle files for ordinary implementation plans.

The release thesis:

```text
Groundwork v0.3 makes each workstream resumable.
It does not manage the whole project.
```

## 2. Background

Groundwork is already an evidence-first R&D workflow base with eight public skills:

```text
to-prd
to-issues
triage
write-plan
prototype
implement
verify
handoff
```

The current public surface should stay unchanged. v0.3 is a lifecycle-state refinement, not a skill-surface expansion.

Groundwork already has several relevant contracts:

- durable artifacts require an audience-first header;
- durable artifacts should prefer `artifacts/<feature-slug>/`;
- `.groundwork/runs`, `.groundwork/harness`, and `.groundwork/tmp` are runtime support, ignored by default;
- `handoff` should be compact and reference existing artifacts instead of copying long documents, diffs, or logs;
- `verify` already uses scope/evidence discipline, QA-FIX-QA structure, and readiness boundaries;
- current repository guidance says new public skills require explicit issue support and `.groundwork` runtime contents should not be committed by default.

v0.3 should therefore avoid re-implementing v0.2.x hardening. It should fill one missing layer: a compact, durable, per-workstream state summary for multi-session continuation.

## 3. Problem Statement

Users often run several sessions against the same project at the same time:

- one session shapes PRD/spec;
- one session implements a feature;
- one session verifies UAT readiness;
- one session reviews a frontend contract document;
- one session fixes a QA gap;
- one session prepares a release or handoff.

Without a narrow lifecycle state interface, the following problems occur:

1. **Cross-session recovery is expensive.** New sessions must rediscover scope, evidence, decisions, and next steps from chat history, diffs, docs, or runtime output.
2. **Gap closure is fragile.** A verify failure, scoped fix, and re-verify requirement may be spread across separate sessions.
3. **Handoff can become a diary.** If handoff tries to preserve durable state, it can grow into a log, implementation diary, or duplicate PRD.
4. **Project-global state creates conflict.** A single global `STATE.md` would mix unrelated tasks and become stale quickly.
5. **Heavy frameworks are tempting but wrong.** Adding `.planning`, `.gsd`, a task DB, hooks, CLI, runtime, or GSD command loop would violate Groundwork’s small-surface product boundary.

v0.3 solves 1–4 while explicitly preventing 5.

## 4. Goals

1. Define a small shared lifecycle-state contract.
2. Allow one `STATE.md` per workstream under `artifacts/<workstream-slug>/STATE.md`.
3. Allow optional `ROADMAP.md` only for multi-milestone or multi-stage initiatives.
4. Keep `handoff` compact and make it reference state instead of owning state.
5. Let `verify` preserve recoverable gap-closure facts only when needed.
6. Let `triage` decide whether lifecycle state is justified.
7. Let `write-plan` use lifecycle state for multi-stage planning without forcing artifacts for ordinary plans.
8. Ensure small tasks do not create or recommend lifecycle artifacts.
9. Add lifecycle-state eval coverage.
10. Preserve current public skill surface and runtime boundary.

## 5. Non-goals

v0.3 does not add:

- public skills;
- user-facing CLI;
- installed hooks;
- runtime daemon;
- task CRUD;
- project task database;
- project-wide session registry;
- statusline integration;
- MCP server;
- tracker API integration;
- automatic PR, push, deploy, or commit behavior;
- `.planning` directory model;
- `.gsd` directory model;
- GSD command loop;
- full autonomous orchestration;
- project-global `STATE.md` by default.

v0.3 does not turn `STATE.md` into:

- PRD;
- issue;
- task DB;
- chat log;
- implementation diary;
- diff/log transcript;
- verify report archive;
- handoff replacement;
- project-wide dashboard.

## 6. Core Concepts

### 6.1 Workstream

A workstream is one independently resumable unit of work.

Examples:

```text
admin-user-filter
payment-refund-flow
frontend-contract-cleanup
release-v0-3
uat-readiness-before-customer-demo
```

A workstream is not the whole project.

### 6.2 `STATE.md`

`STATE.md` is the durable lifecycle state summary for exactly one workstream.

Path:

```text
artifacts/<workstream-slug>/STATE.md
```

It answers:

- What is the current workflow mode?
- What is the active scope?
- What was the last confirmed decision?
- What evidence is verified?
- What claims remain unverified?
- What risks are open?
- Is there an active gap closure?
- What is the next skill or direct action?
- When should the next session stop?

It does not answer:

- What are all active tasks in the project?
- Who owns every task?
- What is the global project status?
- What is the full implementation history?

### 6.3 `ROADMAP.md`

`ROADMAP.md` is optional and only for multi-milestone / multi-stage initiatives.

Path:

```text
artifacts/<workstream-slug>/ROADMAP.md
```

It captures:

- milestones;
- dependencies;
- sequencing;
- decision gates;
- verification gates;
- UAT/release gates;
- stop conditions.

It is not a task database or project board.

### 6.4 Handoff

`handoff` is a transfer package for another session or reader.

It may point to:

```text
artifacts/<workstream-slug>/STATE.md
```

It must not copy full state, full PRD, long diffs, logs, transcripts, or sensitive data.

### 6.5 Canonical Sources

Canonical sources own truth. `STATE.md` only summarizes and links them.

Canonical sources include:

- source code;
- tests;
- runtime/browser evidence;
- PRD/spec;
- GitHub Issue / PR;
- contract documents;
- verification reports;
- UAT/SIT evidence;
- user-confirmed decisions.

If `STATE.md` conflicts with canonical sources, canonical sources win and state is stale.

## 7. Artifact Model

### 7.1 Default durable lifecycle paths

```text
artifacts/<workstream-slug>/STATE.md
artifacts/<workstream-slug>/ROADMAP.md
```

### 7.2 Forbidden default paths

```text
STATE.md
PROJECT-STATE.md
artifacts/STATE.md
.groundwork/STATE.md
.groundwork/tasks/<task-id>/STATE.md
.planning/*
.gsd/*
```

### 7.3 Runtime scratch remains separate

The following are runtime scratch only:

```text
.groundwork/runs/
.groundwork/harness/
.groundwork/tmp/
```

They are ignored by default and are not lifecycle artifacts.

### 7.4 `.groundwork/tasks` boundary

If older documentation still mentions `.groundwork/tasks/<task-id>/`, v0.3 must clarify:

- it is not lifecycle state;
- it is not the default `STATE.md` location;
- it is not a project task database;
- durable lifecycle artifacts use `artifacts/<workstream-slug>/`.

## 8. `STATE.md` Interface

### 8.1 Required template

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

### 8.2 Field rules

`Target Reader` names who resumes or reviews the work.

`Reader Action Needed` states what the next reader should do.

`Decision Supported` explains what decision the state enables.

`Scope` defines the workstream boundary.

`Out of Scope` prevents accidental expansion.

`Evidence Level` describes how strong the current evidence is.

`Last Updated` marks freshness.

`Canonical Sources` links the true sources of facts.

`Current Workflow Mode` uses Groundwork modes, not GSD phases:

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
paused
blocked
done
```

`Current Milestone` is `none` unless there is a real multi-milestone initiative.

`Last Confirmed Decision` records only the latest decision that affects recovery.

`Active Scope` records what is currently being worked on.

`Verified Evidence` references key evidence; it does not copy evidence logs.

`Unverified Claims` lists only claims that affect next action.

`Open Risks` lists material risks, ideally with severity or owner.

`Current Gap Closure` records the current unresolved verify/QA gap. If no active gap exists, write `none`.

`Next Skill` recommends the next Groundwork skill or direct action.

`Stop Condition` tells the next session when to stop.

### 8.3 Length rule

`STATE.md` should stay under 100 lines.

Rules:

- default each body field to 1–3 lines;
- cite artifact/check/command references instead of copying long content;
- keep only current facts and recoverable next steps;
- do not keep historical gap logs;
- close or replace `Current Gap Closure` after re-verify.

### 8.4 Forbidden content

`STATE.md` must not contain:

- full chat history;
- full PRD;
- full issue body;
- full implementation plan;
- full diff;
- command transcript;
- full logs;
- daily diary;
- all-task list;
- project-wide active task registry;
- secrets;
- tokens;
- cookies;
- private keys;
- credentials;
- customer PII;
- sensitive database rows;
- unredacted screenshots;
- unredacted request payloads;
- private reasoning;
- unverified guesses presented as facts.

## 9. `ROADMAP.md` Interface

### 9.1 Required template

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

### 9.2 Trigger

Create or update `ROADMAP.md` only when at least one is true:

- the initiative has multiple milestones;
- multiple workstreams have sequencing dependencies;
- UAT/SIT/release requires stage-level gates;
- user explicitly requests a multi-stage roadmap;
- one `STATE.md` cannot express progression clearly.

### 9.3 Forbidden use

`ROADMAP.md` must not become:

- ordinary task entrypoint;
- all-project task board;
- complete task database;
- GSD phase runtime;
- duplicated `STATE.md` contents.

## 10. Trigger Policy

### 10.1 Create or update `STATE.md` when

At least one hard condition is true:

1. User explicitly asks to pause, resume, switch sessions, save state, or continue later.
2. Work crosses sessions and recovery cost is higher than writing state.
3. A verify gap / QA failure / fix -> re-verify chain remains open.
4. UAT/SIT/release state needs to be reused.
5. Multi-artifact workstream will continue after the current session.
6. Multi-milestone work needs current milestone and next gate.
7. Human decision is pending and the next session needs evidence/options/risks.

### 10.2 Do not create or recommend `STATE.md` when

- small edit;
- one-off explanation;
- small rewrite;
- simple title change;
- low-risk direct answer;
- one-shot verification with no remaining gap;
- existing issue/PR already fully owns state;
- handoff response alone is sufficient.

### 10.3 Weak signals are not enough

The following cannot trigger state alone:

- several artifacts exist;
- task looks complex;
- agent wants to be tidy;
- output looks professional;
- framework habit;
- desire to mimic GSD.

## 11. Skill Integration

### 11.1 `handoff`

v0.3 adds:

- check whether a workstream `STATE.md` exists when cross-session transfer is requested;
- reference existing `STATE.md` when present;
- recommend creating/updating `STATE.md` when trigger threshold is met;
- never copy full state;
- never make handoff the long-term state layer.

Suggested output addition:

```text
Lifecycle State
- State Artifact:
- State Freshness:
- State Update Needed:
```

### 11.2 `verify`

v0.3 adds:

- if verification finds a gap that must survive the session, update or recommend `STATE.md`;
- if no `STATE.md` exists but threshold is met, recommend one;
- if gap can be resolved inside the response, do not write state;
- after re-verify, close or update `Current Gap Closure`;
- never keep stale gap closure;
- never put lifecycle notes before the required `Verification Scope` block.

Suggested output addition after the verification body:

```text
Lifecycle State Update
- Needed: yes / no
- Target: artifacts/<workstream-slug>/STATE.md
- Current Gap Closure:
- Re-verify Required:
- State Freshness Risk:
```

### 11.3 `triage`

v0.3 adds:

- decide whether lifecycle state is justified;
- keep small tasks direct;
- do not equate `ready-for-agent` with needing state;
- recommend state only when cross-session, gap closure, UAT/release, or decision-pending conditions apply;
- do not create a task database.

Suggested output addition:

```text
Lifecycle State Recommendation
- Needed: yes / no
- Reason:
- Artifact:
- External Task Source:
```

### 11.4 `write-plan`

v0.3 adds:

- read `STATE.md` / `ROADMAP.md` when planning a multi-stage workstream;
- do not create lifecycle files for ordinary plans;
- detect stale state by checking canonical sources;
- recommend `ROADMAP.md` only for true multi-milestone work.

Suggested output addition:

```text
Lifecycle Inputs
- STATE.md:
- ROADMAP.md:
- Stale State Risk:
- Roadmap Needed:
```

### 11.5 Other skills

`to-prd`, `to-issues`, `prototype`, and `implement` do not require major v0.3 changes. They continue to follow artifact policy when durable files are created.

## 12. Multi-session Behavior

### 12.1 Different sessions, different workstreams

Each workstream may have its own `STATE.md`:

```text
Session A -> artifacts/admin-user-filter/STATE.md
Session B -> artifacts/payment-refund-flow/STATE.md
Session C -> artifacts/frontend-contract-cleanup/STATE.md
```

Groundwork must not create project-global state by default.

### 12.2 Same workstream, multiple sessions

If multiple sessions touch the same workstream:

1. Read existing `STATE.md` first.
2. Check canonical sources before trusting state.
3. Mark stale state when source truth differs.
4. Update `Last Updated` when changing state.
5. Do not close another session’s gap unless re-verify evidence supports closure.
6. Use git/PR/issue/branch/worktree coordination for real concurrency; Groundwork does not provide locks.

### 12.3 Discoverability

v0.3 does not create project-wide index by default.

Recommended discovery:

- external issue/PR links the state file;
- user prompt names the workstream;
- handoff references the state file.

Optional future idea, not v0.3 default:

```text
artifacts/_index.md
```

If introduced later, it must be link-only and must not become a task DB.

## 13. Internal Automation Boundary

v0.3 may use internal automation to validate lifecycle-state quality, but it must not add user-facing runtime surface.

### 13.1 Allowed in v0.3

#### Optional fresh-context subagent review

A subagent may review lifecycle-state quality when explicitly delegated or when used as a bounded internal reviewer.

Allowed review dimensions:

- does `STATE.md` have required fields?
- is state workstream-scoped, not project-global?
- did it become a task DB?
- are claims backed by canonical sources?
- is `Current Gap Closure` stale?
- does handoff reference state instead of copying it?
- does `ROADMAP.md` require true multi-milestone scope?
- are `.planning` / `.gsd` / root project state avoided?

Subagent restrictions:

- fresh context only;
- no reliance on parent session memory;
- no nested delegation;
- no scope expansion;
- no file mutation unless explicitly delegated;
- no automatic state ownership.

#### Optional maintainer-only validation script

A small local validation helper is allowed if it is maintainer-only and not a user-facing CLI.

Possible script:

```text
scripts/check_lifecycle_state.py
```

Allowed checks:

- required `STATE.md` fields;
- required `ROADMAP.md` fields;
- line count under 100 for `STATE.md`;
- allowed path under `artifacts/<workstream-slug>/`;
- forbidden `.planning` / `.gsd` / project-global state paths;
- forbidden obvious diff/log transcript patterns;
- missing `Canonical Sources` or `Last Updated`.

This script is optional and does not block v0.3 unless implementation chooses to add it.

#### Targeted eval runner / CSV validation

Existing eval style should continue. v0.3 adds lifecycle-state rows and can use existing validation commands.

#### Quarantined learning proposal

Repeated lifecycle-state eval failures may produce a quarantined learning proposal, not an automatic patch.

### 13.2 Not allowed in v0.3

- public CLI;
- installed git hooks;
- runtime daemon;
- automatic state mutation;
- automatic commit/push/PR;
- tracker writes;
- project-wide session registry;
- task CRUD;
- `.planning` / `.gsd` model;
- hook-based enforcement required for normal use.

### 13.3 Hook decision

Hooks are deferred to v0.4+ discussion.

v0.3 may document hook-shaped checks as future automation, but it must not install or require hooks.

Rationale:

- hooks change user workflow;
- hooks imply runtime enforcement;
- hooks need cross-platform support and bypass behavior;
- hooks would expand v0.3 beyond shared contract + evals.

## 14. UX Flows

### 14.1 Pause/resume

User:

```text
我要换会话，保存当前状态，下个 session 继续。
```

Expected behavior:

1. Use `handoff`.
2. Determine lifecycle threshold is met.
3. Reference existing `STATE.md`, or recommend creating one.
4. Produce compact handoff.
5. Do not copy long diffs, logs, or full PRD.

### 14.2 Verify gap closure

User:

```text
验证这个能不能给客户 UAT。
```

If verify finds a P1 gap:

1. Final report begins with `Verification Scope`.
2. Evidence matrix identifies the gap.
3. QA failure shape appears when applicable.
4. Lifecycle state note recommends `Current Gap Closure` update.
5. Next skill is likely `implement`.
6. Stop condition names re-verify evidence.

### 14.3 Re-verify

User:

```text
刚才那个 gap 修了，重新验证。
```

Expected behavior:

1. Re-run or inspect original failing check when possible.
2. If pass, set `Current Gap Closure` to `none`.
3. If partial/fail, update gap closure.
4. Do not keep stale failure history.

### 14.4 Multi-milestone initiative

User:

```text
这个 release 分三阶段做，帮我规划后续状态。
```

Expected behavior:

1. Use `write-plan` or direct planning as appropriate.
2. Recommend optional `ROADMAP.md` only if multi-milestone threshold is met.
3. Keep workstream states separate.
4. Do not create task DB.

### 14.5 Small task

User:

```text
把这个标题改短一点。
```

Expected behavior:

1. Direct answer/edit.
2. No `STATE.md`.
3. No `ROADMAP.md`.
4. No lifecycle recommendation.

## 15. Eval Plan

Add `evals/prompts/lifecycle-state.csv` or extend `evals/prompts/guardrails-regression.csv`.

Suggested rows:

| ID | Expected Skill | Scenario | Expected Behavior | Forbidden Behavior |
| --- | --- | --- | --- | --- |
| life-001 | direct | Small title rewrite | No lifecycle state recommendation | Suggests or creates `STATE.md` |
| life-002 | direct | One-off explanation | No lifecycle artifact | Creates artifact |
| life-003 | handoff | User says pause/resume | References or recommends `STATE.md` | Turns handoff into durable state owner |
| life-004 | verify | UAT verify finds gap | Emits lifecycle gap-closure recommendation | Direct pass or broad reprocess |
| life-005 | verify | Re-verify passes | Closes `Current Gap Closure` | Keeps stale gap |
| life-006 | triage | Determine if task deserves lifecycle state | Gives threshold decision | Creates state for every task |
| life-007 | write-plan | Ordinary plan | No `ROADMAP.md` | Creates roadmap for ordinary task |
| life-008 | write-plan | Multi-milestone initiative | Allows `ROADMAP.md` | Treats roadmap as task DB |
| life-009 | handoff | Existing `STATE.md` | References state | Copies state全文 |
| life-010 | verify | State conflicts with source truth | Marks stale state and trusts canonical source | Blindly trusts state |
| life-011 | any | User asks for `.planning` model | Uses Groundwork path / rejects clone | Creates `.planning` |
| life-012 | any | Multiple sessions, different tasks | Separate workstream states | Project-global `STATE.md` |
| life-013 | verify | Missing failure details | Uses `not provided` / `unverified` | Invents expected/actual |
| life-014 | handoff | Long diff transfer | References artifacts | Pastes long diff |
| life-015 | triage | External issue owns state | Links external source | Duplicates full issue as local DB |

Acceptance standard:

- small tasks do not suggest lifecycle state;
- pause/resume suggests or references state;
- verify gap closure is recoverable;
- re-verify closes stale gap;
- roadmap appears only for multi-milestone contexts;
- no `.planning` / `.gsd` / project-global state;
- handoff references state without owning it;
- state never overrides canonical source truth.

## 16. Implementation Scope

### 16.1 Required files

Add:

```text
skills/_shared/LIFECYCLE-STATE.md
```

Update minimally:

```text
skills/handoff/SKILL.md
skills/verify/SKILL.md
skills/triage/SKILL.md
skills/write-plan/SKILL.md
docs/product-principles.md
docs/workflow-taxonomy.md
docs/prd.md
CHANGELOG.md
.codex-plugin/plugin.json
```

Add evals:

```text
evals/prompts/lifecycle-state.csv
```

or append lifecycle rows to:

```text
evals/prompts/guardrails-regression.csv
```

Optional:

```text
scripts/check_lifecycle_state.py
```

### 16.2 Implementation constraints

- small patches only;
- avoid broad frontmatter trigger rewrites unless necessary;
- avoid verify scope-first regression;
- do not change public skill surface;
- do not add runtime directories;
- do not add hooks;
- do not add public CLI;
- do not add GSD clone paths;
- do not commit `.groundwork/*` runtime contents.

## 17. Validation Plan

Required static checks:

```bash
git diff --check
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
```

If skill descriptions change materially, run targeted runtime evals for:

- lifecycle-state rows;
- adjacent handoff/verify/triage/write-plan routing;
- verify final-report opening;
- small-task direct fallback.

## 18. Acceptance Criteria

### AC-1: Shared contract exists

`skills/_shared/LIFECYCLE-STATE.md` exists and defines `STATE.md`, `ROADMAP.md`, paths, triggers, fields, forbidden content, stale state, multi-session behavior, and skill boundaries.

### AC-2: State is workstream-scoped

The contract says `STATE.md` is workstream-scoped and belongs at:

```text
artifacts/<workstream-slug>/STATE.md
```

It must not default to root/project-global state.

### AC-3: Roadmap is narrow

`ROADMAP.md` is allowed only for multi-milestone / multi-stage / sequencing contexts.

### AC-4: No new public skill

Public skill surface remains exactly the current eight skills.

### AC-5: No runtime surface

No public CLI, installed hook, runtime daemon, task CRUD, tracker integration, statusline, MCP server, `.planning`, `.gsd`, or GSD command loop is added.

### AC-6: Handoff boundary

`handoff` references lifecycle state when appropriate but does not become the durable state owner.

### AC-7: Verify gap closure

`verify` can recommend/update lifecycle state for cross-session gap closure and can close/update `Current Gap Closure` after re-verify without breaking the `Verification Scope` opening rule.

### AC-8: Triage threshold

`triage` can explain whether state is needed and must not create a task DB or recommend state for small tasks.

### AC-9: Write-plan boundary

`write-plan` can read lifecycle artifacts for multi-stage work and must not create lifecycle artifacts for ordinary plans.

### AC-10: Artifact safety

Lifecycle artifacts follow audience-first header, directory policy, redaction, and no-long-diff/no-long-log rules.

### AC-11: Eval coverage

Lifecycle-state eval rows exist and cover small-task no-state behavior, pause/resume, verify gap closure, re-verify closure, multi-milestone roadmap, GSD clone prevention, handoff references, and stale state conflict.

### AC-12: Validation passes

Required static checks pass. Targeted runtime evals pass when run for touched skill descriptions.

## 19. Risks And Mitigations

### Risk: `STATE.md` becomes task DB

Mitigation:

- workstream-scoped only;
- no project-global state;
- no all-task list;
- external issue/PR remains task owner.

### Risk: ceremony expands

Mitigation:

- hard no-state evals for small tasks;
- narrow trigger conditions;
- weak signals cannot trigger state alone.

### Risk: stale state misleads future sessions

Mitigation:

- `Last Updated`;
- `Canonical Sources`;
- stale state rule;
- source truth beats lifecycle state.

### Risk: verify scope-first regression

Mitigation:

- lifecycle note appears after `Verification Scope`;
- targeted verify evals.

### Risk: routing drift

Mitigation:

- minimal frontmatter changes;
- adjacent routing evals.

### Risk: GSD clone creep

Mitigation:

- explicit non-goals;
- forbidden `.planning` / `.gsd` paths;
- no CLI/hook/runtime/task DB.

### Risk: automation overreach

Mitigation:

- subagent is reviewer only;
- optional validation script is maintainer-only;
- hooks deferred;
- no automatic state mutation or commits.

## 20. Release Notes Draft

```md
## v0.3.0 - 2026-05-26

### Added

- Added `skills/_shared/LIFECYCLE-STATE.md` as a narrow shared lifecycle state contract.
- Defined optional workstream-scoped `artifacts/<workstream-slug>/STATE.md` for resumable multi-session R&D work.
- Defined optional `artifacts/<workstream-slug>/ROADMAP.md` for multi-milestone / multi-stage initiatives.
- Added lifecycle state boundary references to `handoff`, `verify`, `triage`, and `write-plan`.
- Added lifecycle-state regression prompts covering small-task no-state behavior, pause/resume, verify gap closure, re-verify closure, multi-milestone roadmap, and GSD clone prevention.

### Changed

- Clarified that lifecycle state is opt-in durable artifact state, not a project task database.
- Clarified that `handoff` references lifecycle state but does not own it.
- Clarified that `.groundwork/*` remains runtime scratch and is not the default durable lifecycle artifact location.

### Not Included

- No new public skill.
- No public CLI.
- No installed hook.
- No runtime.
- No task CRUD.
- No tracker integration.
- No statusline hook.
- No MCP server.
- No `.planning` or `.gsd` directory model.
- No project-global `STATE.md`.
```

## 21. Open Questions

1. Should v0.3 update older `.groundwork/tasks/<task-id>/` wording in `docs/prd.md`, or only clarify the lifecycle boundary in the new shared contract?
2. Should lifecycle eval rows live in a new `evals/prompts/lifecycle-state.csv`, or be appended to `guardrails-regression.csv`?
3. Should `.codex-plugin/plugin.json` be bumped to `0.3.0` in the PRD-only commit, or only when implementation lands?
4. Should optional `scripts/check_lifecycle_state.py` be included in v0.3 implementation, or deferred until evals reveal repeated format drift?
5. Should `Last Updated` require timezone and exact author/session format?
6. Should workstream slug normalization be documented in v0.3?
7. If a user explicitly requests a project-global summary, should Groundwork keep it conversation-only by default, or allow a durable non-lifecycle project summary with a different artifact name?

## 22. Final Decision

Approve v0.3 only as a narrow lifecycle-state contract release:

```text
Add workstream-scoped lifecycle state.
Do not add project-level orchestration.
Do not clone GSD.
Do not create task DB.
Do not expand public skills.
Do not add user-facing CLI or installed hooks.
```

Groundwork v0.3 should make each workstream resumable without becoming a project management system.
