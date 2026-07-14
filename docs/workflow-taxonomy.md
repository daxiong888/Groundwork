# Workflow Taxonomy

This taxonomy explains current workflow boundaries and trigger policy. `docs/plugin-architecture.md`, the route registry, and public skill contracts are canonical for current behavior; scoped historical PRDs remain decision evidence only.

This taxonomy defines Groundwork's internal workflow modes and the public action-named skills that expose them. It is derived from the R&D scenario model in `research/user-work-scenarios.md` and the peer-framework comparison in `research/framework-comparison.md`.

Groundwork starts explicit-first: the user can ask for a mode directly, or Codex can choose a mode when the trigger is clear. Automatic heavy activation should wait until real-task validation proves low false positives.

## Task-State Spine

Groundwork's task-state spine is tracker-neutral markdown, not an external tracker integration or task database:

```text
to-prd
  -> accepted enough
to-issues
  -> vertical slice with task-state fields
triage
  -> needs-info / ready-for-agent / ready-for-human
dispatch when package routing is requested
  -> runtime/package decision only
write-plan, implement, or approved runtime owner
  -> execution evidence
verify
  -> pass / partial / fail / blocked
triage
  -> closeout or gap closure
handoff
  -> reference STATE.md only when durable continuation exists
```

This flow does not call GitHub, Linear, Jira, or other tracker APIs. External issues may own the task source, but Groundwork outputs remain paste-ready or conversation-local unless the user explicitly requests a remote write.

Do not force every issue into `STATE.md`. Lifecycle state remains opt-in and workstream-scoped under `artifacts/<workstream-slug>/STATE.md` only when `skills/_shared/LIFECYCLE-STATE.md` thresholds are met.

## Priority Model

| Priority | Public skill / mode | Product role |
| --- | --- | --- |
| P0 | `to-prd` | Establish product intent, scope, rules, acceptance, and non-goals before implementation artifacts. |
| P0 | `to-issues` | Split PRD/spec/plan into vertical task slices and link them to the best task source. |
| P0 | `triage` | Resolve, classify, unblock, mark AFK/HITL, move to `ready-for-agent` / `ready-for-human`, and close task context. |
| P0 | `write-plan` | Slice the task into implementation steps, dependencies, and verification checkpoints. |
| P0 | `prototype` | Build, revise, and review throwaway logic/state or UI/static HTML prototypes that answer a specific design question. |
| P0 | `implement` | Execute or review code changes against PRD, source, diff, tests, and verification evidence. |
| P0 | `verify` | Verify tests, runtime behavior, UAT/SIT readiness, release acceptance, and customer-safe evidence. |
| P0 | `handoff` | Preserve long-running R&D state across interruptions. |
| P0 | `dispatch` | Produce package-only runtime/adapter routing for accepted ready work without execution claims. |
| P0 | `wiki` | Maintain explicit source-cited project knowledge without promoting synthesis into product or readiness truth. |
| P0 branch | `contract` | Align API, DB, state, frontend behavior, and documentation when planning, prototype, implementation, or verification needs cross-layer truth. |
| P1 | `scope` | Convert ambiguity into scope and acceptance criteria. |
| P1 | `artifact` | Keep target reader, source evidence, and downstream action explicit. |
| P1 | `diagnose` | Confirm existence and cause before patching. |
| P1 | `gate` | Preview, approve, verify, and document risky writes or remote mutations. |
| P2 | `standards` | Discover and apply repo-local workflow standards when repeated work justifies it. |

## Direct

Direct is not a public Groundwork skill or project lifecycle mode. It is the default route when a workflow adds no value, and it may appear in lifecycle state only as a low-ceremony continuation route.

Use direct work for:

- small edits
- simple command output
- direct explanations
- low-risk changes with obvious verification
- one-off questions that do not need durable artifacts

Behavior:

- do the work directly
- report changed files and verification when files change
- avoid ceremony and avoid creating Groundwork artifacts

Escalate from direct work only when the task has ambiguity, cross-layer evidence, user-visible risk, data/environment risk, release risk, or long-running handoff value.

## `to-prd`

Use for:

- new feature or workflow definition
- PRD refinement
- acceptance criteria creation
- business rule clarification
- converting rough user intent into a usable engineering brief

Required evidence:

- user request, existing PRD/spec, prototype, ticket, UAT signal, customer feedback, or source/runtime behavior
- current project truth when the PRD describes existing or brownfield behavior

Output:

- scope and non-goals
- business rules and state rules
- acceptance criteria
- assumptions and unresolved questions
- linked downstream artifacts when they already exist

