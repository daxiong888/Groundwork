---
name: verify
description: Skeptically verify scope-first readiness, frontend integration readiness, implementation acceptance evidence with tests/checks, source-truth, UAT/release evidence, UI evidence, git boundary, or frontend contract confidence. Use for no-command readiness or evidence-sufficiency prompts such as "不要运行命令", "只有 code diff 没有 runtime 或 browser evidence 这次可以算 ready 吗", and other questions about whether code diff alone without runtime or browser evidence can count as ready. Final verification reports must start with the literal line "Verification Scope" followed by the six dash-prefixed fields In Scope, Out of Scope, Covered, Not Covered, Evidence Sources, and User-visible Claim Being Verified. Do not bold, translate, rename, or replace this block. Not for plain implementation conformance review without readiness or acceptance verification, and not for prototype contract-boundary classification.
---

# verify

## Final Report Opening Rule

Runtime smoke rule: copy the required opening block literally. Do not write a prose paragraph, Chinese heading, markdown-bold heading, or bare heading before these six fields.

The final verification report must begin with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`. Once the response enters the verification report body, the first report line must be `Verification Scope`, followed by all required scope fields, not a conclusion, findings heading, contract payload, QA payload, tool recommendation, or subagent prompt.

A bare `Verification Scope` heading is not compliant. If details are missing, keep the field and write `not provided` or `unverified`.

Mandatory skeleton for every final verification report:

```text
Verification Scope
- In Scope:
- Out of Scope:
- Covered:
- Not Covered:
- Evidence Sources:
- User-visible Claim Being Verified:
```

Questions that ask whether missing evidence is enough for readiness, including code-diff-only, no-runtime-evidence, no-browser-evidence, no-command, or "can this count as ready" prompts, are verification reports. Do not answer them as a direct short judgment; start with `Verification Scope`.

Do not bold, decorate, translate, or rename the opening line. `**Verification Scope**`, `Verification Scope:`, `验证范围`, and a bare heading without the six fields are not compliant.

For code-diff-only readiness questions, use this exact opening shape before any verdict:

```text
Verification Scope
- In Scope: whether code diff alone is sufficient readiness evidence
- Out of Scope: command execution, file inspection, runtime execution, browser verification
- Covered: evidence sufficiency based on the user's stated evidence
- Not Covered: tests, runtime behavior, browser behavior, data readiness, environment readiness
- Evidence Sources: user-provided statement only
- User-visible Claim Being Verified: code diff without runtime or browser evidence can count as ready
```

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

## Required Evidence

Use the complete block from `SCOPE-EVIDENCE-TEMPLATE.md` as the required opening for the final verification report. The final-report opening rule above is mandatory for every verify branch.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` before judging readiness when lifecycle state, task state, source truth, or downstream closeout is involved. Source truth beats `STATE.md`: if lifecycle state conflicts with source code, tests, runtime evidence, accepted PRD/issue, or user-confirmed decisions, mark the state stale or insufficient and follow the canonical source.

When lifecycle state is stale or insufficient but lifecycle thresholds do not justify updating `STATE.md`, still report the stale or insufficient state under `Risks` or `Unverified Claims`.

If the requested deliverable is itself a tool recommendation, browser verification note, QA-fix-QA package, contract review note, or subagent prompt, keep the verify wrapper first: emit `Verification Scope` before the specialized payload.

Use source evidence, test output, runtime/browser evidence, data readiness, environment readiness, and UAT/customer evidence as applicable. Select the narrowest matching named lens from `LENSES.md` when the user asks for PRD review, document review, contract review, UAT review, UI review, or git boundary review.

Use implementation evidence review only when the user asks whether a finished implementation is ready, verified, releaseable, handoff-ready, or evidence-supported. For a read-only conformance review of implementation against TASK/PRD with no UAT/readiness judgment, use `implement`.

Use `skills/_shared/VISUAL-HANDOFF-PACKET.md` when the claim depends on a visual handoff packet, HTML packet, screenshot set, generated image, visual artifact, prototype output, or frontend/backend review packet. A visual packet is a communication artifact, not browser evidence, runtime evidence, UAT evidence, release evidence, customer-readiness evidence, or confirmed API/schema/source truth unless the packet names the separate qualifying evidence and `verify` inspects it.

