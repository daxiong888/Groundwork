# Subagent Delegation Package

Target Reader: Codex preparing a fresh-context subagent review.
Reader Action Needed: Give the subagent enough evidence to review without relying on parent session memory.
Decision Supported: Whether delegation is bounded, evidence-backed, and safe to run.
Artifact Type: shared guardrail.
Source of Truth: Groundwork issue #12 acceptance criteria, Groundwork subagent safety preferences, PRD v0.3.3 FR-7 clean review constraints, and docs/prd-v0.5-prototype-first-skill-expansion.md runtime capability boundaries.
Scope: Fresh context packages for review dimensions such as spec compliance, contract compliance, code quality, test adequacy, runtime evidence, git boundary, and clean review fan-out.
Out of Scope: Default subagent use, nested delegation, scope expansion, or file modification without explicit permission.
Evidence Level: Groundwork issue #12 acceptance criteria, Groundwork subagent safety preferences, and PRD v0.3.3 FR-7 clean review constraints.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private payloads, logs, or production data.

Related References:

- `skills/_shared/RUNTIME-CAPABILITY.md` for runtime mismatch, selector enforcement, and capability-status boundaries.

## Required Package

When this package is prepared from the `verify` skill, it must come after the `Verification Scope` block required by `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`. The subagent package is delegated review content, not a replacement for verify's own scope and evidence boundary.

For verify responses, do not start with edit status, directory status, or the generated prompt itself. Start with `Verification Scope`, then include the package and any blocked or missing-evidence notes.

```text
Subagent Review Package
- Role / Lens:
- Objective:
- Source Artifacts:
- In Scope:
- Out of Scope:
- Evidence Bundle:
- Review Dimensions:
- Allowed Actions:
- Disallowed Actions:
- Output Format:
- Stop Condition:
```

Review dimensions may include:

- spec compliance
- contract compliance
- code quality
- test adequacy
- runtime evidence
- git boundary

Rules:

- Use a fresh context package. Do not rely on parent session history.
- When runtime tooling exposes parent-context fork controls, clean review delegation must disable full-history forks (`fork_context=false` or equivalent).
- A reviewer spawned from the parent thread's full history cannot produce Clean Review Evidence for that parent thread. Mark the evidence `unverified` or `blocked` and rerun with a self-contained fresh-context package.
- Include only the artifacts and evidence needed for the delegated review.
- State that the subagent must not spawn more agents unless the user explicitly delegates that.
- State that the subagent cannot expand scope.
- State that the subagent cannot modify files unless file mutation is explicitly delegated.
- Require findings to cite the supplied artifacts, paths, commands, or observations.
- If evidence is missing, require `unverified` or `blocked`, not invented facts.
- Do not silently substitute a subagent for a requested child thread or managed worktree runtime. If the user requested a child thread/worktree and only subagent delegation is available, include the Runtime mismatch block from `skills/_shared/RUNTIME-CAPABILITY.md` and require user approval before fallback execution.
- Do not silently substitute a child thread or managed worktree for a requested subagent. If a subagent was requested and only child-thread/worktree execution is available, include the Runtime mismatch block and require user approval before fallback execution.
- A subagent prompt preference for model, reasoning, or runtime is not `tool_enforced` selector evidence. Use `prompt_preference`, `unavailable`, or `unknown` unless a runtime/tool report proves selector enforcement.

## Clean Review Fan-out

When a subagent is used as a clean reviewer for a completed implementation result, it is a read-only reviewer by default. Use `skills/dispatch/CLEAN-REVIEW-FANOUT.md` for the routing threshold and `skills/dispatch/adapters/codex_app_managed_worktree_thread/CLEAN-REVIEW-PACKAGE-TEMPLATE.md` for the package shape.

Clean review subagent packages must state:

- the reviewer receives fresh context only;
- parent session memory and hidden context are not allowed;
- parent thread history forks are not allowed, and runtime fork controls must disable them when available;
- file edits are not allowed;
- spawning more agents or child threads is not allowed without separate explicit delegation;
- findings must cite supplied package sections, paths, commands, or observations;
- missing evidence must be `unverified` or `blocked`;
- child implementation self-review does not count as clean review.

Large, multiple, or high-risk review packages should route to `clean_reviewer` or a read-only `codex_subagent`. Low-cost coordinator intake remains allowed for small, low-risk, complete packages, but intake is not a substitute for clean review when fan-out triggers apply.
