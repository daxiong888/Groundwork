# PRD v2：Groundwork Dispatch Runtime Router 与多运行时适配层

## Target Reader

本地 Codex 实施线程、Groundwork 维护者、`codex-managed-worktree-threads` 维护者、未来 runtime adapter 维护者。

## Reader Action Needed

基于本 PRD 将需求拆成可实施 issues，并在本地完成 Groundwork 与 `codex-managed-worktree-threads` 的技能/文档/模板/检查脚本改造。

## Decision Supported

将 Groundwork 的 `dispatch` 设计为**通用运行时路由器**，而不是只服务 Codex App managed worktree 的 package generator。

最终形态：

```text
Groundwork dispatch
  = runtime router / execution planner / adapter package generator

codex-managed-worktree-threads
  = Codex App managed worktree thread runtime adapter

codex_subagent
  = dispatch 支持的一类 runtime route，第一阶段只生成 package，不默认自动 spawn

main_thread_direct / main_thread_readonly / clean_reviewer
  = dispatch 支持的轻量 runtime routes
```

## Scope

本 PRD 覆盖：

- Groundwork 新增 public skill：`dispatch`。
- Groundwork 新增 shared spec：`GOAL-CONTRACT.md`。
- Groundwork 新增 dispatch 内部规范：

  - `RUNTIME-ADAPTERS.md`
  - `DISPATCH-PACKAGE.md`
  - `RESULT-PACKAGE.md`
  - `ROUTING-PROFILES.md`
  - `CONFLICT-PREFLIGHT.md`

- Groundwork 扩展 `triage` 的 Agent Brief，使 ready-for-agent 任务可携带 Goal Contract 和 Preferred Runtime。
- Groundwork 扩展 `to-issues` 输出，让 issue draft 带 runtime candidate / isolation / parallelization 字段。
- `codex-managed-worktree-threads` 瘦身为只消费 `runtime_id = codex_app_managed_worktree_thread` 的 runtime adapter。
- Dispatch 支持 subagent route，但第一阶段不强制自动 spawn subagent，只输出 Subagent Package 和能力检测/执行建议。
- 借鉴 `qiaomu-goal-meta-skill` 的强 `/goal` 合同思想。
- 借鉴 Superpowers `dispatching-parallel-agents` 的 independent problem domains / focused prompts / parallel integration 模式。

## Out of Scope

本 PRD 不要求：

- Groundwork 直接调用 Codex App thread tools。
- Groundwork 默认自动 spawn subagents。
- 新增独立 `codex-subagents-adapter` repo 或 public skill。
- 把 `codex-managed-worktree-threads` 物理搬进 Groundwork。
- 创建任务数据库。
- 集成 GitHub / Linear / Jira API。
- 自动 commit、push、open PR、close issue。
- 用 subagent 替代所有 managed worktree thread。
- 让 `codex-managed-worktree-threads` 继续承担 PRD、issue、triage、ready-for-agent、runtime routing 判断。
- 直接 vendor `qiaomu-goal-meta-skill` 或 Superpowers。

---

# 1. Evidence / Source Basis

Groundwork 当前已经有清晰的任务状态主干：`to-prd -> to-issues -> triage -> write-plan or implement -> verify -> triage -> handoff`，并且明确保持 tracker-neutral，不做外部 tracker integration 或 task database。

`to-issues` 的职责是从 accepted PRD/spec/plan 生成 vertical work units，并携带 acceptance criteria、blockers、risk、AFK/HITL、contract impact、verification evidence needed、ready-for-agent missing fields；但它只产生 recommendation candidate，最终 readiness 属于 `triage`。

`triage` 的 ready-for-agent gate 已经要求 acceptance criteria、source/evidence 或 first inspection step、expected output、stop condition、AFK/HITL decision points、blockers、out-of-scope boundaries 都明确。

Groundwork 当前 Agent Brief 已包含 Task、Source/Evidence、Known Source、Key Interfaces、Acceptance Criteria、Out Of Scope、Risk/Gate、Execution、Stop Condition、Verification Expectations 等字段，适合扩展为 Goal Contract 和 runtime routing 输入。

Groundwork plugin architecture 强调 supporting behaviors 应先嵌入现有 skills，只有反复使用证明必要后再成为 public skill，并要求 skills 保持窄触发、证据先行、避免过宽 public surface。

Codex App 官方介绍强调它是面向多个 agents 的 command center，支持 multiple agents 并行工作、separate threads、thread 内 diff review、以及内置 worktrees，让多个 agents 在同一 repo 的 isolated copies 上工作。([OpenAI][1])

OpenAI release notes 在 2026-06-09 的 Codex iOS 更新中提到新增 branch/worktree、Codex profiles、`/goal`、inline review comments 等能力，说明 goals/worktrees/review surface 正在成为 Codex 运行时的重要能力面。([OpenAI][2])

Superpowers `dispatching-parallel-agents` 的核心原则是：面对多个独立 problem domains 时，每个 agent 处理一个独立域；它强调 focused、self-contained、specific output 的 agent prompt，并在 agents 返回后 review summaries、check conflicts、run full test suite。([Playbooks][3])

`qiaomu-goal-meta-skill` 的核心是把模糊任务收敛成可复制的 Codex `/goal` 指令，并要求 outcome、verification、constraints、boundaries、iteration policy、stop conditions、pause conditions；它也明确不默认执行 goal 本身，只创建 goal instruction。([GitHub][4])

Subagent route 应采用 capability detection 和保守 gate：公开 Codex issues 显示，subagent 指令可能需要用户 prompt 显式授权、custom subagents 在不同 Codex surfaces 中可用性不一致、subagent lifecycle/cleanup 也可能存在限制或 bug。([GitHub][5])

---

# 2. Problem

用户当前已经摸索出一套高效流程：

```text
Groundwork to-prd
  -> Groundwork to-issues
  -> 每个 issue 作为独立 goal
  -> Codex App managed worktree 子线程并行实现
```

