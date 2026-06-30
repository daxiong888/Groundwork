---
name: verify
description: Use when skeptically verifying scope-first readiness, frontend integration readiness, implementation acceptance evidence with tests/checks, source-truth, UAT/release evidence, UI evidence, git boundary, or frontend contract confidence. Use for no-command readiness or evidence-sufficiency prompts such as "不要运行命令", "只有 code diff 没有 runtime 或 browser evidence 这次可以算 ready 吗", and other questions about whether code diff alone without runtime or browser evidence can count as ready. Do not use for plain implementation conformance review without readiness or acceptance verification, and do not use for prototype contract-boundary classification. Final verification reports must start with the literal line "Verification Scope" followed by the six dash-prefixed fields In Scope, Out of Scope, Covered, Not Covered, Evidence Sources, and User-visible Claim Being Verified. Do not bold, translate, rename, or replace this block.
---

# verify

## Final Report Opening Rule

Runtime smoke rule: every final verification report begins with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`. Do not bold, decorate, translate, rename, or replace the opening line.

Load `SCOPE-EVIDENCE-TEMPLATE.md` before producing any verification report body. Branch-specific payloads such as scope-first evidence sufficiency, QA failure, UI evidence, release evidence, contract review, git boundary, approval gates, or subagent prompts come after the scope block and require only the matching Branch Index reference.

## Trigger Contract

Use this skill when the user asks for readiness, evidence, UAT/SIT, runtime behavior, release confidence, source-truth validation, or customer/front-end handoff verification.

Should trigger:

- "验证一下能不能给前端验"
- "验证当前实现是否 ready 给前端联调"
- "验证当前 fixture 是否 ready 给前端联调"
- "这个可以给客户 UAT 吗"
- "检查一下 release readiness"
- "发布前确认证据链是否完整"
- "跑一遍证据链"
- "只有 code diff 没有 runtime 或 browser evidence 这次可以算 ready 吗"
- "不要运行命令，只判断现有证据能不能算 ready"
- "确认这次实现是否真的生效"
- "验证 TASK.md 的实现是否满足验收"
- "验证 PRD/TASK 的实现是否满足验收"
- "review 这个 PRD 的验收是否够清楚"
- "做一次 git boundary review"
- "验证这份前端联调文档是否符合后端事实"
- "验证失败后给我 QA -> fix -> QA 处理建议"
- "确认这个 UI 验证该用 Browser 还是 DevTools"
- "验证这个 UI 原型的浏览器行为。说明该用 Browser 还是 DevTools 还是 Playwright。"
- "给子代理准备一个 fresh context review prompt"
- "准备让子代理 review 这次实现。生成 prompt 但不要让子代理改文件。"

Should not trigger:

- The user asks to implement code; use `implement`.
- The user asks to review whether an implementation conforms to a task or PRD, especially when they explicitly exclude UAT/readiness; use `implement`.
- The user asks for code-quality review only, with no acceptance, readiness, or evidence claim; use `implement` or direct review.
- The user asks to review a static prototype, HTML prototype, prototype-only fields, or prototype contract-boundary classification without source-truth verification; use `prototype`.
- The user asks to write a plan before edits; use `write-plan`.
- The user asks whether an issue is ready to start; use `triage`.
- The user asks for only PRD wording; use `to-prd`.
- The user asks for compact continuation context; use `handoff`.
- "按这个任务直接实现"; use `implement`.
- "review 这次实现是否符合 TASK.md，但不要判断 ready/UAT"; use `implement`.
- "这个 issue 能不能给 agent 做"; use `triage`.
- "查项目 wiki 里之前怎么决定的"; use `wiki`.
- "给下个 session 做 handoff"; use `handoff`.

## Required Evidence

Use the complete block from `SCOPE-EVIDENCE-TEMPLATE.md` as the required opening for the final verification report. The final-report opening rule above is mandatory for every verify branch.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/NON-EXECUTOR-BOUNDARY.md` before judging execution, closeout, runtime, cache, release, UAT, customer, thread, subagent, worktree, handoff, branch deletion, or remote mutation claims. Verify reports evidence sufficiency and recommends next task-state action; it does not perform those actions.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` before judging readiness when lifecycle state, task state, source truth, or downstream closeout is involved. Source truth beats `STATE.md`: if lifecycle state conflicts with source code, tests, runtime evidence, accepted PRD/issue, or user-confirmed decisions, mark the state stale or insufficient and follow the canonical source.

When lifecycle state is stale or insufficient but lifecycle thresholds do not justify updating `STATE.md`, still report the stale or insufficient state under `Risks` or `Unverified Claims`.

If the requested deliverable is itself a tool recommendation, browser verification note, QA-fix-QA package, contract review note, or subagent prompt, keep the verify wrapper first: emit `Verification Scope` before the specialized payload.

Use source evidence, test output, runtime/browser evidence, data readiness, environment readiness, and UAT/customer evidence as applicable. Select the narrowest matching named lens from `LENSES.md` when the user asks for PRD review, document review, contract review, UAT review, UI review, or git boundary review.

Use implementation evidence review only when the user asks whether a finished implementation is ready, verified, releaseable, handoff-ready, or evidence-supported. For a read-only conformance review of implementation against TASK/PRD with no UAT/readiness judgment, use `implement`.

Apply `EB-VISUAL-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` and use `skills/_shared/VISUAL-HANDOFF-PACKET.md` when the claim depends on a visual handoff packet, HTML packet, screenshot set, generated image, visual artifact, prototype output, or frontend/backend review packet. Skill-specific delta: verify may inspect separately named qualifying evidence for the specific stronger claim.

Apply `EB-ROLE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` and use `skills/_shared/ROLE-SEPARATION.md` for material readiness claims. Skill-specific delta: `verify` may provide `Independent Verification Evidence` only when it begins from explicit scope and inspects or runs evidence independent from the same-session designer/implementer; otherwise block or mark the readiness claim `unverified`.

Apply `EB-RUNTIME-001` and `EB-CACHE-001` from `skills/_shared/EVIDENCE-BOUNDARY.md`, and use `skills/_shared/RUNTIME-CAPABILITY.md` when verifying model/runtime execution, selector enforcement, subagent or child-thread/worktree routing, runtime cache, installed plugin, marketplace, release, UAT, or customer claims. Skill-specific delta: if only non-runtime evidence is available, mark runtime/tool and selector claims `unverified` or `not applicable`.

Apply `EB-WIKI-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` and use `skills/_shared/LLM-WIKI.md` when a readiness, source-truth, contract, runtime, marketplace, installed-plugin, cache-refresh, or release claim cites a project wiki. Skill-specific delta: verification must inspect the cited qualifying evidence for the specific claim or mark the claim `unverified`, `insufficient`, `stale_suspected`, or `blocked`.

Use `skills/_shared/COGNITIVE-BUDGET.md` when a readiness claim depends on model profile choice. Verify profile fit separately from concrete model execution, and block or mark unverified any Spark or fast-profile final-authority claim.

Use specialized references only when the active branch needs them:

- Scope-first / code-diff-only / no-command readiness: `VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md`.
- Failed verification or QA -> fix -> QA advice: `QA-FAILURE-BRANCH.md` and `QA-FIX-QA.md`.
- Runtime/model selection, selector enforcement, runtime mismatch, subagent/child-thread/worktree routing, or runtime/tool capability claims: `RUNTIME-CAPABILITY-BRANCH.md` and `skills/_shared/RUNTIME-CAPABILITY.md`.
- Runtime cache, marketplace, installed-plugin, UAT, customer, cache-refresh, or release claims: `RELEASE-READINESS-BRANCH.md` and `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`.
- Native closeout package, merge readiness, cleanup separation, or closeout git-boundary claims: `NATIVE-CLOSEOUT-BRANCH.md`.
- Visual, responsive, interaction, browser, console, network, or scripted UI evidence: `UI-READINESS-BRANCH.md` and `UI-TOOL-ROUTER.md`.
- Fresh-context subagent review prompts: `SUBAGENT-REVIEW-BRANCH.md` and `skills/_shared/SUBAGENT-DELEGATION.md`.
- Frontend-facing contract documentation: `CONTRACT-DOC-REVIEW.md`.
- Managed-worktree or complex role separation: `skills/dispatch/COMPLEX-WORK-SEPARATION.md`.
- Cross-session verification gap or release/UAT state: `skills/_shared/LIFECYCLE-STATE.md`.

For complex work separation, `verify` owns evidence sufficiency only. It may confirm whether clean review evidence is present, absent, stale, or insufficient for the claimed readiness question. Fresh clean review, runtime implementation, edits, merge-back approval, archives, branch cleanup, commits, pushes, PRs, tracker mutation, and task closeout remain separate owner/tool actions.

When a P1, public API, migration, schema, security, privacy, auth, permissions, data correctness, shared contract, package schema, adapter contract, state machine, weak-validation, or multi-package change reaches `verify` without fresh clean review evidence, mark the clean review claim `unverified` or `blocked` instead of issuing a readiness `pass`.

Small, low-risk tasks with clear current evidence may still receive lightweight verification. Do not require clean review ceremony when the separation thresholds are not met.

For native closeout, runtime, cache, release, UAT, marketplace, installed-plugin, or cache-refresh claims, load the matching branch files from the Branch Index and apply the owning shared evidence contracts before issuing a verdict.

If a check cannot be run, mark it `unverified`. Apply `EB-VERIFY-001` when only code diff, implementation summary, source-validation checks, or old evidence is available.

When the user forbids running commands, browser checks, or file inspection, still emit the full `Verification Scope` block first. Treat the requested readiness claim as an evidence sufficiency check, put the forbidden checks under `Not Covered`, and mark missing runtime/browser/test evidence as `unverified` instead of answering with a direct no-scope summary.

A `verify` verdict does not directly close a task. After the verification body, recommend the next task-state action:

- `triage closeout` when verdict is `pass` and no material gap remains.
- `gap closure` when verdict is `partial` or `fail` and a scoped fix direction exists.
- `re-verify` when a fix or evidence update must be checked again.
- `blocked needs-info` when missing evidence prevents a readiness judgment.

Never place task-state recommendations before the required `Verification Scope` block.

## Evidence Search Boundary

Default verification is claim-scoped, not repository-wide evidence archaeology.

Start from:

- the user-visible claim being verified;
- user-provided evidence or paths;
- current workspace source, diff, tests, or check output relevant to that claim;
- current runtime or browser evidence when the user asks for runtime, browser, or readiness;
- current installed plugin cache or local `dist/` only when the claim explicitly concerns plugin install, cache, marketplace, package, or release readiness.

Do not default to:

- `evals/baselines/`;
- `artifacts/`;
- `research/`;
- `examples/`;
- historical release notes;
- old handoffs;
- old runtime trials;
- broad `docs/prd-v*` archaeology;
- repo-wide `rg` across historical materials.

Historical baselines may orient investigation only when the user explicitly asks for historical, eval, baseline, release-evidence, or Groundwork-maintainer evidence, or when a current source artifact cites a specific baseline path.

If current `dist/`, installed cache, runtime/browser evidence, or user-provided evidence is missing, report the gap under `Not Covered`, `Unverified Claims`, or `blocked needs-info`; do not compensate by sweeping historical materials.

## Active Verify Modes

Pick the lightest mode that can answer the user's claim.

### `verify-lite`

Trigger: no-command prompts, code-diff-only sufficiency questions, or "现有证据够不够" questions.

Reads: the user claim plus provided/current evidence only.

Output: `Verification Scope` followed by a compact evidence-sufficiency verdict.

Boundary: no historical search.

### `verify-standard`

Trigger: implementation acceptance, TASK/PRD conformance with a readiness or evidence claim, or ordinary verification after a scoped change.

Reads: the task or PRD, source, diff, tests, checks, and current named task artifacts that are directly relevant to the claim.

Output: `Verification Scope` followed by `Claim / AC -> Evidence -> Result -> Gap`.

Boundary: no historical baseline search unless the current source artifact cites it or the user asks for historical/eval/baseline evidence.

### `verify-strict`

Trigger: release, UAT, customer, runtime, cache, marketplace, installed-plugin, selector enforcement, or package-readiness claims.

Reads: strict branch references and current qualifying runtime, cache, release, UAT, marketplace, installed-plugin, selector, or package evidence for the specific claim.

Output: `Verification Scope` plus the strict branch payload and explicit missing-evidence handling.

Boundary: historical baselines are allowed only when explicitly requested or cited by a current source artifact; they do not replace current qualifying evidence.

## CHECKPOINTS

- STOP before any verdict unless `Verification Scope` includes concrete `Covered`, `Not Covered`, and `Evidence Sources` fields.
- STOP before claiming `pass`, readiness, UAT, release, or handoff confidence unless fresh in-scope evidence has been inspected or run.
- If only source, doc, diff, summary, or historical evidence is available, state that evidence boundary and do not upgrade it into runtime, browser, data, environment, or UAT evidence.
- If only a visual handoff packet, HTML packet, screenshot, generated image, visual artifact, or prototype output is available, apply `EB-VISUAL-001`.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Evidence is missing | Mark the claim `unverified` or `blocked`. | Put the missing evidence in `Not Covered`, `Gap`, or `Unverified Claims`; no `pass`. |
| Evidence conflicts | Name the conflict and separate source, diff, test, runtime, and user-provided claims. | Do not choose a readiness verdict until the canonical source is clear. |
| Tests were not run | Report tests as not run. | Do not claim test-backed behavior passed. |
| UI tool choice does not match the claim | Use `UI-TOOL-ROUTER.md` or mark UI evidence `unverified`. | Do not claim visual, responsive, interaction, console, or network evidence from the wrong tool. |
| UAT/customer readiness is claimed without runtime evidence | Separate source, test, runtime/browser, data, environment, and UAT/customer readiness. | Do not give UAT/customer `pass` without the required runtime and readiness evidence. |
| Visual packet output is treated as browser/runtime/UAT/release evidence | Apply `EB-VISUAL-001` and inspect only separately named qualifying evidence. | Mark stronger claims `unverified` unless actual evidence is produced and named. |
| Mock fields from a visual packet are treated as confirmed API/schema truth | Reclassify them as `mock / illustrative / not backend contract` or `proposed contract hypothesis`. | Route source/API/schema confirmation to source inspection or mark the claim `unverified`. |

## Do Not

- Do not use a user summary, implementation summary, changelog, issue comment, or old handoff as evidence unless it is explicitly labeled as the claim being checked.
- Apply `EB-VERIFY-001` before using diff summaries, old test runs, or stale runtime notes for readiness.
- Apply `EB-WIKI-001` before using wiki synthesis, audits, page-level source lists, stale claims, uncited claims, or external graph/search/index output.
- Do not issue a review verdict before declaring scope, coverage, and evidence sources.
- Do not hide source/doc-only or no-command boundaries in prose after the verdict.
- Apply `EB-VISUAL-001` before using visual handoff packets, screenshots, generated images, HTML packets, or prototype output.

## Workflow

1. Start the final verification report with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`; do not put any finding, verdict, recommendation, or conclusion before that block.
2. State the named lens or lenses being used.
3. State claimed behavior before judging it.
4. Run lifecycle preflight when `STATE.md`, task-state, source-truth, UAT/release, or closeout claims are in scope.
5. Choose `verify-lite`, `verify-standard`, or `verify-strict` and apply the Evidence Search Boundary before expanding file reads.
6. Inspect source/diff/test evidence; do not pass readiness from `STATE.md` alone.
7. Run or report relevant checks when available.
8. Load the branch file only for the active branch from the Branch Index below.
9. Separate data, environment, and customer/UAT readiness.
10. Map `Claim / AC -> Evidence -> Result -> Gap -> Severity`.
11. For runtime/model claims, map `capability_status`, `selector_enforcement`, evidence layer, Runtime mismatch, and runtime/cache refresh evidence to the claim. Prompt preference alone cannot satisfy `tool_enforced`.
12. Mark missing checks as `unverified`.
13. Keep any customer-facing summary optional and secondary to engineering readiness.
14. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.
15. Add a task-state recommendation after the verification body.
16. After the verification body, add a lifecycle state note only when `LIFECYCLE-STATE.md` thresholds are met. Never place lifecycle notes before `Verification Scope`.

