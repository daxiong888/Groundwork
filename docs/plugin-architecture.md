# Plugin Architecture

Groundwork should ship as a small Codex-native personal R&D base. Its product surface is broader than skills: bounded skills handle judgment-heavy work, deterministic scripts/tools handle repeatable mechanics, and small repo-local task artifacts preserve durable R&D state when that state creates value.

The implementation stance is intentionally pragmatic: use Superpowers as the Codex plugin skeleton reference, use mattpocock/skills as the strongest lightweight workflow/skill reference, then curate both into Groundwork-native skill names, task semantics, scripts, and artifact rules.

It should not become a standalone agent runtime, project adapter bundle, compatibility layer, or market-positioning exercise against other frameworks.

It should also not become a blind Superpowers + mattpocock bundle. The borrowed pieces must pass through Groundwork's R&D loop: PRD/spec, task context, plan, prototype/contract/design when needed, implementation, verification/UAT, and handoff.

## Source Of Truth

`docs/prd.md` is the v0.1 product source of truth. This architecture document explains implementation shape, but must not expand MVP scope beyond the PRD. If implementation reveals a missing product decision, patch `docs/prd.md` first instead of adding hidden behavior inside skills.

## Current Stage

Current `main` contains v0.4.0 native worktree handoff alignment. Groundwork remains a small Codex-native R&D base: it governs route, policy, evidence, handoff, and closeout contracts while Codex App/runtime adapters own actual worktree creation, Handoff execution, runtime execution, and cleanup operations.

Current contents:

- `.codex-plugin/plugin.json`
- `docs/` product and architecture docs
- `evals/` prompt fixtures, structured smoke, safety, and reliability fixtures, scenario fixtures, fixture repos, baselines, and runtime trial checklist
- `research/` source research and scenario analysis
- `skills/` nine public skills, including `dispatch`, plus required shared guardrails and adapter contracts
- `scripts/` optional future scripts directory, currently empty except `.gitkeep`

The repository includes runtime and eval evidence accumulated across v0.1 through v0.4.0, including plugin discovery, representative workflow trials, fixture validation, Codex App runtime-safety follow-up, dispatch routing coverage, managed-worktree lifecycle contract coverage, governance baseline hardening, and native worktree handoff alignment evidence. The v0.4.0 line does not add task tools, hooks, MCP servers, marketplace publishing flow, or task CRUD.

## MVP Surface

The MVP should cover a thin but complete R&D loop before deepening any single mode:

```text
PRD/spec -> task -> plan -> prototype/contract/design as needed -> implementation -> verification/UAT -> release/handoff
```

This means the first release should expose action-named skills rather than abstract mode names. Because Groundwork itself is the plugin namespace, public skill folder names do not need a repeated `groundwork-` prefix. If any skill is later distributed outside the plugin as a global standalone skill, add a prefix then to avoid collisions.

| Component | Purpose | Why first |
| --- | --- | --- |
| `to-prd` | Turn conversation, source evidence, prototype notes, UAT feedback, or rough requirements into a PRD/spec. | Contract and implementation artifacts are downstream; the workflow needs product/spec intent first. |
| `to-issues` | Split PRD/spec/plan into vertical task slices and link them to the best task source. | Borrows mattpocock's `to-issues` clarity while keeping Groundwork issue-source-first. |
| `triage` | Inspect, classify, unblock, mark AFK/HITL, move to `ready-for-agent` or `ready-for-human`, and close task context. | Separates task state management from task generation; a single abstract task skill would be too broad. |
| `write-plan` | Turn accepted task context into implementation steps, dependencies, stop conditions, and verification checkpoints. | Uses an action name closer to "write a plan" instead of an abstract planning module name. |
| `prototype` | Build, revise, and review throwaway prototypes that answer a specific design question, including logic/state prototypes and UI/static HTML prototypes. | This can directly adapt mattpocock's `prototype` structure because its two-branch model fits Groundwork's R&D use cases. |
| `implement` | Execute or review code changes against PRD/task/plan/source/diff/tests. | Coding is a high-frequency daily workflow and must not depend on peer runtimes. |
| `verify` | Check tests, runtime behavior, UAT/SIT readiness, and release acceptance. | Separates code pass, data readiness, environment readiness, and customer validation. |
| `handoff` | Preserve compact state for long-running R&D work. | Prevents repeated rediscovery after context transitions. |

Supporting behaviors should be embedded in these skills before becoming standalone skills:

| Branch | Owner | Trigger | Output |
| --- | --- | --- | --- |
| `scope` | `to-prd`, `to-issues` | Acceptance, success condition, or user intent is unclear or conflicting. | Clarified acceptance delta, explicit open questions, and whether to continue or stop. |
| `contract` | `write-plan`, `prototype`, `implement`, `verify` | API, DB, state, frontend behavior, docs, or environment alignment affects correctness. | Minimal contract table or checklist tied to source evidence, not a standalone architecture doc. |
| `artifact` | all public skills that may write durable files | Output has a target reader, review need, execution need, verification need, or handoff need. | Artifact purpose, target reader, downstream action, and write/update recommendation. |
| `diagnose` | `implement` | A bug, failing test, runtime anomaly, or unclear cause must be confirmed before edits. | Confirmed cause, rejected hypotheses, or `not confirmed`; no speculative fix without evidence. |
| `gate` | `implement`, `verify`, `handoff` | Deploy, publish, push, migration, destructive command, data write, remote tracker mutation, or shared-skill mutation is requested. | Proposed action, target, risk, rollback/undo note, and explicit approval request. |
| `standards` | review lens only | Repeated work shows repo conventions or quality standards are being rediscovered. | Inline review criteria; standalone skill deferred until repeated usage proves the need. |

## Skill Design Rules

Each skill should include:

- narrow trigger description
- trigger contract with should-trigger and should-not-trigger examples
- evidence to inspect before writing
- direct-answer path for small questions
- artifact path only when durable output is useful
- verification/reporting requirements
- stop conditions
- explicit non-goals
- progressive disclosure: keep `SKILL.md` short, and move long examples, templates, references, and scripts into separate bundled files only when repeated use proves the need
- a `zoom-out` escape hatch for unfamiliar code areas: map modules/callers and source truth before proposing architecture or implementation work
- a Groundwork-native review lens when code changes are involved: compare the diff against both the originating PRD/spec/task and documented repo standards; do not copy mattpocock's in-progress `review` skill as-is

Each skill should avoid:

- requiring subagents
- requiring installation of source frameworks used for research
- assuming `.trellis/`, `.planning/`, or `.gsd/` artifacts exist
- committing, pushing, deploying, publishing, or mutating remote state unless explicitly requested
- turning a one-off direct answer into a durable artifact
- copying personal, deprecated, or in-progress source-framework skills verbatim
- treating deprecated source-framework skills as adoption candidates when a newer replacement exists
- making parallel subagents the default path for design, review, or architecture exploration

When a prompt could match multiple skills, choose the lightest skill that answers the user's current intent:

- clarify intent, acceptance, or requirement shape -> `to-prd`
- split accepted intent into work units -> `to-issues`
- decide readiness, blockers, AFK/HITL, or closeout -> `triage`
- plan accepted work before edits -> `write-plan`
- make code changes -> `implement`
- answer visual, interaction, state, or business-rule uncertainty with a throwaway artifact -> `prototype`
- check readiness, evidence, UAT/SIT, runtime behavior, or release confidence -> `verify`
- preserve compact continuity across sessions -> `handoff`
- small, one-off, low-risk, obvious work -> direct fallback

## Proposed Skill Layout

