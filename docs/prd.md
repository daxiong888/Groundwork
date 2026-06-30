# Groundwork MVP PRD

## Problem Statement

Codex is already useful for day-to-day engineering work, but complex R&D work still loses shape across PRD writing, task slicing, prototype exploration, implementation, verification, UAT evidence, and handoff. Existing workflow frameworks contain useful patterns, but adopting any full framework would add too much installation, ceremony, role-play, runtime ownership, or task-system lock-in.

Groundwork should become a Codex-native personal R&D base: a small plugin that absorbs the useful parts of Superpowers and mattpocock/skills, rejects the parts that do not fit, and keeps the user's real development workflow evidence-first and resumable.

## Product Goal

Build a first usable Groundwork plugin that helps the user move from ambiguous product or engineering intent to a clear next action, verified evidence, and durable artifacts only when they are worth keeping.

The MVP should be usable before it is broad. It should expose a thin but complete workflow:

```text
PRD/spec -> task context -> plan -> prototype/contract/design as needed -> implementation -> verification/UAT -> handoff
```

## Target User

The primary user is a pragmatic engineering/product operator using Codex for software R&D:

- PRD/spec writing and refinement
- task slicing and task-state management
- static HTML/UI prototype creation and review
- logic/state prototype exploration
- frontend integration documentation and review
- backend/frontend implementation and review
- UAT/SIT readiness verification
- release, handoff, and continuation across sessions
- local Codex skill/plugin development

The user values direct execution, but only after relevant facts are grounded in source code, runtime behavior, data, docs, or user-provided evidence.

## Product Positioning

Groundwork is not a new autonomous coding runtime. It is a curated Codex plugin base.

The current product shape:

- Superpowers is the Codex plugin skeleton and packaging reference.
- mattpocock/skills is the strongest lightweight skill/workflow behavior reference.
- Groundwork is the curated R&D base that decides what to keep, rename, merge, or reject.

Groundwork should not become a loose bundle of borrowed skills. Borrowed pieces must pass through Groundwork's R&D loop and usage rules.

## MVP Scope

### Public Skills

Groundwork plugin provides the namespace, so public skill names do not repeat a `groundwork-` prefix:

| Skill | Purpose | Main borrowed source |
| --- | --- | --- |
| `to-prd` | Turn conversation, evidence, prototype notes, UAT feedback, or rough requirements into PRD/spec intent and acceptance. | mattpocock `to-prd`, Spec Kit, Trellis PRD discipline |
| `to-issues` | Split PRD/spec/plan into vertical slices and link them to the best task source. | mattpocock `to-issues`, Spec Kit task slices |
| `triage` | Manage task state, blockers, AFK/HITL, `ready-for-agent`, `ready-for-human`, and closeout. | mattpocock `triage` and agent brief |
| `write-plan` | Turn accepted task context into implementation steps, dependencies, stop conditions, and verification checkpoints. | Superpowers `writing-plans` |
| `prototype` | Build, revise, and review throwaway logic/state or UI/static HTML prototypes that answer a specific question. | mattpocock `prototype` |
| `implement` | Execute or review code changes against PRD/task/plan/source/diff/tests. | Trellis implement/check, Superpowers execution discipline |
| `verify` | Check tests, runtime behavior, data readiness, environment readiness, UAT/SIT, and release acceptance. | Superpowers verification, gstack QA, GSD UAT evidence |
| `handoff` | Preserve compact state for long-running R&D work without duplicating PRDs, plans, issues, commits, or diffs. | mattpocock `handoff` |

### Embedded Branches

These are first-version capabilities, but not public standalone skills:

