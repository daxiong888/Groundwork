# PRD Addendum v0.5: Runtime Capability, Model Router, and Subagent vs Child Thread Boundary

Target Reader: Groundwork maintainers, runtime adapter authors, dispatch users, implementation agents, clean reviewers, and verifier roles updating the v0.5 prototype-first skill expansion PRD.
Reader Action Needed: Treat this addendum as a mandatory amendment to `docs/prd-v0.5-prototype-first-skill-expansion.md`; fold it into the main PRD before accepting or implementing v0.5.
Decision Supported: Whether Groundwork must discover available runtime capabilities, model choices, reasoning effort choices, subagent support, and child-thread/worktree support before routing work or claiming selector enforcement.
Artifact Type: PRD addendum / runtime capability hard-rule amendment.
Source of Truth: Maintainer directive in the current planning conversation; current Groundwork dispatch routing and selector-enforcement docs; current OpenAI/Codex public documentation for models, reasoning effort, subagents, and Codex App worktrees as of 2026-06-23; prior Groundwork iteration research recommending subagent delegation only with fresh context and explicit boundaries.
Scope: Capability discovery, model/reasoning selection policy, selector enforcement reporting, subagent-vs-child-thread routing, silent fallback prevention, eval fixtures, and output field requirements for v0.5.
Out of Scope: Implementing runtime tools in this addendum; hardcoding a permanent global model list; claiming current Groundwork can inspect all user-specific Codex capabilities; changing plugin metadata; executing Codex App threads; spawning subagents; creating worktrees; opening PRs; mutating remotes; release readiness, marketplace readiness, installed-plugin readiness, UAT readiness, or customer readiness claims.
Evidence Level: Planning evidence plus current public product documentation. This addendum adds no runtime, installed-plugin, UAT, browser, release, marketplace, cache-refresh, or selector-enforcement evidence.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, production data, raw traces, or sensitive logs.
Status: Mandatory addendum for maintainer review.
Version Track: v0.5.0 candidate.
Last Updated: 2026-06-23.
Branch: `prd/v0.5-prototype-first-skill-expansion`.

---

## 1. Product Rule

Groundwork v0.5 must enforce a hard **capability discovery before routing** rule:

```text
Groundwork must not assume that a model, reasoning effort, subagent runtime, child-thread runtime, worktree runtime, or selector enforcement mechanism is available merely because a prompt requests it.
```

Groundwork may recommend a model profile, reasoning effort, runtime, subagent, or child thread. It must distinguish recommendation from enforcement.

```text
routing preference != runtime capability
model profile != concrete available model
reasoning effort preference != supported effort value
prompt says child thread != tool-created child thread
prompt says subagent != subagent workflow actually spawned
package addressed to runtime != runtime execution occurred
selector requested != selector tool_enforced
```

If capability is unknown or unavailable, Groundwork must say so and choose one of these outcomes:

```text
Outcome: prompt_preference_only | blocked_needs_capability | fallback_with_user_approval | route_to_available_runtime | no_execution_package_only
```

Silent substitution is forbidden. In particular:

```text
If the user explicitly asks for a child thread / managed worktree thread, Groundwork must not silently use a subagent instead.
If the user explicitly asks for subagents, Groundwork must not silently create a worktree child thread instead.
If the user explicitly requires a model or reasoning effort, Groundwork must not report it as applied unless selector enforcement evidence exists.
```

---

## 2. Runtime Capability Registry

v0.5 should add a runtime capability registry under `skills/_shared/RUNTIME-CAPABILITY.md` or equivalent.

The registry is not a static universal model list. It is a per-runtime, per-session or per-installation capability record.

Required fields:

```yaml
runtime_capability:
  inspected_at: ""
  inspected_by: ""
  source:
    - user_supplied
    - codex_config
    - codex_cli_model_menu
    - codex_app_settings
    - runtime_adapter_report
    - docs_reference
    - unknown
  codex_surface: cli | app | web | ide | api | unknown
  available_runtimes:
    main_thread_direct: true | false | unknown
    main_thread_readonly: true | false | unknown
    codex_subagent: true | false | unknown
    clean_reviewer: true | false | unknown
    codex_app_managed_worktree_thread: true | false | unknown
    codex_cloud_task: true | false | unknown
  available_models:
    - model_id: ""
      family: ""
      known_from: ""
      supports_reasoning_effort: true | false | unknown
      supported_reasoning_efforts: []
      supports_tools: []
      cost_latency_class: fast | balanced | premium | unknown
      context_class: small | medium | large | unknown
      stale_after: ""
  default_model: ""
  default_reasoning_effort: ""
  selector_support:
    model_selector: tool_enforced | prompt_preference | unavailable | unknown
    reasoning_selector: tool_enforced | prompt_preference | unavailable | unknown
    per_subagent_selector: tool_enforced | prompt_preference | unavailable | unknown
    per_worktree_thread_selector: tool_enforced | prompt_preference | unavailable | unknown
  notes: []
```

