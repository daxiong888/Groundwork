---
name: to-issues
description: Split an accepted PRD spec or plan into vertical task slices with task-state fields, acceptance criteria, blockers, AFK/HITL classification, and verification evidence. Use only when the source is accepted enough; raw ideas, "刚说的想法", or conversation-only intent that asks to 拆 issues must route to to-prd first.
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

- The user asks to split a raw idea, "刚说的想法", draft requirement, or conversation-only intent before PRD/spec acceptance; use `to-prd`.
- Requirement intent or acceptance is still unclear; use `to-prd` with `scope`.
- The user asks whether an existing task is ready; use `triage`.
- The user asks for implementation steps for one accepted task; use `write-plan`.
- The user asks to execute code changes; use `implement`.
- The user asks for a tiny direct checklist; use direct fallback.

## Required Evidence

Start from the accepted PRD/spec/plan. If it is missing blockers, source context, contract impact, runtime-routing inputs, Goal Contract inputs, or verification evidence, record the missing details in `Ready-for-Agent Missing Fields`, `Goal Contract Missing Fields`, or `Runtime Missing Fields` instead of fabricating readiness.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` and `skills/_shared/ARTIFACT-PROMOTION.md` before issue splitting. If the source is raw, draft-only, unaccepted, or conversation-only without a named canonical owner, stop at the source-of-truth / promotion gate instead of producing fake-precise issues. An accepted PRD that will drive another session, remote issue creation, implementation, verification, or handoff must be promoted to a canonical artifact or explicitly tied to an external source of truth.

Use `skills/_shared/LOCALE-GUARD.md` for issue titles, issue bodies, headings, summaries, and artifact prose. The user's current session language overrides the English wording of this skill template; keep code identifiers, paths, labels, and CLI flags literal.

`to-issues` can emit a triage recommendation candidate for a slice, such as `ready-for-agent candidate`, `needs-info recommendation`, or `ready-for-human recommendation`, but final readiness belongs to `triage`.

`to-issues` may also emit runtime-routing candidates for later `triage` and `dispatch` use. These are recommendations only; `to-issues` must not create a Goal Contract, dispatch runtime work, or final-mark a slice `ready-for-agent`.

Use these candidate fields when the accepted source supports them:

```text
Implementation Task Type Candidate:
  write_implementation / read_only_review / planning_only / hybrid / diagnosis / verification / direct

Implementation Runtime Candidate:
  codex_app_managed_worktree_thread / codex_subagent / main_thread_direct / main_thread_readonly / clean_reviewer / triage_required

Product Runtime Covered:
  none / goal_contract / to_issues_runtime_candidates / triage_goal_contract / dispatch_core / codex_subagent / codex_app_managed_worktree_thread / other named runtime capability

Isolation Needed:
  context: none / subagent_prompt / thread / review_package
  filesystem: none / current_workspace / codex_managed_worktree / unknown
  diff surface: required / optional / not_required

Parallelization Candidate:
  eligible: yes / no / unknown
  conflict group:
  dependency group:
  merge order hint:

Goal Contract Status:
  not_generated_by_to_issues / missing_fields / ready_for_triage_contract_generation

Goal Contract Missing Fields:
  - ...

Runtime Missing Fields:
  - ...
