# Product Principles

These principles guide current product interpretation. `docs/plugin-architecture.md`, public skill contracts, and accepted scoped PRDs own concrete current behavior; historical PRDs do not globally override newer canonical contracts.

Groundwork is a Codex-native personal base for R&D work. It helps turn ambiguous product, code, prototype, integration, data, and UAT signals into verified engineering decisions, implementation-ready artifacts, safe code changes, and resumable handoffs.

It is not a generic assistant, a full autonomous agent runtime, a market-positioning alternative to existing frameworks, or an adapter that depends on those frameworks being installed.

## 1. Evidence Before Edits

When the request is based on a suspected issue, first confirm whether the issue exists. If the evidence says no change is needed, report that clearly and do not edit files.

Evidence can come from source code, docs, tests, API contracts, database schemas, runtime behavior, browser-visible state, UAT records, user-provided artifacts, or command output. The point is not to collect everything; it is to inspect the smallest reliable source of truth before changing code or documents.

For nontrivial bugs, requirements, contracts, or readiness claims, evidence-first work should reduce the problem to first principles: phenomenon, primitive facts, hard constraints, invariants, causal mechanism, root cause or core need, minimal sufficient solution, and falsifiable verification signal. The paired adversarial step is to look for the strongest counterexample, missing evidence, hidden assumption, edge state, scope creep, and claim boundary before upgrading any conclusion.

`Minimal` applies only after sufficiency is established. Prefer the lowest-blast-radius solution among options that address the confirmed cause, restore the affected invariants, and admit a falsifiable check; a smaller symptom workaround that leaves the cause intact is not a minimal sufficient solution. If the sufficient solution exceeds accepted scope or authority, surface that boundary instead of silently substituting an under-fix.

## 2. R&D Work Is The Center

Groundwork should optimize for software R&D workflows:

- PRD/spec creation, refinement, and acceptance definition
- task creation, slicing, state tracking, and continuation
- implementation planning
- frontend integration contracts
- static HTML prototype creation and review
- implementation and implementation review
- verification, UAT/SIT readiness, and release acceptance
- PRDs, technical docs, review reports, and handoff artifacts
- confirmed bug diagnosis and focused fixes
- release, deploy, test-data, and remote-mutation gates

It should not make timesheet automation, AI news reports, local Mac cleanup, generic browsing, or broad business consulting part of the core product.

## 3. Small Tasks Stay Small

Groundwork must not turn a simple edit, command, or direct answer into ceremony. Workflow mode should add value only when ambiguity, risk, reuse, or context size justifies it.

Default behavior:

- direct answer for one-off questions
- direct edit for obvious low-risk implementation work
- lightweight check for suspected bugs
- durable artifact only when later implementation, review, UAT, release, or handoff will reuse it

## 4. Source Truth Beats Framework Habit

Local source code, controllers, DTOs, VO/PO models, enums, mapper SQL, tests, docs, static prototypes, runtime requests, database records, and visible browser behavior outrank generic framework assumptions.

Framework research can inspire Groundwork behavior, but no compared framework owns the truth for a user's project.

## 5. Curated Framework Intake

Groundwork should absorb useful framework ideas without inheriting whole frameworks. It should not install, wrap, call, sync, or reconfigure Trellis, Superpowers, gstack, BMAD, Spec Kit, Agent OS, GSD, or similar systems.

Adopt a pattern only when it improves the user's actual R&D flow. Exclude patterns that mainly add ceremony, global installation burden, role-play, autonomous runtime complexity, or fixed artifact paths. Adopted ideas should become Groundwork-native concepts, modes, checks, scripts, or artifacts.

## 6. Separate Artifact Types

Do not collapse everything into one document. Different artifacts have different readers and acceptance signals:

- PRD: business scope, rules, acceptance, non-goals
- task record: durable unit of work, state, priority, source, linked artifacts, contract impact, readiness gaps, and verification expectation
- plan: implementation slices, order, dependencies, and checks
- static prototype: executable requirement evidence
- implementation contract: routes, requests, fields, enums, states, examples, and edge cases
- implementation review: PRD/spec/diff/test/verification gaps
- UAT readiness note: capability, data, environment, and customer-validation status
- handoff summary: current state, evidence, blockers, changed files, commands, next action
- lifecycle state: workstream-scoped recovery state for cross-session continuation, gap closure, UAT/release reuse, and pending decisions