但这个流程当前有四类结构性问题。

## 2.1 运行时选择过早绑定到 managed worktree thread

不是所有任务都需要 worktree：

```text
read-only review
multi-perspective critique
architecture/security/QA lens review
planning-only
triage
codebase exploration
root-cause diagnosis without edits
```

这些任务需要的是上下文隔离、角色隔离或并行探索，不一定需要 filesystem isolation 或 diff review surface。

## 2.2 `codex-managed-worktree-threads` 职责膨胀

如果继续增强它，它会逐步承担：

```text
PRD acceptance
issue readiness
AFK/HITL
task type classification
runtime selection
Goal Contract generation
model/reasoning profile assignment
parallel conflict preflight
```

这些其实是 Groundwork 的任务语义层，不应该放在 runtime adapter 中。

## 2.3 Goal Mode 容易污染 coordinator

用户说“每个 issue 用 goal mode 实现”时，模型可能在当前主线程启动 Goal Mode，而不是把 `/goal` 放进 child thread prompt。

这需要更硬的结构边界：

```text
Groundwork triage/dispatch 生成 Goal Contract
runtime adapter 只把 Goal Contract 投递给被选中的 child runtime
main/coordinator thread 永远不执行 child goal
```

## 2.4 Subagent 能力值得接入，但不应默认替代 threads

Subagent 更适合 read-only exploration、多视角 review、独立问题域诊断、planning 或 findings 输出。Managed worktree thread 更适合 write implementation、独立 diff、验证和长期可见生命周期。

因此需要一个通用 `dispatch` runtime router，而不是一个只会生成 managed worktree package 的 narrow dispatcher。

---

# 3. Product Goal

建立一个六层架构：

```text
Layer 1 · Product Intent
Groundwork to-prd
  -> accepted PRD / spec / acceptance criteria

Layer 2 · Task Slicing
Groundwork to-issues
  -> vertical issues / task slices with runtime candidates

Layer 3 · Readiness + Goal Contract
Groundwork triage + GOAL-CONTRACT
  -> ready-for-agent Agent Brief + strong /goal contract + preferred runtime candidate

Layer 4 · Dispatch / Runtime Router
Groundwork dispatch
  -> runtime_id, isolation level, parallel group, execution profile, adapter package

Layer 5 · Runtime Adapters
- codex_app_managed_worktree_thread
- codex_subagent
- main_thread_direct
- main_thread_readonly
- clean_reviewer
- future adapters

Layer 6 · Result Integration
Groundwork verify / triage / handoff
  -> result package, review package, findings package, validation evidence, closeout
```

核心产品目标：

```text
Groundwork decides what should run, why, where, with what constraints.

Runtime adapters execute only packages for their supported runtime.
```

---

# 4. Final Architecture Decision

## 4.1 Groundwork owns

```text
- PRD truth
- issue slicing
- readiness
- AFK/HITL
- Goal Contract
- runtime routing
- isolation-level choice
- parallelization / conflict preflight
- execution profile decision
- adapter package generation
- expected result package definition
- verification / closeout recommendation
```

## 4.2 `codex-managed-worktree-threads` owns

```text
- Codex App thread tool discovery
- validating packages with runtime_id = codex_app_managed_worktree_thread
- creating Codex App managed worktree child threads
- delivering child prompts
- placing /goal only in child thread prompt
- model/reasoning selector enforcement when tools expose it
- read_thread monitoring
- review package collection
- managed worktree lifecycle/status reporting
- no remote writes without explicit approval
```

## 4.3 `codex_subagent` in Phase 1 owns no automatic execution

First implementation should only define:

```text
- subagent runtime capability profile
- subagent package schema
- subagent findings/diagnosis result package schema
- tool availability / explicit approval gate
```

It should not automatically spawn subagents unless the local runtime exposes tools and the user explicitly asks execution.

---

# 5. Key Concepts

## 5.1 Goal Contract

A Goal Contract is a strong executable goal specification, not execution itself.

Required shape:

```text
Goal Contract
- Goal Command:
- Outcome:
- Source Truth:
- Acceptance Criteria Mapping:
- Verification:
- Constraints:
- Boundaries:
- Iteration Policy:
- Stop When:
- Pause If:
- Non-goals:
- Risk / Gate:
```

Rules:

```text
- Goal Command must start with /goal.
- Chinese user-facing content may be Chinese, but command prefix remains /goal.
- No placeholders in executable goal: no [Outcome], TODO, TBD, 待定.
- Product truth, business rules, and acceptance criteria must not be invented.
- Low-risk execution details may use conservative defaults if assumptions are explicit.
- Unknown/specialized/high-risk domains should use discovery-first goals.
- Verification must name concrete evidence: command, test, browser path, screenshot, logs, runtime output, artifact path, or review checklist.
- Boundaries must limit writes and name forbidden areas.
- Iteration Policy must bound retry behavior.
- Stop When and Pause If are required.
```

## 5.2 Runtime Adapter

A runtime adapter is an execution backend with declared capabilities.

Examples:

```text
codex_app_managed_worktree_thread
codex_subagent
main_thread_direct
main_thread_readonly
clean_reviewer
```

Each adapter has:

```text
- runtime_id
- context isolation level
- filesystem isolation level
- write capability
- diff surface capability
- parallel capability
- lifecycle visibility
- goal support
- model/reasoning selector support
- best_for
- avoid_for
- required output package
```

## 5.3 Dispatch Package

A Dispatch Package is the output of Groundwork `dispatch`. It contains runtime-specific packages for chosen adapters.

`dispatch` may output packages for multiple runtimes, but no adapter consumes packages not addressed to it.

## 5.4 Result Package

A Result Package is the unified envelope for all runtime outputs.

Specific result types:

```text
worktree thread -> review_package
subagent readonly review -> findings_package
subagent diagnosis -> diagnosis_package
main thread direct -> direct_result
clean reviewer -> review_findings
```