Use `skills/_shared/ROLE-SEPARATION.md` for material readiness claims. `verify` may provide `Independent Verification Evidence` only when it begins from explicit scope and inspects or runs evidence independent from the same-session designer/implementer. If the only available evidence is same-session self-check, implementation summary, or self-run tests, block or mark the readiness claim `unverified` instead of passing it.

Use `skills/_shared/RUNTIME-CAPABILITY.md` when verifying model/runtime execution, selector enforcement, subagent or child-thread/worktree routing, runtime cache, installed plugin, marketplace, release, UAT, or customer claims. If only prompt text, package text, source diff, or implementation summary is available, mark runtime/tool and selector claims `unverified` or `not applicable`; do not claim `tool_enforced`.

Use `skills/_shared/LLM-WIKI.md` when a readiness, source-truth, contract, runtime, marketplace, installed-plugin, cache-refresh, or release claim cites a project wiki. Wiki pages are claim inventory and orientation only. Verification must inspect the cited source, authoritative artifact, test output, runtime/browser evidence, cache/source refresh evidence, or release evidence that is specific to the claim. If the wiki claim is stale, contested, uncited, page-level-source-only, glossary-only, or source-inaccessible, mark the claim `unverified`, `insufficient`, `stale_suspected`, or `blocked` and report the required next evidence.

Use `skills/_shared/COGNITIVE-BUDGET.md` when a readiness claim depends on model profile choice. Verify profile fit separately from concrete model execution, and block or mark unverified any Spark or fast-profile final-authority claim.

Use specialized references when they apply:

- `QA-FIX-QA.md` for failed verification or QA-to-fix-to-QA advice that needs expected/actual/reproduction/severity/diagnosis/fix/re-QA.
- `CONTRACT-DOC-REVIEW.md` for frontend-facing contract documentation.
- `UI-TOOL-ROUTER.md` for visual, responsive, interaction, browser, console, network, or scripted UI evidence.
- `skills/_shared/LIFECYCLE-PREFLIGHT.md` for source-truth precedence, lifecycle-state staleness, artifact promotion, and git-topology gates before readiness or closeout.
- `skills/_shared/LIFECYCLE-STATE.md` when a verification gap, re-verify chain, UAT/SIT/release state, or cross-session decision must survive the current response.
- `skills/_shared/SUBAGENT-DELEGATION.md` for fresh-context subagent review prompts.
- `skills/dispatch/COMPLEX-WORK-SEPARATION.md` when verification follows managed worktree work whose risk or scope may require separate planning, implementation, clean review, verification, and coordinator closeout roles.

For complex work separation, `verify` owns evidence sufficiency only. It may confirm whether clean review evidence is present, absent, stale, or insufficient for the claimed readiness question. It must not replace fresh clean review, perform runtime implementation, edit files, approve merge-back, archive threads, clean up branches, commit, push, open PRs, mutate trackers, or close the task directly.

When a P1, public API, migration, schema, security, privacy, auth, permissions, data correctness, shared contract, package schema, adapter contract, state machine, weak-validation, or multi-package change reaches `verify` without fresh clean review evidence, mark the clean review claim `unverified` or `blocked` instead of issuing a readiness `pass`.

Small, low-risk tasks with clear current evidence may still receive lightweight verification. Do not require clean review ceremony when the separation thresholds are not met.

When verifying a `native_closeout_package`, treat merge readiness and cleanup decisions as separate claims:

- reject or mark blocked any `merge_decision.recommendation: merge` when `evidence_summary` is empty or missing;
- reject or mark blocked any `merge_decision.recommendation: merge` when `git_boundary_status.status_checked` is not true or `git_boundary_status.safe_to_stage_or_merge` is not true;
- reject or mark blocked any `merge_decision.recommendation: merge` when intended files, unrelated dirty files, staged files, or explicit denylist evidence is missing from `git_boundary_status`;
- reject or mark blocked any `merge_decision.recommendation: merge` when `review_findings_status` is not `passed`;
- reject or mark blocked any `merge_decision.recommendation: merge` when `merge_decision.merge_source` is `none`, `unknown`, empty, missing, or lacks source evidence;
- verify that `merge_decision.merge_source` uses only `patch_bundle`, `visible_branch`, `codex_handoff`, `pathspec_checkout`, `none`, or `unknown`;
- verify that `cleanup_decision.thread_action`, `cleanup_decision.worktree_action`, and `cleanup_decision.branch_action` are separate fields and are not represented as merge recommendations;
- do not treat archive, worktree retention, Codex-managed cleanup, or branch cleanup as merge readiness evidence;
- do not claim thread archive, worktree cleanup, branch deletion, runtime execution, cache refresh, release readiness, or UAT readiness unless the package includes direct evidence for that specific claim.

