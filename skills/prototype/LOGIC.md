# Logic Prototype Branch

Use this branch for state machines, data shapes, reducers, business rules, validation logic, or terminal prototypes.

Required output:

```text
Prototype Question
Model / Rule Under Test
Inputs
States / Transitions
Cases Covered
Observed Result
Known Gaps
Implementation Implications
Cleanup Decision
```

Rules:

- Keep logic prototypes small and disposable.
- Prefer deterministic code or tables when behavior must be repeatable.
- Do not treat prototype code as production code.
- If results contradict PRD/task assumptions, feed that back before implementation.
