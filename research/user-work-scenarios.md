# User Work Scenarios

Groundwork should focus on software R&D work: turning ambiguous product or environment signals into PRDs/specs, managed tasks, verified engineering decisions, implementation-ready artifacts, reviewed prototypes, safe code changes, testable data, and release/UAT handoffs.

It should not become a generic personal assistant, news/report writer, system-cleanup helper, or business-consulting tool. Those workflows exist in the user's history, but they are not the center of this project.

## Source Basis

This document is based on session records and memory available through 2026-05-19. The evidence points to one dominant product direction:

- R&D work often starts from incomplete business wording, stale docs, static HTML prototypes, frontend integration questions, implementation tasks, UAT observations, or suspected bugs.
- Before integration contracts and implementation, many tasks need a PRD/spec and a small task record that captures scope, state, evidence, and verification expectations.
- The useful agent behavior is not "write more text"; it is "find the source of truth, verify whether the problem exists, then produce the smallest reliable engineering artifact or change."
- The user repeatedly cares about DB/API/state-flow/UI consistency, prototype realism, frontend implementability, coding implementation quality, target-reader clarity, real environment readiness, preview-before-write safeguards, and clean handoff across long-running tasks.

## Core Scope

Groundwork is most useful when the task has at least one of these properties:

- It crosses product requirement, backend code, frontend behavior, database state, and environment data.
- It requires distinguishing verified facts from assumptions before editing code or documents.
- It turns requirements into concrete R&D artifacts: PRD/spec, task record, implementation plan, static HTML prototype, frontend integration document, review report, technical PPT, test-data note, release checklist, or handoff summary.
- It turns accepted tasks into code changes, tests, implementation notes, and review evidence.
- It changes something with R&D or environment risk: code, test/UAT data, release artifacts, plugin/skill installation, CI/build behavior, or deployment state.
- It needs a durable handoff between roles: product, frontend, backend, QA, deployment, customer-facing stakeholder, or future agent session.

Groundwork should stay lightweight when the user only needs a direct answer, a one-off command, or a non-R&D artifact.

Groundwork should also avoid framework conflicts. It is a personal R&D base, not an adapter for Trellis, GSD, Spec Kit, Agent OS, or similar systems. The product direction is to absorb useful ideas into Groundwork-native workflow, task management, modes, tools, and artifacts, not to stack another workflow system on top of existing ones.

## Scenario Matrix

| Core scenario | Trigger signals | Evidence to inspect | Expected output | Main guardrail |
| --- | --- | --- | --- | --- |
| Requirement-to-engineering clarification | "整理成 PRD", "这个是不是需求", "这期做什么" | Existing docs, UAT behavior, DB/ES records, state machine, user corrections | Scope note, PRD delta, task boundary, acceptance criteria | Do not turn data/config gaps into product requirements |
| Task creation and management | "建一个 task", "拆一下任务", "继续这个任务", "这个 task 到哪了" | PRD/spec, acceptance criteria, current repo state, existing task artifacts, verification needs | Task record, task status, plan, artifact links, next action | Do not create heavy task ceremony for obvious direct work |
| Frontend integration documentation and review | "前端集成文档", "字段/状态是不是猜的", "接口怎么接" | Controllers, DTO/VO/PO, enums, mapper SQL, runtime requests, existing docs | Frontend-implementable API/state/field handoff | Prefer code/runtime truth over stale docs |
| Prototype creation and review | "做个静态 HTML 原型", "改这个原型", "评审这个页面", "这个交互是不是覆盖了", "这个状态模型跑一下" | PRD, workflow/state rules, existing HTML, browser-visible behavior, API/state constraints, logic/data model questions | Logic/state prototype, static prototype, prototype patch, or review report with concrete gaps | Do not treat prototypes as visual-only mockups; a prototype must answer a specific question |
| R&D artifact audience alignment | "PRD/集成文档/PPT 面向对象不清", "这个文档给谁看" | Intended readers, source evidence, artifact type, downstream action needed | Audience-specific outline, rewrite, or review findings | Do not mix business narrative, implementation contract, and presentation story |
| Implementation task execution and review | "实现这个 task", "按 PRD 开发", "检查实现结果" | PRD/task, specs, codebase, tests, commit diff | Code patch, tests, implementation review, verification result | Do not let task summaries hide code truth or verification gaps |
| UAT/SIT readiness verification | "有没有数据可以测", "链路通不通", "客户能不能验" | Read-only DB/ES checks, UAT pages, task states, environment config, deployment state | Readiness conclusion, blocking gaps, minimal fix path | Separate capability, data readiness, and environment stability |
| Confirm-before-edit bug work | "先确认问题是否存在", suspected defect list, stale page/copy/API behavior | Source, tests, logs, runtime reproduction, dirty diff | Exists/not-exists judgment, minimal patch if needed, verification result | No speculative edits |
| Test data and mock handoff | "造一些数据", "给前端联调", "mock 数据说明" | Live schema, gateway responses, current rows, data consumption behavior | Seed plan, mock-data doc, consumable write targets, verification | No secrets; do not reuse already-consumed rows |
| Release/deploy/runtime gate | "部署到 UAT", "发布", "提交并推送", "更新 skill" | Git diff, build result, remote path, rollback point, package/install state, post-checks | Release/deploy checklist, commands/results, rollback note | Do not push/publish/deploy without explicit intent |
| Developer workflow/tooling governance | "Codex 指令", "skill/plugin", "迁移到 Codex", "subagent" | Real config files, manifests, skill docs, install/update behavior, runtime markers | Compact rules, migration/compatibility answer, scoped tooling change | Do not mutate shared assets for Codex-only behavior |
| Long-running R&D handoff | "继续刚才", multi-day UAT/release/debug work | Changed files, commands, approvals, pages inspected, blockers, verified facts | Resume-ready state and next actions | Preserve task boundary and decision-relevant evidence |