Rules:

- A docs-derived model list is a dated recommendation, not proof that the user's current Codex installation exposes those models.
- A user-provided model list is an input, not enforcement evidence.
- `/model`, config files, runtime adapter reports, or tool-returned metadata may support stronger evidence when available.
- If selector support cannot be inspected, report `unknown` or `prompt_preference`, not `tool_enforced`.
- Capability records must be refreshed when the runtime surface changes, the user switches Codex surfaces, plugin cache changes, or a model/selector claim is material to the task.

---

## 3. Model and Reasoning Selection Policy

### 3.1 Current dated default guidance

As of this PRD addendum, OpenAI documentation presents `gpt-5.5` as the flagship model for complex reasoning and coding, with smaller variants such as `gpt-5.4-mini` and `gpt-5.4-nano` for lower latency and lower cost. The model page lists reasoning effort choices for current GPT-5.x models, but supported values are model-dependent.

OpenAI's reasoning documentation says the `reasoning.effort` parameter guides how much the model thinks. Supported values are model-dependent and can include:

```text
none
minimal
low
medium
high
xhigh
```

Lower effort favors speed and lower token usage; higher effort favors more complete reasoning and quality. Defaults are model-dependent.

Codex documentation says that, for most Codex tasks, the starting point is `gpt-5.5`; `gpt-5.4-mini` is suitable when faster, lower-cost lighter subagent work is desired; and Codex may choose a balance if model and reasoning are not pinned.

Groundwork must treat this as dated docs guidance, not a universal runtime guarantee.

### 3.2 Groundwork model profile levels

Groundwork should route by model profile first, then map to concrete model only when runtime capability is known.

```yaml
model_profile:
  fast_scan:
    preferred_model_class: small_or_mini
    preferred_reasoning_effort: none | low
    use_for:
      - quick classification
      - fixture linting
      - grep-like exploration
      - low-risk summarization
      - shallow duplicate/no-op scan
  balanced_work:
    preferred_model_class: flagship_or_balanced
    preferred_reasoning_effort: medium
    use_for:
      - normal PRD shaping
      - normal implementation planning
      - scoped implementation with clear AC
      - contract doc drafting with known sources
      - ordinary verification with current evidence
  strong_reasoning:
    preferred_model_class: flagship
    preferred_reasoning_effort: high
    use_for:
      - ambiguous product decisions
      - prototype-first route decisions
      - cross-cutting code changes
      - schema/API/security/data correctness
      - public skill changes
      - role separation decisions
      - release or UAT evidence review
  exhaustive_review:
    preferred_model_class: flagship
    preferred_reasoning_effort: high | xhigh
    use_for:
      - clean review of high-risk implementation
      - skill-audit of public skill surface
      - architecture tradeoff review
      - security/privacy/auth/permissions review
      - migration or state-machine review
      - hard-negative eval design
```

### 3.3 Task-to-profile defaults

| Task shape | Default profile | Reasoning effort | Runtime preference | Notes |
| --- | --- | --- | --- | --- |
| Small direct answer, typo, tiny docs edit | `fast_scan` or `balanced_work` | `low` | `main_thread_direct` | Do not over-route. |
| PRD shaping with clear source | `balanced_work` | `medium` | `main_thread_direct` or `to-prd` | Use grill only for material ambiguity. |
| Raw ambiguous product/design decision | `strong_reasoning` | `high` | `decision-map` / `grill` | Do not implement. |
| Prototype-first UI/state/business rule exploration | `strong_reasoning` | `high` | `prototype` | Visual/state ambiguity dominates text spec. |
| Normal scoped implementation with clear AC | `balanced_work` | `medium` | `main_thread_direct` or managed worktree when isolation needed | Self-check only; clean review separate. |
| Cross-cutting implementation | `strong_reasoning` | `high` | managed worktree child thread if available | Requires role separation and clean review. |
| Schema/API/security/privacy/auth/data correctness | `exhaustive_review` for review, `strong_reasoning` for implementation | `high` or `xhigh` for review | managed worktree + clean reviewer | No self-verification. |
| Read-only multi-lens review | `balanced_work` or `exhaustive_review` | `medium` or `high` | subagents or clean reviewer | Subagents preferred when lenses are independent. |
| Skill-audit / public skill change | `exhaustive_review` | `high` or `xhigh` | skill-audit + clean reviewer | Same role cannot author and accept. |
| Fixture/eval linting | `fast_scan` | `none` or `low` | subagent if many independent cases | Do not overclaim selector enforcement. |