```

Runtime candidate rules:

- `read_only_review` must not suggest `codex_app_managed_worktree_thread`; prefer `codex_subagent`, `main_thread_readonly`, or `clean_reviewer` based on whether the slice needs parallel review, coordinator-level review, or clean review package inspection.
- `planning_only` must not suggest `codex_app_managed_worktree_thread`; prefer `main_thread_readonly`, `main_thread_direct`, `codex_subagent`, or `triage_required` when planning scope or source truth is unclear.
- `hybrid` must suggest split first or `triage_required`; do not route the whole hybrid slice to a write worktree. A read-only investigation sub-slice may use `codex_subagent` or `main_thread_readonly`, and a managed worktree candidate can appear only after a concrete write implementation subtask exists.
- `write_implementation` may suggest `codex_app_managed_worktree_thread` only when source context, write boundary, acceptance criteria, and verification expectations are clear enough for later Goal Contract generation.
- `diagnosis` may suggest `codex_subagent` when the investigation is independent and read-only.

## Workflow

1. Confirm the source of truth and whether it is accepted enough to slice.
2. If the PRD/spec/plan is not accepted enough, stop and request acceptance, canonical artifact promotion, or a named external source of truth.
3. Apply the locale guard before drafting user-visible headings or issue text.
4. Split into vertical user-visible or behavior-visible slices, not horizontal layer buckets.
5. Include acceptance criteria, blockers, risk, AFK/HITL classification, contract impact, verification evidence needed, candidate runtime-routing fields, Goal Contract/runtime missing fields, and ready-for-agent missing fields for each slice.
6. Prefer tracker-neutral markdown. Include paste-ready GitHub/Linear wording only when useful, but do not call tracker APIs.
7. Recommend `triage` for final readiness classification or `write-plan` for an accepted slice.

## CHECKPOINTS

- STOP before splitting unless the source is accepted enough: `prd_accepted`, `issue_ready`, or a named external task source that carries acceptance state or named owner confirmation.
- STOP before drafting issue acceptance criteria unless the accepted source has clear acceptance criteria text. If stable AC IDs or equivalent canonical acceptance labels are missing, keep the existing acceptance text and record the missing stable IDs in `Ready-for-Agent Missing Fields`; do not invent labels.
- STOP before producing ready-for-agent candidates unless each slice is vertical, behavior-visible, and has an independent verification expectation.
- STOP before downstream issue creation, implementation handoff, or multi-session use if the accepted source is conversation-only; apply the artifact-promotion or external source-of-truth gate first.

`accepted enough` means all of the following are true:

- source truth is a canonical artifact, an accepted PRD/spec/plan, an issue-ready local artifact, or a named external task source;
- acceptance is explicit through `prd_accepted`, `issue_ready`, user confirmation, or the external source carrying acceptance state;
- external sources include a named owner or equivalent confirmation authority, not only a link or title;
- acceptance criteria are clear enough to preserve as slice criteria, even if they lack stable AC IDs;
- no mixed or conflicting source truth remains unresolved;
- conversation-only accepted material has been promoted or explicitly tied to an external source before it drives downstream issue creation, implementation, verification, or handoff.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Source is raw, draft-only, or unaccepted PRD/spec | Stop at the acceptance/source-of-truth gate. | Request PRD/spec acceptance, `to-prd` shaping, or a named canonical owner before issue splitting. |
| Conversation-only PRD/spec is accepted but will drive another session, remote issue creation, implementation, verification, or handoff | Stop at the artifact-promotion gate. | Ask to promote the accepted source to a canonical artifact or name an external source of truth before issue splitting. |
| Accepted source has clear acceptance criteria text but no AC IDs or equivalent canonical acceptance labels | Continue issue drafting from the existing acceptance text. | Record missing stable AC IDs or canonical labels in `Ready-for-Agent Missing Fields`; do not invent labels or block splitting. |
| Accepted source has no clear acceptance criteria | Stop before issue drafting. | Ask for acceptance criteria or return the missing criteria as a blocking `Ready-for-Agent Missing Fields` item without inventing them. |
| Source of truth is unclear, mixed, or conflicting | Name the conflict and choose `source truth: unknown` or `mixed`. | Do not split until a canonical artifact, external issue, PR, or user-confirmed owner is named. |
| Named external task source lacks acceptance state or named owner confirmation | Stop at the source-of-truth gate. | Do not treat the source name alone as accepted enough. |
| User asks to directly split issues but acceptance is not confirmed | Stop before fake-precise issue drafts. | Explain that acceptance confirmation is required before vertical slices can be treated as issue-ready. |

## Do Not

- Do not turn raw, draft-only, or conversation-only PRD text into ready-for-agent issue drafts.
- Do not invent AC IDs, canonical acceptance labels, owners, blockers, contract impact, or verification evidence to make slices look precise.
- Do not treat ordinary unnumbered bullets, section headings, narrative requirement order, or model-generated numbering as equivalent canonical acceptance labels; use them only as source acceptance text when they are clear.
- Do not skip the source-of-truth or artifact-promotion gate because the user says to "just split issues".
- Do not call GitHub, Linear, Jira, or other tracker APIs; keep output tracker-neutral unless another approved workflow explicitly takes over.
- Do not mark final readiness; `to-issues` may only produce a triage recommendation candidate.
- Do not suggest `codex_app_managed_worktree_thread` for `read_only_review`, `planning_only`, or unsplit `hybrid` slices.
- Do not use runtime candidate fields as proof that the task is executable; missing Goal Contract, source package, validation, or runtime details remain candidate gaps for `triage` / future `dispatch`.

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
- Implementation Task Type Candidate
- Implementation Runtime Candidate
- Product Runtime Covered
- Isolation Needed
- Parallelization Candidate
- Goal Contract Status
- Goal Contract Missing Fields
- Runtime Missing Fields
- Ready-for-Agent Missing Fields
- Triage Recommendation Candidate: ready-for-agent candidate / needs-info recommendation / ready-for-human recommendation
Ordering Notes
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when each issue draft has a clear vertical slice, acceptance criteria, blockers, execution type, contract impact, verification evidence needed, runtime-routing candidate fields, Goal Contract/runtime missing fields, ready-for-agent missing fields, triage recommendation candidate, and next action.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Follow `skills/_shared/ARTIFACT-PROMOTION.md`: do not let accepted PRD or issue source truth remain only in conversation when it will drive downstream work.
Do not call tracker APIs in MVP. Write local issue artifacts only when no better source owns the work and durable state is useful. Do not force `STATE.md` for every issue; lifecycle state remains opt-in under `skills/_shared/LIFECYCLE-STATE.md`.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