| Branch | Owner | Trigger | Output |
| --- | --- | --- | --- |
| `scope` | `to-prd`, `to-issues` | Acceptance, success condition, or user intent is unclear or conflicting. | Clarified acceptance delta, explicit open questions, and whether to continue or stop. |
| `contract` | `write-plan`, `prototype`, `implement`, `verify` | API, DB, state, frontend behavior, docs, or environment alignment affects correctness. | Minimal contract table or checklist tied to source evidence, not a standalone architecture doc. |
| `artifact` | all public skills that may write durable files | Output has a target reader, review need, execution need, verification need, or handoff need. | Artifact purpose, target reader, downstream action, and write/update recommendation. |
| `diagnose` | `implement` | A bug, failing test, runtime anomaly, or unclear cause must be confirmed before edits. | Confirmed cause, rejected hypotheses, or `not confirmed`; no speculative fix without evidence. |
| `gate` | `implement`, `verify`, `handoff` | Deploy, publish, push, migration, destructive command, data write, remote tracker mutation, or shared-skill mutation is requested. | Proposed action, target, risk, rollback/undo note, and explicit approval request. |
| `standards` | review lens only | Repeated work shows repo conventions or quality standards are being rediscovered. | Inline review criteria; standalone skill deferred until repeated usage proves the need. |

## Usage Experience

### Natural Invocation

The user can invoke skills explicitly or naturally in Chinese:

- "把这个需求整理成 PRD" -> `to-prd`
- "基于这个 PRD 拆 issues" -> `to-issues`
- "triage 一下这个 issue，看看能不能给 agent 做" -> `triage`
- "给这个任务写实现计划" -> `write-plan`
- "做个静态原型" / "跑一下这个状态模型" -> `prototype`
- "按这个任务实现" -> `implement`
- "验证一下能不能给前端/客户验" -> `verify`
- "给下个 session 做 handoff" -> `handoff`

Skill names stay English. User-facing output defaults to Chinese unless the target artifact or user request requires English.

### Direct Fallback

Small tasks should stay small. Groundwork should answer or edit directly when the work is one-off, low-risk, obvious, and does not need durable context.

Groundwork should activate only when ambiguity, risk, reuse, long-running state, verification, handoff, prototype, contract, or task-source value justifies the workflow.

### Skill Conflict Rules

When a prompt could match multiple skills, choose the lightest skill that answers the user's current intent:

- If the user asks to clarify intent, acceptance, or requirement shape, use `to-prd`, not `to-issues`.
- If the user asks to split accepted intent into work units, use `to-issues`.
- If the user asks whether a task is ready, blocked, AFK, HITL, or should be closed, use `triage`.
- If the task is accepted but edits have not started, use `write-plan`.
- If code changes are requested, use `implement`.
- If visual, interaction, state, or business-rule uncertainty needs a throwaway artifact to answer a question, use `prototype`.
- If readiness, evidence, UAT/SIT, runtime behavior, or release confidence is requested, use `verify`.
- If continuity across sessions or compact state transfer is requested, use `handoff`.
- If the prompt is small, one-off, low-risk, obvious, and does not need durable context, use direct fallback.

### Guided Continuation

Groundwork should not run the whole workflow automatically. Each skill should finish by reporting:

- current result
- evidence and assumptions
- remaining gaps
- recommended next skill or direct next action
- whether an artifact should be written or updated

The next step runs only after the user says to continue or explicitly asks for it.

### Artifact Policy

Default to conversation output. Write files only when the result must be reused, reviewed, executed, verified, or handed off.

When a real external source exists, link or update that source rather than duplicating it locally. Workstream-scoped lifecycle state belongs under `artifacts/<workstream-slug>/STATE.md`, with optional `artifacts/<workstream-slug>/ROADMAP.md` only for true multi-milestone work. Older local fallback files under `.groundwork/tasks/<task-id>/` are scratch or fallback context, not lifecycle state, not the default durable artifact location, and not a task database.

Do not create empty template files for completeness. Create only files with real content.

### Artifact Safety Rules

Groundwork artifacts must never copy secrets, tokens, cookies, private keys, production credentials, customer PII, or other sensitive personal data.

Logs, screenshots, copied requests, database rows, or handoff notes must be redacted when they may contain sensitive values. Handoff may reference secret locations abstractly, but must not quote secret values.

External writes require explicit user approval with target, action, risk, and rollback or undo note. Shared skill mutation requires explicit approval and a diff summary before editing shared skill files.

### Runtime Safety Boundary

