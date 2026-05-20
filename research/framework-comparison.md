# Framework Comparison

This document compares workflow systems that influenced Groundwork. It is a design input, not a dependency list.

## Source Snapshot

Accessed on 2026-05-19.

| Framework | GitHub source | Primary source evidence checked | License posture |
| --- | --- | --- | --- |
| Trellis | <https://github.com/mindfold-ai/trellis> | `README.md`, `.trellis/workflow.md`, `.trellis/config.yaml`, `.trellis/spec/`, `.trellis/agents/`, `packages/cli/package.json` | AGPL-3.0 |
| Superpowers | <https://github.com/obra/superpowers> | `README.md`, `skills/brainstorming`, `skills/writing-plans`, `skills/test-driven-development`, `skills/subagent-driven-development`, skills directory layout | MIT |
| gstack | <https://github.com/garrytan/gstack> | `AGENTS.md`, `codex/SKILL.md`, role skill directories such as `plan-eng-review`, `qa`, `review`, `ship`, `careful`, `freeze` | MIT |
| GSD / get-shit-done | <https://github.com/gsd-build/get-shit-done> | `README.md`, `docs/ARCHITECTURE.md`, `docs/COMMANDS.md`, `docs/CONFIGURATION.md`, `commands/gsd/`, `package.json` | MIT |
| GSD 2 | <https://github.com/gsd-build/gsd-2> | `README.md`, `VISION.md`, `package.json`, `gsd-orchestrator/`, `packages/`, `native/`, `docs/` | MIT |
| mattpocock/skills | <https://github.com/mattpocock/skills> | `README.md`, `skills/engineering/tdd`, `diagnose`, `grill-with-docs`, `setup-matt-pocock-skills`, `to-prd`, `to-issues`, `triage`, `prototype`, `zoom-out`, `improve-codebase-architecture`, `improve-codebase-architecture/INTERFACE-DESIGN.md`, `skills/productivity/handoff`, `grill-me`, `write-a-skill`; `skills/in-progress/review` checked as experimental only | MIT |
| BMAD-METHOD | <https://github.com/bmad-code-org/BMAD-METHOD> | `README.md`, module list, installation flow, workflow/agent claims, release metadata | MIT |
| GitHub Spec Kit | <https://github.com/github/spec-kit> | `README.md`, Spec-Driven Development phases, `specify init`, supported integration list, command flow | MIT |
| Agent OS | <https://github.com/buildermethods/agent-os> | `README.md`, standards discovery/deployment claims, spec-shaping capability, release metadata | MIT |

Local source retrieval note: the initial download attempts failed because the sandbox could not resolve GitHub and escalated HTTPS/GitHub CLI calls hit TLS/API errors. After the network issue was resolved, the source framework repositories were downloaded under `refer/github/frameworks/`. Both GSD repositories are now available locally: `gsd-build/get-shit-done` at commit `473c279` from 2026-05-19, and `gsd-build/gsd-2` at commit `76568ed` from 2026-05-18. The analysis below uses those local source clones as the primary evidence.

## Executive Summary

| Framework | Current shape | Best idea for Groundwork | Main risk for Groundwork | Groundwork decision |
| --- | --- | --- | --- | --- |
| Trellis | Multi-platform repo harness with `.trellis/spec`, `.trellis/tasks`, `.trellis/workspace`, Python scripts, and a TypeScript CLI | Repo-local, reviewable task context and spec injection | Mandatory task lifecycle, subagent defaults, and commit/finish ceremony can dominate small work | Borrow evidence files, context curation, and direct-mode escape hatches; avoid default task harness |
| Superpowers | Skill-pack methodology with explicit brainstorm → spec → plan → TDD → subagent execution → review | Strong behavioral skills with clear trigger points and concrete anti-patterns | Mandatory design approval, TDD absolutism, and subagent loops can reduce user control | Borrow small skill mechanics and verification discipline; avoid automatic all-task methodology |
| gstack | Role-driven skill suite for product, design, engineering, QA, browser testing, shipping, security, and guardrails | Practical review lenses and operational safety skills | Large role surface, telemetry/update preambles, browser assumptions, and global workflow branding | Borrow individual review lenses and safety controls; avoid installing a virtual org by default |
| GSD / get-shit-done | Meta-prompting, context-engineering, and spec-driven workflow layer with `.planning/`, slash/skill commands, phase planning, execution, UAT, review, and ship flows | Human-readable planning state, context-rot mitigation, phase workflow, and verification gates | Still assumes a large command surface, subagent-heavy execution, parallel waves, and permission-bypass-friendly automation | Use as the main GSD input; borrow artifact/state ideas, not its full phase engine |
| GSD 2 | Successor standalone TypeScript/Rust coding-agent runtime with database-backed state, CLI, TUI/web, worktrees, dispatch, recovery, telemetry, and MCP | Durable runtime state, recovery, observability, explicit unit hierarchy, and automation failure handling | Far beyond a Codex plugin: autonomous execution, DB runtime, provider routing, native engine, and orchestration complexity | Keep as an adjacent runtime reference; avoid becoming this kind of agent app |
| mattpocock/skills | Small composable engineering/productivity skills plus repo-local domain docs and issue-tracker setup | Human-controlled workflow pieces: issue-source-first tasks, vertical slices, triage, agent briefs, prototypes, handoffs, code truth, domain language, and behavior tests | Assumes issue tracker/domain-doc setup, includes personal material and experimental areas, and carries some Claude-era packaging | Borrow composability, task-source abstraction, `CONTEXT.md`/ADR separation, prototype/handoff discipline, diagnosis loops, interface-design thinking, and vertical TDD; adapt to Codex-local truth |
| BMAD-METHOD | Full agile AI development framework with modules, workflows, specialist agents, and scale-adaptive planning | Planning depth changes with task complexity instead of one-size-fits-all ceremony | Large agent/persona/workflow surface can overtake user control and existing repo truth | Borrow scale-adaptive planning; avoid adopting the full agile-method package |
| GitHub Spec Kit | Officially backed Spec-Driven Development toolkit with CLI-generated specs/plans/tasks and agent integrations | Strong spec-as-contract workflow and explicit constitution/spec/plan/tasks/implement phases | More greenfield/spec-first than Groundwork's UAT and brownfield contract-checking needs | Borrow spec contracts and phase clarity; adapt for brownfield evidence and integration truth |
| Agent OS | Lightweight standards discovery/injection and spec-shaping system for AI coding agents | Extract and inject codebase standards without owning full execution | Narrower than Groundwork: mostly standards/specs, not runtime/UAT/evidence workflows | Borrow standards discovery and indexing; keep Groundwork broader but still lightweight |

