---
name: implement
description: Execute implementation-ready code changes, scoped fixes, confirmed bug diagnosis, explicit PRD-bypass implementation, implementation delivery gates, PR-bound implementation, push/PR/issue-closeout requests paired with implementation, and read-only implementation conformance reviews against TASK/PRD/diff. Use only after source truth is accepted enough for execution or the user explicitly bypasses PRD/spec shaping; requirements shaping before acceptance belongs upstream.
---

# implement

## Trigger Contract

Use this skill when the user asks for code changes, implementation execution, implementation review, or diagnosis before a scoped fix.

Should trigger:

- "按这个任务实现"
- "根据这个 plan 改代码"
- "修一下这个 confirmed bug"
- "修一下这个问题"
- "实现这个接口调整"
- "先确认 bug 再改"
- "先确认是不是真 bug，再做最小修改"
- "只报告诊断结论和最小修改方向"
- "明确跳过 PRD 直接实现这个小改，但先做 git topology 和测试说明"
- "我确认跳过 PRD 直接改这个客户可见文案，并先走风险确认"
- "review 这次实现是否符合 PRD"
- "review 这次实现是否符合 TASK.md 但不要判断 UAT"
- "review 这次实现是否符合 TASK.md，不要判断能否给客户 UAT，不要编辑文件"
- "检查这次实现是否满足 TASK.md，但不做 readiness / UAT 判断"
- "review this implementation against the task without readiness judgment"
- "按这个任务实现并做最小自测"
- "实现完后直接 git push origin main 并关闭相关 GitHub issues"
- "实现这个 issue，最后提交 PR"
- "实现并处理 push / PR / issue closeout"

Should not trigger:

- Requirements need shaping, or the user gives only a raw product/draft PRD/workflow/plugin/marketplace/runtime idea without explicit PRD bypass; use `to-prd`.
- Work needs task slicing; use `to-issues`.
- Task readiness is unknown; use `triage`.
- The user only asks for a plan; use `write-plan`.
- The user asks if the finished work is ready; use `verify`.
- The user asks whether an implementation can pass UAT or release; use `verify`.
- The user only asks for a full implementation plan before edits; use `write-plan`.

## Required Evidence

Inspect relevant files, direct callers/callees, tests, config, and diffs before editing when they affect correctness. Check dirty worktree state before changes. Do not invent exact file paths, APIs, schemas, commands, or runtime behavior before inspection.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` to confirm the implementation source of truth and requirement state before editing. Raw or draft requirements are not implementation-ready unless the user explicitly requests a bypass.
Explicit PRD/spec bypass is valid only when the user clearly asks to skip PRD/spec shaping and implement directly. Vague urgency, a proposed solution, or "do it" alone is not a bypass. When bypass is valid, acknowledge it and still apply source inspection, git topology, mini-plan, test/no-test, and risk gates.

Use `skills/_shared/GIT-TOPOLOGY-GATE.md` before writing files for PR-bound implementation, and again before staging, committing, pushing, opening a PR, or closing remote issues. If the current branch is `main` / `master` / `trunk`, the branch name is empty, or `HEAD` is detached and the work is PR-bound, output a gate decision and stop before edits until a branch or worktree decision is made.

Use `LIGHTWEIGHT-PLAN.md` before editing: What, Why, Files, Test, Risk. Map acceptance criteria to planned change, test/check, and expected evidence.

Apply `EB-ROLE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` and use `skills/_shared/ROLE-SEPARATION.md` for material changes. Skill-specific delta: `implement` may provide `Self-check Evidence` from its own inspection and checks, but material closeout still requires the role-separation final-report fields.

Use `skills/_shared/REVIEW-LOOP.md` when implementation is performed in a child thread, managed worktree, subagent, or other reviewable execution package. Skill-specific delta: set `Clean Review Evidence` to `pending`, `missing`, or `not applicable`; if implementation fixes a clean-review finding, mark any prior clean review stale for the latest diff and route the package back to fresh clean review unless a documented low-risk coordinator-intake exception applies.

Apply `EB-RUNTIME-001` and `EB-CACHE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md`, and use `skills/_shared/RUNTIME-CAPABILITY.md` when the implementation request or final report references runtime/model selection, selector enforcement, child-thread/worktree execution, subagents, runtime cache, marketplace, or installed-plugin behavior. Skill-specific delta: `implement` may report source-validation checks it ran.

Apply `EB-RELEASE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` and use `skills/_shared/RELEASE-EVIDENCE-CLAIM.md` when an implementation final report makes or scopes out runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh claims.

Apply `EB-WIKI-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` and use `skills/_shared/LLM-WIKI.md` when a project wiki is present or the user cites wiki pages. Skill-specific delta: wiki context may identify likely files, concepts, prior decisions, or stale-risk areas, but implementation must inspect source, contracts, tests, or authoritative artifacts before changing code. If implementation reveals durable reusable architecture, contract, procedure, or error-book knowledge, emit a `Wiki Update Candidate` or recommend the `wiki` route instead of updating wiki pages unless the user explicitly requested wiki maintenance.

Use `skills/_shared/COGNITIVE-BUDGET.md` when recommending a model profile. Recommend `model_profile` before any concrete model, and do not use Spark or any fast profile as final clean reviewer, final verifier, public skill approver, release/UAT authority, or customer authority.

For read-only implementation conformance review, do not force a fix plan. Inspect the task/PRD, source, tests, and git boundary when available; report whether the implementation satisfies acceptance, what evidence was checked, what gaps remain, and explicitly avoid UAT/release/readiness verdicts unless the user asks for them.

### Conformance Field Set

Use this exact field set for read-only conformance review and any implementation final report that includes conformance evidence:

```text
Scope:
Acceptance Map:
Evidence Inspected:
Findings P0/P1/P2:
Non-Readiness Boundary:
Gaps:
Next Action:
```

`Non-Readiness Boundary` must say that the review is limited to implementation conformance and does not decide UAT, release, customer readiness, deployment readiness, or final acceptance unless the user explicitly asks for that scope.

### Runtime Output Contract

For implementation, diagnose-before-edit, explicit PRD-bypass implementation, gated implementation, blocked implementation, or implementation conformance review, final reports must include the `Conformance Field Set` as line-prefixed fields.

If the implementation is blocked before edits because source truth, git topology, permissions, or tests are unavailable, still include those labels and put the blocker under `Findings P0/P1/P2`, `Gaps`, and `Next Action`.

When `Risk Gate` is not `none`, or when the prompt asks for git, customer-visible, data-write, destructive, push, PR, issue-closeout, deploy, publish, migration, remote, or shared-skill execution, include the exact gate field labels as line-prefixed fields before executing anything:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
```