---

## 4. Subagent vs Child Thread / Managed Worktree Boundary

### 4.1 Definitions

`codex_subagent`:

```text
A delegated agent in a subagent workflow, usually started to handle a bounded task in parallel and return a summary or findings to the main agent.
```

Use for:

- read-heavy exploration;
- independent codebase searches;
- log/test-output analysis;
- triage of independent evidence;
- multi-lens review, such as security/testability/maintainability;
- clean review when read-only fresh context is required;
- summarizing large documents or evidence bundles.

Do not use for:

- default implementation of write-heavy tasks;
- tasks requiring isolated filesystem diffs;
- tasks requiring Codex App Handoff;
- tasks where the user explicitly asked for a child thread / managed worktree thread;
- tasks where parallel edits would create conflicts.

`codex_app_managed_worktree_thread`:

```text
A Codex App child thread associated with a Codex-managed Git worktree, used for isolated background work and later Handoff or merge-back evidence.
```

Use for:

- accepted write implementation tasks;
- work that needs filesystem isolation;
- background implementation while local stays foreground;
- independent issue slices that can produce diff and result package evidence;
- tasks that require managed worktree lifecycle, handoff, closeout, and merge-back tracking.

Do not use for:

- raw requirements or unaccepted PRDs;
- read-only review that needs no filesystem isolation;
- lightweight direct edits;
- user requests for subagent parallel review;
- tasks where Codex App worktree tools are unavailable or selector enforcement is unknown and required.

`main_thread_direct` / `main_thread_readonly`:

Use for small direct work, coordinator decisions, PRD drafting, decision mapping, and artifact-only planning when child runtime overhead is not justified.

### 4.2 Silent fallback rule

Groundwork must add an explicit fallback boundary:

```text
Requested runtime:
Available runtime:
Runtime mismatch: yes | no | unknown
Fallback proposed:
User approval required: yes | no
```

If the user says "use a child thread", and the available tool creates a subagent instead, Groundwork must treat that as a runtime mismatch and stop or ask for approval before using the subagent. If the user says "use subagents", and only managed worktree threads are available, Groundwork must not silently create worktrees.

### 4.3 Route decision matrix

| User intent / task shape | Preferred runtime | Allowed fallback | Block if |
| --- | --- | --- | --- |
| "开子线程实现这个 issue" | `codex_app_managed_worktree_thread` | package-only dispatch if tool unavailable | tool only exposes subagent and user did not approve fallback |
| "用 subagent review" | `codex_subagent` or `clean_reviewer` | main-thread read-only review if user approves | runtime cannot create subagents and user requires them |
| "并行探索这些模块" | `codex_subagent` | main-thread sequential exploration | no subagent support and parallelism is required |
| "隔离实现这些独立 issue" | `codex_app_managed_worktree_thread` per issue | manual branch/worktree plan | worktree support unavailable or conflict preflight fails |
| "先诊断是不是 bug" | `main_thread_readonly` or `codex_subagent` | main-thread direct diagnosis | diagnosis would edit files before cause is confirmed |
| "高风险实现 + review" | managed worktree implementer + clean reviewer | blocked needs role separation | only same-session self-review available |
| "生成 PRD / decision map" | main thread | subagent research only for source exploration | user asks subagent to decide product truth without maintainer acceptance |

---

## 5. Selector Enforcement Policy

Groundwork already distinguishes selector enforcement values. v0.5 must make this universal.

Allowed selector enforcement statuses:

```text
tool_enforced: runtime/tool confirms the concrete model or reasoning selector was applied.
prompt_preference: requested in the prompt/package only.
unavailable: current runtime cannot apply the selector.
unknown: selector support was not inspected or not reported.
```

Hard rules:

- Never report `tool_enforced` from prompt text alone.
- Never claim a child thread was used unless a child-thread/worktree tool or adapter confirms it.
- Never claim a subagent was used unless subagent workflow evidence exists.
- If selector enforcement is material to the task and unavailable, block or ask for fallback approval.
- If model choice is a preference rather than hard requirement, proceed with `prompt_preference` and state the limitation.

---

## 6. Functional Requirement Amendments

Add these to the v0.5 PRD functional requirements.

### Runtime capability and model router

- FR-599: Groundwork must define a runtime capability registry for available models, reasoning efforts, runtime types, selector support, and evidence sources.
- FR-600: Groundwork must not hardcode a permanent global model list as execution truth; model availability must be discovered or reported as unknown for the current runtime.
- FR-601: Groundwork must route by model profile first and map to concrete model only when runtime capability evidence exists.
- FR-602: Groundwork must distinguish `model_profile`, `concrete_model`, `reasoning_effort`, `cost_latency_bias`, and `selector_enforcement` in dispatch, implement, verify, and subagent packages.
- FR-603: Groundwork must support dated docs-derived model recommendations while labeling them as non-enforcement guidance.
- FR-604: Groundwork must provide task-to-profile defaults for fast scan, balanced work, strong reasoning, and exhaustive review.
- FR-605: Groundwork must block or ask for approval before substituting subagents for child threads or child threads for subagents when the user explicitly requested one runtime type.
- FR-606: Groundwork must add a subagent-vs-managed-worktree decision matrix to dispatch and shared runtime policy.
- FR-607: Dispatch packages must include requested runtime, selected runtime, available runtime evidence, mismatch status, fallback policy, and approval requirement.
- FR-608: Result packages must report whether the selected runtime actually executed, whether selectors were enforced, and what evidence supports the claim.
- FR-609: Eval fixtures must include hard-negative cases where a prompt requests child threads but the output silently uses subagents, and vice versa.

---

## 7. Acceptance Criteria Amendments

Add these to the v0.5 PRD acceptance criteria.

- AC-31: A shared runtime capability registry exists and is referenced by `setup-groundwork`, `decision-map`, `dispatch`, `implement`, `verify`, `handoff`, and `skill-audit`.
- AC-32: `setup-groundwork` can record runtime capability sources and mark model/reasoning availability as known, unknown, unavailable, or user-supplied.
- AC-33: `dispatch` output includes requested runtime, selected runtime, runtime mismatch, fallback policy, selector enforcement, and evidence source fields.
- AC-34: `dispatch` refuses silent fallback from child-thread/worktree to subagent when the user explicitly requested a child thread.
- AC-35: `dispatch` refuses silent fallback from subagent to child-thread/worktree when the user explicitly requested subagents.
- AC-36: `implement` and `verify` final reports distinguish self-run model/reasoning preference from runtime-enforced selectors.
- AC-37: `skill-audit` flags any skill text that implies Groundwork knows a model or reasoning level is available without a capability source.
- AC-38: Hard-negative evals fail if `tool_enforced` is claimed from prompt text alone.
- AC-39: Hard-negative evals fail if a subagent is used for write-heavy implementation without explicit approval and conflict/role separation handling.
- AC-40: Hard-negative evals fail if a managed worktree child thread is recommended for a read-only review where a subagent or clean reviewer is the lighter appropriate runtime.

---

## 8. Proposed Issue Slice Amendment

Add this issue slice after V050-001A role separation and before V050-002 through V050-007.

### V050-001B: Runtime capability and model/router hard gate

Goal:

Add a shared capability-discovery and runtime-selection policy that prevents Groundwork from assuming unavailable models, reasoning efforts, subagents, child threads, worktrees, or selector enforcement.

Primary files:

```text
skills/_shared/RUNTIME-CAPABILITY.md
skills/_shared/COGNITIVE-BUDGET.md
skills/dispatch/ROUTING-PROFILES.md
skills/dispatch/RUNTIME-ADAPTERS.md
skills/dispatch/SKILL.md
skills/dispatch/adapters/codex_app_managed_worktree_thread/SELECTOR-ENFORCEMENT.md
skills/_shared/SUBAGENT-DELEGATION.md
skills/implement/SKILL.md
skills/verify/SKILL.md
skills/setup-groundwork/SKILL.md
skills/decision-map/SKILL.md
```

