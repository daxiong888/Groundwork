# Managed Worktree Selector Enforcement

## Target Reader

Dispatch users, runtime adapters, and reviewers interpreting model profile or reasoning effort fields.

## Reader Action Needed

Report selector enforcement as evidence from the adapter, not as an assumption from the dispatch package.

## Decision Supported

Whether a result may report `tool_enforced`, must fall back to `prompt_preference`, or should use `unavailable` or `unknown`.

## Scope

Selector enforcement reporting for model profile, reasoning effort, and cost/latency bias fields in managed worktree adapter results.

## Out of Scope

Choosing the model, changing runtime capabilities, treating selector preferences as proof, and blocking execution unless enforceable selectors were explicitly required.

## Evidence Level

Derived from Groundwork execution profile rules and managed worktree adapter result requirements.

## Allowed Values

- `tool_enforced`: the adapter confirms the model or reasoning selectors were applied by a tool or runtime API.
- `prompt_preference`: selectors were included in the child prompt only.
- `unavailable`: the available runtime tools cannot apply selectors.
- `unknown`: selector support was not inspected or not reported.

## Rules

- Dispatch may request `model_profile`, `reasoning_effort`, and `cost_latency_bias`.
- Package contents alone never prove `tool_enforced`.
- If the adapter cannot inspect selector application, report `prompt_preference`, `unavailable`, or `unknown`.
- Result and review packages must include evidence for the selected enforcement status.
- Do not turn a selector preference into a blocker unless the package or user explicitly requires enforceable selector support.