## Scenario Priority

Groundwork should start with the scenarios that repeatedly convert messy R&D context into implementation-ready decisions or code. The priority is not a statement about importance forever; it is the first product cut.

| Priority | Scenario / mode | Estimated share of high-frequency R&D work | Why it belongs here |
| --- | --- | --- | --- |
| P0 | PRD/spec and task creation / `to-prd`, `to-issues`, `triage` | 20-25% | A full workflow needs business/spec intent and task context before prototype, contract, implementation, and UAT work can stay coherent. |
| P0 | Frontend integration documentation and review / contract branch inside `write-plan`, `prototype`, `implement`, or `verify` | 20-25% | This is the clearest repeated pain: docs, backend truth, frontend implementability, state values, and runtime behavior drift apart. It should be a first-version capability, not necessarily a standalone skill. |
| P0 | Implementation task execution and review / `implement` | 20-25% | Coding is a daily high-frequency action, even when recent sessions hide it behind Trellis-generated tasks. Groundwork must handle code truth, diff, tests, and verification directly. |
| P0 | Prototype creation and review / `prototype` | 15-20% | Prototypes are executable requirement evidence: often static HTML/UI in the user's work, but also useful for logic/state questions. |
| P0 | Verification and UAT/SIT readiness / `verify` | 10-15% | The user often needs to know whether code, runtime behavior, data, environment, and customer acceptance are actually ready. |
| P0 | Long-running R&D handoff / `handoff` | 5-10% | Multi-step research, docs, runtime checks, and code work need compact resumability. |
| P1 | Requirement-to-engineering clarification / `scope` | 8-12% | Important entry point, but should stay lightweight unless ambiguity or acceptance risk is high. |
| P1 | R&D artifact audience alignment / `artifact` | 8-12% | Needed for PRD, integration docs, technical PPTs, and generated summaries that otherwise mix readers. |
| P1 | Confirm-before-edit bug work / `diagnose` | 8-12% | Valuable because it prevents speculative fixes, but it can be a mode inside implementation work. |
| P1 | Release/deploy/runtime gate / `gate` | 5-8% | Important for safety, but it should activate only around mutation, deployment, publish, push, or remote state. |
| P2 | Developer workflow/tooling governance / `standards` | 3-6% | Useful for Groundwork itself, but should not dominate the product. |
| P2 | Test-data and mock handoff as standalone mode | 3-6% | Important, but better folded into `contract` or `verify` unless data mutation is the main task. |

For MVP, P0 scenarios should shape the first usable plugin. This means PRD/spec and task management are core, while prototype, implementation, verification/UAT, and handoff are first-version skills. Contract work should be embedded as a branch when API/UI/DB/state truth is needed. P1 scenarios can be included as thinner paths or checklists. P2 scenarios should wait unless they block the plugin itself.

## Scenario 1: Requirement-To-Engineering Clarification

This is the entry point when a fuzzy business or UAT observation must become engineering work.

Typical triggers:

- A UAT feedback item may be a requirement, a data problem, a config problem, or a misunderstanding.
- A business PRD needs to be split from a frontend/static-page implementation PRD.
- A product iteration needs P0/P1 boundaries before implementation starts.