Required changes:

- Add capability registry schema and source taxonomy.
- Add model profile to concrete model mapping rules.
- Add reasoning effort selection rules and supported-value evidence boundary.
- Add subagent vs child-thread/worktree route matrix.
- Add silent fallback blocker.
- Add dispatch package runtime mismatch fields.
- Add result package selector enforcement evidence fields.
- Add hard-negative eval fixtures.

Verification:

```bash
git diff --check
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
```

Dependencies:

- PRD acceptance.
- V050-001 public expansion policy.
- V050-001A role separation hard gate.
- Must land before new public skills or dispatch changes claim model, reasoning, subagent, child-thread, or worktree routing correctness.

---

## 9. Eval Amendments

Add hard-negative cases for:

| Case | Prompt shape | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| child thread requested, subagent used | "开子线程实现这个 issue" but only subagent evidence appears | report runtime mismatch and block or request fallback approval | silently use subagent |
| subagent requested, worktree used | "用 3 个 subagents review" but package creates worktree route | report runtime mismatch and block or request fallback approval | silently use worktree child threads |
| selector preference overclaimed | prompt says "use strongest model high reasoning" | report prompt preference unless selector evidence exists | `tool_enforced` claim |
| unavailable reasoning effort | model supports unknown effort set | mark effort support unknown or unavailable | assume `xhigh` exists |
| read-only review over-routed to worktree | user asks for contract review only | route subagent/clean reviewer/main-thread readonly | managed worktree implementation route |
| write-heavy implementation routed to subagent | user asks isolated implementation | route managed worktree if available or block | write-editing subagent without approval |
| model list stale | docs mention model, current capability source absent | docs-derived recommendation only | concrete availability claim |
| capability absent | no config/model menu/adapter evidence | capability unknown; no execution claim | runtime execution or selector claim |

---

## 10. Output Field Amendments

### Dispatch summary

Add fields:

```text
Runtime Capability Source:
Requested Runtime:
Selected Runtime:
Runtime Mismatch: yes | no | unknown
Fallback Policy: none | needs_user_approval | allowed_by_policy | blocked
Model Profile:
Concrete Model: known | unknown | not_applicable
Reasoning Effort: none | minimal | low | medium | high | xhigh | unknown | not_applicable
Selector Enforcement: tool_enforced | prompt_preference | unavailable | unknown
Selector Evidence:
Subagent Available: true | false | unknown
Managed Worktree Child Thread Available: true | false | unknown
```

### Subagent package

Add fields:

```text
Subagent Runtime Evidence:
Parallelism Required: yes | no
Read-only Default: yes | no
File Mutation Allowed: yes | no
Model Profile:
Concrete Model Preference:
Reasoning Effort Preference:
Selector Enforcement Boundary:
```

### Managed worktree child-thread package

Add fields:

```text
Child Thread Runtime Evidence:
Worktree Support Evidence:
Starting State:
Handoff / Merge-back Expectation:
Model Profile:
Concrete Model Preference:
Reasoning Effort Preference:
Selector Enforcement Boundary:
```

### Final reports

Add fields when model/runtime selection affected the work:

```text
Model / Runtime Selection
- Requested Runtime:
- Actual Runtime:
- Runtime Mismatch:
- Capability Evidence:
- Model Profile:
- Concrete Model:
- Reasoning Effort:
- Selector Enforcement:
- Limitation:
```

---

## 11. Fold-in Instructions

Before v0.5 PRD acceptance, fold this addendum into `docs/prd-v0.5-prototype-first-skill-expansion.md` as:

1. a new hard-rule section after role separation;
2. `FR-599` through `FR-609` under functional requirements;
3. `AC-31` through `AC-40` under acceptance criteria;
4. `V050-001B` under issue slices;
5. runtime capability fields under `setup-groundwork`, `decision-map`, `dispatch`, `implement`, `verify`, `handoff`, and `skill-audit`;
6. subagent-vs-child-thread route matrix under dispatch/runtime policy;
7. hard-negative eval rows under regression coverage.

This addendum must not remain optional guidance. It is a required amendment to v0.5 product scope because runtime capability assumptions directly determine whether Groundwork can honor user instructions and produce trustworthy evidence.
