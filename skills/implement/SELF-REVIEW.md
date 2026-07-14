# Implement Self-Review

Purpose: internal post-edit `implement` self-check; never final readiness, clean review, release approval, or UAT evidence.

Perform this self-review before the final response. Surface only material failures, remaining gaps, or evidence boundaries; do not print the full block when all items are already covered by the outcome, changed-files, checks, and risk summary.

```text
Self-Review
- Scope kept:
- Root-cause sufficiency:
- Acceptance mapping:
- Tests/checks:
- Git boundary:
- Remaining gaps:
- Verify next:
```

Rules:

- `Scope kept` states whether the diff only touched intended files.
- `Root-cause sufficiency` states whether the change addresses the confirmed cause and restores the affected invariant across known affected paths, or explicitly identifies a remaining workaround/scope gap.
- `Acceptance mapping` maps each material acceptance criterion to a change and check, or marks it unresolved.
- `Tests/checks` names commands actually run and results. Do not claim a check passed unless it was run.
- `Git boundary` summarizes staged/unstaged/unrelated files when commits or handoff are in scope.
- `Remaining gaps` lists missing evidence, no-test justification, or risks.
- `Verify next` recommends `verify` for readiness when user-facing, UAT, release, or cross-environment confidence is needed.