---

# 6. Functional Requirements

## FR-1：新增 Groundwork public skill `dispatch`

### Required Files

```text
Groundwork/
  skills/dispatch/SKILL.md
  skills/dispatch/RUNTIME-ADAPTERS.md
  skills/dispatch/DISPATCH-PACKAGE.md
  skills/dispatch/RESULT-PACKAGE.md
  skills/dispatch/ROUTING-PROFILES.md
  skills/dispatch/CONFLICT-PREFLIGHT.md
  evals/prompts/dispatch.csv
  evals/scenarios/groundwork-runtime-router.md
```

### Trigger Contract

Should trigger:

```text
- “把这些 ready-for-agent issues 分发给 agent 做”
- “根据这些 issues 决定哪些开 worktree，哪些用 subagent”
- “给这些任务分配模型和思考强度”
- “判断哪些 issue 可以并行”
- “生成 execution matrix”
- “生成 dispatch package”
- “多视角评审但不要创建 worktree”
- “这些任务哪些适合 subagent，哪些适合 managed worktree”
```

Should not trigger:

```text
- 需求还没 accepted -> use to-prd
- issues 还没拆 -> use to-issues
- readiness 未知 -> use triage
- 单个小任务直接实现 -> use implement
- 只写实现计划 -> use write-plan
- 只做完成验证 -> use verify
```

### Output Shape

````text
Dispatch Summary

Source Truth
- PRD:
- Issue Set:
- Readiness Source:
- Evidence Level:

Runtime Capability Check
- Available / assumed runtimes:
- Runtime selectors available:
- Subagent execution available:
- Worktree thread execution available:
- Fallback behavior:

Task Matrix
| Task | Type | Readiness | Runtime | Isolation | Parallelization | Goal | Execution Profile | Validation | Result Package | Approval Needed |
|---|---|---|---|---|---|---|---|---|---|---|

No-Execution / Blocked / Needs Split
- Task:
- Reason:
- Required next action:

Runtime Packages
```yaml
dispatch_version: 2
...
````

Next Action

````

### Required Behavior

`dispatch` must:

```text
- classify task type
- confirm readiness source
- consume Goal Contract when available
- identify missing Goal Contract fields
- assign runtime_id
- assign isolation level
- assign execution profile
- identify parallelization eligibility
- identify conflict groups
- generate runtime-specific package
- define expected result package
- stop before execution unless user explicitly requests execution and tools are available
````

---

## FR-2：新增 `RUNTIME-ADAPTERS.md`

### Required File

```text
Groundwork/skills/dispatch/RUNTIME-ADAPTERS.md
```

### Runtime Capability Profiles

#### Runtime: Codex App managed worktree thread

```yaml
runtime_id: codex_app_managed_worktree_thread
display_name: Codex App Managed Worktree Thread
supports_parallel: true
context_isolation: thread
filesystem_isolation: codex_managed_worktree
can_write_files: true
diff_review_surface: strong
lifecycle_visibility: strong
supports_long_running_tasks: true
supports_goal_mode: true
supports_model_selector: tool_if_available
supports_reasoning_selector: tool_if_available
best_for:
  - independent write implementation
  - feature issue
  - bug fix
  - migration with isolated worktree
  - task requiring durable diff
  - task requiring validation evidence
avoid_for:
  - read-only review
  - planning-only work
  - tiny direct edits
  - tasks with shared-file conflict unless serialized
required_output:
  - review_package
```

#### Runtime: Codex subagent

```yaml
runtime_id: codex_subagent
display_name: Codex Subagent
supports_parallel: true
context_isolation: subagent_prompt
filesystem_isolation: none_or_tool_dependent
can_write_files: false_by_default
diff_review_surface: weak_to_medium
lifecycle_visibility: medium_or_tool_dependent
supports_long_running_tasks: limited_or_tool_dependent
supports_goal_mode: prompt_level
supports_model_selector: tool_if_available
supports_reasoning_selector: tool_if_available
best_for:
  - read-only parallel review
  - independent codebase exploration
  - independent test failure diagnosis
  - multi-perspective review
  - root-cause investigation
  - findings or plan output
avoid_for:
  - high-risk writes
  - tasks requiring durable diff surface
  - tasks requiring isolated filesystem
  - tasks needing reliable cleanup unless runtime confirms support
required_output:
  - findings_package
  - diagnosis_package
  - no_file_edits_unless_explicit
```

#### Runtime: Main thread direct

```yaml
runtime_id: main_thread_direct
display_name: Main Thread Direct
supports_parallel: false
context_isolation: none
filesystem_isolation: current_workspace
can_write_files: true
diff_review_surface: current_session
lifecycle_visibility: strong
supports_goal_mode: no_for_child_goal
best_for:
  - tiny edits
  - direct answers
  - one-off low-risk fixes
  - coordination
avoid_for:
  - multi-task parallel work
  - isolated experiments
  - work requiring independent lifecycle
required_output:
  - direct_result
```

#### Runtime: Main thread read-only

```yaml
runtime_id: main_thread_readonly
display_name: Main Thread Read-only
supports_parallel: false
context_isolation: none
filesystem_isolation: none
can_write_files: false
best_for:
  - PRD review
  - dispatch matrix review
  - architecture critique
  - user-facing decision support
required_output:
  - findings_package
```

#### Runtime: Clean reviewer

```yaml
runtime_id: clean_reviewer
display_name: Clean Reviewer
supports_parallel: maybe
context_isolation: review_package
filesystem_isolation: none
can_write_files: false
best_for:
  - review package inspection
  - diff conformance review
  - security lens
  - QA lens
  - product lens
avoid_for:
  - implementation
required_output:
  - review_findings
```

### Runtime Selection Rules