If the target reader and downstream action are unclear, clarify them before generating or rewriting the artifact.

## 7. Human Control Is A Feature

Groundwork should help the user steer. It should not hide major decisions inside autonomous execution, uncontrolled subagents, automatic commits, or broad auto-triggering.

Subagents are optional execution tools, not the methodology. Use them only when the work is parallel, bounded, and clearly beneficial.

## 8. Verification Is Part Of The Deliverable

A result is not complete just because code changed or a document reads well. Groundwork outputs should carry acceptance evidence whenever feasible:

- exact test/build/lint commands and results for code
- browser/runtime checks for user-visible behavior
- API/DB evidence for data-dependent claims
- post-deploy or post-publish checks for release work
- explicit "not run" or "not available" notes when verification cannot be performed

Verification should scale with risk. Do not over-test low-risk docs, but do not under-verify code, data, UAT, or release work.

## 9. Preview Before Risky Writes

Groundwork should gate actions that mutate durable or remote state:

- deployment
- publishing
- push/PR operations
- schema/data migration
- UAT/test data writes
- destructive filesystem or git operations
- shared skill/plugin changes

The gate should show intent, target, command/action, expected effect, rollback or recovery path, and verification plan.

## 10. Local Adaptation Over Global Pollution

Codex-specific workflow behavior should live in the Groundwork plugin or repo-local files. Do not mutate shared `~/.agents/skills` assets for Codex-only preferences.

If Groundwork needs repo-local durable files, prefer the real task source first: an issue, PRD/spec file, current conversation, or future orchestration context. Use `artifacts/<workstream-slug>/STATE.md` only when lifecycle-state thresholds are met for one resumable workstream, and optional `artifacts/<workstream-slug>/ROADMAP.md` only for true multi-milestone work. Older `.groundwork/tasks/<task-id>/` language is local scratch or fallback context, not lifecycle state, not the default durable artifact location, and not a project task database. Do not mirror `.trellis/`, `.planning/`, `.scratch/`, or `.gsd/` structures.

## Public Workflow Principles

Groundwork should remain a small complete workflow, not a skill-only bundle. User-visible skill names stay action-oriented. Do not repeat a `groundwork-` prefix inside the plugin; the plugin already provides the namespace.

1. `to-prd` for turning conversation, evidence, prototype notes, UAT feedback, or rough requirements into PRD/spec intent and acceptance.
2. `to-issues` for splitting PRD/spec/plan into vertical slices with task-state fields and linking them to the best task source.
3. `triage` for task state, severity, state transition reason, AFK/HITL classification, `ready-for-agent` briefs, blockers, and closeout.
4. `write-plan` for implementation slices and verification checkpoints.
5. `prototype` for throwaway logic/state or UI/static HTML prototypes that answer a specific requirement, interaction, state, or design question.
6. `implement` for code execution or implementation review.
7. `verify` for tests, runtime checks, UAT readiness, and release acceptance.
8. `handoff` for continuation and cross-session state.
9. `dispatch` for package-only runtime and adapter routing after readiness.
10. `wiki` for explicit source-cited project knowledge maintenance.

Supporting behaviors can remain internal at first:

- `scope` for ambiguous acceptance inside `to-prd` / `to-issues`
- `artifact` for target-reader alignment
- `contract` for API/UI/DB/state alignment when planning, prototype, implementation, or verification needs cross-layer truth
- `diagnose` for confirm-before-edit bug work
- `gate` for risky writes and remote mutations

The core task-state chain is:

```text
to-prd -> to-issues -> triage -> dispatch when runtime packaging is requested -> implement/runtime owner -> verify -> triage closeout/gap closure -> handoff when needed
```

This chain stays tracker-neutral by default. It can produce paste-ready text for external issues, but it does not call GitHub, Linear, Jira, or other tracker APIs unless the user explicitly requests and approves that remote write. It also does not force every task into lifecycle state; `STATE.md` is reserved for workstream-scoped continuation under the lifecycle-state thresholds.

Groundwork should become useful before it becomes broad, but it should still cover the whole R&D loop at a thin level before deepening any single mode.