Evidence:

- Current PRD, design docs, state-flow docs, API docs, database docs, and task notes.
- Real UAT behavior when the observation came from an environment.
- DB/ES records when the question depends on actual data readiness.
- User-provided wording corrections, because the user often refines business language precisely.

Output:

- Scope note or PRD section that separates verified facts, inferred causes, unresolved questions, and recommended decisions.
- Explicit current-task boundary and deferred items.
- Acceptance criteria that can drive code or UAT verification.

Failure modes:

- Writing polished prose before proving the underlying cause.
- Mixing global PRD, implementation task, frontend handoff, and customer summary into one artifact.
- Treating lack of test data as missing product capability.

## Scenario 1.5: Task Creation And Management

This is the missing workflow layer between PRD/spec and implementation. A task record is the durable unit of work that ties together PRD, plan, prototype, contract, implementation, verification, UAT, and handoff evidence.

Typical triggers:

- A PRD/spec is accepted and needs to become actionable work.
- A direct request becomes multi-step, cross-layer, or risky enough to track.
- A task needs to be resumed, blocked, reprioritized, verified, or archived.
- Review findings need to become implementation work.

Evidence:

- PRD/spec, acceptance criteria, or bug reproduction evidence.
- Existing task artifacts, current git status, and relevant repo context.
- Required downstream artifacts: plan, contract, prototype, verification, release, handoff.

Output:

- Task record with id, title, status, priority, type, source, artifact links, and next action.
- Optional implementation plan when the task is not obvious.
- Clear state transitions: draft, ready, in_progress, blocked, verification, done, archived.

Failure modes:

- Creating task ceremony for an obvious direct edit.
- Letting a task record replace the PRD/spec or code/runtime truth.
- Making task state opaque or tool-only.

## Scenario 2: Frontend Integration Documentation And Review

This covers API, state, DB, and frontend handoff accuracy. It is a core scenario because the user has repeatedly produced and reviewed frontend integration documents, not merely generated API notes.

Typical triggers:

- A frontend integration document may use guessed controller paths, field names, or status values.
- A handoff document needs to be rewritten so frontend can implement directly.
- A review asks whether existing integration documentation matches current backend behavior.
- Runtime request behavior differs from docs.
- Backend state-flow, database values, and UI entry points need one consistent vocabulary.

Evidence:

- Controllers, service methods, query objects, DTO/VO/PO classes, enums, mapper SQL, and tests.
- Existing frontend docs, API docs, database docs, and state-flow docs.
- Browser/network/runtime request evidence when UI transformation or cache behavior matters.
- Environment config such as tenant mappings, DingTalk template config, or Nacos values when it affects runtime behavior.

Output:

- Field-by-field and status-by-status contract map.
- Request/response examples only when backed by source or runtime evidence.
- Mismatch list: doc-only, code-only, runtime-only, ambiguous.
- Frontend-ready implementation notes: entry points, request timing, required fields, optional fields, enum/value domains, loading/empty/error behavior, and known environment caveats.
- Review findings when the input is an existing doc, ordered by implementation risk.

Failure modes:

- Keeping stale or guessed names because they are already in a doc.
- Treating old design text as authoritative over current code.
- Producing a readable doc that is still not implementable.

## Scenario 3: Prototype Creation And Review

This covers prototype work the user has done heavily, especially static HTML/UI prototypes, while directly absorbing mattpocock's broader definition: a prototype is throwaway code that answers a question.

Typical triggers:

- A PRD or business flow needs to be turned into a static HTML/UI prototype.
- A state model, data shape, or business rule needs to be driven interactively before implementation.
- A static HTML prototype needs to represent a PRD or revised business flow.
- Existing prototype screens need new menus, dialogs, state examples, or workflow branches.
- A prototype review asks whether menus, dialogs, statuses, actions, and edge states are complete.
- A page appears visually plausible but may not match the real backend/API/state-flow constraints.
- A prototype needs browser verification rather than only source inspection.

Evidence:

- PRD, frontend integration doc, state-flow, API/database docs, state/data model notes, and existing static HTML.
- Browser-visible behavior: navigation, modal opening, state switching, text overflow, empty/loading/error states, and responsive breakpoints when relevant.
- Real code or API contract when prototype fields/actions are meant to map to implementation.
- User corrections about business wording and workflow boundaries.

Output:

- New logic/state prototype or static HTML/UI prototype when the task is to make the flow concrete.
- Prototype patch when the requested change is clear.
- Review report with concrete gaps: missing entry point, wrong state semantics, unclear action ownership, incomplete edge state, inconsistent terminology, or non-implementable interaction.
- Browser verification notes when visual state or interaction is part of the claim.
- Clear distinction between prototype construction, visual polish, state-model learning, business coverage, and implementation contract gaps.

Failure modes:

- Treating static HTML as a mock picture instead of an executable requirement artifact.
- Treating logic/state prototypes as production code instead of temporary learning tools.
- Creating a beautiful prototype that does not cover required business states or actions.
- Reviewing only visual layout while missing business workflow or API-state mismatch.
- Adding attractive UI sections that do not map to required operations.

## Scenario 4: R&D Artifact Audience Alignment

This covers the repeated problem that PRDs, frontend integration docs, technical PPTs, and generated summaries can become unclear because they do not name the reader or downstream action.

Typical triggers:

- "这个内容面向对象不明."
- A PRD mixes business narrative, implementation detail, and acceptance notes.
- A frontend integration document reads like a product overview instead of an implementation contract.
- A PPT or briefing needs to explain engineering progress, risk, or architecture to a specific audience.
- A skill/plugin is created to route artifact generation through clearer roles.

Evidence:

- Target reader: business stakeholder, product owner, frontend developer, backend developer, QA, deployment owner, customer, or leadership.
- Artifact type and intended downstream action: decide scope, implement API, test flow, approve release, explain risk, or align stakeholders.
- Source evidence: code, docs, runtime behavior, UAT result, prototype, or issue list.
- Existing artifact structure and where it mixes audiences.

Output:

- Audience declaration before writing or reviewing.
- Artifact-specific structure:
  - PRD: business goal, scope, rules, acceptance, non-goals.
  - Frontend integration doc: routes, requests, fields, enums, states, examples, edge cases.
  - Review report: findings by severity/risk with evidence.
  - Technical PPT: narrative, decision points, evidence, risks, next steps.
- Rewrite or review findings that remove audience mixing.

Failure modes:

- One document trying to serve business approval, frontend implementation, backend design, and management reporting at once.
- PPTs that look polished but do not say what decision or action the audience should take.
- PRDs that bury business rules under API details, or integration docs that bury request fields under product narrative.

## Scenario 5: Implementation Task Execution And Review

This covers high-frequency coding work as a first-class Groundwork scenario.

Typical triggers:

- A task has a PRD, acceptance criteria, or implementation brief and needs code changes.
- A completed task needs code review against PRD, specs, tests, and actual diff.
- The user asks whether the implementation is correct, complete, and verified.

Evidence:

- Task PRD, implementation brief, repo standards, current git diff, and commits.
- Relevant repo specs such as backend guidelines, cross-layer thinking guides, quality guidelines, and domain specs.
- Source files changed by the task and tests/build commands that were run or should have been run.
- Runtime/UAT evidence when the implementation changes user-visible or environment behavior.

Output:

- Code changes when the task is actively being implemented.
- Implementation review when the task was already handled by an agent.
- Gap list between PRD acceptance criteria and actual diff/tests.
- Verification summary with exact commands/results, or a clear statement of missing verification.
- Follow-up tasks only when they are real residual implementation work, not generic cleanup.

Failure modes:

- Reviewing only the PRD or only the final summary without reading the diff and tests.
- Letting task summaries obscure unresolved code, data, or environment risks.
- Requiring another workflow framework to be installed or active before Groundwork can execute or review implementation work.

## Scenario 6: UAT/SIT Readiness Verification

This covers whether a flow can actually be tested or accepted in a target environment.

Typical triggers:

- "下周客户要验收，这个环境有没有数据?"
- "这条链路是不是通的?"
- "页面状态和执行记录说明什么?"
- "这个部署是不是生效了?"

Evidence:

- UAT/SIT page state through browser verification when visual behavior matters.
- Read-only DB/ES checks before data changes.
- Task creation/review records, mapping tables, tenant config, and environment constraints.
- Deployment path, static asset cache, session/login state, and backend availability.

Output:

- Readiness conclusion split into four claims: capability works, data is sufficient, environment is stable, customer can validate.
- Blocking gaps and the smallest config/data/deploy fix path.
- Stakeholder-ready summary when the result needs to be sent out.

Failure modes:

- Overclaiming readiness from a single API success.
- Repeating login/OCR or other fragile environment steps unnecessarily.
- Hiding data risk behind vague wording.

## Scenario 7: Confirm-Before-Edit Bug Work