Use `TDD-LITE.md` for behavior changes when feasible: RED failing test/reproduction, GREEN minimal change, REFACTOR only after green. If no failing test or reproduction is feasible, give a no-test justification and do not claim TDD.

If the work starts from a verification failure, use `skills/verify/QA-FIX-QA.md`: confirm expected, actual, reproduction, severity, minimal diagnosis, fix plan, and re-QA requirement before editing. Fix only the scoped failure and rerun the original failing check.

If using a subagent for review, use `skills/_shared/SUBAGENT-DELEGATION.md`. The reviewer gets fresh context and cannot expand scope or modify files unless explicitly delegated.

## Workflow

1. Confirm source task, scope, and stop condition.
2. Run lifecycle preflight and `skills/_shared/GIT-TOPOLOGY-GATE.md`; inspect current branch, dirty state, relevant diffs, and whether branch/worktree is required before editing.
3. Choose the implementation branch before output or edits:
   - Bug diagnosis or diagnose-before-edit: reproduce or inspect first, separate confirmed cause from hypothesis, then continue only with the minimum scoped fix or stop with diagnosis evidence.
   - Read-only conformance review: inspect the task/PRD, source, tests, and git boundary when available; output conformance findings and stop without edits.
   - PR-bound implementation, push, PR, or issue closeout: run the git topology and remote-write gates first, then continue only when branch/worktree and approval requirements are satisfied.
   - Ordinary scoped implementation: continue with the lightweight plan and focused edit path.
4. Inspect relevant code and tests before editing.
5. If wiki context is available, treat it as orientation and follow cited source paths before the `Implementation Mini-Plan`.
6. For edit paths, write the `Implementation Mini-Plan` from `LIGHTWEIGHT-PLAN.md`.
7. Use TDD-lite where feasible: RED, GREEN, REFACTOR.
8. Make minimal focused changes.
9. Run the fastest relevant checks, including the original failing check when one exists.
10. Add or update a focused regression test/check when feasible and proportional to risk.
11. If fixing a verify or clean-review failure, confirm the original failed check or cited finding was re-QA'd, list `findings_addressed`, and explain unresolved gaps.
12. If runtime/model selection is material, include `capability_status`, `selector_enforcement`, evidence layer, and Runtime mismatch status; use `unknown`, `unavailable`, or `prompt_preference` rather than silent substitution when runtime/tool evidence is absent.
13. For runtime/cache claims, name installed plugin root, source root, cache/source refresh or equivalence evidence, run scope, commands/trials, and limitations; otherwise state that runtime evidence was not refreshed and is not claimed.
14. Include a `Wiki Update Candidate` only when the implementation produced durable reusable project knowledge and the current request did not already authorize wiki maintenance. Apply `EB-WIKI-001`, `EB-ROLE-001`, and `EB-VERIFY-001` to keep that candidate advisory.
15. For child-thread, managed-worktree, subagent, or package-returning implementation, include a `Review Loop` status with `status`, `previous_review_stale_reason`, `findings_addressed`, `next_review_required`, and `next_route`.
16. In the final report, include `Scope`, `Acceptance Map`, `Evidence Inspected`, `Findings P0/P1/P2`, `Non-Readiness Boundary`, `Gaps`, and `Next Action` when the task touches implementation conformance, gated implementation, or reviewable delivery evidence.
17. Run self-review from `SELF-REVIEW.md`.
18. Report local evidence and remaining gaps, but do not claim final readiness.
19. Recommend clean review for reviewable implementation packages, then `verify` only when a readiness or evidence-sufficiency claim is in scope.