Groundwork `gate` is a workflow preflight and communication contract, not a replacement for Codex runtime safety. It helps the active owner skill surface proposed action, target, risk, rollback/undo, and approval need before high-risk work.

Actual enforcement of shell, network, filesystem, remote tracker, deployment, or git side effects belongs to the Codex runtime, including sandbox settings, approval policy, Auto Review, host permissions, and available credentials. Groundwork must not rely on natural skill selection as the only safety boundary.

Runtime safety tests should run in an environment that can exercise the relevant Codex approval path, such as the Codex App or an interactive approval mode. A non-interactive run with approvals disabled can validate skill-selection behavior, but it is not an Auto Review test.

## Skill Trigger Contracts

Each public skill must be written as a testable natural-language program, not only as prose. Every public `SKILL.md` must define:

- `name`
- concise `description` with key trigger words front-loaded
- should-trigger examples, including explicit invocation and natural Chinese prompts
- should-not-trigger examples, including small direct-fallback prompts
- required input evidence or inspection step
- output shape
- stop condition
- recommended next skill or direct next action
- artifact write/update condition

Descriptions should stay short and boundary-focused because Codex implicit invocation depends on `description`, and descriptions may be shortened when many skills are available. Long examples, templates, and rubrics belong in bundled references only when repeated usage proves the need.

Minimum fixture coverage for each public skill:

- explicit invocation
- natural Chinese invocation
- realistic noisy prompt
- adjacent false-positive prompt
- small direct-fallback prompt

## Prototype Requirements

The `prototype` skill should directly adapt mattpocock's two-branch structure:

```text
skills/prototype/
  SKILL.md
  LOGIC.md
  UI.md
```

Core rule:

```text
A prototype is throwaway code that answers a question.
```

`LOGIC.md` handles state machines, data shapes, reducers, business rules, and small interactive terminal prototypes.

`UI.md` handles UI/static HTML prototypes, variants, browser-visible states, and interaction review.

Groundwork-specific additions:

- static HTML/UI prototype review is a high-frequency default scenario
- browser verification should be used when visual or interaction claims matter
- if browser/runtime inspection is unavailable, visual and interaction claims must be marked `unverified`
- do not claim layout, color, responsiveness, hover/focus, animation, or state-transition correctness without browser/runtime evidence
- prototype output must capture the question answered, decision needed, explored states/interactions, coverage evidence status, known gaps, implementation implications, and feedback into PRD/task/contract/implementation
- prototype code must be deleted or absorbed after the question is answered
- UI prototypes default to one minimum verifiable prototype; multiple variants are used only when the user asks for options or the problem is explicitly a visual or interaction tradeoff
- prototype cleanup decision must be explicit: delete, absorb, or keep temporarily with reason

Suggested `prototype` output shape:

```text
Prototype Question
Decision Needed
States Explored
Interactions Explored
Coverage Evidence Status: prototype_only / browser_verified / runtime_verified / unverified
Known Gaps
Implementation Implications
PRD / Issue / Contract Updates
Cleanup Decision
```

## Review Requirements

Review is not a public standalone MVP skill. It appears inside specific skills:

- `prototype`: review business flow, states, interactions, and implementability
- `implement`: review diff against PRD/task/plan, repo conventions, and verification evidence
- `verify`: review readiness across code/test/runtime/data/environment/customer validation
- `contract`: review API/DB/state/frontend/documentation alignment
- `triage`: review whether a task is ready for agent or human work

Do not copy mattpocock's in-progress `review` skill as-is. Groundwork should build its own review lens around actual R&D scenarios.

## First-Cut Skill Assets

The MVP should not create a uniform folder shape for every skill. Assets follow the borrowed skill shape only when useful:

| Skill | First-cut assets |
| --- | --- |
| `to-prd` | `SKILL.md` with compact PRD output format |
| `to-issues` | `SKILL.md` with vertical-slice rules and issue output format |
| `triage` | `SKILL.md`, `AGENT-BRIEF.md`; `OUT-OF-SCOPE.md` deferred until repeated usage proves the need |
| `write-plan` | `SKILL.md` with Groundwork's lighter plan format |
| `prototype` | `SKILL.md`, `LOGIC.md`, `UI.md` |
| `implement` | `SKILL.md` |
| `verify` | `SKILL.md` with inline verification output format |
| `handoff` | `SKILL.md` |

