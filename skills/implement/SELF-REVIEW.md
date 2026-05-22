# Implement Self-Review

Target Reader: Codex running the Groundwork `implement` skill.
Reader Action Needed: Review the local implementation before reporting completion or handing off to `verify`.
Decision Supported: Whether the implementation stayed scoped and what evidence still needs verification.
Scope: Post-edit self-review for scoped implementation work.
Out of Scope: Final readiness verdict, release approval, or customer/UAT pass.
Evidence Level: Groundwork issue #6 acceptance criteria and Groundwork implementation review requirements.

Include self-review in the final implementation response:

```text
Self-Review
- Scope kept:
- Acceptance mapping:
- Tests/checks:
- Git boundary:
- Remaining gaps:
- Verify next:
```

Rules:

- `Scope kept` states whether the diff only touched intended files.
- `Acceptance mapping` maps each material acceptance criterion to a change and check, or marks it unresolved.
- `Tests/checks` names commands actually run and results. Do not claim a check passed unless it was run.
- `Git boundary` summarizes staged/unstaged/unrelated files when commits or handoff are in scope.
- `Remaining gaps` lists missing evidence, no-test justification, or risks.
- `Verify next` recommends `verify` for readiness when user-facing, UAT, release, or cross-environment confidence is needed.
