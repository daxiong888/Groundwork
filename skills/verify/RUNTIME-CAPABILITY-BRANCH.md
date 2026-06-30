# Runtime Capability Branch

Target Reader: Codex running `verify` for model/runtime selection, selector enforcement, runtime mismatch, subagent/child-thread/worktree routing, or runtime/tool capability claims.
Reader Action Needed: Preserve runtime capability status, selector evidence, mismatch handling, and cache/source boundaries after the required scope block.
Decision Supported: Whether a runtime/model claim is tool-enforced, prompt preference only, unavailable, unknown, or unsupported by current evidence.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/_shared/RUNTIME-CAPABILITY.md`, `skills/_shared/COGNITIVE-BUDGET.md`, and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`.
Scope: Runtime capability status, selector enforcement, evidence layer, requested/available runtime mismatch, fallback approval, and runtime/cache evidence boundaries.
Out of Scope: Selecting or executing a runtime, spawning subagents, creating child threads, refreshing plugin cache, publishing releases, or proving UAT/customer readiness.
Evidence Level: Source-validation policy only unless a tool/runtime adapter reports execution or selector evidence for the specific run.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required References

- Load `SCOPE-EVIDENCE-TEMPLATE.md` first.
- Apply `EB-RUNTIME-001` and `EB-CACHE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` before verifying runtime execution, selector enforcement, installed-plugin, marketplace, cache, or cache-refresh claims.
- Apply `skills/_shared/NON-EXECUTOR-BOUNDARY.md` before treating dispatch packages, prompt text, source diffs, or old baselines as execution evidence.
- Load `skills/_shared/RUNTIME-CAPABILITY.md` for status enums, selector rules, evidence layers, mismatch handling, and cache/source boundaries.
- Load `skills/_shared/COGNITIVE-BUDGET.md` when the claim depends on model profile, reasoning effort, cost/latency bias, or Spark/fast-profile authority.
- Load `RELEASE-READINESS-BRANCH.md` when runtime/cache evidence is used to support release, UAT, customer, marketplace, installed-plugin, or cache-refresh claims.

## Runtime Capability Payload

Use this payload after `Verification Scope` when runtime/model selection or selector enforcement is material:

```text
Runtime Capability
- capability_status:
- selector_enforcement:
- Evidence layer:
- Requested runtime:
- Available runtime:
- Runtime mismatch:
- Fallback proposed:
- User approval required:
```

Rules:

- `tool_enforced` requires tool, runtime adapter, or API evidence for the specific run.
- Prompt text, Goal Contract text, Dispatch Package text, model menu seeds, routing profiles, or source diff alone can support only prompt preference or unknown/unverified status.
- If requested and available/proposed runtimes differ, report `Runtime mismatch: yes | unknown` and require approval when isolation, file-write capability, context isolation, or review authority changes.
- If runtime support was not inspected, use `capability_status: unknown` and `selector_enforcement: unknown` or `prompt_preference`; do not silently substitute a runtime.
- Runtime/cache claims must name installed plugin root, source root, cache/source refresh or equivalence evidence, run scope, commands/trials, and limitations, or state that runtime/cache evidence is not claimed.