No CLI, tracker API integration, hooks, MCP server, UI, or task CRUD tool is required for MVP.

## Codex Plugin Packaging Requirements

MVP plugin layout:

```text
groundwork/
  .codex-plugin/
    plugin.json
  skills/
    _shared/
      LIFECYCLE-STATE.md
    to-prd/
      SKILL.md
    to-issues/
      SKILL.md
    triage/
      SKILL.md
      AGENT-BRIEF.md
    write-plan/
      SKILL.md
    prototype/
      SKILL.md
      LOGIC.md
      UI.md
    implement/
      SKILL.md
    verify/
      SKILL.md
    handoff/
      SKILL.md
```

`OUT-OF-SCOPE.md`, templates, examples, scripts, hooks, `.mcp.json`, `.app.json`, and assets are deferred unless real usage proves they are needed.

Minimum plugin manifest:

```json
{
  "name": "groundwork",
  "version": "0.1.0",
  "description": "Codex-native personal R&D workflow base for PRD, task slicing, planning, prototypes, implementation, verification, and handoff.",
  "skills": "./skills/"
}
```

MVP packaging acceptance:

1. `.codex-plugin/plugin.json` points to the bundled `skills/` directory.
2. Codex can install or enable Groundwork as a local plugin.
3. Codex can discover the eight bundled public skills from the plugin manifest's `skills` path and each skill's `SKILL.md` frontmatter.
4. Explicit invocation works for every public skill.
5. Natural Chinese invocation triggers the expected skill in fixture prompts.
6. No first-cut skill requires CLI, hooks, MCP, tracker API, external app auth, or source-framework installation.

## Verification And Readiness Contracts

### `ready-for-agent`

`ready-for-agent` requires all of the following:

- acceptance criteria exist
- source/evidence location is known, or the first inspection step is specified
- risk is low or medium, or the required `gate` point is identified
- expected artifact or output is clear
- stop condition is clear
- AFK/HITL decision points are marked
- blockers and out-of-scope boundaries are explicit

A task with only a title, vague request, or missing evidence path is `needs-info`, not `ready-for-agent`.

### `ready-for-human`

`ready-for-human` means Groundwork has gathered enough evidence, options, tradeoffs, and risks for a human decision, but should not continue autonomously.

`ready-for-human` requires all of the following:

- decision needed is explicit
- options or recommendation are clear
- evidence and uncertainty are separated
- risk of each option is stated
- next human action is specific
- no hidden implementation or external write is performed

### `implement`

`implement` may execute code changes and report local evidence, but it must stop before claiming final readiness. Readiness is decided by `verify` or by the user.

When a suspected bug or failing behavior is involved, `implement` must use its embedded `diagnose` branch: reproduce or inspect first, distinguish confirmed cause from plausible hypothesis, and avoid speculative edits.

### `verify`

`verify` is skeptical by default. It must not summarize implementation intent as evidence.

`verify` final reports begin with the complete six-field `Verification Scope` block before the verification summary or any specialized payload:

```text
Verification Scope
- In Scope:
- Out of Scope:
- Covered:
- Not Covered:
- Evidence Sources:
- User-visible Claim Being Verified:

Verification Summary
- Verdict: pass / partial / fail / blocked
- Claimed Behavior
- Source Evidence
- Test Evidence
- Runtime / Browser Evidence
- Data Readiness
- Environment Readiness
- Customer / UAT Readiness
- Risks
- Unverified Claims
- Next Action
```

If evidence is unavailable, `verify` must say `unverified` and explain the missing check. Customer-facing wording is optional and short; the main output remains engineering readiness.

## Skill Eval Plan

Groundwork MVP needs lightweight regression fixtures before production skill writing is considered complete.