```text
- Choose managed worktree thread when code writes + filesystem isolation + durable diff are required.
- Choose subagent when task is read-only, exploratory, diagnostic, or perspective-based.
- Choose main_thread_direct for trivial direct work.
- Choose main_thread_readonly for coordinator-level review and decision support.
- Choose clean_reviewer when reviewing a completed review package or diff evidence.
```

---

## FR-3：新增 `DISPATCH-PACKAGE.md`

### Required File

```text
Groundwork/skills/dispatch/DISPATCH-PACKAGE.md
```

### Schema

```yaml
dispatch_version: 2

source:
  prd: ""
  issue_set: ""
  readiness_source: ""
  source_truth_status: accepted | external_accepted | issue_ready | mixed | unknown
  redactions_applied: ""

runtime_policy:
  allow_parallel: true
  max_parallel_units: 3
  remote_writes_allowed: false
  destructive_actions_allowed: false
  default_runtime_preference_order:
    - codex_app_managed_worktree_thread
    - codex_subagent
    - main_thread_direct
    - main_thread_readonly
    - clean_reviewer

model_policy:
  selector_enforcement: tool_if_available_else_prompt_preference

tasks:
  - task_id: ""
    title: ""
    task_type: write_implementation | read_only_review | planning_only | hybrid | diagnosis | verification | direct
    readiness: ready_for_agent | ready_for_human | needs_info | blocked | needs_split | accepted_direct
    runtime_id: codex_app_managed_worktree_thread | codex_subagent | main_thread_direct | main_thread_readonly | clean_reviewer
    runtime_reason: ""

    isolation:
      context: thread | subagent_prompt | none | review_package
      filesystem: codex_managed_worktree | current_workspace | none | tool_dependent
      diff_surface: required | not_required | optional

    parallelization:
      eligible: true
      conflict_group: ""
      dependency_group: ""
      max_parallel_group_size: 1
      merge_order_hint: ""

    source_package:
      prd_excerpt: ""
      issue_body: ""
      relevant_comments: ""
      known_source_or_first_inspection_step: ""
      redactions_applied: ""

    goal_contract:
      goal_command: ""
      outcome: ""
      source_truth: ""
      acceptance_criteria_mapping: ""
      verification: ""
      constraints: ""
      boundaries: ""
      iteration_policy: ""
      stop_when: ""
      pause_if: ""
      non_goals: ""
      risk_gate: ""

    execution_profile:
      model_profile: ""
      reasoning_effort: low | medium | high
      cost_latency_bias: fast | balanced | quality
      routing_reason: ""
      selector_enforcement: tool_if_available_else_prompt_preference

    validation:
      fastest_signal: ""
      required_evidence: ""

    runtime_package:
      adapter: ""
      thread_title: ""
      subagent_role: ""
      subagent_prompt: ""
      can_write_files: false
      expected_output: review_package | findings_package | diagnosis_package | direct_result | review_findings

    approval:
      required: false
      reason: ""
```

### Rules

```text
- runtime_id determines which adapter may consume the package.
- codex_app_managed_worktree_thread requires task_type = write_implementation.
- codex_app_managed_worktree_thread requires goal_contract, source_package, validation, review_package.
- codex_subagent defaults to can_write_files = false.
- codex_subagent may only write if user explicitly requests write-capable subagent execution and runtime confirms safe support.
- read_only_review must not route to codex_app_managed_worktree_thread.
- planning_only must not route to codex_app_managed_worktree_thread.
- hybrid must route to needs_split or split_first until a write implementation subtask exists.
- remote_writes_allowed defaults false.
- destructive_actions_allowed defaults false.
```

---

## FR-4：新增 `RESULT-PACKAGE.md`

### Required File

```text
Groundwork/skills/dispatch/RESULT-PACKAGE.md
```

### Unified Result Envelope

```yaml
result_package:
  task_id: ""
  runtime_id: ""
  status: ready_for_review | needs_remediation | blocked | no_execution_needed | no_worktree_needed
  output_type: review_package | findings_package | diagnosis_package | direct_result | review_findings

  task:
    title: ""
    task_type: ""
    goal_contract_used: true
    source_truth: ""

  runtime:
    adapter: ""
    execution_profile_requested: ""
    execution_profile_actual: ""
    selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown

  changes:
    changed_files: []
    diff_summary: ""
    diff_or_findings_completeness: complete | redacted_complete | redacted_partial | not_applicable

  validation:
    applicability: applicable | not_applicable
    commands_run: []
    results: ""
    checks_not_run: ""
    evidence: ""

  findings:
    summary: ""
    details: ""
    citations_or_paths: ""

  risk:
    remaining_risks: []
    blockers: []
    recommended_next_route: verify | triage | dispatch_write_task | human_decision | done
```

### Runtime-specific Output Requirements

```text
codex_app_managed_worktree_thread:
  output_type = review_package
  must include changed files, diff summary, validation evidence

codex_subagent:
  output_type = findings_package or diagnosis_package
  must include no-file-edit assertion unless explicitly write-enabled

main_thread_direct:
  output_type = direct_result

main_thread_readonly:
  output_type = findings_package

clean_reviewer:
  output_type = review_findings
```

---

## FR-5：新增 `ROUTING-PROFILES.md`

### Required File

```text
Groundwork/skills/dispatch/ROUTING-PROFILES.md
```

### Routing Table

| Task Shape                                                     | Default Runtime                                     | Reason                                                       |
| -------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------ |
| Small direct answer or tiny low-risk edit                      | `main_thread_direct`                                | Runtime overhead not justified                               |
| Accepted independent write issue                               | `codex_app_managed_worktree_thread`                 | Needs filesystem isolation, diff, validation, review package |
| High-risk schema/API/migration/security/data correctness write | `codex_app_managed_worktree_thread`                 | Needs isolation and high-quality review                      |
| Read-only multi-perspective review                             | `codex_subagent` or `clean_reviewer`                | Needs role/context isolation, not worktree                   |
| PRD / architecture / security / QA critique                    | `codex_subagent` or `main_thread_readonly`          | Usually read-only                                            |
| Independent codebase exploration                               | `codex_subagent`                                    | Useful context isolation without worktree                    |
| Independent test failure diagnosis                             | `codex_subagent`                                    | One problem domain per agent                                 |
| Hybrid investigation + possible fix                            | `codex_subagent` first, then dispatch write subtask | Avoid premature worktree creation                            |
| Planning-only                                                  | `main_thread_readonly` or `codex_subagent`          | No writes                                                    |
| Review completed worktree package                              | `clean_reviewer`                                    | Review package is the source                                 |
| Shared-file or shared-contract conflicts                       | serialize / ask approval                            | Do not default parallelize                                   |

