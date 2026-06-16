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

Goal Contract
- Goal Command:
- Outcome:
- Source Truth:
- Acceptance Criteria Mapping:
- Verification:
- Constraints:
- Boundaries:
- Iteration Policy:
- Stop When:
- Pause If:
- Non-goals:
- Risk / Gate:
- Preferred Runtime:
- Result Package Expected:

Execution Profile Recommendation
- Runtime Candidate:
- Model Profile:
- Reasoning Effort:
- Cost/Latency Bias:
- Routing Reason:

Next Action
```

`ready-for-agent` requires acceptance criteria, known evidence or first inspection step, clear output, clear stop condition, AFK/HITL decision points, blockers, and out-of-scope boundaries. If any readiness-blocking field is missing, keep the task in `needs-info` or `ready-for-human` instead of producing an agent-ready brief.

Include `Goal Contract` only for executable `ready-for-agent + AFK` tasks. `Goal Command` must start with `/goal`, and `Pause If` must cover the AFK/HITL decision points that would require a human decision, missing source truth, approval, access, or risk escalation.

Do not emit an executable child goal for `needs-info`, `ready-for-human`, or HITL-only tasks. HITL tasks may include a human-decision brief that names the decision, options, risks, and next human action, but not a dispatchable `/goal`.

`Preferred Runtime` and `Execution Profile Recommendation` are recommendations for later `dispatch` routing. `triage` may recommend runtime candidate, model profile, reasoning effort, cost/latency bias, and routing reason, but must not claim selector enforcement or final routing.