This is the default for suspected defects and regression lists.

Typical triggers:

- The user says "先确认问题是否存在，存在再修改."
- A previous handoff doc may be wrong.
- A browser page, backend endpoint, copy text, or cache state looks suspicious.

Evidence:

- Exact source files and focused tests.
- Runtime reproduction path where behavior matters.
- Logs, API responses, or browser/network state if the issue is environment-dependent.
- `git status --short` and relevant diffs before editing.

Output:

- Exists / does not exist / inconclusive judgment with evidence.
- Minimal code or doc patch only if the issue exists.
- Focused verification command or manual check result.

Failure modes:

- Editing from a task list without reproduction.
- Broadening into unrelated cleanup.
- Reverting or masking user changes in a dirty worktree.

## Scenario 8: Test Data And Mock Handoff

This covers data work for frontend联调, backend validation, and UAT rehearsal.

Typical triggers:

- "给前端造一些数据."
- "写一份 mock 数据说明."
- "有没有可消耗的写数据?"
- "dev/UAT 直接灌数据可以吗?"

Evidence:

- Live schema and existing tenant rows.
- Real gateway responses for read/write APIs.
- Whether data is baseline read data, expanded-state examples, or fresh write targets.
- Sensitive values and customer-visible fields.

Output:

- Seed-data plan or SQL aligned to live schema.
- Separation between stable read examples and consumable write targets.
- Mock-data doc with placeholders for sensitive fields.
- Post-seed or post-gateway verification when feasible.

Failure modes:

- Assuming code schema equals live schema.
- Using rows that the workflow will immediately consume.
- Putting secrets, private URLs, tokens, or personal data into docs.

## Scenario 9: Release, Deploy, And Runtime Gate

This covers changes leaving the local workspace.

Typical triggers:

- "部署到 UAT."
- "发布 npm 包."
- "提交并推送远程."
- "更新 skill."
- "页面还是旧的，你看一下."

Evidence:

- Git diff, staged files, branch, build/test output.
- Remote deployment paths, backup/rollback directories, required SDK/runtime directories.
- Package version, install state, lockfiles, plugin/skill metadata.
- Post-deploy UI/API checks.

Output:

- Release or deployment checklist with exact commands and results.
- Rollback point or explicit rollback limitation.
- Runtime verification, not only local build success.
- Install/update distinction for tooling releases.

Failure modes:

- Deploying or publishing without explicit intent.
- Assuming a documented update path works without checking the installed state.
- Ignoring stale browser/app/static cache when runtime state does not match source.

## Scenario 10: Developer Workflow And Tooling Governance

This covers the development environment around the agent itself.

Typical triggers:

- Codex global or repo-local instructions need cleanup.
- An external workflow skill or plugin needs migration or compatibility judgment.
- A skill is needed to keep PRD, integration doc, and PPT generation aligned to the right target reader.
- A shared skill should remain shared, but Codex needs local behavior.
- The user asks about Inline mode, subagents, or multi-agent control.

Evidence:

- Real persisted config locations, not assumed files.
- `.codex`, `.agents`, plugin manifests, skill frontmatter, README/install docs, lockfiles.
- License files and third-party notices when bundling content.
- Runtime markers for true subagents: `spawn_agent`, new agent/thread id, `wait_agent`, independent lifecycle.

Output:

- Compact rules and scoped config changes.
- Clear boundary: shared skill, Codex-local fork, plugin-bundled skill, or repo-local policy.
- Role boundary for artifact skills, such as business narrative, renderer, and format bridge responsibilities.
- Verified install/update/migration instructions.
- Compatibility answer with evidence.

Failure modes:

- Turning global instructions into a large process manual.
- Mutating shared `~/.agents/skills` for Codex-only preferences.
- Letting a renderer or PPT skill silently decide product narrative or implementation contract.
- Installing overlapping global skills.
- Spawning nested agents for tightly coupled work.

## Scenario 11: Long-Running R&D Handoff

This is the glue for multi-step engineering work.

Typical triggers:

- The task spans several documents, source files, browser checks, and environment operations.
- The user says "继续刚才" or switches between research docs.
- Work is interrupted or context-compacted.

Evidence to preserve:

- Files changed and files intentionally left unchanged.
- Commands run, exact failures, approvals, and environment constraints.
- Pages inspected and visible/runtime states.
- Verified facts, memory-derived facts, inferences, blockers, and next actions.

Output:

- Resume-ready state summary.
- Clear current task boundary and deferred adjacent work.
- Decision-relevant evidence without noisy logs.

