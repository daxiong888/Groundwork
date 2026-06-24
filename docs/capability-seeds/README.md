# Capability Seeds

Target Reader: Groundwork maintainers, dispatch authors, implementers, verifiers, clean reviewers, and runtime capability policy editors.
Reader Action Needed: Record dated capability observations as evidence inputs without treating them as current runtime availability or selector enforcement.
Decision Supported: Whether a capability observation may guide a prompt preference, refresh request, runtime inspection, or documentation update.
Artifact Type: maintainer reference.
Source of Truth: `docs/prd-v0.5-prototype-first-skill-expansion.md` FR-543 and AC-D3; `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md` V050-002; `skills/_shared/RUNTIME-CAPABILITY.md`.
Scope: Dated capability seed storage, required labels, evidence boundary, refresh expectations, and setup-reference handling.
Out of Scope: Public `setup-groundwork` skill creation, official OpenAI/Codex behavior claims, runtime selector enforcement, installed-plugin cache evidence, marketplace evidence, UAT, release, or customer readiness.
Evidence Level: Source-validation policy only. Capability seed files are evidence inputs, not runtime/tool enforcement evidence.
Safe to Share / Redaction Notes: Safe to share as-is when seeds omit secrets, credentials, private URLs, cookies, personal data, raw logs, and unredacted screenshots.

Capability seeds are dated observations that can help Groundwork choose what to inspect or request next. They are not a permanent model table, setup requirement, official product claim, or proof that a selector was applied.

## Required Seed Boundary

Every capability seed should state:

- observed date
- observer/source type
- surface observed, or `unknown` when not known
- exact observed labels or facts
- screenshot or artifact status, without storing sensitive data
- not-proven boundaries
- refresh conditions
- status pair using the shared runtime language

Use this status pair for user-observed seeds unless stronger evidence exists:

```yaml
capability_status: user_supplied
selector_enforcement: unknown
evidence_layer: user_observed_model_menu_seed
runtime_evidence: not_claimed
official_current_behavior: not_claimed
```

If a seed is later used only to request a preferred model, reasoning level, or runtime in a prompt/package, the selector status may become `prompt_preference` for that request. It must not become `tool_enforced` unless a tool, runtime adapter, or API report confirms the selector was applied for the specific run.

## Setup Guidance Boundary

Setup guidance is lightweight and non-mandatory. Maintainers may use this directory to capture capability observations that affect routing or verification, but ordinary Groundwork use must not require a setup questionnaire or a public `setup-groundwork` skill.

Prefer this order:

1. Use repo-local instructions and existing canonical docs.
2. Record only the capability seed facts needed for the current decision.
3. Ask or inspect runtime capability only when model/runtime selection is material.
4. Keep official current behavior unclaimed unless current official documentation was verified and cited.
5. Keep runtime/plugin/cache/UAT/release claims unclaimed unless the corresponding evidence was gathered.

## Current Seeds

- [`codex-model-menu-2026-06-23.md`](codex-model-menu-2026-06-23.md): user-supplied Codex model menu observation. It is `user_supplied` dated evidence and does not prove current availability or selector enforcement.
