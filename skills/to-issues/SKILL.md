---
name: to-issues
description: Split an accepted PRD spec or plan into vertical task slices with task-state fields, acceptance criteria, blockers, AFK/HITL classification, and verification evidence. Use when the user asks to 拆 issues, 拆任务, create implementation slices, or turn accepted intent into tracker-neutral work units.
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

Start from the accepted PRD/spec/plan. If it is missing acceptance criteria, blockers, source context, contract impact, or verification evidence, record the missing details in `Ready-for-Agent Missing Fields` instead of fabricating readiness.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` and `skills/_shared/ARTIFACT-PROMOTION.md` before issue splitting. If the source is raw, draft-only, unaccepted, or conversation-only without a named canonical owner, stop at the source-of-truth / promotion gate instead of producing fake-precise issues. An accepted PRD that will drive another session, remote issue creation, implementation, verification, or handoff must be promoted to a canonical artifact or explicitly tied to an external source of truth.

Use `skills/_shared/LOCALE-GUARD.md` for issue titles, issue bodies, headings, summaries, and artifact prose. The user's current session language overrides the English wording of this skill template; keep code identifiers, paths, labels, and CLI flags literal.

`to-issues` can mark a slice as a `ready-for-agent candidate`, but final readiness belongs to `triage`.

## Workflow

1. Confirm the source of truth and whether it is accepted enough to slice.
2. If the PRD/spec/plan is not accepted enough, stop and request acceptance, canonical artifact promotion, or a named external source of truth.
3. Apply the locale guard before drafting user-visible headings or issue text.
4. Split into vertical user-visible or behavior-visible slices, not horizontal layer buckets.
5. Include acceptance criteria, blockers, risk, AFK/HITL classification, contract impact, verification evidence needed, and ready-for-agent missing fields for each slice.
6. Prefer tracker-neutral markdown. Include paste-ready GitHub/Linear wording only when useful, but do not call tracker APIs.
7. Recommend `triage` for final readiness classification or `write-plan` for an accepted slice.

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
- Contract Impact: API / DB / UI state / docs / verification contract / none
- Verification Evidence Needed
- Ready-for-Agent Missing Fields
- Readiness Candidate: ready-for-agent candidate / needs-info / ready-for-human
Ordering Notes
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when each issue draft has a clear vertical slice, acceptance criteria, blockers, execution type, contract impact, verification evidence needed, ready-for-agent missing fields, readiness candidate, and next action.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Follow `skills/_shared/ARTIFACT-PROMOTION.md`: do not let accepted PRD or issue source truth remain only in conversation when it will drive downstream work.
Do not call tracker APIs in MVP. Write local issue artifacts only when no better source owns the work and durable state is useful. Do not force `STATE.md` for every issue; lifecycle state remains opt-in under `skills/_shared/LIFECYCLE-STATE.md`.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