The strongest shared lesson is that reliable agent work needs explicit source-of-truth files, not just better prompts. The strongest negative lesson is that a workflow layer becomes counterproductive when it claims ownership of every task.

Groundwork should be a Codex-native control surface for evidence-first work: choose the lightest workflow that can produce accepted evidence, write durable artifacts only when they will be reused, and leave orchestration to Codex unless a real repeated operation needs deterministic code.

## Comparison Dimensions

| Dimension | Trellis | Superpowers | gstack | GSD / get-shit-done | mattpocock/skills | Groundwork implication |
| --- | --- | --- | --- | --- | --- | --- |
| Unit of work | Task directory with PRD, JSONL context, status, research, archive | Design/spec and implementation plan files | Skill invocation, role review, browser/ship command | Project → phase backed by `.planning/` artifacts; plans can be executed in waves | Skill invocation; optional issue/doc setup | Groundwork should support task artifacts but not require them for direct work |
| Context strategy | Inject specs from `.trellis/spec` and curated `implement.jsonl` / `check.jsonl` | Skill instructions decide when to read/write specs and plans | Role skills plus session state in `~/.gstack` | `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, phase `CONTEXT.md`, research and UAT files | Domain glossary, ADRs, issue tracker config | Prefer local truth discovery plus small evidence files over persistent runtime state |
| Planning style | PRD first; task creation strongly encouraged | Brainstorm before creative work; write design and plan | Product/CEO/design/eng review before build | `new-project` → `discuss-phase` → `plan-phase`, with research and plan verification | Grill the user and docs, one question at a time | Use planning only when ambiguity or acceptance risk justifies it |
| Execution style | Subagent implement/check by default on supported platforms; inline paths exist | Subagent-per-task with two-stage review | Skill-specific role execution; QA/browser/release modes | `execute-phase` runs plan waves, often with fresh subagent contexts and atomic commits; `quick` exists for trivial work | Mostly single-skill guidance; human-controlled | Do not make subagents default; use them only for clear parallel payoff |
| Verification | Trellis check agent, lint/typecheck/tests, finish workflow | TDD, code review, verification-before-completion | Review, QA, browser, health, release checks | `verify-work`, UAT artifacts, code review, plan-review convergence, package legitimacy checks | Fast feedback loop first, regression test when correct seam exists | Groundwork should require explicit verification evidence but keep the mechanism lightweight |
| Memory and learning | `.trellis/workspace` journals; spec updates after tasks | Plan/spec files under docs; skill knowledge mostly in repo | `~/.gstack` sessions, learnings, analytics | Human-readable `.planning/` docs, `STATE.md`, learnings, codebase maps, optional graph/intel artifacts | `CONTEXT.md`, `docs/adr/`, setup docs | Store durable business/project learning in reviewable repo docs, not opaque global state |
| Autonomy bias | Medium to high | High once plan is approved | Medium to high, depending on skill | High for phase work, though direct and quick modes exist | Low to medium | Groundwork should bias toward user-steered work and explicit acceptance signals |
| Portability | Multi-agent platform generation | Multi-agent skill framework | Claude-first with Codex support paths | Multi-runtime skill/command installer including Codex | Agent-skill package with setup assumptions | Groundwork should be Codex-native first, with portable concepts only where cheap |

## Additional Framework Dimensions

The table above keeps the original five-system comparison readable. These three additional frameworks are close enough to include in the main research set, but they stress different design questions.

| Dimension | BMAD-METHOD | GitHub Spec Kit | Agent OS | Groundwork implication |
| --- | --- | --- | --- | --- |
| Unit of work | Agile workflows, stories, modules, and agent-guided phases | Spec, implementation plan, task list, implementation command set | Standards and specs shaped from codebase conventions | Groundwork should separate "work item" from "evidence artifact"; not all useful evidence is a task |
| Context strategy | Module and agent manifests plus phase-specific documents | Generated project principles, specs, plans, and tasks | Discover standards, index them, inject relevant ones | Groundwork should discover local truth and inject only relevant context |
| Planning style | Scale-adaptive: quick flow, full method, or enterprise track | Spec-first: define intent before implementation | Shape spec against project standards | Groundwork's scope mode should explicitly choose planning depth |
| Execution style | Specialist agents and workflows drive the lifecycle | Agent integration implements from generated artifacts | Works alongside existing agents rather than replacing them | Groundwork should prefer "alongside Codex" over a competing runtime |
| Verification | Review/test/commit workflow claims plus Test Architect module | Task/implementation phases depend on agent/tool checks | Standards alignment more than runtime verification | Groundwork still needs explicit runtime, API, DB, UI, and UAT verification |
| Memory and learning | Framework/module config and project artifacts | Versioned specs and plans | Indexed standards | Groundwork should keep durable learning reviewable and repo-local |
| Autonomy bias | Medium to high | Medium | Low to medium | Groundwork should stay user-steered by default |
| Portability | Multiple AI IDE/tool integrations | Multiple coding-agent integrations, including Codex | Claude Code, Cursor, Antigravity, and similar tools | Portability is useful, but Codex-native behavior should remain first-class |

## Trellis

Trellis is not just a prompt pack. Its current source shows a full repo-local harness:

- `.trellis/spec/` stores package/layer guidelines.
- `.trellis/tasks/{MM-DD-name}/` stores `prd.md`, `implement.jsonl`, `check.jsonl`, `task.json`, optional `research/`, and `info.md`.
- `.trellis/workspace/<developer>/` stores session journals and indexes.
- `.trellis/scripts/` controls developer identity, task lifecycle, active-task pointers, context lookup, PR creation, and journal recording.
- `packages/cli` publishes `@mindfoldhq/trellis` with `trellis` / `tl` binaries.

The real value is the separation between durable project knowledge and per-task execution context. Specs are not "remembered"; they are injected through files. Task research is not left in chat; it is written under the task. `implement.jsonl` and `check.jsonl` force a curation step before subagents act, which prevents generic agents from reading either too much or too little.

The main risk is that Trellis makes the managed task path the default. Its workflow text says even "small" work should not be downgraded unless the current user message explicitly contains an escape phrase. It also defaults to main-session coordination with implement/check subagents on supported platforms, then expects spec update, commit, and finish/archive discipline.

Groundwork should borrow:

- repo-local evidence artifacts for PRDs, research, context maps, and acceptance evidence
- explicit distinction between direct answers and managed tasks
- context curation before implementation or review
- finish/resume discipline for long-running work
- "research output must be written to files" for work likely to survive compaction

Groundwork should avoid:

- default task creation for every implementation
- requiring subagents before main-session work
- mandatory commit/finish lifecycle
- `.trellis/` as a universal source of truth
- promoting every post-task observation into durable project spec

## Superpowers

Superpowers is a methodology expressed as skills. The source tree currently exposes skills for brainstorming, writing plans, executing plans, TDD, subagent-driven development, code review, verification, git worktrees, finishing branches, and skill writing.

Its strongest idea is that each skill is explicit about when it should fire and what failure modes it is preventing. Examples:

- `brainstorming` says it must run before creative work, asks one question at a time, and blocks implementation until a design is approved.
- `writing-plans` writes plans for an engineer with no codebase context and decomposes work into bite-sized, testable tasks.
- `test-driven-development` makes the red/green cycle concrete and treats "test passed immediately" as evidence that the test is not proving the new behavior.
- `subagent-driven-development` uses fresh subagents per task with spec-compliance review before code-quality review.

This is valuable because it encodes engineering discipline as concrete behaviors rather than vague advice. It is also risky because the skills are intentionally forceful. Mandatory brainstorming for "every project", mandatory design approval, hardline TDD language, and subagent loops can turn a two-line fix into a process exercise.

Groundwork should borrow:

- skills as small behavioral units with clear trigger descriptions
- one-question-at-a-time clarification for ambiguous work
- plan files that name exact files, verification commands, and acceptance checks
- vertical TDD for deterministic behavior changes
- verification-before-completion as a non-negotiable reporting habit

Groundwork should avoid:

- automatic heavy activation before simple edits
- dogmatic TDD for configuration, docs, throwaway prototypes, or low-risk UI copy
- subagent-per-task as a default execution model
- storing Groundwork outputs under `docs/superpowers/`-style fixed paths

## gstack

gstack is a large role and workflow suite. Its `AGENTS.md` describes skills for plan-mode reviews, implementation/review, release/deploy, operational memory, browser/agent integration, and safety/scoping. The surface includes `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/review`, `/investigate`, `/qa`, `/ship`, `/land-and-deploy`, `/context-save`, `/context-restore`, `/careful`, `/freeze`, `/guard`, `/browse`, and more.

The best part is not the role naming itself. The best part is that each role lens asks a different kind of question:

- CEO/product review checks whether the request is the right product bet.
- Engineering review checks architecture, data flow, edge cases, tests, performance, and rollout risk.
- Design review checks visual quality and interaction fit.
- QA uses real browser flows, not just static review.
- Security uses OWASP/STRIDE-style threat lenses.
- Safety skills such as `careful` and `freeze` constrain destructive or over-broad work.

The risk is surface area and runtime assumption. Some skills include update checks, telemetry prompts, `~/.gstack` session files, Claude paths, browser-daemon assumptions, and role branding. Installing the whole thing would pull Groundwork away from evidence-first Codex workflows into a "virtual software team" operating model.

Groundwork should borrow:

- named review lenses as optional checklists, not personas
- a separate investigation mode that forbids fixes before evidence
- browser QA when user-visible behavior is the acceptance signal
- scoping guardrails like freeze/careful, adapted to Codex permissions
- release readiness as a distinct review mode

Groundwork should avoid:

- role theater that produces generic commentary
- default global browser/tool policy changes
- telemetry/update preambles inside normal workflow skills
- hidden state under `~/.gstack` as a dependency
- treating every feature as a mini startup/product review

## GSD: get-shit-done vs GSD 2

There are two relevant GSD repositories, and they should not be treated as interchangeable.

| Repository | What it is | Fit as Groundwork comparator |
| --- | --- | --- |
| `gsd-build/get-shit-done` | A meta-prompting, context-engineering, and spec-driven workflow system for Claude Code, Codex, OpenCode, Gemini CLI, Cursor, and similar runtimes | High. This is the better same-level comparison because it installs commands/skills into existing agent runtimes and stores workflow evidence in human-readable project files |
| `gsd-build/gsd-2` | The successor standalone coding-agent runtime built on the Pi SDK with DB-backed state, CLI, TUI/web, MCP, worktrees, provider routing, native packages, and autonomous auto mode | Low as a direct input. Useful mainly as an upper-bound reference for what Groundwork should not become |

The better primary comparator for Groundwork is `get-shit-done`, not `gsd-2`.

`get-shit-done` is still heavy, but it sits at the same workflow layer Groundwork is exploring. Its source describes a lightweight meta-prompting, context-engineering, and spec-driven system, with commands such as `/gsd-new-project`, `/gsd-discuss-phase`, `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-verify-work`, `/gsd-ship`, `/gsd-map-codebase`, `/gsd-code-review`, `/gsd-ui-review`, `/gsd-debug`, `/gsd-fast`, `/gsd-quick`, and `/gsd-sketch`. Its project state lives under `.planning/` as `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, phase `CONTEXT.md`, research, UAT, review, learning, graph, and report artifacts.

