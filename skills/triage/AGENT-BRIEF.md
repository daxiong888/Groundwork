# Agent Brief Format

Use this only when a task is truly `ready-for-agent`.

```text
Task
Current Behavior
Desired Behavior
Source / Evidence
Known Source / First Inspection Step
Key Interfaces
Acceptance Criteria
Out Of Scope
Blockers
Risk / Gate
Execution: AFK / HITL
AFK/HITL Decision Points
Stop Condition
Verification Expectations
Next Action
```

`ready-for-agent` requires acceptance criteria, known evidence or first inspection step, clear output, clear stop condition, AFK/HITL decision points, blockers, and out-of-scope boundaries. If any readiness-blocking field is missing, keep the task in `needs-info` or `ready-for-human` instead of producing an agent-ready brief.