Failure modes:

- Restarting discovery from scratch after every interruption.
- Carrying an old objective into a new user instruction.
- Losing the distinction between verified current facts and stale memory.

## Secondary Or Out-Of-Core Scenarios

These appear in the user's history but should not drive the main Groundwork design:

| Scenario | Groundwork stance |
| --- | --- |
| Local Mac diagnostics | Useful as a diagnostic pattern, but not a core R&D workflow unless it blocks development. |
| AI daily reports and other finished information products | Should stay direct-answer/report-generation work, not a Groundwork framework pillar. |
| Working-hours / timesheet automation | Explicitly excluded from Groundwork core; it was a temporary operational need, not a product direction. |
| General business cost estimation | Relevant only when it turns into development scope, milestones, or acceptance criteria. |
| Generic browser/UI operation | Use only when it verifies R&D behavior, not as a standalone automation goal. |

## Groundwork Mode Mapping

| Mode | Primary scenarios | Purpose |
| --- | --- | --- |
| `scope` | Requirement clarification, iteration boundary | Convert ambiguous business input into engineering scope and acceptance criteria. |
| `to-prd` | PRD/spec creation and refinement | Capture business intent, rules, scope, non-goals, and acceptance criteria before downstream work. |
| `to-issues` | Task slicing and source linking | Resolve source task context, create or link tasks, split vertical slices, mark AFK/HITL, and link artifacts. |
| `triage` | Task state management | Classify task state, blockers, `ready-for-agent` / `ready-for-human`, closeout, and agent-ready brief quality. |
| `write-plan` | Task planning | Turn accepted task into executable implementation/review steps when direct work is not enough. |
| `contract` | Frontend integration documentation and review, mock docs | Align API, DB, state, frontend behavior, and documentation as an internal branch rather than a required standalone MVP skill. |
| `prototype` | Prototype creation and review | Build, revise, and review logic/state or UI/static HTML prototypes as executable requirement artifacts, then verify them visually when needed. |
| `artifact` | PRD, integration doc, review report, technical PPT | Keep target reader, source evidence, and downstream action explicit. |
| `implement` | Implementation tasks and code review | Execute or review code changes against PRD, specs, diff, tests, and verification evidence. |
| `verify` | Tests, runtime checks, UAT/SIT readiness, test data | Verify whether code, data, environment, and customer acceptance are ready. |
| `diagnose` | Confirm-before-edit bug work | Prove existence and cause before patching. |
| `gate` | Release, deploy, test-data writes, remote mutations | Enforce preview, approval, verification, and rollback awareness. |
| `standards` | Developer tooling, instructions, skills, plugins | Keep development workflows compact, scoped, and reproducible. |
| `handoff` | Long-running R&D work | Preserve state and decisions across interruptions. |

## Mode Invocation Contracts

Each mode should be implementable as a bounded Groundwork skill, deterministic tool, or plugin command. The contract below is the behavior surface, not a final CLI syntax.