When verifying runtime, cache, release, UAT, marketplace, or cache-refresh claims, require a `release_evidence_claim` object for each material claim:

```yaml
release_evidence_claim:
  claim_type: runtime | cache | release | uat | marketplace | cache_refresh | not_applicable
  claim: ""
  evidence_status: verified | unverified | not_applicable
  installed_plugin_root: ""
  source_root: ""
  cache_or_source_refresh:
    method: refresh_step | source_equivalence | not_run | not_applicable
    evidence: ""
  run_scope: targeted | full | not_run | not_applicable
  commands_or_trials: []
  limitations: []
```

- Documentation, schema, fixture, PRD, or issue-pack edits alone must set runtime, cache, release, UAT, marketplace, and cache-refresh evidence to `unverified` or `not_applicable`.
- A `verified` runtime or cache claim must name the installed plugin root, source root, cache/source refresh or equivalence method, run scope, commands or trials, and limitations.
- Release readiness is not inferred from PRD acceptance, issue-pack completion, fixture pass, package completeness, or clean review alone; it requires separate release-gate evidence.
- Codex App Handoff execution evidence is separate from Groundwork package/schema evidence and must be represented as commands or trials before it can support a release or handoff-readiness claim.

If a check cannot be run, mark it `unverified`. A code diff or implementation summary alone is not readiness evidence.

When the user forbids running commands, browser checks, or file inspection, still emit the full `Verification Scope` block first. Treat the requested readiness claim as an evidence sufficiency check, put the forbidden checks under `Not Covered`, and mark missing runtime/browser/test evidence as `unverified` instead of answering with a direct no-scope summary.

A `verify` verdict does not directly close a task. After the verification body, recommend the next task-state action:

- `triage closeout` when verdict is `pass` and no material gap remains.
- `gap closure` when verdict is `partial` or `fail` and a scoped fix direction exists.
- `re-verify` when a fix or evidence update must be checked again.
- `blocked needs-info` when missing evidence prevents a readiness judgment.

Never place task-state recommendations before the required `Verification Scope` block.

## CHECKPOINTS

- STOP before any verdict unless `Verification Scope` includes concrete `Covered`, `Not Covered`, and `Evidence Sources` fields.
- STOP before claiming `pass`, readiness, UAT, release, or handoff confidence unless fresh in-scope evidence has been inspected or run.
- If only source, doc, diff, summary, or historical evidence is available, state that evidence boundary and do not upgrade it into runtime, browser, data, environment, or UAT evidence.
- If only a visual handoff packet, HTML packet, screenshot, generated image, visual artifact, or prototype output is available, classify it as communication artifact evidence only and do not upgrade it into source/API, browser, runtime, UAT, release, customer-readiness, or final readiness evidence.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Evidence is missing | Mark the claim `unverified` or `blocked`. | Put the missing evidence in `Not Covered`, `Gap`, or `Unverified Claims`; no `pass`. |
| Evidence conflicts | Name the conflict and separate source, diff, test, runtime, and user-provided claims. | Do not choose a readiness verdict until the canonical source is clear. |
| Tests were not run | Report tests as not run. | Do not claim test-backed behavior passed. |
| UI tool choice does not match the claim | Use `UI-TOOL-ROUTER.md` or mark UI evidence `unverified`. | Do not claim visual, responsive, interaction, console, or network evidence from the wrong tool. |
| UAT/customer readiness is claimed without runtime evidence | Separate source, test, runtime/browser, data, environment, and UAT/customer readiness. | Do not give UAT/customer `pass` without the required runtime and readiness evidence. |
| Visual packet output is treated as browser/runtime/UAT/release evidence | Reclassify it as a communication artifact and inspect only separately named qualifying evidence. | Mark browser/runtime/UAT/release/customer-readiness claims `unverified` unless actual evidence is produced and named. |
| Mock fields from a visual packet are treated as confirmed API/schema truth | Reclassify them as `mock / illustrative / not backend contract` or `proposed contract hypothesis`. | Route source/API/schema confirmation to source inspection or mark the claim `unverified`. |

