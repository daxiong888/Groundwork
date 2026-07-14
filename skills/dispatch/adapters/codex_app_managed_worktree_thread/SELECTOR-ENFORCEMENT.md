# Managed Worktree Selector Evidence

Target Reader: Dispatch users, managed-worktree runtime adapters, and reviewers interpreting execution-profile evidence.
Reader Action Needed: Keep the request-side selector policy separate from the selector status returned by the adapter.
Decision Supported: Whether a managed-worktree result has enough adapter evidence to report selector application.
Artifact Type: runtime adapter delta.
Source of Truth: `skills/_shared/RUNTIME-CAPABILITY.md` and the managed-worktree Result Package template.
Scope: Managed-worktree selector request and returned-evidence mapping.
Out of Scope: Choosing concrete models, changing runtime capabilities, or defining the global selector status enum.
Evidence Level: Source-validation adapter contract only; actual enforcement requires run-specific adapter/tool evidence.
Safe to Share / Redaction Notes: Safe to share as-is; returned adapter evidence must not expose private runtime payloads.

`skills/_shared/RUNTIME-CAPABILITY.md` owns the `selector_enforcement` values and proof rules. This adapter does not redefine them.

- Dispatch may request `model_profile`, `reasoning_effort`, and `cost_latency_bias` with `selector_policy`.
- A child prompt or package proves only the request. It never proves selector application.
- The Result Package records `selector_enforcement` plus `selector_enforcement_evidence` returned by the adapter.
- Without adapter/tool confirmation, use the canonical non-enforced or unknown status; do not infer `tool_enforced`.
- Missing selector support blocks execution only when the user or package explicitly requires enforceable selectors.