### Execution Profile Defaults

| Task Shape                         | Model Profile                          | Reasoning Effort | Cost/Latency Bias |
| ---------------------------------- | -------------------------------------- | ---------------- | ----------------- |
| Tiny direct or doc/config change   | fast coding model                      | low              | fast              |
| Normal feature issue with clear AC | balanced coding model                  | medium           | balanced          |
| Cross-cutting feature              | strongest coding/reasoning available   | high             | quality           |
| Migration/schema/API/security      | strongest coding/reasoning available   | high             | quality           |
| Read-only multi-perspective review | reviewer profile                       | medium/high      | balanced/quality  |
| Codebase exploration               | fast/balanced reasoning profile        | medium           | balanced          |
| High-risk clean review             | strongest reviewer/reasoning available | high             | quality           |

### Selector Enforcement

```text
- If runtime exposes model/reasoning selectors, pass them.
- If runtime does not expose selectors, include execution profile in prompt.
- Do not claim tool-enforced selector unless runtime confirms it.
```

---

## FR-6：新增 `CONFLICT-PREFLIGHT.md`

### Required File

```text
Groundwork/skills/dispatch/CONFLICT-PREFLIGHT.md
```

### Checks

Before routing tasks in parallel, dispatch must check likely conflicts in:

```text
- files
- modules
- routes
- API contracts
- DB schemas
- migrations
- generated artifacts
- shared fixtures
- public types/interfaces
- test snapshots
- state machines
- shared config
```

### Rules

```text
- Same conflict group cannot be parallelized as write tasks without explicit approval.
- Read-only subagent reviews may run in parallel even when they inspect same area.
- Hybrid tasks must split before write parallelization.
- If conflict cannot be determined, mark conflict_group = unknown and ask for serialization or approval.
- Merge order hint is required for conflicting write tasks.
```

---

## FR-7：新增 Groundwork `GOAL-CONTRACT.md`

### Required File

```text
Groundwork/skills/_shared/GOAL-CONTRACT.md
```

### Required Fields

```text
Goal Command
Outcome
Source Truth
Acceptance Criteria Mapping
Verification
Constraints
Boundaries
Iteration Policy
Stop When
Pause If
Non-goals
Risk / Gate
Preferred Runtime
Result Package Expected
```

### Integration Points

```text
to-issues:
  identifies missing Goal Contract fields but does not final-mark ready.

triage:
  creates Goal Contract for ready-for-agent tasks.

dispatch:
  consumes Goal Contract and may reject tasks with missing required fields.

runtime adapters:
  receive Goal Contract but do not generate product truth.
```

### Quality Bar

A strong Goal Contract:

```text
- has one concrete outcome
- maps acceptance criteria to verification
- names exact checks or evidence where known
- protects unrelated files, user data, secrets, and default branches
- defines write boundary
- defines iteration policy
- defines stop evidence
- defines pause conditions
- names preferred runtime or lets dispatch choose one
```

Reject or revise if it:

```text
- says only “make it better”, “finish this”, “fix bugs”
- lacks verification
- allows broad edits without reason
- asks for repeated retries without new evidence
- has no pause condition
- leaves placeholders
- turns vague quality adjectives into unverifiable criteria
```

---

## FR-8：新增 `lint_goal_contract.py`

### Required File

```text
Groundwork/scripts/lint_goal_contract.py
```

### Inputs

```bash
python3 scripts/lint_goal_contract.py <goal-contract-file>
```

### Checks

Must fail on:

```text
- missing /goal
- missing Verification / 验证
- missing Constraints / 约束
- missing Boundaries / 边界
- missing Iteration Policy / 迭代策略
- missing Stop When / 完成条件
- missing Pause If / 暂停条件
- missing Preferred Runtime
- placeholder labels: [Outcome], [Verification], TODO, TBD, 待定
- vague phrases: make sure it works, 随便改, edit anything, keep trying
- verification too vague
- boundaries too broad
- iteration policy unbounded
```

### Output

Pass:

```text
Goal Contract Lint: pass
```

Fail:

```text
Goal Contract Lint: fail
Findings:
- <field>: <reason>
```

---

## FR-9：扩展 `triage` Agent Brief

### Required Files

```text
Groundwork/
  skills/triage/SKILL.md
  skills/triage/AGENT-BRIEF.md
  evals/prompts/triage.csv
```

### New Agent Brief Shape

```text
Task
Current Behavior
Desired Behavior
Source / Evidence
Known Source / First Inspection Step
Key Interfaces
Acceptance Criteria
Out Of Scope
Blockers
Risk / Gate
Execution: AFK / HITL
AFK/HITL Decision Points
Stop Condition
Verification Expectations

Goal Contract
- Goal Command:
- Outcome:
- Source Truth:
- Acceptance Criteria Mapping:
- Verification:
- Constraints:
- Boundaries:
- Iteration Policy:
- Stop When:
- Pause If:
- Non-goals:
- Risk / Gate:
- Preferred Runtime:
- Result Package Expected:

Execution Profile Recommendation
- Runtime Candidate:
- Model Profile:
- Reasoning Effort:
- Cost/Latency Bias:
- Routing Reason:

Next Action
```

### Rules