## Do Not

- Do not use a user summary, implementation summary, changelog, issue comment, or old handoff as evidence unless it is explicitly labeled as the claim being checked.
- Do not treat a diff summary, old test run, or stale runtime note as current readiness evidence.
- Do not treat wiki synthesis, wiki audits, wiki page-level source lists, stale wiki claims, uncited wiki claims, or external graph/search/index output as source truth, verification pass evidence, release evidence, UAT evidence, marketplace evidence, installed-plugin evidence, or cache-refresh evidence.
- Do not issue a review verdict before declaring scope, coverage, and evidence sources.
- Do not hide source/doc-only or no-command boundaries in prose after the verdict.
- Do not treat visual handoff packets, screenshots, generated images, HTML packets, or prototype output as browser evidence, runtime evidence, UAT evidence, release evidence, or confirmed API/schema/source truth by themselves.

## Workflow

1. Start the final verification report with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`; do not put any finding, verdict, recommendation, or conclusion before that block.
2. State the named lens or lenses being used.
3. State claimed behavior before judging it.
4. Run lifecycle preflight when `STATE.md`, task-state, source-truth, UAT/release, or closeout claims are in scope.
5. Inspect source/diff/test evidence; do not pass readiness from `STATE.md` alone.
6. Run or report relevant checks when available.
7. Use `UI-TOOL-ROUTER.md` when visual or interaction claims matter.
8. Use `CONTRACT-DOC-REVIEW.md` when frontend-facing docs or API contract claims matter.
9. Separate data, environment, and customer/UAT readiness.
10. For visual packets, map packet sections, `Mock vs Confirmed`, `Do Not Implement / Do Not Assume`, and `Evidence Boundary` before judging any readiness claim.
11. Map `Claim / AC -> Evidence -> Result -> Gap -> Severity`.
12. For runtime/model claims, map `capability_status`, `selector_enforcement`, evidence layer, Runtime mismatch, and runtime/cache refresh evidence to the claim. Prompt preference alone cannot satisfy `tool_enforced`.
13. If verification fails or the user asks how to handle a QA failure, include the `QA Failure` shape from `QA-FIX-QA.md`. If concrete failure details are missing, still emit the shape and mark missing fields as `not provided` or `unverified`; do not substitute a generic process. Do not update a failure verdict to `pass` until the original reproduction/check has been re-QA'd.
14. Mark missing checks as `unverified`.
15. Keep any customer-facing summary optional and secondary to engineering readiness.
16. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.
17. Add a task-state recommendation after the verification body.
18. After the verification body, add a lifecycle state note only when `LIFECYCLE-STATE.md` thresholds are met. Never place lifecycle notes before `Verification Scope`.

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
- Gap Closure Plan:
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
- Runtime Capability:
  - capability_status:
  - selector_enforcement:
  - Evidence layer:
  - Requested runtime:
  - Available runtime:
  - Runtime mismatch:
  - Fallback proposed:
  - User approval required:
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
- UI Evidence
- Visual Packet Evidence Boundary
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

Omit the `QA Failure` block only when there is no failed verification and the user did not ask for QA -> fix -> QA handling. When it appears, keep every field; write `not provided` for missing prompt details and `unverified` for details that were not checked. Use `skills/_shared/SEVERITY.md`; `none` is invalid inside `QA Failure` because the block exists only for failed or blocked verification.

Keep `Task State Recommendation` after the verification body. Omit it only when the user requested a specialized payload that cannot include task-state guidance without expanding scope; in that case, put the task-state gap in `Next Action`.

Omit the `Lifecycle State Update` block when lifecycle thresholds are not met. When it appears, keep it after the verification body and after the task-state recommendation.

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
