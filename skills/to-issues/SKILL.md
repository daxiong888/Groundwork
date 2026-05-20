---
name: to-issues
description: Split an accepted PRD spec or plan into vertical task slices with acceptance criteria blockers and AFK or HITL classification. Use when the user asks to 拆 issues, 拆任务, create implementation slices, or turn accepted intent into tracker-neutral work units.
---

# to-issues

## Trigger Contract

Use this skill when accepted PRD/spec/plan intent needs to become vertical work units.

Should trigger:

- "基于这个 PRD 拆 issues"
- "把这个需求拆成可执行任务"
- "帮我按垂直切片拆一下"
- "这个计划怎么拆给 agent 做"
- "生成可以贴到 GitHub 的任务草稿"

Should not trigger:

- Requirement intent or acceptance is still unclear; use `to-prd` with `scope`.
- The user asks whether an existing task is ready; use `triage`.
- The user asks for implementation steps for one accepted task; use `write-plan`.
- The user asks to execute code changes; use `implement`.
- The user asks for a tiny direct checklist; use direct fallback.

## Required Evidence

Start from the accepted PRD/spec/plan. If it is missing acceptance criteria, blockers, or source context, mark the issue as `needs-info` instead of fabricating readiness.

## Workflow

1. Confirm the source of truth and whether it is accepted enough to slice.
2. Split into vertical user-visible or behavior-visible slices, not horizontal layer buckets.
3. Include acceptance criteria, blockers, risk, AFK/HITL classification, and verification expectation for each slice.
4. Prefer tracker-neutral markdown. Include paste-ready GitHub/Linear wording only when useful.
5. Recommend `triage` for readiness classification or `write-plan` for an accepted slice.

## Output Shape

```text
Issue Set Summary
Source
Issue Drafts
- Title
- Goal
- Acceptance Criteria
- Evidence / Source
- Blockers
- Execution: AFK / HITL
- Verification
Ordering Notes
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when each issue draft has a clear slice, acceptance criteria, blockers, execution type, verification expectation, and next action.

## Artifact Rule

Do not call tracker APIs in MVP. Write local issue artifacts only when no better source owns the work and durable state is useful.
