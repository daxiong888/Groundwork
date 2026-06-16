# Subagent Read-only Review Scenario

This scenario complements `evals/prompts/dispatch.csv` by checking the Phase 1 `codex_subagent` route as a package-only dispatch output.

## Scenario: Package-only read-only review

Prompt:

```text
这个 accepted read-only review 任务需要产品和安全两个视角并行评审。请生成 dispatch package，但不要 spawn subagent，不要调用 runtime tool，也不要改文件。
```

Expected first skill: `dispatch`

Expected route: `codex_subagent`

Expected runtime behavior:

- `runtime_id = codex_subagent`
- `isolation.context = subagent_prompt`
- `isolation.filesystem = none` or `tool_dependent`
- `runtime_package.subagent_package.can_write_files = false`
- `runtime_package.subagent_package.expected_output = findings_package` or `diagnosis_package`
- `runtime_package.subagent_package.execution_status = package_only` unless runtime capability detection and explicit execution request or approval are both present

Expected package contents:

- role-specific prompt for each requested lens
- self-contained context package
- explicit constraints, including no file edits and no runtime execution claim
- stop condition and pause condition
- result schema naming `findings_package` or `diagnosis_package`

Expected result package:

- `runtime_id = codex_subagent`
- `output_type = findings_package` or `diagnosis_package`
- capability detection outcome is reported as unavailable, unknown, or not approved when no execution tool is used
- selector enforcement is `prompt_preference`, `unavailable`, or `unknown` unless an adapter confirms `tool_enforced`

Risk / gate:

Dispatch produces the package only. It must not claim a subagent was spawned, that review execution happened, or that validation ran unless a runtime adapter actually executed the package and returned evidence.