This overlaps with Groundwork's target more directly than GSD 2:

- it treats context rot as a first-class problem
- it uses durable markdown/JSON artifacts rather than only chat history
- it has explicit phase discussion, planning, execution, verification, UAT, review, and ship surfaces
- it includes direct/quick modes for small tasks
- it supports Codex as one runtime rather than replacing Codex
- it exposes useful adjacent ideas such as codebase mapping, UI review, debug, docs verification, learnings extraction, and state drift checks

The risk is that `get-shit-done` still wants to own a full phase lifecycle. It assumes `.planning/` as the project workflow directory, provides a large command surface, encourages subagent orchestration, supports parallel execution waves, and documents permission-bypass-friendly automation patterns. For Groundwork, those are design warnings: helpful for comparison, too broad to copy.

`gsd-2` has moved beyond markdown workflow into agent runtime territory. Its README explicitly positions it as the evolution of `get-shit-done` into a real coding agent. The source includes package workspaces, Pi SDK agent components, native/Rust packages, MCP server, web/TUI surfaces, `.gsd/` projections, and a SQLite database as authoritative runtime state.

Its core shape is:

- milestone -> slice -> task hierarchy
- fresh context per task
- automatic planning, execution, verification, completion, reassessment, and next-slice dispatch
- DB-backed state, memories, workers, leases, locks, paused sessions, and crash recovery
- worktree isolation and merge/cleanup lifecycle
- TUI, web UI, headless mode, MCP, extension system, provider routing, cost/token reporting, and native execution helpers

