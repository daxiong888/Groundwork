# Implement Lightweight Plan

Purpose: internal five-line checkpoint for scoped `implement` work; not a full plan or readiness artifact.

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
- For nontrivial bug or mechanism work, make `Why` name the confirmed cause or concrete test seam and affected invariant; make `What` describe a sufficient fix, not only the visible symptom.
- Keep `Files` to inspected files or clearly label uninspected areas as likely areas, not facts.
- Do not optimize for fewer lines or files until the planned solution is sufficient. If sufficiency requires scope or authority not yet accepted, stop and surface that boundary before editing.
- Do not require `write-plan` for small tasks where the user asked to implement now, but still use this five-line mini-plan unless the change is truly trivial and already fully bounded.
- Recommend `write-plan` only when sequencing, dependencies, stop conditions, or scope are too large to safely hold inline.

Use this lightweight plan as an execution checkpoint, not a durable artifact, unless the user asks for a written implementation plan.
