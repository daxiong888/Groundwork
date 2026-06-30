Target Reader: Groundwork dispatchers, implementers, verifiers, subagent package authors, runtime adapter authors, and clean reviewers.
Reader Action Needed: Separate runtime capability seeds, routing preferences, concrete runtime evidence, selector enforcement evidence, and runtime mismatch handling before making runtime or model claims.
Decision Supported: Whether Groundwork may recommend, request, claim, block, or ask approval for model/runtime selection and selector enforcement.
Artifact Type: shared guardrail.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-520 through FR-524, FR-543, AC-C5 through AC-C7, AC-D2, AC-D3, and `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md` V050-001B and V050-002.
Scope: Lazy runtime capability discovery, selector-enforcement statuses, evidence layers, runtime mismatch reporting, capability seed handling, and runtime/cache claim boundaries.
Out of Scope: Implementing router automation, creating child threads or subagents, maintaining a permanent global model table, proving installed-plugin runtime behavior, or replacing runtime adapter contracts.
Evidence Level: Source-validation policy only. This file does not prove installed plugin, marketplace, runtime, model, selector, cache refresh, UAT, release, browser, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private payloads, logs, or production data.

# Runtime Capability Boundary

## Core Rule

Groundwork must not assume that a model, reasoning effort, subagent runtime, child-thread runtime, worktree runtime, or selector enforcement mechanism is available merely because a prompt requests it.

Prompt preferences are useful routing intent. They are not runtime/tool evidence.

```text
prompt_preference != tool_enforced
capability seed != runtime availability
official docs != user-specific selector enforcement
community evidence != acceptance gate
runtime routing recommendation != runtime execution evidence
```

## Lazy Capability Discovery

Only inspect or ask for detailed runtime capability fields when model/runtime selection is material:

- the user requests a concrete runtime, model, reasoning effort, subagent, child thread, or worktree;
- dispatch recommends a runtime or model profile;
- a result/final report would claim model/runtime execution or selector enforcement;
- unavailable runtime support would change the route, stop condition, or approval gate;
- runtime/cache evidence is used for release, UAT, marketplace, or installed-plugin claims.

When material, include the minimal status pair:

```yaml
capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
```

Status rules:

- `known`: local source, package, or runtime contract evidence establishes the capability boundary, but not necessarily selector enforcement.
- `unknown`: the capability was not inspected, was unavailable to inspect, or the current runtime did not report it.
- `user_supplied`: a user-observed seed, menu label, screenshot summary, or stated environment fact. This can guide a question or preference but cannot prove runtime/tool enforcement.
- `docs_reference`: official documentation was consulted and cited as dated product guidance. It cannot prove this user's current runtime availability or selector enforcement.
- `tool_enforced`: a tool, runtime adapter, or API call reports that the relevant runtime or selector was actually applied for the specific run.

Selector enforcement rules:

- `tool_enforced`: only when a tool/runtime adapter confirms the selector was applied by tool, API, or runtime mechanism for the specific run.
- `prompt_preference`: the desired model/profile/reasoning/runtime was included in a prompt or package, but enforcement was not proven.
- `unavailable`: the runtime is known not to expose or accept that selector.
- `unknown`: support was not inspected or reported.

Do not claim `tool_enforced` from prompt text, Goal Contract text, Dispatch Package contents, a model menu seed, or a routing profile alone.

## Evidence Layers

Keep these layers separate in packages and final reports:

| Evidence Layer | May Support | Must Not Support |
| --- | --- | --- |
| Prompt preference | Desired model profile, runtime, reasoning, or cost/latency bias | Actual execution, availability, or selector enforcement |
| Runtime/tool evidence | Specific runtime availability, execution, or selector application reported by the tool/adapter | Product truth outside the reported runtime/run |
| User-observed model menu seed | Dated visible labels for one observed surface | Universal availability, API support, per-subagent support, per-worktree support, runtime execution, or selector enforcement |
| Official docs | Dated product guidance when cited and current enough for the claim | User-specific availability, installed plugin behavior, or selector enforcement |
| Community evidence | Supporting signal or research context | Mandatory acceptance gate, representative consensus, or runtime/tool enforcement |
| Local characterization eval | Groundwork-specific fit for a profile or workflow | Universal benchmark, release readiness, or customer/UAT readiness |

