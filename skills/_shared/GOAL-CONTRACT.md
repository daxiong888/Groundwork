# Goal Contract

Target Reader: Groundwork `triage`, future `dispatch`, runtime adapters, and implementation agents that prepare or consume executable agent tasks.
Reader Action Needed: Use this contract to write, review, or reject executable `/goal` work before it is handed to an implementation runtime.
Decision Supported: Whether a task has enough source truth, verification, boundaries, iteration limits, and pause conditions to run as an executable agent goal.
Scope: Shared Goal Contract field set, quality bar, integration points, linter expectations, and rejection criteria for executable agent tasks.
Out of Scope: Implementing `dispatch`, changing public skill behavior, creating task databases, calling runtime tools, or inventing product truth.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md` FR-7, FR-8, AC-9, AC-10, and Issue 1 in `artifacts/dispatch-runtime-router/issue-map.md`.

## Required Shape

Use this shape for executable agent tasks:

```text
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
```

Chinese user-facing content is supported. Chinese labels may be used where the surrounding artifact requires them, but code identifiers, command prefixes, repo paths, runtime IDs, and result package names should remain literal.

## Field Rules

- Goal Command: must start with `/goal` and describe one executable task. It must not be a placeholder such as `/goal <one executable task>`, a bare `/goal`, bracketed template text, or an otherwise executable-looking command that still embeds placeholders such as `/goal Implement <task> [acceptance]`.
- Outcome: must name one concrete result, not a vague improvement.
- Source Truth: must cite the canonical PRD, issue, source file, artifact, or explicit user-provided package used to constrain the goal.
- Acceptance Criteria Mapping: must map acceptance criteria to expected evidence or checks. Do not invent acceptance criteria when source truth is unclear.
- Verification: must name concrete evidence such as a command, test, browser path, screenshot, log excerpt, runtime output, artifact path, or review checklist.
- Constraints: must state required safety, scope, or workflow constraints such as no staging, no remote writes, no dependency churn, or no secrets exposure.
- Boundaries: must define the write boundary and forbidden areas, including unrelated files, user data, secrets, default branches, production systems, runtime scratch, or external repos when applicable.
- Iteration Policy: must bound retries or remediation. Repeated attempts require new evidence or a changed hypothesis.
- Stop When: must define the evidence that ends the goal.
- Pause If: must define conditions that require human input, source clarification, approval, missing tooling resolution, or risk escalation.
- Non-goals: must list explicitly excluded work.
- Risk / Gate: must name remaining risks, approval gates, destructive actions, or remote mutation gates.
- Preferred Runtime: must name the preferred runtime such as `codex_app_managed_worktree_thread`, `codex_subagent`, `main_thread_direct`, `main_thread_readonly`, `clean_reviewer`, or state that `dispatch` may choose.
- Result Package Expected: must name the required output package such as `review_package`, `findings_package`, `diagnosis_package`, or another declared package.

## Integration Points

- `to-issues`: identifies missing Goal Contract fields but does not final-mark readiness.
- `triage`: creates a Goal Contract only for ready-for-agent executable tasks.
- `dispatch`: consumes a Goal Contract and may reject tasks with missing required fields.
- runtime adapters: receive a Goal Contract but do not generate product truth.

## Quality Bar

A strong Goal Contract:

- has one concrete outcome;
- maps acceptance criteria to verification;
- names exact checks or evidence where known;
- protects unrelated files, user data, secrets, production systems, and default branches;
- defines the write boundary;
- defines bounded iteration policy;
- defines stop evidence;
- defines pause conditions;
- names a preferred runtime or lets `dispatch` choose one;
- names the expected result package.

Reject or revise the contract if it:

- says only `make it better`, `finish this`, `fix bugs`, or an equivalent vague outcome;
- uses a placeholder Goal Command such as `/goal <one executable task>`, `/goal [task]`, `/goal {task}`, `/goal Implement <task> [acceptance]`, or a bare `/goal`;
- lacks verification or uses only `make sure it works`;
- allows broad edits without reason, such as `edit anything` or `随便改`;
- asks for repeated retries without new evidence, such as `keep trying`;
- has no stop evidence or pause condition;
- leaves placeholders such as `[Outcome]`, `[Verification]`, `TODO`, `TBD`, or `待定`;
- turns vague quality adjectives into unverifiable criteria;
- invents product truth when business rules or acceptance criteria are unclear.

## Lightweight Lint

Use the local linter for a fast structural check:

```bash
python3 scripts/lint_goal_contract.py <goal-contract-file>
```

The linter scans the full Markdown file, including fenced code blocks. It accepts either same-line field values or indented/block values immediately after a required label, and it requires the extracted `Goal Command` value itself to start with `/goal`. It also rejects structurally detectable placeholder commands, including bare placeholders and embedded placeholder tokens such as `/goal Implement <task> [acceptance]`. It intentionally does not perform full Markdown AST validation.

`evals/prompts/goal-contract.csv` is a fixture-only manifest for Goal Contract lint coverage. It is not part of the runtime default suite because `goal-contract` is a shared contract and linter, not a public skill runtime route.

Passing output:

```text
Goal Contract Lint: pass
```

Failing output:

```text
Goal Contract Lint: fail
Findings:
- <field>: <reason>
```