```text
skills/
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

`OUT-OF-SCOPE.md`, templates, examples, scripts, hooks, `.mcp.json`, `.app.json`, and assets are deferred unless real usage proves they are needed. Add supporting examples only after the first real task validates the workflow:

```text
skills/<skill-name>/examples/
skills/<skill-name>/templates/
```

Do not add broad shared references until there is repeated need. Small skill files are easier to trigger correctly and easier to review.

## First-Cut Skill Assets

Do not give every skill the same folder shape by default. Mirror the borrowed skill only where the borrowed skill proves the asset is useful:

| Skill | Borrowed shape | First-cut assets |
| --- | --- | --- |
| `to-prd` | mattpocock `to-prd` keeps the PRD template inline in `SKILL.md`. | `SKILL.md` with compact PRD output format. Add `templates/prd.md` only if the inline format becomes too long. |
| `to-issues` | mattpocock `to-issues` keeps vertical-slice rules and issue template inline. | `SKILL.md` with vertical-slice rules and issue output format. No script or tracker API in MVP. |
| `triage` | mattpocock `triage` uses `AGENT-BRIEF.md` and `OUT-OF-SCOPE.md` reference files. | `SKILL.md`, `AGENT-BRIEF.md`; `OUT-OF-SCOPE.md` deferred until repeated usage proves the need. |
| `write-plan` | Superpowers `writing-plans` is a detailed SKILL with plan header and task structure. | `SKILL.md` with Groundwork's lighter plan format. Do not copy Superpowers' commit-heavy or subagent-first defaults. |
| `prototype` | mattpocock `prototype` uses branch references: `LOGIC.md` and `UI.md`. | Directly adapt this shape: `SKILL.md`, `LOGIC.md`, `UI.md`. Keep the core rule that a prototype is throwaway code that answers a question. Groundwork-specific additions should cover static HTML prototype review, browser verification, and feedback into PRD/task/contract/implementation. |
| `implement` | Source ideas are behavioral: Trellis implement/check, Superpowers execution discipline, mattpocock diagnose/TDD/review signals. | `SKILL.md` only at first; link to `diagnose` / review lens sections inside the skill. |
| `verify` | Source ideas are behavioral: Superpowers verification-before-completion, gstack QA, GSD UAT evidence. | `SKILL.md` plus a small verification output format inline. Add `templates/verification.md` only after repeated use. |
| `handoff` | mattpocock `handoff` is intentionally tiny and avoids duplication. | `SKILL.md` only, with a compact handoff format and artifact-reference rule. |

Scripts are not required for the first cut. Add scripts only after a repeated operation is clearly deterministic and failure-prone, such as local fallback task indexing or artifact link validation. Do not build task CRUD, tracker API integration, hooks, MCP, UI, or a CLI until the skills have been used on real work.

## Task Source Strategy

Groundwork should not own a full task-management system. It should resolve a task context from the best available source:

- current conversation
- user-provided PRD/spec/task document
- GitHub/GitLab issue
- Linear/Jira or another issue tracker described by the user
- TaskRepo markdown task
- future Symphony issue/run context
- local markdown fallback

When an external source exists, Groundwork should link to it and preserve its authority. When no external source exists and durable state is useful, Groundwork can create a local fallback task.

Task states should stay small and agent-oriented:

- `draft`
- `needs-info`
- `ready-for-agent`
- `ready-for-human`
- `in-progress`
- `verification`
- `done`
- `wontfix`

Task breakdown should use vertical slices rather than horizontal layer buckets. Each slice should have acceptance criteria, blockers, and an execution type:

- `AFK`: an agent can implement it with no further human context.
- `HITL`: it requires human judgment, design review, access, or manual validation.

Each `to-issues` slice should also carry task-state fields that make later `triage` deterministic:

- `Contract Impact`: API / DB / UI state / docs / verification contract / none.
- `Verification Evidence Needed`: the evidence required before closeout.
- `Ready-for-Agent Missing Fields`: readiness-blocking fields that must be completed before `triage` can mark the task ready.

`to-issues` may identify a `ready-for-agent candidate`, but only `triage` can make the final readiness decision.

`ready-for-agent` should mean the task has an agent-ready brief, not merely a title. The brief should include current behavior, desired behavior, key interfaces, acceptance criteria, blockers, out-of-scope boundaries, verification expectations, known source/evidence location or first inspection step, risk or required `gate`, clear stop condition, and AFK/HITL decision points. When an external issue tracker owns the task, Groundwork should post or generate this brief in that source rather than duplicating it locally.

`ready-for-human` should mean Groundwork has gathered enough evidence, options, tradeoffs, and risks for a human decision, but should not continue autonomously. It requires an explicit decision needed, clear options or recommendation, separated evidence and uncertainty, stated risk for each option, a specific next human action, and no hidden implementation or external write.

`triage` verdicts should include severity and transition reason. Severity describes the current blocker or gap impact, not overall task priority. If a task moves from `needs-info` to `ready-for-agent`, the verdict must identify the evidence added or fields completed.

`verify` does not close tasks directly. After the verification body it should recommend `triage closeout`, `gap closure`, `re-verify`, or `blocked needs-info` so task state returns to `triage` with evidence.

## Repo-Local Artifacts

Groundwork should default to direct answers and normal repo files. Use `artifacts/<workstream-slug>/STATE.md` only for workstream-scoped lifecycle state that meets the pause/resume, gap closure, UAT/release reuse, multi-stage, or pending-decision thresholds. Use optional `artifacts/<workstream-slug>/ROADMAP.md` only for true multi-milestone or sequencing work.

Older `.groundwork/tasks/<task-id>/` language is local scratch or fallback context when no better task source owns the work. It is not lifecycle state, not the default durable artifact location, and not a project task database.

Possible future artifact shape after real usage proves the need:

```text
.groundwork/
  tasks/
    2026-05-19-feature-slug/
      task.json
      prd.md
      plan.md
      prototype.md
      contract.md
      verification.md
      handoff.md
  index.md