### Canonical Runtime Evidence Layer Enum

Use these machine values when an `evidence_layer` enum is required:

```text
prompt_preference
runtime_tool_evidence
user_observed_model_menu_seed
official_docs
community_evidence
local_characterization_eval
```

Mirrored inline template locations must match this enum:

- `skills/_shared/COGNITIVE-BUDGET.md`
- `skills/_shared/DECISION-MAPPING.md`
- `skills/dispatch/SKILL.md`

Capability seed facts must be labeled as seed facts and kept separate from runtime/tool enforcement evidence.

## Capability Seed Handling

Capability seeds are dated evidence inputs, not setup requirements or runtime truth. Store reusable seed notes under [`docs/capability-seeds/`](../../docs/capability-seeds/) with the audience-first header fields and an explicit status pair.

For a user-observed model menu seed, use:

```yaml
capability_status: user_supplied
selector_enforcement: unknown
evidence_layer: user_observed_model_menu_seed
runtime_evidence: not_claimed
official_current_behavior: not_claimed
```

If a seed is used in a Dispatch Package, Goal Contract, or prompt as a desired selector, the selector status may be `prompt_preference` for that request. Keep `selector_enforcement` as `unknown` for the seed itself, and do not upgrade it to `tool_enforced` unless the executing tool/runtime reports enforcement for that specific run.

The 2026-06-23 Codex model menu seed is recorded at [`docs/capability-seeds/codex-model-menu-2026-06-23.md`](../../docs/capability-seeds/codex-model-menu-2026-06-23.md). It documents a user-supplied observation only. It does not prove current official OpenAI/Codex behavior, every Codex surface, API availability, subagent/worktree availability, runtime execution, installed-plugin behavior, or selector enforcement.

## Runtime Mismatch Handling

Groundwork must not silently substitute subagents and child-thread/worktree runtimes in either direction.

Use this block when the requested runtime and available/proposed runtime might differ:

```text
Requested runtime:
Available runtime:
Runtime mismatch: yes | no | unknown
Fallback proposed:
User approval required: yes | no
```

Rules:

- If the user explicitly asks for a child thread, managed worktree thread, or worktree-isolated runtime, a subagent is a mismatch unless the user approves fallback.
- If the user explicitly asks for a subagent, a managed worktree child thread is a mismatch unless the user approves fallback.
- If runtime availability is `unknown`, report `Runtime mismatch: unknown` and ask, inspect, or block according to task risk instead of silently substituting.
- A package may propose fallback, but execution requires approval when the requested runtime is explicit and the fallback changes isolation, file-write capability, context isolation, or review authority.

## Runtime And Cache Claim Boundary

Source edits, documentation checks, CSV parse checks, local fixture inspection, and prompt/package generation are source-validation evidence only.

Runtime/cache claims must either name all of these or explicitly state that runtime evidence was not refreshed and is not claimed:

- installed plugin root;
- local source root;
- cache/source refresh method or source-equivalence evidence;
- run scope, such as targeted or full;
- commands or runtime trials used;
- limitations.

Do not claim installed-plugin runtime behavior, marketplace behavior, selector enforcement, UAT readiness, release readiness, browser evidence, customer readiness, or cache refresh from local source diff alone.

## Final Report Language

Use direct evidence labels:

```text
Runtime Evidence: not claimed; local source-validation checks only.
Selector Enforcement: prompt_preference | unavailable | unknown unless tool/runtime evidence proves tool_enforced.
Cache/Source Evidence: not refreshed unless installed plugin root, source root, and refresh/equivalence evidence are named.
```

When runtime support is unknown, prefer `unavailable/unknown` language over a silent fallback or concrete model claim.
