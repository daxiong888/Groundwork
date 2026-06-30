Target Reader: Groundwork skill authors, routers, implementers, clean reviewers, verifiers, and maintainers deciding whether an enumerable choice needs a decision map.
Reader Action Needed: Use this reference when options are already enumerable and the user needs tradeoffs, dependencies, decision criteria, or a recommended path without turning the work into PRD shaping, implementation planning, dispatch, or verification.
Decision Supported: Whether to answer directly, route to `to-prd`, use decision mapping as a shared lens, route to `write-plan`, route to `dispatch`, or stop before downstream execution or readiness claims.
Artifact Type: shared workflow reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-541, AC-A3, AC-D1, and V050-004A in `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md`.
Scope: Decision mapping for enumerable options, tradeoffs, dependencies, decision criteria, route negatives, model/profile guidance, and evidence boundaries.
Out of Scope: Creating a public `decision-map` skill, implementing a chosen path, verifying a chosen path, replacing `to-prd`, replacing `write-plan`, replacing `dispatch`, or claiming runtime/browser/UAT/release evidence.
Evidence Level: Source-validation policy. This shared reference is local guidance only until separately reviewed and verified.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private payloads, logs, or production data.

# Shared Decision Mapping Reference

## Public Surface Boundary

`decision-map` is a conditional public candidate only after route-conflict negatives prove a distinct invocation moment against `write-plan`, `dispatch`, `to-prd`, and direct answers.

Do not create `skills/decision-map/SKILL.md` or a public `decision-map` template for this shared-reference slice. Public exposure belongs to the later V050-004B slice and requires maintainer acceptance, route-negative evidence, and independent skill-quality review.

## Core Definition

Decision mapping is the shared route lens for choosing among enumerable options.

Use decision mapping when the options can be named and the work is to compare:

- tradeoffs;
- dependencies;
- decision criteria;
- consequences;
- confidence and evidence gaps;
- a recommended path or next decision.

Decision mapping supports choosing a path. It does not implement the chosen path, verify the chosen path, approve a PRD, mark implementation readiness, perform dispatch execution, claim runtime evidence, or provide clean review.

## Trigger Conditions

Use decision mapping when all of these are true:

- The user is asking which path, option, architecture, workflow, runtime approach, or skill route to choose.
- The meaningful options are enumerable from the prompt, source truth, or a quick local inspection.
- The answer depends on comparing tradeoffs, dependencies, decision criteria, or consequences.
- The output can remain a decision aid without writing source files, creating a public skill, generating a runtime package, or claiming readiness.

Decision mapping may be conversation-only. Create a durable artifact only when the user asks for one or when artifact promotion is required by the surrounding workflow.

## Route Negatives

Do not use decision mapping when a narrower route can safely proceed:

- Direct answer: answer directly when the request is tiny, factual, repo-doc-answerable, or has an obvious low-risk answer without material tradeoffs.
- `to-prd`: use PRD shaping when the user asks to write a PRD/spec, define acceptance, clarify raw requirements, or resolve non-enumerable product ambiguity.
- Shared grilling: use `skills/_shared/GRILLING.md` when material unknowns are not yet enumerable and the next safe step is one clarification question.
- `write-plan`: use `write-plan` when the task is accepted enough and the user needs implementation steps, dependencies, stop conditions, and verification checkpoints.
- `dispatch`: use `dispatch` when accepted, ready tasks need runtime routing, model/profile recommendation, package-only handoff, execution matrix, or Result Package expectations.
- `prototype`: use `prototype` when a throwaway UI, interaction, state, visual, or business-rule artifact can answer the question faster than a comparison table.
- `implement`: use `implement` when the user asks for scoped code/file changes now and source truth is implementation-ready or explicitly bypassed.
- `verify`: use `verify` for readiness, evidence sufficiency, runtime/browser/UAT/release claims, or acceptance verification.

## Output Guidance

A decision map should be compact and reviewable:

- Decision question.
- Options considered.
- Criteria and weights only when weights are known or explicitly assumed.
- Tradeoffs by option.
- Dependencies and blockers.
- Evidence gaps.
- Recommended path.
- Next route: direct answer, `to-prd`, `write-plan`, `dispatch`, `prototype`, `implement`, `verify`, `handoff`, or blocked.
- Evidence boundary: decision aid only, not implementation, verification, clean review, runtime evidence, browser evidence, UAT evidence, release evidence, or customer readiness.

## Runtime And Model Boundary

When decision mapping compares model, runtime, child-thread, worktree, subagent, or selector choices, use `skills/_shared/RUNTIME-CAPABILITY.md` and `skills/_shared/COGNITIVE-BUDGET.md`.

Decision maps may recommend a model profile or runtime preference, but selector enforcement remains `prompt_preference`, `unavailable`, or `unknown` unless tool/runtime evidence proves `tool_enforced` for the specific run.

Use these labels when runtime/model choice is material:

The inline `evidence_layer` values below mirror the canonical runtime evidence layer enum in `skills/_shared/RUNTIME-CAPABILITY.md` and must be updated together.

```yaml
model_profile: fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration
capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
evidence_layer: prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval
runtime_evidence: not_claimed
```

Do not claim selector enforcement, runtime execution, installed-plugin behavior, cache refresh, marketplace behavior, UAT readiness, release readiness, or customer readiness from a decision map.