| Mode | Trigger examples | Required evidence | Output shape | Direct answer vs artifact | Stop condition |
| --- | --- | --- | --- | --- | --- |
| `to-prd` | "写 PRD", "整理需求", "这个是不是需求", "to-prd" | User intent, existing docs, observed behavior, source/runtime evidence when relevant | PRD/spec with scope, non-goals, rules, acceptance criteria, open questions | Direct answer for narrow requirement judgment; artifact for accepted feature/task scope | Business authority or acceptance criteria are unavailable and cannot be clarified |
| `to-issues` | "拆任务", "to-issues", "从 PRD 拆 issues", "建 task" | PRD/spec, acceptance criteria, conversation, issue tracker, local markdown fallback, git/status context | Linked task source or local task record, vertical slices, AFK/HITL split, artifact links, next action | Direct answer for tiny work; task artifact only for multi-step/reusable/risky work without a better source | Work is too small to justify task tracking or source intent is unclear |
| `triage` | "triage", "任务状态", "能不能交给 agent", "ready-for-agent", "close task" | Existing issue/task/slices, blockers, comments, verification evidence, relevant source/runtime facts | State decision, missing info, blockers, agent-ready brief, closeout note | Direct answer for one task state decision; artifact/update when a durable task source owns the work | State transition would mutate external tracker without explicit user intent |
| `write-plan` | "制定实现计划", "拆实现步骤", "怎么做", "write plan" | Task record, PRD/spec, relevant source, constraints, expected verification | Plan with exact files/steps/commands/checkpoints | Direct outline for simple work; artifact for multi-step implementation | Plan would be speculative without source inspection |
| `contract` | "前端集成文档", "字段是不是猜的", "接口怎么接" | PRD/task context when available, current docs plus real controllers/DTOs/VOs/enums/SQL or runtime request evidence | Integration contract map, mismatch list, frontend-ready handoff | Direct answer for one field/status; artifact for multi-endpoint or multi-state handoff | Cannot locate source truth or runtime evidence and the result would become guessed |
| `prototype` | "做静态 HTML 原型", "评审这个原型", "改这个页面", "跑一下这个状态模型" | PRD/business flow/state model plus existing HTML or implementation constraints when available | Logic/state prototype, HTML prototype patch, review findings, browser verification note, captured answer | Direct answer for a small review; artifact/edit for prototype creation or patch | Required workflow/state rules are unknown and cannot be inferred safely |
| `implement` | "实现这个 task", "按 PRD 开发", "检查实现结果" | PRD/task brief or acceptance criteria, relevant source, git diff/status, tests/build commands | Code patch or implementation review with verification results | Direct answer only for read-only implementation assessment; edit when user asks to implement/fix | Acceptance signal is unknown, relevant source cannot be found, or changes would be unsafe without approval |
| `verify` | "有没有数据可以测", "链路通不通", "客户能不能验", "测试过了吗" | Environment target, test/build/runtime/page/API/DB evidence, current task/config/data state | Verification/readiness conclusion split by code/test/runtime/data/environment/customer validation | Direct answer for read-only readiness check; artifact for customer-facing or team handoff | Environment access is unavailable and no reliable substitute evidence exists |
| `handoff` | "继续刚才", context transition, multi-day work | Changed files, commands, failures, verified facts, blockers, next action | Resume-ready summary or `.groundwork/tasks/<task-id>/handoff.md` artifact | Direct summary for short work; artifact for long-running or reusable work | Current objective conflicts with newest user instruction |
| `scope` | "这个是不是需求", "这期做什么", "整理成 PRD" | Existing docs, observed behavior, user corrections, source/runtime evidence if relevant | Scope note, PRD delta, acceptance criteria | Direct answer for narrow decision; artifact for feature/task boundary | The decision depends on unavailable business authority |
| `artifact` | "面向对象不清", "PRD/集成文档/PPT 给谁看" | Target reader, source evidence, artifact type, downstream action | Audience-specific outline, rewrite, or review findings | Direct answer for structure advice; artifact/edit when rewriting | Target reader cannot be identified |
| `diagnose` | "先确认问题是否存在", suspected bug | Reproduction path, source/tests/logs/runtime evidence, dirty diff | Exists/not-exists/inconclusive judgment, then minimal patch if requested | Direct answer until existence is proven; edit only after evidence | No deterministic feedback loop or reproduction path can be built |
| `gate` | "部署", "发布", "提交并推送", "造数据" | Diff, command preview, target environment, rollback or recovery path | Preview, approval gate, executed command/results, rollback note | Direct answer for risk review; action only after explicit intent | User intent is ambiguous or rollback/destructive scope is unclear |
| `standards` | "Codex 指令", "skill/plugin", "迁移到 Codex" | Real config/manifests/skills/plugin docs/install state | Compact standards, migration plan, scoped config patch | Direct answer for compatibility; edit only after reading real files | Change would mutate shared assets for Codex-only behavior |

## MVP Boundary

Groundwork MVP should be a small Codex-native workflow plugin, not another installed workflow stack. Public skill names should favor action clarity over abstract mode labels.

MVP includes:

- `to-prd`: PRD/spec creation and refinement from conversation, source evidence, prototype notes, or UAT feedback.
- `to-issues`: issue-source-first task slicing, artifact links, vertical slices, AFK/HITL split, and local markdown fallback.
- `triage`: task state, `ready-for-agent` / `ready-for-human`, blockers, agent-ready brief, and closeout.
- `write-plan`: task slicing and execution planning when direct work is insufficient.
- `prototype`: logic/state or UI/static HTML prototype creation, revision, and review as executable requirement evidence.
- `implement`: implementation and implementation-review path based on PRD/task, diff, tests, and verification.
- `verify`: verification/UAT readiness evidence for code, runtime, data, and customer validation.
- `handoff`: compact resume state for long-running R&D work.

MVP includes thin supporting paths:

- `scope` as an internal branch of `to-prd` / `to-issues`.
- `artifact` for target-reader alignment.
- `contract` for source-truth-backed integration handoff and review when the task crosses API/UI/DB/state boundaries.
- `diagnose` for confirm-before-edit bug work.
- `gate` for explicit write/deploy/publish/data mutation safety.