The value of GSD 2 for Groundwork is mostly conceptual. It proves that long-horizon autonomous work needs a durable state machine, not just prompt discipline. It also shows which concerns become real once autonomy is high: recovery, locks, costs, orphaned worktrees, provider errors, state projections, and operator UI.

Groundwork should borrow from `get-shit-done`:

- human-readable project state files for durable context
- context-rot prevention through explicit context curation
- phase discussion before planning when decisions are underspecified
- verification and UAT artifacts before closeout
- quick/direct paths for trivial work
- codebase mapping, UI review, docs verification, and learnings extraction as optional modes
- state drift checks as a concept for long-running work

Groundwork should borrow from GSD 2 only sparingly:

- milestone/slice/task vocabulary for genuinely large work
- "task must fit in one context window" as a slicing heuristic
- recovery and observability ideas: what changed, what was verified, what is blocked, what remains
- explicit failure states instead of optimistic completion

Groundwork should avoid:

- database-backed runtime state in the initial plugin
- autonomous `/auto` loops
- provider/model routing ownership
- worktree management and merge strategy as core Groundwork behavior
- cost dashboards, web UI, TUI, MCP server, native engine scope, and standalone agent-runtime responsibilities

## mattpocock/skills

mattpocock/skills is closest to Groundwork's desired operating style: small, human-controlled engineering skills rather than a whole agent runtime. Its README explicitly contrasts this approach with systems that "own the process." The source tree groups skills by engineering, productivity, misc, personal, deprecated, and in-progress.

The strongest engineering patterns are:

- `tdd` emphasizes behavior through public interfaces, vertical tracer bullets, one test at a time, and refactor only after green.
- `diagnose` starts with a fast deterministic feedback loop, then reproduce, hypothesize, instrument, fix, regression-test, and clean up.
- `grill-with-docs` challenges plans against `CONTEXT.md`, ADRs, code truth, and precise domain language.
- `setup-matt-pocock-skills` makes repo-specific assumptions explicit: issue tracker, triage labels, and domain-doc layout.
- `to-prd` turns current conversation and codebase understanding into a PRD, then publishes it to the configured issue tracker.
- `to-issues` breaks a PRD/spec/plan into independently grabbable vertical-slice issues, marked as HITL or AFK with blockers and acceptance criteria.
- `triage` moves issues through a small state machine: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`.
- `prototype` frames throwaway prototypes as tools that answer a specific question, split into logic/state prototypes and UI variants.
- `handoff` avoids duplicating existing artifacts and instead references PRDs, plans, ADRs, issues, commits, diffs, and next-session focus.
- `zoom-out` asks for a higher-level module/caller map when the agent is too deep in implementation details.
- `improve-codebase-architecture` looks for "deepening" opportunities: fewer shallow pass-through modules, stronger interfaces, better locality, and tests through the interface.
- `improve-codebase-architecture/INTERFACE-DESIGN.md` is the current successor to the deprecated `design-an-interface` skill for "Design It Twice" interface exploration.
- `write-a-skill` uses progressive disclosure: keep `SKILL.md` concise, move large references/examples/scripts into bundled files, and make trigger descriptions precise.
- `review` exists only under `skills/in-progress/`; treat it as an experimental signal, not a stable upstream skill to copy.

Deprecated skills should not be absorbed as source material:

- `design-an-interface` is deprecated; use the newer `improve-codebase-architecture/INTERFACE-DESIGN.md` path if Groundwork needs interface-design guidance.
- `ubiquitous-language` is superseded by the newer `CONTEXT.md` direction.
- `qa` and `request-refactor-plan` are useful historical signals only; Groundwork should express bug intake and refactor planning through its own PRD/task/plan/review flow.
- `git-guardrails-claude-code` is Claude-specific; Groundwork can keep the safety principle, but should not copy the hook implementation.

This style is useful because it leaves the user in control while still improving agent behavior. It also matches Groundwork's real target: business-context-heavy work where source truth, domain vocabulary, and acceptance evidence matter more than a universal lifecycle.

The most important task-management lesson is that mattpocock/skills does not try to own a task database. It treats the issue tracker as the task system, then teaches agents how to create, split, triage, and brief issues. The local fallback is markdown under `.scratch/<feature>/`, where the PRD and issues live as files with a `Status:` line. That is closer to Groundwork's "personal base" direction than either a full Trellis lifecycle or a standalone task CLI.

The risk is that some skills assume a repo has or wants a specific issue-tracker and domain-doc layout. They also remain a personal skill collection, not a Codex-native plugin architecture.

Groundwork should borrow:

- composable skills with narrow triggers
- domain glossary and ADR separation
- diagnosis before fixes
- behavior-first tests through public interfaces
- "explore code instead of asking" when the answer is locally discoverable
- zoom out to a module/caller map when a code area is unfamiliar
- setup flows that present findings before writing repo conventions
- issue tracker as task source, not a hardcoded task database
- local markdown issue tracker fallback for solo/local work
- vertical-slice task breakdown with HITL/AFK classification
- `ready-for-agent` as a quality gate for whether an agent can work without more human context
- durable agent briefs with current behavior, desired behavior, key interfaces, acceptance criteria, and out-of-scope boundaries
- Groundwork-native diff review against both originating spec and repo standards; do not copy mattpocock's in-progress review skill as-is
- progressive disclosure for Groundwork skills, templates, references, and scripts
- optional safety gates as a host/hook feature, not a required runtime dependency

Groundwork should avoid:

- requiring issue tracker setup before basic value
- cloning personal skill names or paths
- creating docs lazily without a clear reuse reason
- assuming `CLAUDE.md` is the primary instruction surface
- treating deprecated or in-progress skills as adoption candidates
- making parallel-subagent exploration the default for everyday design/review work

## BMAD-METHOD

BMAD-METHOD is a large agile AI development framework. Its current source and README position it as an AI-driven agile development module inside a broader BMad ecosystem, with official modules for the core method, custom BMad Builder workflows, Test Architect, game development, and creative intelligence. The repository advertises 34+ workflows, 12+ domain experts, party mode, and a complete lifecycle from brainstorming to deployment.

The most important idea is scale-adaptive planning. BMAD explicitly distinguishes quick flows for bug fixes and small features from full PRD/architecture/UX planning and heavier enterprise tracks. That is closer to Groundwork's desired trigger policy than frameworks that route everything through one ceremony.

The risk is that BMAD still owns a lot of process. Specialized agents, workflow menus, module installation, phase maps, and party-mode collaboration can be useful for greenfield product creation, but they can also overfit the agent session to BMAD's method instead of the user's existing business, repo, UAT, and delivery constraints.

Groundwork should borrow:

- scale-adaptive planning depth
- explicit distinction between quick fixes, full feature work, and enterprise/compliance work
- test strategy as its own planning concern
- guided "what next" help for users who do not know which workflow to run

Groundwork should avoid:

- treating agile roles as required personas
- importing a full module ecosystem before the core plugin proves value
- party-mode or multi-agent collaboration as a default
- allowing framework artifacts to outrank local product and code truth

## GitHub Spec Kit

GitHub Spec Kit is a Spec-Driven Development toolkit, not just a prompt collection. Its README describes SDD as putting specifications at the center of AI-assisted development: intent before implementation, rich spec creation, multi-step refinement, and AI interpretation of the resulting artifacts. The `specify init` CLI bootstraps project files and supports multiple agent integrations, including Codex.

The core command shape is especially relevant to Groundwork:

- establish project principles
- specify what to build
- plan how to build it
- generate tasks
- implement through the selected coding agent

This is valuable because it treats the spec as a contract rather than a temporary planning note. It also cleanly separates "what" from "how", which matters when AI agents otherwise jump straight into implementation.

The risk is that Spec Kit's center of gravity is spec-driven construction. Groundwork's target work includes brownfield verification, frontend/backend/DB contract drift, UAT readiness, real-environment data checks, and customer-safe handoff. Those cases often start with existing source truth and observed behavior, not a blank spec.

Groundwork should borrow:

- spec-as-contract framing
- explicit phase names for constitution, specification, plan, tasks, and implementation
- agent-integration portability while keeping the generated artifacts stable
- support for both greenfield and brownfield enhancement

Groundwork should avoid:

- assuming a spec exists before evidence gathering
- treating generated tasks as more authoritative than controllers, schemas, enums, UI, or runtime behavior
- forcing Groundwork artifacts into Spec Kit command naming
- optimizing for greenfield creation over brownfield correctness

## Agent OS

Agent OS is a lighter system than Trellis, BMAD, or GSD. Its current README frames it as a way to inject codebase standards and write better specs for Spec-Driven Development. Its core capabilities are Discover Standards, Deploy Standards, Shape Spec, and Index Standards.

This is directly relevant to Groundwork's "local truth first" principle. Many agent failures come from stale or generic project instructions. Agent OS focuses on extracting existing standards, organizing them, and injecting only the relevant parts when shaping a spec.

The risk is narrowness rather than heaviness. Standards discovery and spec shaping are valuable, but Groundwork also needs diagnosis, UAT readiness, integration contract checks, runtime verification, and handoff artifacts. Agent OS is an input and alignment layer, not the whole workflow surface.

Groundwork should borrow:

- discover standards from the actual codebase before writing new conventions
- keep standards organized and searchable
- inject relevant standards instead of loading a monolithic instruction file
- shape specs against existing repo practices

Groundwork should avoid:

- reducing evidence-first work to standards management
- creating a separate standards index before there is repeated need
- assuming code standards answer business acceptance questions
- replacing runtime verification with standards compliance

## Adjacent Systems

These systems are useful ecosystem signals, but they are not direct inputs for the first Groundwork base.

### AgentHub

AgentHub advertises 20 specialist subagents, 42 skills, and 17 workflows for Claude Code and OpenAI Codex. The noteworthy design choice is approval-first execution: medium and heavy workflows show what will run and provide token estimates before dispatching.

Groundwork should borrow the workflow-weight idea:

- light workflows run directly
- medium workflows show a short preview
- heavy workflows require an explicit gate with agents, skills, scope, alternatives, and estimated cost

Groundwork should not import AgentHub's whole agent catalog. That would recreate the same role-surface risk seen in gstack and BMAD.

### Caliber / ai-setup

Caliber's `ai-setup` is best understood as agent-configuration infrastructure. It syncs codebase-tailored skills, MCPs, and config files for Claude Code, Codex, and Cursor. That makes it adjacent to Groundwork rather than a first-order workflow input.

Groundwork should watch this category for one reason: stale agent configuration is a real failure mode. If Groundwork later needs a project bootstrap/setup flow, it should learn from tools that scan the repo and generate/update agent config. It should not start by owning cross-agent config sync.

## Layers To Exclude

Several popular projects are important but sit at a different layer:

- AutoGen, CrewAI, LangGraph, and similar libraries are general agent application frameworks.
- OpenHands, Cline, Roo Code, and similar projects are coding tools or agent apps.
- GitHub Copilot coding agent, Claude Code, and Codex are runtimes/hosts, not comparable workflow layers.
- Generic skill directories and marketplaces are discovery surfaces, not frameworks by themselves.

Groundwork should cite these only when they clarify ecosystem placement, not as first-order design inputs.

## Groundwork Intake Implications

Groundwork should be a curated personal base, not a clone of any compared system. It should absorb transferable ideas into a Codex-native, evidence-first workflow layer:

1. Put PRD/spec and task management before implementation contracts.
2. Default to direct work when the acceptance signal is obvious.
3. Escalate into a managed task only when the work needs durable PRD, task state, plan, contract, verification, or handoff evidence.
4. Write durable artifacts only for durable value: PRDs, task records, plans, contract maps, UAT evidence, handoffs, ADRs, or reusable domain language.
5. Treat subagents as optional execution tools, not a methodology.
6. Keep global instructions and shared skills small; put Groundwork-specific behavior in the plugin.
7. Prefer local source truth and runtime evidence over generic framework ceremony.
8. Choose planning depth explicitly: quick direct work, scoped feature planning, or heavier release/UAT/compliance planning.
9. Make verification reporting mandatory, but let verification scale with risk.
10. Treat standards/specs as contracts to check against source truth, not substitutes for source truth.
11. Treat Groundwork as a personal base, not an adapter layer. It should not require installing Trellis, Superpowers, gstack, BMAD, Spec Kit, Agent OS, or any other compared framework.

## Framework Intake Boundary

Groundwork should stand on its own as a curated base:

- The comparison frameworks are research inputs, not runtime dependencies or rivals.
- Borrowed ideas should become Groundwork-native concepts, modes, checks, tools, or artifacts.
- Groundwork should not install, wrap, call, sync, or reconfigure another framework.
- Groundwork should not design around legacy artifacts produced by other frameworks.
- Groundwork-owned behavior should live in the Groundwork plugin, skills, and its own repo-local artifacts.

## Coverage Against The Target R&D Process

After including PRD and task management as first-class concerns, Groundwork's target process is broader than "planning docs" and broader than a skill pack, but still narrower than a full autonomous agent runtime.

Target chain:

```text
idea / request / bug / UAT signal
-> PRD / spec
-> task creation and slicing
-> task plan
-> static prototype / integration contract / technical design as needed
-> implementation / implementation review
-> verification / UAT readiness
-> release gate
-> handoff / learning
```

The compared frameworks each cover part of this chain:

| Framework | Strong coverage | Weak or missing against Groundwork's target |
| --- | --- | --- |
| Trellis | PRD, task directory, task metadata, active task, implement/check context, workspace memory | Strong task harness but too mandatory; PRD and task are tightly coupled to Trellis lifecycle |
| Superpowers | Brainstorming, plans, TDD, debugging, verification, subagent review | Strong method skills but weak persistent task management; plan files are not a task system |
| gstack | Product/design/engineering/QA/release review lenses | Broad role surface can help review, but does not give a focused artifact chain for PRD -> prototype -> contract -> UAT |
| GSD / get-shit-done | Project/requirements/roadmap/state, phase plans, UAT, code/UI/docs review, quick/direct modes | Strong project lifecycle but phase-oriented and command-heavy; heavier than Groundwork's desired task manager |
| GSD 2 | Autonomous implementation runtime, DB-backed durable state, recovery, verification gates, worktree/agent orchestration | Far beyond Groundwork's desired scope; optimizes standalone autonomous execution more than user-steered R&D artifacts |
| mattpocock/skills | Small composable skills, issue-tracker setup, PRD-to-issues, triage, ready-for-agent briefs, prototype, handoff, diagnose/TDD, docs challenge | Strongest lightweight task-workflow reference; weaker on UAT/release evidence and cross-layer contract artifacts, but much broader than the earlier one-line reading suggested |
| BMAD-METHOD | Scale-adaptive planning and full agile lifecycle | Useful planning-depth idea, but the role/workflow package is heavier than Groundwork's personal-base boundary |
| GitHub Spec Kit | Spec-as-contract, plan/tasks/implement phase clarity, independent user-story task organization | More spec-first/greenfield than Groundwork's brownfield evidence and operational handoff needs |
| Agent OS | Standards discovery, standards injection, spec shaping | Valuable standards layer, but not enough for implementation review, runtime verification, prototype, and UAT readiness |

The estimated fit is:

- Full R&D delivery chain coverage target: about 75-85%.
- High-frequency AI-assisted R&D work coverage target: about 85-90%.
- Deliberately out of scope: full autonomous scheduling, production observability, permanent CI/CD platform ownership, and installing source frameworks as dependencies.

## Task Management Evaluation

Groundwork needs its own task management layer. The layer should sit after PRD/spec and before implementation, and it should be light enough for Codex-native daily work.

| Framework | Task-management model | Strength | Weakness | Groundwork lesson |
| --- | --- | --- | --- | --- |
| Trellis | One task directory under `.trellis/tasks/{date-slug}/` with `task.json`, `prd.md`, optional research, `implement.jsonl`, `check.jsonl`, archive, active-task scripts, assignee, priority, branch, PR, subtasks, and lifecycle hooks | Best file-based task object among the compared systems; simple to inspect, easy to resume, and clear PRD/task linkage | Too coupled to Trellis lifecycle, agents, archive ceremony, and `.trellis` as source of truth | Borrow task directory + metadata + PRD + context curation; make lifecycle opt-in and Groundwork-native |
| GitHub Spec Kit | Feature folder with `spec.md`, `plan.md`, `tasks.md`, checklists, contracts, data model, quickstart; tasks organized by independently testable user stories | Best spec-to-task decomposition; strong independent slice discipline and traceability | Assumes spec-first flow and generated feature folders; less natural for bug/UAT/brownfield operational work | Borrow spec -> plan -> tasks, user-story slices, task IDs, parallel markers, and acceptance-driven task grouping |
| mattpocock/skills | Configured issue tracker, local markdown fallback under `.scratch/`, vertical-slice `to-issues`, triage roles, `ready-for-agent`, durable agent briefs | Best lightweight issue-centric task workflow; does not own a task database and keeps tasks tied to real issue trackers | Assumes setup docs and external tracker vocabulary; local fallback path is mattpocock-specific | Borrow task source abstraction, vertical slices, AFK/HITL, triage roles, and agent brief template; adapt paths and setup to Groundwork |
| GSD / get-shit-done | `.planning/PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, phases, plans, UAT, summaries, learnings, codebase maps | Best project-level continuity and roadmap/state model | Phase/milestone model is heavier than per-task daily work; large command surface | Borrow project/requirements/state concepts as optional higher-level context, not as mandatory phase engine |
| GSD 2 | DB-backed milestone/slice/task runtime with workers, leases, dispatches, verification evidence, worktrees, auto-mode, recovery | Best runtime reliability for autonomous execution | Too heavy and app-like for Groundwork MVP | Borrow state/failure vocabulary and verification evidence concepts; reject DB runtime for MVP |
| Superpowers | Plan documents with checkbox steps, exact files, commands, expected outputs, TDD sequence, execution handoff | Strong execution plan quality | No native durable task object or lifecycle; plan path is framework-specific | Borrow plan granularity and exact execution steps; integrate under Groundwork task files |
| BMAD-METHOD | Agile workflows, stories, modules, agents, Test Architect, broader planning tracks | Strong scale-adaptive planning and role-aware artifacts | Too much agile/persona machinery for Codex plugin MVP | Borrow planning-depth selection, not the full agile model |
| gstack | Review findings emit task JSONL, TODO format, approval gates, role lenses | Good at converting review findings into implementation tasks | Tasks are downstream of review, not primary PRD-to-task management | Borrow task emission schema ideas and review-to-task aggregation |