Groundwork should not invent all skill-authoring checks from scratch. Before custom eval harness work, use existing skill-authoring workflows as references or helpers, including Codex `skill-creator`, Claude Code create-skill style workflows, and mattpocock `write-a-skill`. These helpers inform how Groundwork skills are created, reviewed, and optimized; they are not public Groundwork skills in MVP.

Every public skill should pass an authoring review before fixture evaluation:

- description has clear trigger words and should/should-not boundaries
- `SKILL.md` stays concise and uses progressive disclosure
- instructions set the right degree of freedom for the task
- scripts, references, assets, and examples are added only when they reduce repeated work or improve reliability
- bundled resources are discoverable from `SKILL.md` without deep reference chasing
- placeholder files and auxiliary docs are removed unless they are directly needed by the skill
- basic validation checks required frontmatter, naming, and plugin discovery metadata

Minimum eval fixtures:

- at least 5 prompts per public skill
- explicit invocation fixture
- natural Chinese invocation fixture
- realistic noisy invocation fixture
- should-not-trigger fixture
- direct-fallback fixture for small one-off work
- at least one risky-write or artifact-write boundary fixture across the suite
- at least one handoff fixture that checks artifact references rather than duplication

Suggested eval file layout:

```text
evals/
  prompts/
    to-prd.csv
    to-issues.csv
    triage.csv
    write-plan.csv
    prototype.csv
    implement.csv
    verify.csv
    handoff.csv
  baselines/
    2026-05-20-v0.1.md
```

Minimum CSV fields:

```csv
id,skill,should_trigger,prompt,expected_behavior,artifact_allowed,risky_write_allowed
```

Initial evals may be manual or script-assisted. The first milestone records a baseline; numeric thresholds become hard release gates only after the first fixture run reveals realistic behavior.

MVP success signals:

- each public skill can be invoked explicitly
- natural Chinese fixture prompts select the intended skill often enough to be usable
- small one-off fixture prompts do not create artifacts
- `verify` output includes concrete evidence or marks claims as unverified
- `handoff` is compact by default and references existing artifacts
- every skill output ends with one recommended next action

Forward-testing is useful for complex skills, but it is not the default path. When used, it should run in a fresh context with raw task artifacts, avoid leaking the expected answer, and avoid modifying live or risky systems without explicit approval.

## Borrowed Source Decision Log

Every borrowed source used in a public skill must have a short decision note before implementation:

- source project and path
- license or usage boundary
- decision: keep, rename, merge, adapt, use as authoring helper, or reject
- reason
- Groundwork-specific changes

This prevents Groundwork from becoming a loose bundle and keeps future rollback or replacement possible.

## Non-Goals

Groundwork MVP will not:

- create production skills before this PRD is reviewed
- become a standalone agent runtime
- wrap or depend on Trellis, Superpowers, gstack, BMAD, Spec Kit, Agent OS, GSD, or mattpocock/skills
- create a full task management system
- auto-run `to-prd -> to-issues -> triage -> write-plan -> implement -> verify -> handoff`
- force every task into PRD/issues/artifacts
- make `review`, `contract`, `diagnose`, `gate`, or `standards` standalone MVP skills
- copy deprecated or in-progress upstream skills as adoption candidates
- default to subagents
- mutate remote issue trackers, data, deployment targets, git remotes, or shared skills without explicit user intent

## Acceptance Criteria

MVP is acceptable when:

1. Codex can load or enable the plugin and discover the eight public skills.
2. Each skill has a trigger contract, concise trigger description, and clear stop conditions.
3. Small, one-off work falls back to direct work without creating artifacts.
4. `to-prd` can produce a PRD/spec from conversation and evidence.
5. `to-issues` can split a PRD/spec/plan into vertical slices with acceptance criteria, blockers, AFK/HITL classification, contract impact, verification evidence needed, and ready-for-agent missing fields.
6. `triage` can decide `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`, or closeout, includes severity and state transition reason, and `ready-for-agent` follows the readiness contract.
7. `write-plan` can produce executable implementation steps without forcing subagent-first or commit-heavy workflow, and does not invent exact file paths, APIs, schemas, or commands before inspection.
8. `prototype` supports both `LOGIC.md` and `UI.md` branches and always states the question being answered.
9. `implement` respects PRD/task/plan/source/diff/test evidence, runs diagnosis before speculative bug fixes, does not invent exact file paths, APIs, schemas, or commands before inspection, and does not claim final readiness.
10. `verify` separates claimed behavior, source evidence, test evidence, runtime/browser evidence, data readiness, environment readiness, customer/UAT readiness, and unverified assumptions, then recommends `triage closeout`, `gap closure`, `re-verify`, or `blocked needs-info` after the verification body.
11. `handoff` is compact by default and references existing artifacts, including existing `STATE.md`, instead of duplicating them.
12. All user-facing output defaults to Chinese unless the artifact target requires otherwise.
13. No first-cut skill requires external tracker API access, hooks, MCP, UI, app auth, source-framework installation, or a local task CLI.
14. Artifact safety rules prevent secrets, PII, credentials, and sensitive logs from being copied into durable files.
15. Groundwork `gate` is documented as a workflow preflight while Codex runtime safety remains the enforcement boundary.
16. Minimum eval fixtures exist for all public skills before production skill implementation is considered complete.

## Review Angles

Use this PRD for multi-angle review before implementation:

### Product Review

- Does this solve the user's real R&D workflow, not just create a skill collection?
- Is the MVP thin enough to run quickly but complete enough to close a workflow loop?
- Are the non-goals strong enough to prevent framework creep?

### Workflow UX Review

- Can the user invoke skills naturally in Chinese without memorizing exact English names?
- Does guided continuation avoid both over-automation and disconnected one-off outputs?
- Is direct fallback strong enough to keep small tasks small?

### Skill Design Review

- Are the eight public skills the right surface?
- Are `contract`, `diagnose`, `gate`, `scope`, `artifact`, and `standards` correctly embedded rather than standalone?
- Are trigger descriptions likely to be precise enough for Codex to load the right skill?

### Task Management Review

- Is issue-source-first task handling clear enough?
- Is local fallback constrained enough to avoid becoming a task database?
- Is `ready-for-agent` defined with enough evidence and acceptance criteria?

### Prototype Review

- Is direct adaptation of mattpocock `prototype` appropriate?
- Are Groundwork-specific additions enough for static HTML/UI prototype creation and review?
- Does the cleanup/absorb rule prevent prototype rot?

### Implementation Review

- Is the proposed first-cut asset structure small enough?
- Are any scripts needed before real usage, or should they wait?
- Are there missing plugin packaging requirements from Superpowers' Codex plugin shape?

### Safety Review

- Are risky writes gated clearly?
- Are remote tracker updates and local file writes sufficiently controlled?
- Are secrets and sensitive data excluded from artifacts?

## Resolved MVP Decisions

1. `to-prd` stays conversation-first. It writes a file only when the user asks, the result needs review/reuse/handoff, or it becomes a task source of truth.
2. `to-issues` outputs tracker-neutral markdown by default. It may include an optional GitHub/Linear paste-ready variant, but MVP does not call tracker APIs.
3. `triage` defers `OUT-OF-SCOPE.md` until repeated usage proves the need. It remains an optional future reference, not an MVP default file.
4. `write-plan` includes exact file paths only after source inspection confirms them. Before inspection, it lists likely areas to inspect without inventing paths.
5. `prototype/UI.md` defaults to one minimum verifiable prototype. Multiple variants are used only when requested or when the problem is explicitly about visual or interaction tradeoffs.
6. `verify` keeps engineering readiness as the main output. It may add a short optional customer/UAT note, but it is not a customer-message generator.
7. Plugin docs must include suggested Chinese trigger phrases for every public skill.
8. Implementation notes are conversation-only by default. Durable implementation notes are optional decision artifacts only for nontrivial review, verification, or handoff needs, and follow `docs/implementation-notes-policy.md`; Groundwork does not require a running `implementation-notes.html` or Markdown file during `implement`.