```text
- ready-for-agent + AFK should include Goal Contract.
- ready-for-human must not include executable child goal.
- needs-info must not include fake executable goal.
- HITL tasks may include human-decision brief, not dispatchable child goal.
- Pause If must cover AFK/HITL Decision Points.
- Preferred Runtime is a recommendation; dispatch makes final route.
```

---

## FR-10：扩展 `to-issues` 输出

### Required Files

```text
Groundwork/
  skills/to-issues/SKILL.md
  evals/prompts/to-issues.csv
```

### New Fields Per Issue Draft

```text
Task Type Candidate:
  write_implementation / read_only_review / planning_only / hybrid / diagnosis / verification / direct

Runtime Candidate:
  codex_app_managed_worktree_thread / codex_subagent / main_thread_direct / main_thread_readonly / clean_reviewer / triage_required

Isolation Needed:
  context: none / subagent_prompt / thread / review_package
  filesystem: none / current_workspace / codex_managed_worktree / unknown
  diff surface: required / optional / not_required

Parallelization Candidate:
  eligible: yes / no / unknown
  conflict group:
  dependency group:
  merge order hint:

Goal Contract Missing Fields:
  - ...

Runtime Missing Fields:
  - ...

Verification Evidence Needed:
  - ...

Triage Recommendation Candidate:
  ready-for-agent candidate / needs-info recommendation / ready-for-human recommendation
```

### Rules

```text
- to-issues still must not final-mark ready-for-agent.
- read_only_review must not suggest codex_app_managed_worktree_thread.
- planning_only must not suggest codex_app_managed_worktree_thread.
- hybrid must suggest split_first or triage_required.
- write_implementation can suggest codex_app_managed_worktree_thread when verification and source context are clear.
- diagnosis can suggest codex_subagent if independent and read-only.
```

---

## FR-11：瘦身 `codex-managed-worktree-threads`

### Required Files

```text
codex-managed-worktree-threads/
  SKILL.md
  references/dispatch-package-contract.md
  references/thread-prompt-template.md
  references/review-package-template.md
  references/result-package-template.md
  references/rationale.md
  README.md
```

### New Scope

`codex-managed-worktree-threads` is only the adapter for:

```text
runtime_id = codex_app_managed_worktree_thread
```

It must consume only tasks with:

```text
task_type = write_implementation
readiness = ready_for_agent
runtime_id = codex_app_managed_worktree_thread
isolation.filesystem = codex_managed_worktree
goal_contract present
source_package present
validation present
expected_output = review_package
```

### Reject / No-op Conditions

It must not create thread for:

```text
runtime_id != codex_app_managed_worktree_thread
task_type = read_only_review
task_type = planning_only
task_type = hybrid
readiness != ready_for_agent
goal_contract missing
source_package missing
validation missing
expected_output != review_package
remote write requested without explicit approval
```

### Child Prompt Requirements

Child prompt must contain:

```text
You are working in a Codex App background thread with a Codex-managed worktree.
You are the child implementation thread for exactly one task.
The coordinator/main thread must remain a coordinator and must not enter Goal Mode.

Task:
- ID:
- Type:
- Runtime ID: codex_app_managed_worktree_thread
- Thread title:
- Child Goal Mode: yes

Goal Contract:
<full goal contract>

Execution Profile:
- Model profile requested:
- Reasoning effort requested:
- Cost/latency bias:
- Routing reason:
- Tool selector enforcement status:

Source Package:
...

Acceptance Criteria:
...

Non-goals:
...

Validation:
...

Rules:
- Do not use subagents for implementation.
- Do not manually create git worktrees.
- Do not stage, commit, push, open PRs, close issues, or change remote state.
- Do one focused implementation pass, then run validation.
- If validation fails due to introduced changes, make only the narrow fix and rerun relevant validation.
- Do not broaden scope.
- Return exactly the review package schema.
```

### Adapter Status Table

```text
| Task | Runtime | Thread | Goal Mode | Execution Profile | Selector Enforcement | State | Changed Files | Validation | Clean Review | Risks | Merge Order |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

---

## FR-12：Subagent Package Contract

### Phase 1 Scope

No automatic spawning by default.

Groundwork `dispatch` should output:

```yaml
subagent_package:
  runtime_id: codex_subagent
  task_id: ""
  role: product_reviewer | security_reviewer | qa_reviewer | codebase_explorer | root_cause_diagnoser | planner
  can_write_files: false
  context_package: ""
  prompt: ""
  constraints: ""
  expected_output: findings_package | diagnosis_package
  max_iterations: 1
  stop_when: ""
  pause_if: ""
  result_schema: ""
```

### Rules

```text
- Subagent package defaults to read-only.
- Subagent package must be self-contained.
- Subagent package must name expected output.
- Subagent package must include constraints.
- Subagent package must not assume filesystem isolation.
- Subagent execution requires capability detection.
- Subagent execution requires explicit user approval unless user prompt directly asked to use subagents.
- Subagent result must be converted into Result Package.
```

### Future Adapter Option

Only after repeated stable usage, consider:

```text
codex-subagents-adapter/
  SKILL.md
  references/subagent-package-contract.md
  references/findings-package-template.md