## Output Shape

```text
Verification Scope
- In Scope:
- Out of Scope:
- Covered:
- Not Covered:
- Evidence Sources:
- User-visible Claim Being Verified:

Verification Summary
- Lens
- Verdict: pass / partial / fail / blocked
- Claimed Behavior
- Claim / AC -> Evidence -> Result -> Gap -> Severity
- Source Evidence
- Test Evidence
- Runtime / Browser Evidence
- Data Readiness
- Environment Readiness
- Customer / UAT Readiness
- Role:
- Design Source:
- Self-check Evidence:
- Clean Review Evidence:
- Independent Verification Evidence:
- Runtime Evidence:
- Browser Evidence:
- UAT Evidence:
- Release Evidence:
- Readiness Boundary:
- Required Next Independent Role:
- Git Boundary
- Optional Branch Payloads:
- Risks
- Unverified Claims
- Next Action

Task State Recommendation
- Next Task-State Action: triage closeout / gap closure / re-verify / blocked needs-info
- Reason:
- Evidence Needed Before Closeout:
- Suggested Triage Input:

Lifecycle State Update
- Needed: yes / no
- Target: artifacts/<workstream-slug>/STATE.md
- Current Gap Closure:
- Re-verify Required:
- State Freshness Risk:
```

Omit the `QA Failure` block unless there is a failed verification or the user asked for QA -> fix -> QA handling. Load `QA-FAILURE-BRANCH.md` before emitting that block.

