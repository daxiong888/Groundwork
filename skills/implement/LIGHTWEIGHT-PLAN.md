# Implement Lightweight Plan

Target Reader: Codex running the Groundwork `implement` skill.
Reader Action Needed: Make a small implementation plan before editing without requiring a full `write-plan` workflow.
Decision Supported: Whether the requested implementation is scoped enough to edit and what checks will prove the local change.
Scope: Minimal planning inside `implement` after source/task inspection has started.
Out of Scope: Full project plans, multi-checkpoint plans, PRD shaping, or task slicing.
Evidence Level: Groundwork issue #6 acceptance criteria and `docs/prd.md` implement contract.

Use this plan before file edits unless the change is truly trivial and already fully bounded.

```text
Implementation Mini-Plan
- What:
- Why:
- Files:
- Test:
- Risk:
```

Rules:

- Inspect the task, PRD/spec, source, tests, config, and relevant diffs before naming exact files when correctness depends on them.
- Map acceptance criteria to planned change, test/check, and expected evidence.
- Keep `Files` to inspected files or clearly label uninspected areas as likely areas, not facts.
- Do not require `write-plan` for small tasks where the user asked to implement now, but still use this five-line mini-plan unless the change is truly trivial and already fully bounded.
- Recommend `write-plan` only when sequencing, dependencies, stop conditions, or scope are too large to safely hold inline.

Use this lightweight plan as an execution checkpoint, not a durable artifact, unless the user asks for a written implementation plan.