```

---

# 7. User Stories

## US-1：PRD 到 issue 到 runtime route

作为用户，我希望 Groundwork 能从 accepted PRD 拆出 issues，再根据每个 issue 的任务性质选择合适 runtime，而不是默认全部开 worktree。

## US-2：只读多视角评审走 subagent 或 clean reviewer

作为用户，我希望产品、架构、安全、QA 多视角评审不创建 worktree，而是走 subagent/read-only reviewer，并返回 structured findings。

## US-3：写实现任务走 managed worktree thread

作为用户，我希望真正需要代码修改、diff review、验证证据的任务进入 Codex App managed worktree child thread。

## US-4：hybrid 任务先诊断再写

作为用户，我希望“先调查，可能需要修”的任务先走 read-only diagnosis，再把明确的 write subtask dispatch 到 worktree。

## US-5：每个任务独立选择模型和思考强度

作为用户，我希望 dispatch 为每个 task 独立选择 model profile、reasoning effort、cost/latency bias，并记录原因。

## US-6：主线程不误入 Goal Mode

作为用户，我希望 `/goal` 只出现在被 dispatch 的 runtime package 里，主线程只做 coordinator。

## US-7：结果统一回流

作为用户，我希望 worktree review package、subagent findings、diagnosis package、clean review findings 都能用统一 Result Package 回到 Groundwork verify / triage。

---

# 8. Acceptance Criteria

## AC-1：dispatch 是 runtime router

```text
Given ready-for-agent tasks
When dispatch runs
Then it assigns runtime_id per task
And it does not assume all tasks use codex_app_managed_worktree_thread
```

## AC-2：managed worktree adapter 瘦身

```text
Given codex-managed-worktree-threads receives a dispatch package
When a task runtime_id is not codex_app_managed_worktree_thread
Then it must not create a thread
And it reports unsupported_runtime or no_worktree_needed
```

## AC-3：read-only 不创建 worktree

```text
Given task_type = read_only_review
When dispatch routes it
Then runtime_id must be codex_subagent, main_thread_readonly, or clean_reviewer
And worktree adapter package must not include it
```

## AC-4：planning-only 不创建 worktree

```text
Given task_type = planning_only
When dispatch routes it
Then runtime_id must not be codex_app_managed_worktree_thread
```

## AC-5：write implementation 默认 managed worktree

```text
Given task_type = write_implementation
And readiness = ready_for_agent
And Goal Contract/source/validation are present
When dispatch routes it
Then default runtime_id should be codex_app_managed_worktree_thread unless task is trivial or user overrides
```

## AC-6：hybrid 必须 split first

```text
Given task_type = hybrid
When dispatch routes it
Then runtime_id should be codex_subagent or main_thread_readonly for investigation
And write worktree route must wait until concrete write subtask exists
```

## AC-7：subagent route 默认只读

```text
Given runtime_id = codex_subagent
When dispatch generates package
Then can_write_files defaults false
And expected output is findings_package or diagnosis_package
```

## AC-8：subagent execution requires capability gate

```text
Given dispatch outputs subagent packages
When local runtime does not expose subagent execution tools
Then dispatch must output package only
And not claim execution happened
```

## AC-9：Goal Contract required for executable agent tasks

```text
Given task is ready_for_agent and executable
When triage or dispatch prepares it
Then Goal Contract must include /goal, verification, constraints, boundaries, iteration policy, stop_when, pause_if
```

## AC-10：no product truth invention

```text
Given business rules or acceptance are unclear
When Goal Contract is generated
Then it must not invent product truth
And task should route to needs_info or ready_for_human
```

## AC-11：parallelization preflight

```text
Given two write tasks share likely files/schema/API/migration/public contracts
When dispatch evaluates them
Then it must assign conflict group
And not parallelize them by default
```

## AC-12：execution profile per task

```text
Given multiple tasks with different risk
When dispatch generates matrix
Then each task has model_profile, reasoning_effort, cost_latency_bias, routing_reason
```

## AC-13：selector enforcement transparency

```text
Given adapter supports model/reasoning selectors
When adapter executes package
Then status reports tool_enforced

Given adapter does not support selectors
When adapter executes package
Then prompt includes profile preference
And status reports prompt_preference_not_tool_enforced
```

## AC-14：unified result package

```text
Given any runtime finishes
When result is reported
Then it must be wrapped as Result Package
And include runtime_id, status, output_type, evidence, risks, blockers, next route
```

## AC-15：end-to-end scenario

```text
Given accepted PRD with:
- one write implementation issue
- one read-only multi-perspective review
- one hybrid diagnosis/fix issue
- one high-risk migration issue
When local Codex runs to-issues -> triage -> dispatch
Then:
- write implementation routes to managed worktree
- read-only review routes to subagent or clean reviewer
- hybrid routes to diagnosis first
- migration routes to managed worktree with high reasoning and conflict preflight
```

---

# 9. Suggested Implementation Issues

## Issue 1：Add Goal Contract shared spec and linter

Files:

```text
skills/_shared/GOAL-CONTRACT.md
scripts/lint_goal_contract.py
evals/prompts/goal-contract.csv
evals/scenarios/goal-contract-from-vague-task.md
```

Acceptance:

```text
- Required fields documented.
- Linter catches placeholders, vague verification, broad boundaries, unbounded iteration.
- Chinese labels supported.
- Preferred Runtime and Result Package Expected included.
```

## Issue 2：Extend triage Agent Brief with Goal Contract and Preferred Runtime

Files:

```text
skills/triage/SKILL.md
skills/triage/AGENT-BRIEF.md
evals/prompts/triage.csv
```

Acceptance:

```text
- ready-for-agent + AFK emits Goal Contract.
- needs-info and ready-for-human do not emit executable child goals.
- Preferred Runtime is recommendation only.
- Pause If maps to HITL decision points.
```

## Issue 3：Extend to-issues with runtime candidate fields

Files:

```text
skills/to-issues/SKILL.md
evals/prompts/to-issues.csv
```

Acceptance:

```text
- Each issue has Task Type Candidate.
- Each issue has Runtime Candidate.
- Each issue has Isolation Needed.
- Each issue has Parallelization Candidate.
- to-issues still does not final-mark ready-for-agent.
```

## Issue 4：Add dispatch runtime router skill

Files:

```text
skills/dispatch/SKILL.md
skills/dispatch/RUNTIME-ADAPTERS.md
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/RESULT-PACKAGE.md
skills/dispatch/ROUTING-PROFILES.md
skills/dispatch/CONFLICT-PREFLIGHT.md
evals/prompts/dispatch.csv
evals/scenarios/groundwork-runtime-router.md
```

Acceptance:

```text
- Produces runtime_id per task.
- Supports codex_app_managed_worktree_thread, codex_subagent, main_thread_direct, main_thread_readonly, clean_reviewer.
- Produces Dispatch Package v2.
- Produces Result Package expectation.
- Does not execute runtime tools.
```

## Issue 5：Slim codex-managed-worktree-threads into managed worktree adapter

Files:

```text
codex-managed-worktree-threads/SKILL.md
codex-managed-worktree-threads/references/dispatch-package-contract.md
codex-managed-worktree-threads/references/thread-prompt-template.md
codex-managed-worktree-threads/references/review-package-template.md
codex-managed-worktree-threads/references/result-package-template.md
codex-managed-worktree-threads/references/rationale.md
codex-managed-worktree-threads/README.md
```

Acceptance:

```text
- Only accepts runtime_id = codex_app_managed_worktree_thread.
- Rejects read-only/planning/hybrid/subagent packages.
- Does not decide readiness or runtime route.
- Places /goal only inside child prompt.
- Requires review package.
- Reports selector enforcement transparently.
```

## Issue 6：Add Subagent Package contract to dispatch

Files:

```text
skills/dispatch/RUNTIME-ADAPTERS.md
skills/dispatch/DISPATCH-PACKAGE.md
skills/dispatch/RESULT-PACKAGE.md
evals/scenarios/subagent-readonly-review.md
```

Acceptance:

```text
- codex_subagent package exists.
- can_write_files defaults false.
- package is self-contained and role-specific.
- expected output is findings_package or diagnosis_package.
- no automatic spawn unless future adapter/tool support is explicit.
```

## Issue 7：End-to-end docs and eval scenario

Files:

```text
docs/runtime-dispatch-workflow.md
evals/scenarios/groundwork-to-runtime-dispatch.md
README.md
```

Acceptance:

```text
- Shows to-prd -> to-issues -> triage -> dispatch -> runtime adapter.
- Includes examples for write implementation, read-only review, hybrid diagnosis, migration.
- Shows how results return to verify / triage.
```

---

# 10. Implementation Prompt for Local Codex

```text
/goal Implement PRD v2 "Groundwork Dispatch Runtime Router 与多运行时适配层" as a staged skill/documentation refactor.