MVP excludes:

- Autonomous scheduling or auto-run loops.
- Database-backed runtime state.
- Worktree orchestration, merge strategy ownership, or provider/model routing.
- Installing, wrapping, or migrating into Trellis, Superpowers, gstack, BMAD, Spec Kit, Agent OS, GSD, or similar source frameworks.
- General personal productivity, timesheet automation, news/report generation, or Mac cleanup as core modes.

Suggested artifact policy:

- Default to direct answers when the result is one-off and short-lived.
- Write repo-local artifacts only when they will be reused across implementation, review, UAT, release, or handoff.
- Prefer the real task source when it exists: GitHub/GitLab issue, Linear/Jira ticket, TaskRepo markdown task, PRD/spec file, current conversation, or future Symphony context.
- Use `.groundwork/tasks/<task-id>/` only as the local fallback for managed work. Keep files small, human-readable, and task-scoped. Do not mirror `.trellis/`, `.planning/`, `.scratch/`, or `.gsd/` structures.

## End-To-End Workflow Examples

### Flow 1: PRD To Task To Prototype To Implementation Contract

1. `to-prd`: clarify business boundary, non-goals, rules, and acceptance criteria.
2. `to-issues`: resolve or create the task source, split vertical slices, mark AFK/HITL work, and link expected artifacts.
3. `triage`: confirm whether slices are `ready-for-agent`, `ready-for-human`, blocked, or too vague.
4. `write-plan`: decide whether prototype, contract, technical design, or data setup is needed before code.
5. `prototype`: build or revise the static HTML prototype and browser-check key states.
6. `contract`: map prototype fields/actions to real API, DB, enum, and frontend state truth.
7. `implement`: implement or review the code against PRD/task/plan/prototype/contract.
8. `verify`: run tests/runtime/UAT-readiness checks appropriate to the risk.
9. `handoff`: preserve remaining gaps, verification commands, and next actions.

Success signal: frontend can implement without guessing, backend/code changes are verified, and the prototype does not contradict the implementation contract.

### Flow 2: Suspected Bug To Verified Fix

1. `diagnose`: reproduce or prove the suspected issue does not exist.
2. `contract` or `verify`: inspect API/state/data/environment truth if the bug crosses layers.
3. `implement`: patch only the verified issue and run focused tests/checks.
4. `handoff`: report exact evidence, files changed, commands run, and residual risk.

Success signal: the answer says exists / not exists / inconclusive with evidence, and any patch is minimal and verified.

### Flow 3: UAT Readiness To Customer-Safe Conclusion

1. `verify`: split readiness into code/test, capability, data, environment, and customer validation.
2. `contract`: confirm that current docs/API/UI state match what UAT will exercise.
3. `gate`: preview and approve any data/config/deploy mutation before execution.
4. `artifact`: produce a customer-safe or team-safe summary if the result must be shared.
5. `handoff`: preserve environment caveats and next validation steps.

Success signal: the team knows whether the customer can validate now, what blocks validation, and the smallest safe fix path.

## Cross-Scenario Principles

- Code/runtime truth beats stale docs.
- Evidence comes before wording and before editing.
- Read-only checks come before data mutation.
- Preview-before-write applies to test/UAT data, release actions, deployment actions, and remote state.
- Separate requirement, prototype, contract, review report, technical presentation, test data, UAT readiness, release, and handoff artifacts.
- Do not require or trigger installation of Trellis, Superpowers, gstack, BMAD, Spec Kit, Agent OS, or similar frameworks; Groundwork should define its own modes and artifacts.
- Name the target reader and downstream action before generating or reviewing PRDs, integration docs, review reports, or technical PPTs.
- Distinguish capability readiness from data readiness.
- Verification should match risk: tests for code, browser/runtime checks for UI, DB/API checks for data, post-deploy checks for release.
- If the requested behavior already exists, report evidence and do not edit.
- Keep outputs implementation-ready rather than merely polished.

## Open Gaps To Confirm

The current R&D-focused model may still miss:

- Whether Groundwork should explicitly cover database migration / schema-review workflows.
- Whether it should include CI failure triage as a first-class scenario.
- Whether frontend visual design-quality review should go beyond prototype/business-flow review and become first-class.
- Whether customer-facing acceptance reports and release notes should be first-class artifacts.
- Which private/UAT operations need stricter gates than normal preview-before-write.
