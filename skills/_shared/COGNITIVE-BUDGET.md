Target Reader: Groundwork dispatchers, implementers, verifiers, reviewers, runtime adapter authors, and maintainers selecting model/reasoning profiles.
Reader Action Needed: Route by cognitive/model profile before mapping to concrete models, and keep final-authority restrictions visible.
Decision Supported: Which model profile, reasoning preference, and cost/latency bias to request without overclaiming concrete model availability or selector enforcement.
Artifact Type: shared guardrail.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` section 10.3 and `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md` V050-001B.
Scope: Canonical model profiles, reasoning/thinking preference boundaries, Spark final authority restrictions, and concrete model mapping gates.
Out of Scope: Maintaining a permanent global model table, implementing model/router automation, proving current model availability, or replacing runtime adapter evidence.
Evidence Level: Source-validation policy only. Concrete model availability and selector enforcement require separate runtime/tool evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private payloads, logs, or production data.

# Cognitive Budget Profiles

## Core Rule

Groundwork routes by model profile before mapping to a concrete model.

Concrete model labels are runtime-specific evidence, not permanent global truth. A dated seed or docs reference may inform a preference, but the executing runtime/tool must provide evidence before a final report claims concrete model execution or selector enforcement.

## Profile Table

| Profile | Default Use | Reasoning / Thinking Preference | Cost / Latency Bias | Boundary |
| --- | --- | --- | --- | --- |
| `fast_scan` | quick classification, fixture linting, low-risk summarization, tiny docs/config inspection | low to medium | fast | Not final readiness, high-risk review, public skill approval, release/UAT authority, or customer authority. |
| `balanced_work` | normal PRD/doc work, scoped implementation with accepted AC, ordinary verification with current evidence | medium; raise only when risk justifies it | balanced | Not high-risk final authority. |
| `strong_reasoning` | ambiguous product decisions, prototype-first routing, public skill design, cross-cutting plans | high | quality | Not a substitute for role separation, clean review, or independent verification. |
| `exhaustive_review` | independent clean review, skill-audit, architecture/security/privacy/schema/data correctness review | high or xhigh when available | quality | Still needs source evidence, role separation, and verification scope; does not prove runtime readiness by itself. |
| `spark_iteration` | bounded fast coding iteration with a fast feedback loop | low or medium; high only for bounded loops when available | fastest practical loop | Spark final authority restrictions apply: not final clean reviewer, final verifier, public skill approver, release/UAT authority, or customer authority. |

## Profile-To-Model Mapping Gate

Before mapping a profile to a concrete model, record the evidence layer:

```yaml
model_profile: fast_scan | balanced_work | strong_reasoning | exhaustive_review | spark_iteration
concrete_model: ""
reasoning_or_thinking_preference: low | medium | high | xhigh | unknown
cost_latency_bias: fast | balanced | quality
capability_status: known | unknown | user_supplied | docs_reference | tool_enforced
selector_enforcement: tool_enforced | prompt_preference | unavailable | unknown
evidence_layer: prompt_preference | runtime_tool_evidence | user_observed_model_menu_seed | official_docs | community_evidence | local_characterization_eval
```

Rules:

- Prefer a profile and reasoning/thinking preference in dispatch packages.
- Map to `concrete_model` only when current runtime/tool evidence, an explicit user instruction, or a labeled seed/docs reference is relevant to the route.
- If mapping comes from a seed or docs reference, set `selector_enforcement` to `prompt_preference`, `unavailable`, or `unknown` unless runtime/tool evidence proves `tool_enforced`.
- Do not maintain or present a permanent global model table as runtime truth.
- Do not treat Codex UI thinking labels as API reasoning-effort values, or API docs as proof of Codex UI selector enforcement.

## Final Authority Restrictions

Fast profiles can accelerate iteration, but they cannot close material authority gates.

`fast_scan` and `spark_iteration` must not be used as:

- final clean reviewer;
- final verifier;
- public skill approver;
- release/UAT authority;
- customer authority.

For material changes, route final clean review to an independent reviewer with an appropriate `exhaustive_review` or stronger available reviewer profile, then route readiness claims through `verify` with independent evidence.