```

This shape is not an MVP scaffold requirement. All files except `task.json` are optional and should be created only when the task needs that artifact.

Suggested `task.json` fields:

```json
{
  "id": "2026-05-19-feature-slug",
  "title": "Feature slug",
  "status": "ready-for-agent",
  "priority": "P1",
  "type": "feature",
  "execution": "AFK",
  "source": "local",
  "externalRef": "",
  "blockedBy": [],
  "artifacts": {
    "prd": "prd.md",
    "plan": "plan.md",
    "verification": "verification.md"
  }
}
```

Artifact rules:

- Keep files human-readable markdown/json.
- Keep each artifact tied to a concrete task or decision.
- Do not create empty template files for completeness.
- Redact logs, screenshots, copied requests, database rows, and handoff notes when they may contain sensitive values.
- Do not mirror `.trellis/`, `.planning/`, or `.gsd/`.
- Do not store secrets, credentials, private tokens, cookies, or sensitive personal data.
- Do not treat Groundwork artifacts as more authoritative than source/runtime truth.

## Scripts

Add deterministic scripts only when repeated operations need reliability beyond prompt instructions.

Good script candidates:

- plugin packaging validation
- skill surface linting
- external task link validation
- vertical-slice issue draft generation
- agent-ready brief scaffold
- task index generation
- artifact shape validation
- contract checklist scaffold
- markdown link/path validation

Defer task CRUD and artifact scaffolding until repeated real usage proves the need. The MVP should not require a local task CLI.

Avoid scripts for:

- business judgment
- generic artifact writing
- autonomous scheduling
- provider/model routing
- worktree orchestration
- source-framework migration

## Hooks

Hooks should be optional host integrations, not the core correctness mechanism.

Superpowers is the best packaging reference here: its Codex plugin surface is primarily `plugin.json + skills`, while its richer hook/session-start behavior appears in non-Codex runtime packaging. Groundwork should therefore keep artifacts and scripts hook-friendly, but the MVP should remain correct without hooks unless Codex plugin hook support is confirmed in the current platform.

Possible future hooks:

- session start: surface active Groundwork task index
- pre-edit: remind the agent to inspect `task.json`, PRD, and plan when inside a managed task
- pre-finish: check whether verification and handoff evidence were updated
- pre-risky-write: invoke the gate preview for deploy, publish, data write, destructive git, or shared-skill mutation

## Non-MVP Exclusions

Do not build these into the MVP:

- project-specific adapters such as `groundwork-hannah-cloud` or `groundwork-laihu-uat`
- working-hours/timesheet support
- full agile role systems
- virtual team orchestration
- database-backed runtime state
- web UI, TUI, MCP server, native engine, or standalone agent app
- global skill cleanup or shared `~/.agents/skills` mutation

Project-specific behavior can later live in repo-local Groundwork notes or optional examples, but the core plugin should stay general to R&D work.

## Installation And Packaging

Before publishing or installing broadly:

- validate `.codex-plugin/plugin.json`
- keep skill names stable and specific
- verify Codex discovers the plugin skills from the plugin manifest's `skills` path and each skill's `SKILL.md` frontmatter
- document install and update behavior
- document what files the plugin may create
- document that Groundwork does not install or wrap the frameworks it borrows ideas from

If marketplace metadata or `agents/openai.yaml` is needed later, add it only after the MVP skill surface stabilizes.

## Architecture Rules

- Keep plugin-local behavior inside this repository.
- Treat `docs/prd.md` as the v0.1 source of truth.
- Keep Groundwork-specific behavior in plugin skills or repo-local files.
- Do not edit shared `~/.agents/skills` for Groundwork-specific behavior.
- Do not require subagents for normal work.
- Keep skill descriptions narrow to prevent over-triggering.
- Prefer source/runtime evidence over generated artifacts.
- Prefer direct answers over artifacts for one-off work.
- Gate risky writes and remote mutations.
- Use deterministic scripts only for repeated mechanical checks.
- Do not invent exact file paths, APIs, schemas, commands, layout quality, or runtime behavior before inspection.
- Mark visual, interaction, state-transition, runtime, data, or environment claims as `unverified` when the needed evidence is unavailable.

## Eval Baseline

Skill authoring and eval fixtures should be written together. The MVP baseline uses prompt fixtures first, not a heavy custom harness.

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

Each public skill should start with at least five prompt fixtures: explicit invocation, natural Chinese invocation, realistic noisy invocation, adjacent false-positive, and small direct-fallback. Record the first run as a baseline before introducing numeric release thresholds.