Keep `Task State Recommendation` after the verification body. Omit it only when the user requested a specialized payload that cannot include task-state guidance without expanding scope; in that case, put the task-state gap in `Next Action`.

Omit the `Lifecycle State Update` block when lifecycle thresholds are not met. When it appears, keep it after the verification body and after the task-state recommendation.

## Branch Index

- Scope-first / no-command / code-diff-only evidence sufficiency: `VERIFY-SCOPE.md`.
- QA failure or QA -> fix -> QA advice: `QA-FAILURE-BRANCH.md`.
- Runtime/cache/release/UAT/customer/marketplace/installed-plugin readiness: `RELEASE-READINESS-BRANCH.md`.
- Runtime/model selector, capability, or mismatch claims: `RUNTIME-CAPABILITY-BRANCH.md`.
- Native closeout package, merge readiness, cleanup separation, or closeout git-boundary claims: `NATIVE-CLOSEOUT-BRANCH.md`.
- Browser-visible, responsive, interaction, visual, console, or network evidence: `UI-READINESS-BRANCH.md`.
- Fresh-context subagent review prompt preparation: `SUBAGENT-REVIEW-BRANCH.md`.
- Frontend-facing contract documentation: `CONTRACT-DOC-REVIEW.md`.
- Lifecycle or named review lens selection: `LENSES.md`.

## Stop Condition

Stop when evidence supports a verdict or the blocking missing evidence is explicit.

## Gate Rule

If verification would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, stop before execution and output Proposed Action, Target, Risk, Rollback/Undo, and Approval Needed. Do not execute until explicit user approval.

Before git-boundary review, staging, or commit-related verification, follow `skills/_shared/GIT-BOUNDARY.md`. Never approve `git add .`; require explicit pathspec staging and a statement of unrelated modified, untracked, or ignored files.

Before delegating a review to a subagent, use `skills/_shared/SUBAGENT-DELEGATION.md`. The subagent must receive fresh context, must not rely on parent session history, and must not expand scope or modify files unless explicitly delegated.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Write verification artifacts only when they are needed for UAT/SIT, release, review, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