Outcome:
Groundwork gains a dispatch runtime router that can route ready tasks to codex_app_managed_worktree_thread, codex_subagent, main_thread_direct, main_thread_readonly, or clean_reviewer. Goal Contract becomes a shared execution contract. codex-managed-worktree-threads is slimmed into only the managed worktree runtime adapter.

Verification:
Inspect both repositories first. Run any existing repo checks/evals if available. Add and run a lightweight goal contract linter with at least one pass fixture and one fail fixture. If no test harness exists, run markdown/linter smoke checks and manually inspect changed files. Produce a review package mapping changes to PRD acceptance criteria.

Constraints:
Do not push, commit, open PRs, close issues, or mutate remote state. Do not invent product truth. Do not make Groundwork execute runtime tools. Do not make codex-managed-worktree-threads decide PRD acceptance, issue slicing, readiness, runtime routing, or Goal Contract generation.

Boundaries:
In Groundwork, modify only skills/docs/evals/scripts related to Goal Contract, triage Agent Brief, to-issues runtime candidate fields, and dispatch runtime router. In codex-managed-worktree-threads, modify only SKILL/templates/README/rationale/contract references needed to make it a managed worktree adapter. Do not add tracker APIs, task databases, hooks, MCP servers, or unrelated runtime code.

Iteration policy:
Implement in slices:
1. Goal Contract + linter.
2. triage Agent Brief extension.
3. to-issues candidate fields.
4. dispatch runtime router docs/contracts.
5. codex-managed-worktree-threads adapter slimming.
6. end-to-end scenario.
After each slice, run the smallest available check and inspect diffs before continuing.

Stop when:
The repositories contain a coherent to-prd -> to-issues -> triage -> dispatch -> runtime adapter flow; dispatch can route different task types to different runtimes; managed worktree adapter only accepts eligible write implementation packages; subagent route is represented as package-only unless runtime execution is explicitly available; validation evidence and changed files are reported.

Pause if:
A decision is needed about publishing a new public skill name, physically merging codex-managed-worktree-threads into Groundwork, enabling automatic subagent spawn, remote writes, tracker API integration, or changing Groundwork's task-state spine.
```

---

# 11. Final Product Decision

The corrected decision is:

```text
Groundwork dispatch is not a managed-worktree-only dispatcher.
Groundwork dispatch is the runtime router.

codex-managed-worktree-threads is not a Groundwork semantic skill.
codex-managed-worktree-threads is the first runtime adapter.

codex_subagent is a supported runtime route.
In Phase 1 it is package-only and capability-gated, not automatically spawned.

Goal Contract is shared Groundwork execution contract.
It belongs before runtime selection, not inside one adapter.
```

This gives us a cleaner and more extensible system:

```text
Task semantics stay in Groundwork.
Runtime mechanics stay in adapters.
Subagents and worktree threads can coexist.
Dispatch chooses the right isolation/runtime per task.
Results return through a unified Result Package.
```

[1]: https://openai.com/index/introducing-the-codex-app/?utm_source=chatgpt.com "Introducing the Codex app | OpenAI"
[2]: https://openai.com/products/release-notes/?utm_source=chatgpt.com "Release Notes | OpenAI | OpenAI"
[3]: https://playbooks.com/skills/obra/superpowers/dispatching-parallel-agents "dispatching-parallel-agents skill by obra/superpowers"
[4]: https://github.com/joeseesun/qiaomu-goal-meta-skill/blob/main/SKILL.md "qiaomu-goal-meta-skill/SKILL.md at main · joeseesun/qiaomu-goal-meta-skill · GitHub"
[5]: https://github.com/openai/codex/issues/23496?utm_source=chatgpt.com "Skill instructions to use subagents are ignored unless repeated in the prompt · Issue #23496 · openai/codex"