## CHECKPOINTS

- STOP before file edits unless the change is truly trivial and already fully bounded, or the inline `Implementation Mini-Plan` has five bounded lines: What/scope, Why, Files, Test, and Risk.
- STOP before fixing a suspected bug unless at least one evidence seam exists: a reproduction, a confirmed cause, a failing test/check, or a specific test seam to add. Without that seam, output only the diagnosis conclusion, confidence, and minimum modification direction.
- STOP before staging, committing, or reporting commit readiness unless the git boundary is confirmed from `skills/_shared/GIT-BOUNDARY.md`; preserve explicit pathspec staging and never use `git add .`.
- Keep the mini-plan lightweight. Do not route small scoped implementation work to `write-plan` only because these checkpoints exist.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Bug cannot be reproduced or confirmed | Stop before edits or continue only with source-level diagnosis when enough evidence exists. | Separate confirmed facts from hypotheses and state the smallest safe next check or modification direction. |
| No test seam or feasible check exists | Give a no-test justification before any edit, or stop if the behavior would be speculative. | Name the missing seam, why it is unavailable, alternate evidence, and follow-up verification. |
| Dirty worktree state is present or unclear | Inspect relevant diffs before edits and decide whether the current worktree is safe. | List intended files, unrelated dirty/untracked files, and whether edits are blocked, scoped, or require a separate topology. |
| Unrelated files appear in the diff, staged set, or intended commit | Stop staging/commit work until the boundary is explicit. | Report allowlist, denylist, `git diff --name-only`, and `git diff --cached --name-only`; leave unrelated files unstaged. |
| Acceptance criteria or scoped source truth is unclear | Stop before implementation or ask the highest-impact clarification question. | Do not infer product behavior; state what is known, what is missing, and the minimum clarification needed. |

## Do Not

- Do not use `git add .` or stage without an explicit intended pathspec allowlist.
- Do not claim done, fixed, tested, or ready without naming the checks actually run and their results.
- Do not expand scope beyond the accepted task, original failure, or user-approved fix boundary.
- Do not invent APIs, schemas, fields, lifecycle states, or runtime behavior that were not inspected or provided.
- Do not implement from wiki synthesis alone; apply `EB-WIKI-001`.
- Do not force small scoped tasks into a full `write-plan` flow when the inline lightweight plan is sufficient.

## Output Shape

```text
Implementation Summary
Scope:
Acceptance Map:
Evidence Inspected:
Findings P0/P1/P2:
Non-Readiness Boundary:
Gaps:
Next Action:
Implementation Mini-Plan
TDD-Lite / No-Test Justification
Files Changed
Checks Run
Unverified Claims
Runtime Capability:
- capability_status:
- selector_enforcement:
- Evidence layer:
- Requested runtime:
- Available runtime:
- Runtime mismatch:
- Fallback proposed:
- User approval required:
Review Loop:
- status:
- previous_review_stale_reason:
- findings_addressed:
- next_review_required:
- next_route:
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
Self-Review
Result
Remaining Gaps
Artifact Recommendation
```

## Stop Condition

Stop when the requested scoped change is implemented or blocked with evidence. Final readiness belongs to `verify` or the user.

## Gate Rule

If implementation would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, customer-visible change, or shared skill mutation, stop before execution and output Proposed Action, Target, Risk, Rollback/Undo, and Approval Needed. Do not execute until explicit user approval.

For any prompt that requests `git push`, PR creation, issue closeout, tracker mutation, deploy, publish, or other remote write, the final response must include the exact five gate field labels below even when another blocker is also present, such as missing source truth, a non-Git workspace, read-only sandbox, or missing remote permissions. Do not replace the gate with a generic "blocked" explanation.

If PR-bound implementation is requested from `main` / `master` / `trunk`, an empty branch name, detached `HEAD`, or unrelated dirty files make the current worktree unsafe, stop before edits and output:

```text
Proposed Action:
Target:
Risk:
Rollback/Undo:
Approval Needed:
Execution Topology: branch_required / worktree_required / blocked
```

Before staging, committing, or reporting commit readiness, follow `skills/_shared/GIT-BOUNDARY.md`. Never use `git add .`; require explicit pathspec staging, intended allowlist, explicit denylist, `git diff --name-only`, `git diff --cached --name-only`, and a statement of unrelated modified, untracked, or ignored files.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Do not create durable artifacts unless they are needed for execution, review, verification, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