Recommendation: Groundwork task management should be issue-source-first. It should borrow mattpocock's issue tracker abstraction and triage roles, Spec Kit's independently testable slices, Trellis' linked artifact discipline, and GSD-style state only where needed.

Groundwork task sources should be pluggable:

- current conversation
- local markdown fallback
- GitHub/GitLab issue
- Linear/Jira or another issue tracker described by the user
- TaskRepo markdown task
- future Symphony issue/run context

Initial Groundwork task states should stay small:

- `draft`
- `needs-info`
- `ready-for-agent`
- `ready-for-human`
- `in-progress`
- `verification`
- `done`
- `wontfix`

Initial local fallback artifact:

```text
.groundwork/
  tasks/
    YYYY-MM-DD-slug/
      task.md          # task source, status, HITL/AFK, blockers, acceptance
      prd.md           # business requirement / spec for this task
      plan.md          # implementation plan when needed
      contract.md      # API/UI/DB/state contract when needed
      prototype.md     # prototype notes or links when needed
      verification.md  # tests, runtime checks, UAT evidence
      handoff.md       # resume state and next action
      task.json        # small machine-readable index
```

Initial `task.json` should stay small:

```json
{
  "id": "slug",
  "title": "Task title",
  "status": "draft|needs-info|ready-for-agent|ready-for-human|in-progress|verification|done|wontfix",
  "priority": "P0|P1|P2|P3",
  "type": "feature|bug|prototype|contract|uat|docs|release",
  "execution": "AFK|HITL",
  "createdAt": "YYYY-MM-DD",
  "updatedAt": "YYYY-MM-DD",
  "source": "conversation|local|github|gitlab|linear|jira|taskrepo|symphony|other",
  "externalRef": "",
  "blockedBy": [],
  "artifacts": {
    "prd": "prd.md",
    "plan": "plan.md",
    "contract": "contract.md",
    "verification": "verification.md",
    "handoff": "handoff.md"
  }
}
```

