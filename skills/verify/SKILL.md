---
name: verify
description: Skeptically verify scope-first readiness, implementation acceptance evidence with tests/checks, source-truth, UAT/release evidence, UI evidence, git boundary, or frontend contract confidence; not for plain implementation conformance review without readiness or acceptance verification, and not for prototype contract-boundary classification.
---

# verify

## Final Report Opening Rule

The final verification report must begin with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`. Once the response enters the verification report body, the first report line must be `Verification Scope`, followed by all required scope fields, not a conclusion, findings heading, contract payload, QA payload, tool recommendation, or subagent prompt.

A bare `Verification Scope` heading is not compliant. If details are missing, keep the field and write `not provided` or `unverified`.

Brief progress or tool-use prefaces are allowed before the final report only when they do not contain a verdict, findings, customer/UAT readiness conclusion, contract conclusion, QA decision, UI tool recommendation, approval decision, or subagent prompt body.

No exception for report bodies: UI tool routing, frontend/backend contract review, QA failure handling, git-boundary review, approval gates, release readiness, and fresh-context subagent prompt preparation all start the final report with the scope block.

Short branch examples:

- UI routing report: `Verification Scope` block first, then `UI Evidence` and Browser/DevTools/Playwright choice.
- Contract review report: `Verification Scope` block first, then `Frontend Contract Review` or source-truth findings.
- Subagent review package: `Verification Scope` block first, then the fresh-context review prompt.
- QA failure report: `Verification Scope` block first, then the exact `QA Failure` block.

## Trigger Contract

Use this skill when the user asks for readiness, evidence, UAT/SIT, runtime behavior, release confidence, source-truth validation, or customer/front-end handoff verification.

Should trigger:

- "验证一下能不能给前端验"
- "这个可以给客户 UAT 吗"
- "检查一下 release readiness"
- "发布前确认证据链是否完整"
- "跑一遍证据链"
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
- The user asks to review a static prototype, HTML prototype, prototype-only fields, or prototype contract-boundary classification without source-truth verification; use `prototype`.
- The user asks to write a plan before edits; use `write-plan`.
- The user asks whether an issue is ready to start; use `triage`.
- The user asks for only PRD wording; use `to-prd`.
- The user asks for compact continuation context; use `handoff`.

## Required Evidence

Use the complete block from `SCOPE-EVIDENCE-TEMPLATE.md` as the required opening for the final verification report. The final-report opening rule above is mandatory for every verify branch.

If the requested deliverable is itself a tool recommendation, browser verification note, QA-fix-QA package, contract review note, or subagent prompt, keep the verify wrapper first: emit `Verification Scope` before the specialized payload.

Use source evidence, test output, runtime/browser evidence, data readiness, environment readiness, and UAT/customer evidence as applicable. Select the narrowest matching named lens from `LENSES.md` when the user asks for PRD review, document review, contract review, UAT review, UI review, or git boundary review.

Use implementation evidence review only when the user asks whether a finished implementation is ready, verified, releaseable, handoff-ready, or evidence-supported. For a read-only conformance review of implementation against TASK/PRD with no UAT/readiness judgment, use `implement`.

Use specialized references when they apply:

- `QA-FIX-QA.md` for failed verification or QA-to-fix-to-QA advice that needs expected/actual/reproduction/severity/diagnosis/fix/re-QA.
- `CONTRACT-DOC-REVIEW.md` for frontend-facing contract documentation.
- `UI-TOOL-ROUTER.md` for visual, responsive, interaction, browser, console, network, or scripted UI evidence.
- `skills/_shared/LIFECYCLE-STATE.md` when a verification gap, re-verify chain, UAT/SIT/release state, or cross-session decision must survive the current response.
- `skills/_shared/SUBAGENT-DELEGATION.md` for fresh-context subagent review prompts.

If a check cannot be run, mark it `unverified`. A code diff or implementation summary alone is not readiness evidence.

## Workflow

1. Start the final verification report with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`; do not put any finding, verdict, recommendation, or conclusion before that block.
2. State the named lens or lenses being used.
3. State claimed behavior before judging it.
4. Inspect source/diff/test evidence.
5. Run or report relevant checks when available.
6. Use `UI-TOOL-ROUTER.md` when visual or interaction claims matter.
7. Use `CONTRACT-DOC-REVIEW.md` when frontend-facing docs or API contract claims matter.
8. Separate data, environment, and customer/UAT readiness.
9. Map `Claim / AC -> Evidence -> Result -> Gap -> Severity`.
10. If verification fails or the user asks how to handle a QA failure, include the `QA Failure` shape from `QA-FIX-QA.md`. If concrete failure details are missing, still emit the shape and mark missing fields as `not provided` or `unverified`; do not substitute a generic process.
11. Mark missing checks as `unverified`.
12. Keep any customer-facing summary optional and secondary to engineering readiness.
13. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.
14. After the verification body, add a lifecycle state note only when `LIFECYCLE-STATE.md` thresholds are met. Never place lifecycle notes before `Verification Scope`.

## Output Shape

```text
Verification Scope
- In Scope:
- Out of Scope:
- Covered:
- Not Covered:
- Evidence Sources:
- User-visible Claim Being Verified:

QA Failure
- Expected:
- Actual:
- Reproduction:
- Severity: P0 / P1 / P2 / P3
- Minimal Diagnosis:
- Fix Plan:
- Re-QA Required:
- Regression Note:
- Scoped Next Action:

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
- Git Boundary
- UI Evidence
- Risks
- Unverified Claims
- Next Action

Lifecycle State Update
- Needed: yes / no
- Target: artifacts/<workstream-slug>/STATE.md
- Current Gap Closure:
- Re-verify Required:
- State Freshness Risk:
```

Omit the `QA Failure` block only when there is no failed verification and the user did not ask for QA -> fix -> QA handling. When it appears, keep every field; write `not provided` for missing prompt details and `unverified` for details that were not checked.

Omit the `Lifecycle State Update` block when lifecycle thresholds are not met. When it appears, keep it after the verification body.

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
