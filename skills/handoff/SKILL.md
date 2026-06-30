---
name: handoff
description: Preserve or write compact continuation state for long-running R&D work without duplicating PRDs plans issues commits or diffs. Use when the user asks to create a handoff, save state for next session, continue in the next session, prepare continuation context, resume notes, or compact state transfer; do not use for one-off explanations of what handoff means.
---

# handoff

## Trigger Contract

Use this skill when the user needs compact state transfer across sessions, agents, or future continuation.

Should trigger:

- "给下个 session 做 handoff"
- "下个 session 继续验证"
- "整理一下后续接手上下文"
- "我要换会话，保存关键状态"
- "给同事一个接手摘要"
- "把当前进展压缩成 continuation notes"

Should not trigger:

- The user asks what handoff is or asks for a one-off explanation of Groundwork handoff; answer directly.
- The user asks for a PRD; use `to-prd`.
- The user asks for issue slicing; use `to-issues`.
- The user asks for readiness proof; use `verify`.
- The work is small enough to answer directly.
- The user asks to duplicate full PRDs, diffs, or logs.
- "把这个需求整理成 PRD"; use `to-prd`.
- "按这个任务改代码"; use `implement`.
- "验证这次能不能发布"; use `verify`.
- "查 wiki 里的长期知识"; use `wiki`.
- "这事一句话回答即可"; answer directly.

## Required Evidence

Reference existing PRDs, issues, plans, commits, diffs, verification notes, lifecycle state, and artifacts. Do not copy secrets, sensitive logs, full diffs, or long documents. If the handoff includes git state, staging, commit boundary, or files that must remain out of scope, use `skills/_shared/GIT-BOUNDARY.md`.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

For Codex-native Local to Worktree or Worktree to Local continuation, use a `native_handoff_package`. Groundwork prepares this compact package only; official Codex Handoff owns moving the thread and code between Local and Worktree and owns the Git operations performed by that native flow. Do not claim that Groundwork executes Codex App Handoff, creates the native worktree, restores the associated worktree, archives the thread, or moves code.

Required shape:

```yaml
native_handoff_package:
  direction: local_to_worktree | worktree_to_local
  goal: ""
  scope: []
  out_of_scope: []
  base:
    base_ref: ""
    base_commit: ""
    branch: ""
  native_context:
    thread_ref:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
    worktree_path:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
    worktree_association:
      value: ""
      availability: visible | unavailable_before_handoff | unavailable_in_current_surface | redacted
  route_decision_ref: ""
  relevant_artifacts: []
  changed_files: []
  evidence:
    commands_run: []
    checks_passed: []
    checks_failed: []
    not_run: []
  open_risks: []
  next_command: ""
  stop_condition: ""
  redaction_notes: ""
```

Native handoff package rules:

- The package must be self-contained enough for a new session to continue without hidden parent-session history.
- The package must cite canonical artifacts instead of copying full PRDs, full issue bodies, long diffs, logs, or transcripts.
- `native_context.thread_ref`, `native_context.worktree_path`, and `native_context.worktree_association` must always include explicit `availability` values.
- Local to Worktree packages prepared before Codex creates or exposes the native worktree must set `native_context.worktree_path.availability: unavailable_before_handoff`; do not invent a future path, native ID, or thread reference.
- Worktree to Local packages must include `changed_files`, `evidence`, `open_risks`, `stop_condition`, and all `native_context` fields with explicit availability markers before closeout. If visible native context exists, record it with `availability: visible`; if it is hidden in the current surface, mark it `unavailable_in_current_surface`; if intentionally withheld, mark it `redacted`.
- Worktree to Local `changed_files` must list the returned file boundary. If no files changed, include an explicit empty list plus evidence that no files changed.
- The package must state `redaction_notes` even when no sensitive data was present.
- The package must never instruct a future reader to use `git add .`; use explicit pathspecs and denylist guidance when staging or commit continuation is in scope.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` to decide whether lifecycle state is needed, stale, or only referenced. Use `skills/_shared/ARTIFACT-PROMOTION.md` to separate canonical artifacts from recoverable lifecycle state: handoff should cite PRDs, issue maps, verification reports, and external issues instead of copying them.

Use `REVIEW-PACKAGE.md` when the next reader needs a review package rather than a basic continuation summary. Use `skills/_shared/SUBAGENT-DELEGATION.md` when the handoff prepares a fresh-context subagent review.
Use `skills/dispatch/COMPLEX-WORK-SEPARATION.md` when handoff preserves continuation state for managed worktree work whose risk or scope may require separate planning, implementation, clean review, verification, and coordinator closeout roles.

For complex work separation, `handoff` preserves continuation state and ownership boundaries only. It must not become a runtime executor, clean reviewer, verifier, coordinator closeout, merge-back owner, archive owner, branch cleanup owner, commit path, push path, PR path, or tracker mutation path. It may name the next owning role and cite the evidence needed for that role.

When a P1, public API, migration, schema, security, privacy, auth, permissions, data correctness, shared contract, package schema, adapter contract, state machine, weak-validation, or multi-package change is handed off without fresh clean review evidence, record that as an open gap or do-not-assume item. Do not let handoff wording imply that child implementer self-check is clean review.

Use `skills/_shared/ROLE-SEPARATION.md` when preserving material continuation state. Handoff may report received evidence and the next independent role, but must not upgrade `Self-check Evidence` into `Clean Review Evidence` or `Independent Verification Evidence`.

Use `skills/_shared/VISUAL-HANDOFF-PACKET.md` when handoff cites or carries a visual handoff packet, HTML packet, screenshot set, generated visual artifact, prototype output, or frontend/backend review packet. Treat it as a communication artifact, not readiness evidence; put unsupported API/schema/source, browser, runtime, UAT, release, and customer-readiness claims under `Do-Not-Assume` unless separate qualifying evidence is named.

Use `skills/_shared/LLM-WIKI.md` when continuation state includes reusable project knowledge or cites a project wiki. Handoff may reference wiki pages as orientation and may emit a `Wiki Update Candidate` for durable reusable knowledge, but it must not turn every handoff into a wiki diary, update wiki pages without explicit wiki-maintenance scope, or present wiki synthesis as source truth, clean review evidence, independent verification evidence, runtime evidence, UAT evidence, release evidence, marketplace evidence, installed-plugin evidence, or cache-refresh evidence.

Use `skills/_shared/RELEASE-EVIDENCE-CLAIM.md` when a handoff preserves runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh claims. If the handoff only references source-validation or continuation evidence, set those stronger claims to `unverified` or `not_applicable`.

Small, low-risk continuation notes should remain compact. Do not force a full separation package when no separation threshold applies and a concise handoff can safely identify source truth, current state, gaps, and next action.

Use `skills/_shared/LIFECYCLE-STATE.md` when the user asks to pause, resume, switch sessions, save state, continue later, or otherwise preserve workstream recovery state.

When an existing workstream `artifacts/<workstream-slug>/STATE.md` is present, handoff must reference it instead of copying it. Report the state artifact path, freshness (`fresh`, `stale`, or `unknown`), and whether an update is needed. Do not paste full lifecycle state, PRDs, issue bodies, plans, diffs, logs, or transcripts into the handoff.

## State Freshness Algorithm

Use this algorithm before reporting `State Freshness` for an existing `artifacts/<workstream-slug>/STATE.md`:

1. Read the existing state file enough to inspect `Last Updated`, `Canonical Sources`, current risks/gaps, and next action. Do not copy the full state into the handoff.
2. Verify `Last Updated` is comparable:
   - ISO 8601 timestamp with timezone; or
   - exact date plus source-order evidence that can be compared.
3. Verify `Canonical Sources` is present, readable, and points to the artifacts, issue, PRD, code, tests, runtime evidence, or user-confirmed decision that currently own truth.
4. Compare state claims against the canonical sources available in the current handoff scope.
5. Report one of:
   - `fresh` only when `Last Updated` is comparable, `Canonical Sources` are readable and resolvable, all checked canonical sources are not newer/conflicting or newer sources are explicitly irrelevant, and the handoff names the checked source set.
   - `stale` when a checked canonical source conflicts with `STATE.md`, a later source supersedes it, or a verified gap/risk changed after `Last Updated`.
   - `unknown` when the file cannot be read, `Last Updated` is missing/unreadable/not comparable, `Canonical Sources` is missing/unreadable/unresolvable, canonical sources conflict with each other, checked source set is not named, or freshness cannot be evidenced from available sources.

Default to `State Freshness: unknown` and `State Update Needed: yes` unless freshness is evidenced. Do not infer freshness from path existence, confidence, or absence of known conflicts.

When freshness is `stale` or `unknown`, keep the handoff actionable:

- name the missing field, unreadable section, conflicting source, or unavailable check;
- follow canonical source truth over lifecycle state;
- put unverifiable claims in `Open Gaps`, `Risks`, or `Do-Not-Assume`;
- recommend updating `STATE.md` only when the lifecycle-state threshold still applies.

## Workflow

1. Identify the next reader and next action.
2. Run lifecycle preflight for source truth, artifact promotion, lifecycle-state need, git topology, and stop condition.
3. Reference existing canonical artifacts instead of duplicating them.
4. Check whether a workstream `artifacts/<workstream-slug>/STATE.md` exists when lifecycle threshold is met.
5. Apply the State Freshness Algorithm, then reference existing `STATE.md` by path when present, with freshness and update-needed status, or recommend creating/updating it when the threshold is met.
6. Capture current state, decisions, evidence, gaps, and risks.
7. Capture allowed/disallowed files when file boundary matters.
8. Preserve visual packet boundaries when present: require state/flow, UI surface, API contract mapping, Mock vs Confirmed fields, open questions, `Do Not Implement / Do Not Assume`, and evidence boundary, or record the missing packet sections as continuation gaps.
9. Include `native_handoff_package` when continuation crosses Local and Worktree. Keep Codex-native thread/worktree fields as explicit availability-marked context, not inferred runtime claims.
10. Include audience, goal, current decision, source artifacts, evidence, open risks, next skill, do-not-assume, git boundary, and redaction note when producing a review package.
11. Add a `Wiki Update Candidate` only when the handoff reveals durable reusable project knowledge; otherwise keep wiki out of the handoff.
12. Include only enough detail to resume safely; default to a one-screen continuation summary when no durable handoff file is needed.
13. Recommend the next skill or direct action.

## CHECKPOINTS

- STOP before producing a final handoff or review package if the continuation goal, source artifacts, evidence, open risks, next skill or direct action, or `Do-Not-Assume` boundary is missing.
- STOP before marking open risks as `None` unless the source artifacts, evidence, git boundary, and verification gaps were checked closely enough to justify that claim.
- STOP before copying PRDs, plans, issue bodies, commits, full lifecycle state, long diffs, logs, or transcripts; cite canonical artifacts and summarize only resume-critical state.
- STOP before asking the next reader to act if the next skill, target file/path/artifact, first command/check, or human decision needed is not executable from the handoff.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Evidence is insufficient for a claim | Move the claim to `Open Gaps`, `Risks`, or `Do-Not-Assume`. | Name the missing source, check, runtime evidence, or artifact instead of presenting the claim as verified. |
| Open risks are missing or unclassified | Stop and classify each material risk by impact on continuation, verification, git boundary, customer/UAT, or artifact scope. | Use `None` only when the checked evidence supports no remaining material risk. |
| Git status or file boundary is unclear | Run or request the git-boundary evidence required for the handoff scope. | Include intended files, explicit denylist, staged/unstaged status, and unrelated dirty/untracked files; never rely on `git add .`. |
| Next step is not executable | Rewrite the next action as a concrete next skill or direct action with target, input artifact, and first check. | If a human decision is required, state the decision and options instead of delegating vague follow-up. |
| Existing `STATE.md` is missing or unreadable | Do not invent state contents. | Report `State Freshness: unknown`, `State Update Needed: yes` when lifecycle threshold applies, and name the missing/unreadable path. |
| `Last Updated` is missing, unreadable, or not comparable | Do not mark state fresh. | Report `State Freshness: unknown`, `State Update Needed: yes`, and name the bad or missing field. |
| `Canonical Sources` is missing or unreadable | Do not treat lifecycle state as source truth. | Report `State Freshness: unknown`, `State Update Needed: yes`, and ask the next action to inspect or restore canonical sources. |
| Canonical sources conflict with each other or with `STATE.md` | Follow the strongest checked canonical source and mark the conflict. | Report `State Freshness: stale` when state conflicts with source truth, or `unknown` when source truth cannot be resolved; keep the conflict in `Risks` or `Do-Not-Assume`. |
| Freshness is unverifiable from available evidence | Do not infer freshness from file presence. | Report `State Freshness: unknown`, `State Update Needed: yes`, and name the missing evidence/check. |

## Do Not

- Do not turn the handoff into a diary, transcript, or chronological status log.
- Do not use handoff as an auto-wiki writer or treat wiki pages as continuation source truth without separately named source evidence.
- Do not claim Groundwork performs official Codex Handoff, creates native Codex worktrees, moves code between Local and Worktree, or owns native Handoff Git operations.
- Do not copy long diffs, full PRDs, issue bodies, plans, commits, lifecycle state, raw logs, or transcripts.
- Do not hide unverified claims; label them as open gaps, risks, or `Do-Not-Assume`.
- Do not duplicate canonical artifacts when a stable path, issue ID, commit, or redacted source identifier is enough.
- Do not change the compact continuation-state boundary: handoff is a transfer package, not the PRD, plan, issue map, commit history, or durable lifecycle-state owner.

## Output Shape

```text
Current State
Goal
Current Decision
Source Artifacts
Decisions Made
Evidence
Role:
Design Source:
Self-check Evidence:
Clean Review Evidence:
Independent Verification Evidence:
Runtime Evidence:
Browser Evidence:
UAT Evidence:
Release Evidence:
Readiness Boundary:
Required Next Independent Role:
Open Gaps
Risks
Lifecycle State
- State Artifact:
- State Freshness: fresh / stale / unknown
- State Update Needed: yes / no
- State Reference Mode: existing-state-reference / recommend-state / no-state-needed
Allowed / Disallowed Files
Git Boundary
Do-Not-Assume
Visual Packet Evidence Boundary
Redaction Note
Next Action
Artifact Recommendation
```

## Stop Condition

Stop when the next session can resume without rediscovering core context.

## Gate Rule

Do not post, push, publish, update trackers, mutate shared skill files, or write remote handoff artifacts without explicit approval with Target, Action, Risk, and Rollback/Undo.

Do not ask a future session to use `git add .`. When handoff includes commit continuation, include intended pathspecs, explicit denylist, and unrelated dirty/untracked files that must stay unstaged.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Follow `skills/_shared/ARTIFACT-PROMOTION.md`: canonical artifacts remain the source of truth, while `STATE.md` remains compact recovery state.
Keep handoff compact by default: cite canonical artifacts, summarize only resume-critical state, and avoid copying full PRDs, issue bodies, plans, diffs, logs, or transcripts. Write a handoff file only when durable continuation is needed. Reference secret locations abstractly and never quote secret values. Existing `STATE.md` remains the lifecycle state owner; handoff is the transfer package, not the durable state layer.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