This should be supported by scripts/tools, not only skills:

- create/list/show/update/close local task fallback
- link external task source
- split PRD/spec/plan into vertical slices
- mark slices as AFK or HITL
- validate task artifact shape
- generate task index
- check broken artifact links
- optionally inject current task context at session start if Codex plugin hooks or host-level hooks support it

Hooks should be treated as optional host capabilities. Superpowers' Codex plugin surface is primarily `plugin.json + skills`, while its hook system is mainly shown in non-Codex runtime packaging. Groundwork should design hook-friendly artifacts, but not rely on hooks for MVP correctness unless Codex plugin support is confirmed.

## Candidate Groundwork Components

| Candidate component | Source inspiration | Why it fits Groundwork | Constraint |
| --- | --- | --- | --- |
| `to-prd` | mattpocock `to-prd`, Spec Kit, Trellis PRD, BMAD planning | Creates the business/spec foundation before contract and implementation | Must support brownfield evidence, not only greenfield features |
| `to-issues` | mattpocock `to-issues`, Trellis task dir, Spec Kit tasks, GSD state | Resolves task source, creates or links tasks, slices vertical work, marks AFK/HITL, and preserves artifact links | Must be issue-source-first; `.groundwork/tasks/<task-id>/` is a local fallback, not the universal source of truth |
| `triage` | mattpocock triage/agent brief, GSD state continuity, gstack task emission | Tracks status, blockers, `ready-for-agent` / `ready-for-human`, closeout, and resume surface | Must not become a heavyweight issue tracker clone |
| `write-plan` | Superpowers writing-plans, Spec Kit plan/tasks, get-shit-done plan-phase | Turns accepted task into executable steps | Must not force large plans for obvious edits |
| `diagnose` | mattpocock diagnose, gstack investigate | Forces feedback loop before fix | Must stop when no loop can be built |
| `contract` | Trellis context curation, real project API/DB/UI checks | Compares DB/API/state/UI truth sources | Must cite real files/controllers/enums |
| `prototype` | mattpocock prototype, gstack design/QA lenses, user static HTML prototype work | Builds, revises, and reviews throwaway logic/state or UI/static HTML prototypes that answer a concrete design question | Must stay tied to business flow, state behavior, and implementation constraints, not just visual polish |
| `artifact` | User artifact-audience skill, Superpowers planning discipline, mattpocock write-a-skill progressive disclosure | Keeps PRD, integration docs, reviews, skills, and technical PPTs aimed at the right reader | Must not let one artifact serve every audience |
| `implement` | Trellis implement/check loop, Superpowers TDD/review, mattpocock diagnose/TDD/review/zoom-out | Executes or reviews code changes against PRD, specs, diff, tests, and verification evidence | Must not require Trellis or any source-framework runtime |
| `verify` | gstack QA, Trellis evidence persistence, get-shit-done verification/UAT | Produces test, runtime, UAT, and customer-safe readiness evidence | Must separate code pass, runtime pass, data readiness, environment readiness, and customer validation |
| `tdd` | Superpowers TDD, mattpocock TDD | Useful for deterministic logic and regressions | Must allow non-TDD paths for docs/config/prototypes |
| `handoff` | mattpocock handoff, Trellis journals, `get-shit-done` state files, GSD 2 recovery | Preserves state across context transitions without duplicating PRDs, plans, issues, commits, or diffs | Must be short enough to read and resume from |
| `standards` | Agent OS, Trellis spec, mattpocock domain docs, ubiquitous-language, review standards axis | Discovers and injects local standards when repeated work needs them | Must not create standards bureaucracy before repeated need |
| `gate` | AgentHub, BMAD scale-adaptive flow, mattpocock git guardrails | Previews medium/heavy workflows before spending time or tokens and protects risky operations | Must not prompt-gate lightweight direct work |

## Borrowing Matrix

This matrix translates framework research into implementation decisions. "Borrow" means Groundwork should express the idea in its own plugin/skill/artifact language. "Reject" means the source framework solves a different product problem or carries too much process weight.