Stop when:

- business authority is missing and the decision would invent product policy
- source/runtime truth contradicts the requested behavior and the conflict needs user confirmation

## `to-issues`

Use for:

- splitting PRD/spec/plan into independently verifiable vertical slices
- producing paste-ready, tracker-neutral issue drafts from accepted source
- preserving acceptance criteria, blockers/dependencies, contract impact, and verification expectations for each slice
- recording AFK/HITL as candidate metadata only when it changes downstream triage
- linking the accepted source and relevant existing artifacts without mutating an external tracker

Required evidence:

- source request, PRD/spec, issue, task document, or current conversation
- external issue/task source when one exists
- existing external issue, PRD, or local artifact if it already owns the work
- nearest source/runtime evidence when task scope depends on current behavior

Output:

- tracker-neutral issue drafts with title, goal, accepted source, and acceptance criteria
- vertical slices with blockers and acceptance criteria when splitting work
- contract impact, verification evidence needed, and ready-for-agent missing fields for each slice
- optional AFK/HITL candidate, ordering, linked-artifact references, and next action when they change execution or review
- a `triage` candidate when final readiness, lifecycle state, or closeout judgment is needed

Stop when:

- the work is too small to benefit from durable state
- accepted source or acceptance criteria are missing; route back to `to-prd`
- final readiness, lifecycle state, or closeout must be decided; route to `triage`
- a state transition would mutate an external tracker without explicit user intent

## `triage`

### Use When

- user asks to triage, unblock, classify, or close task context
- existing issue/task lacks enough information for agent work
- work needs `ready-for-agent` / `ready-for-human` judgment
- slices need AFK/HITL review
- work needs lifecycle-state or closeout classification
- task state changed after implementation, verification, or handoff

### Inputs

- existing issue, local task artifact, PRD/spec, conversation, or task slices
- blockers, comments, git status, verification evidence, and relevant source/runtime facts

### Output

- task state
- severity for the current blocker or gap
- state transition reason, including evidence added and evidence still missing
- AFK/HITL classification
- missing information or blocker list
- agent-ready brief when state becomes `ready-for-agent`
- human decision, options, risks, and next action when state becomes `ready-for-human`
- closeout note when work is done or `wontfix`

## `write-plan`

Use for:

- implementation planning after PRD/task creation
- decomposing a task into independently checkable slices
- deciding whether prototype, contract, technical design, or data setup is needed before code
- preparing a reviewable execution plan

Required evidence:

- PRD/spec or task brief
- relevant source tree, existing docs, tests, and known constraints
- current dirty worktree state when planning edits

Output:

- ordered implementation slices
- dependency and parallelization notes
- files or modules likely to change
- verification checkpoints per slice
- stop conditions and risk gates

Stop when:

- acceptance criteria are unknown
- plan accuracy depends on source areas that cannot be inspected

## `contract`

Use for:

- frontend integration documentation
- field, enum, status, or route drift
- API/DB/state/UI consistency checks
- mock data notes tied to real contracts
- review of handoff docs that may contain guessed names

Required evidence:

- PRD/task context when available
- current doc or user question
- real controllers, DTOs/VOs/POs, enums, mapper SQL, schema, frontend code, runtime requests, or API responses

Output:

- truth sources checked
- integration contract map
- mismatch list: doc-only, code-only, runtime-only, ambiguous
- frontend-ready implementation notes
- verification status

Stop when:

- source/runtime truth cannot be located and the result would become guessed

## `prototype`

Use for:

- logic/state prototype creation
- static HTML or UI prototype creation
- prototype revision
- prototype review
- business-flow coverage checks
- browser-visible interaction checks
- state-model or data-shape sanity checks

Required evidence:

- PRD, scope note, business workflow, state model, data model, or user-provided prototype request
- existing HTML when modifying or reviewing
- API/state/implementation constraints when prototype elements map to real implementation

Output:

- explicit question the prototype answers
- logic/state prototype, static HTML artifact, or patch
- review findings with concrete gaps
- browser verification notes when visual or interaction claims matter
- distinction between visual polish, business coverage, state-model feedback, and implementation-contract gaps

Stop when:

- required workflow/state rules are unknown and cannot be inferred safely

## `implement`

Use for:

- "实现这个 task"
- "按 PRD 开发"
- implementation review
- code changes driven by PRD, prototype, contract, or bug evidence
- checking agent-generated code against acceptance criteria

Required evidence:

- PRD/task brief/acceptance criteria or clear user request
- relevant source files
- `git status --short` and relevant diffs in dirty worktrees
- tests/build/lint commands that are available or expected

Output:

- code patch, or implementation review findings
- files changed
- PRD/spec/diff/test gaps
- exact verification commands and results
- residual risks or skipped checks

Stop when:

- acceptance signal is unknown
- relevant source cannot be found
- changes would be unsafe without approval

## `verify`

Use for:

- test/build/lint verification
- browser/runtime behavior checks
- UAT/SIT readiness
- release acceptance
- customer validation readiness
- test data availability checks
- runtime chain checks
- customer-safe readiness summaries

Required evidence:

- target environment
- page/API/DB/config/task-state evidence
- known data consumption behavior when data is involved

Output:

- verification result split into code/test, runtime, data, environment, and customer validation when relevant
- blockers
- minimal safe fix path
- task-state recommendation: `triage closeout`, `gap closure`, `re-verify`, or `blocked needs-info`
- stakeholder-safe wording when needed

Stop when:

- environment access is unavailable and no reliable substitute evidence exists

## `handoff`

Use for:

- "继续刚才"
- context compaction
- interrupted work
- multi-day R&D tasks
- multi-artifact implementation/review/UAT flows

Required evidence:

- current goal
- changed files
- commands run and results
- verified facts, inferences, blockers, and next action

Output:

- concise resume-ready summary
- existing `artifacts/<workstream-slug>/STATE.md` reference when lifecycle state exists
- state freshness and update-needed status without copying the full state
- optional recommendation to create or update workstream-scoped lifecycle state when pause/resume, gap closure, UAT/release reuse, or pending decision thresholds are met
- no full PRD, plan, issue, diff, log, or project-global state copy

Stop when:

- the previous objective conflicts with the newest user instruction

## `scope`

Use for:

- vague requirements
- PRD/task boundary
- "这个是不是需求"
- "这期做什么"
- unclear acceptance criteria

Required evidence:

- existing docs or user-provided context
- observed behavior or source/runtime truth when the decision depends on it
- user corrections when business wording matters

Output:

- scope note
- non-goals
- assumptions and unresolved questions
- smallest valuable slice
- acceptance criteria

Stop when:

- the decision depends on unavailable business authority

## `artifact`

Use for:

- PRD audience alignment
- frontend integration doc structure
- review report structure
- technical PPT narrative
- generated text where the target reader is unclear

Required evidence:

- intended reader
- downstream action
- source evidence
- artifact type

Output:

- audience-specific outline
- rewrite or review findings
- explicit reader/action declaration

Stop when:

- target reader cannot be identified

## `diagnose`

Use for:

- suspected bugs
- regressions
- failed tests
- UAT/runtime surprises
- "先确认问题是否存在"

Required evidence:

- reproduction path or closest feedback loop
- source/tests/logs/runtime evidence
- dirty diff status before edits

Output:

- exists / does not exist / inconclusive judgment
- evidence
- minimal patch only after existence is proven
- verification result

Stop when:

- no deterministic feedback loop or reproduction path can be built

## `gate`

Use for:

- deploys
- publishes
- pushes/PR operations
- test/UAT data writes
- schema or data migrations
- destructive filesystem or git operations
- shared skill/plugin mutations

Required evidence:

- target
- command/action preview
- expected effect
- rollback or recovery path
- verification plan

Output:

- risk preview
- approval gate
- executed command/results when approved
- rollback note
- post-action verification

Stop when:

- user intent is ambiguous
- destructive or remote scope is unclear
- rollback/recovery constraints are unknown for high-risk actions

## `standards`

Use for:

- repo-local Groundwork conventions
- Codex plugin/skill structure
- migration or compatibility checks
- repeated workflow standards

Required evidence:

- real config files
- plugin manifests
- skill docs
- install/update behavior
- local repo conventions

Output:

- compact standards
- scoped config or plugin changes
- compatibility answer with evidence

Stop when:

- the change would mutate shared assets for Codex-only behavior

## Trigger Policy

Initial trigger policy:

- prefer explicit invocation: "use Groundwork", "按 Groundwork 流程", "建一个 Groundwork task", "用 contract 模式"
- infer mode only when the trigger is strong and the user expects action
- choose direct work when the task is small and acceptance is obvious
- ask a targeted question only when missing details materially affect correctness, safety, destructive scope, or user-visible behavior

Do not auto-trigger:

- source-framework installation
- autonomous loops
- subagent orchestration
- durable artifact creation for one-off answers
- risky writes without explicit intent