| Groundwork feature | Borrow from | Reject from source frameworks | Implementation implication |
| --- | --- | --- | --- |
| `to-prd` | mattpocock `to-prd`, Spec Kit spec-as-contract, Trellis PRD files, BMAD planning discipline, Agent OS spec shaping | Greenfield-only spec flow, mandatory ceremonies, generated specs outranking brownfield source truth | Put PRD/spec before contract and implementation; include scope, non-goals, business rules, acceptance, and source/runtime conflicts. |
| `to-issues` | mattpocock issue tracker abstraction, local markdown fallback, `to-issues`, AFK/HITL; Spec Kit task slices; Trellis linked artifacts | Full Trellis lifecycle, DB-backed runtime state, autonomous dispatch, framework-owned source of truth | Resolve the best task source first. Link GitHub/GitLab/Linear/Jira/TaskRepo/Symphony-style context when available; use `.groundwork/tasks/<task-id>/task.json` only as an inspectable local fallback. |
| `triage` | mattpocock triage states and agent brief, GSD state continuity, gstack review-to-task aggregation | A full issue tracker clone, opaque state database, over-classifying tiny tasks | Keep states small; `ready-for-agent` requires a real agent-ready brief, not just a title. |
| `write-plan` | Superpowers writing-plans, Spec Kit tasks, get-shit-done phase plans | Mandatory large plans, plan approval for trivial work, subagent-first execution | Convert accepted task state into exact files, steps, dependencies, verification checkpoints, and stop conditions. |
| `scope` | Trellis PRD discipline, Superpowers one-question clarification, BMAD scale-adaptive planning, Spec Kit what/how separation | Trellis default task lifecycle, Superpowers mandatory brainstorming for all work, BMAD role workflows, Spec Kit greenfield-first assumption | Use as a branch inside PRD/task work; start with a small scope note and escalate to a durable spec only when ambiguity or reuse justifies it. |
| `contract` | Trellis context curation, Agent OS standards discovery, mattpocock docs challenge, real project code-truth practice | Generated docs outranking controllers/schemas/enums, standards-only answers, fixed peer-framework artifact paths | Read source/runtime truth first; output field/status/API mismatch maps and frontend-ready handoff. |
| `prototype` | mattpocock `prototype` shape (`SKILL.md` + `LOGIC.md` + `UI.md`), gstack design/QA lenses, `get-shit-done` sketch/UI review, the user's static HTML prototype workflow | Visual-only design review, marketing-page defaults, role theater, framework-specific prototype directories | Directly adapt mattpocock's two-branch prototype model. Treat prototypes as tools that answer a specific question; browser-check important UI states and feed decisions back into PRD/task/contract/implementation. |
| `artifact` | User artifact-audience skill direction, Superpowers plan-writing discipline, gstack document/review lenses, mattpocock write-a-skill progressive disclosure | One artifact serving all audiences, renderer skills deciding business narrative, generic polished prose | Require target reader and downstream action before PRD, integration doc, review report, technical PPT, or skill artifact generation. |
| `implement` | Trellis implement/check separation, Superpowers TDD/review, mattpocock diagnose/TDD/review/zoom-out, `get-shit-done` quick/execute/verify split | Mandatory subagent execution, automatic commits, full phase engine, DB-backed runtime orchestration | Implement or review code directly in Codex; require diff/source/test/spec evidence; use zoom-out maps when unfamiliar and subagents only for clear parallel payoff. |
| `verify` | gstack QA, `get-shit-done` UAT/verify-work, Trellis evidence persistence | Single API success as readiness proof, opaque runtime state, autonomous closeout | Split readiness into code/test, runtime, data, environment, and customer validation; preserve evidence and blockers. |
| `diagnose` | mattpocock diagnose, gstack investigate, Superpowers verification-before-completion | Fix-before-reproduce behavior, broad cleanup, speculative edits | First build a feedback loop and existence judgment; patch only proven defects. |
| `gate` | AgentHub workflow weight preview, BMAD quick/full/enterprise distinction, Codex permission model, mattpocock git guardrails | Prompt-gating every lightweight task, hidden remote mutation, bypass-permission defaults, Claude-specific hook copying | Gate only medium/heavy or risky actions: data writes, deploys, publishes, pushes, migrations, destructive commands. Optional hooks can preview or block dangerous git operations if Codex host support exists. |
| `handoff` | mattpocock handoff, Trellis journals, `get-shit-done` `STATE.md`/reports, GSD 2 recovery concepts | Large opaque state database, full runtime recovery engine, verbose session dumps, duplicating content already captured in PRDs/issues/plans/diffs | Produce compact resume summaries that reference existing artifacts; use `.groundwork/tasks/<task-id>/handoff.md` only when local fallback owns the task. |
| `standards` | Agent OS standards discovery, Trellis specs, mattpocock domain docs, ubiquitous-language, review standards axis, Caliber config sync as adjacent signal | Upfront standards bureaucracy, cross-agent config sync ownership, shared-skill mutation for Codex-only behavior | Discover existing repo standards only when repeated work needs them; keep Groundwork-specific behavior in the plugin and use standards as a review lens rather than a paperwork layer. |

## Minimal Personal Base From Framework Research

The comparison now points to an action-named workflow MVP, not a skill-only MVP:

1. `to-prd` for PRD/spec creation or refinement.
2. `to-issues` for issue-source-first task slicing, with local file fallback only when needed.
3. `triage` for task state, blockers, AFK/HITL, and agent-ready briefs.
4. `write-plan` for execution planning.
5. Task execution/review using contract, prototype, implementation, and verification capabilities as needed.
6. Verification, release gate, and handoff.

Core chain:

```text
PRD/spec -> task -> plan -> prototype/contract/design as needed -> implementation -> verification/UAT -> release/handoff
```

Skills are still useful, but they are not the whole product. Groundwork should include:

- skills for judgment-heavy workflows
- scripts/tools for task CRUD and artifact validation
- templates for PRD/task/plan/verification/handoff
- optional hooks only when host support is confirmed and the workflow still works without them

Groundwork should deliberately avoid absorbing these whole systems:

- Trellis on complete managed task lifecycle.
- GSD 2 on standalone coding-agent runtime.
- BMAD on full agile AI method.
- gstack on virtual team role surface.
- Spec Kit on greenfield spec-first project generation.
- Agent OS on standards management as the whole product.

## Final Position

Groundwork should be a complete but thin R&D workflow surface, not an autopilot.

It should help Codex ask: what evidence do we need, what workflow is lightest, and what output will be accepted? It should not force every task into the same lifecycle, own autonomous execution, or import a large role system. The reusable core is narrower: source truth first, durable evidence when useful, explicit verification, and user-steered escalation only when the work actually needs more structure.
