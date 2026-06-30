---
name: verify
description: Use when skeptically verifying scope-first readiness, frontend integration readiness, implementation acceptance evidence with tests/checks, source-truth, UAT/release evidence, UI evidence, git boundary, or frontend contract confidence. Do not use for plain implementation conformance review without readiness or acceptance verification, and do not use for prototype contract-boundary classification. Final verification reports must start with the literal line "Verification Scope" followed by the six dash-prefixed fields In Scope, Out of Scope, Covered, Not Covered, Evidence Sources, and User-visible Claim Being Verified.
---

# verify

## Use When

Use this skill when the user asks for readiness, evidence sufficiency, UAT/SIT, runtime behavior, release confidence, source-truth validation, customer/front-end handoff verification, git-boundary review, QA failure handling, UI evidence/tool choice, or fresh-context review prompt preparation.

Examples:

- "验证一下能不能给前端验"
- "这个可以给客户 UAT 吗"
- "检查一下 release readiness"
- "只有 code diff 没有 runtime 或 browser evidence 这次可以算 ready 吗"
- "不要运行命令，只判断现有证据能不能算 ready"
- "验证 PRD/TASK 的实现是否满足验收"
- "做一次 git boundary review"
- "验证失败后给我 QA -> fix -> QA 处理建议"
- "给子代理准备一个 fresh context review prompt"

## Do Not Use When

- The user asks to implement or fix code; use `implement`.
- The user asks for implementation conformance review while explicitly excluding readiness/UAT; use `implement`.
- The user asks for code-quality review only, with no acceptance, readiness, or evidence claim; use `implement` or direct review.
- The user asks about a static prototype or prototype contract-boundary classification without source-truth verification; use `prototype`.
- The user asks for a plan before edits; use `write-plan`.
- The user asks whether an issue is ready to start; use `triage`.
- The user asks for compact continuation context; use `handoff`.
- The user asks to query durable wiki knowledge; use `wiki`.

## Runtime Mode Router

Pick the lightest mode that can answer the claim.

- `verify-lite`: no-command prompts, code-diff-only sufficiency questions, or "现有证据够不够" questions. Read only the user claim plus provided/current evidence. Load `VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md`.
- `verify-standard`: implementation acceptance, TASK/PRD conformance with readiness/evidence claims, or ordinary verification after a scoped change. Inspect the task/PRD, source, diff, tests, checks, and current named artifacts directly relevant to the claim.
- `verify-strict`: release, UAT, customer, runtime, cache, marketplace, installed-plugin, selector enforcement, or package-readiness claims. Load only the matching strict branch reference and inspect current qualifying evidence.

Historical baselines are allowed only when the user explicitly asks for historical/eval/baseline/release evidence or a current source artifact cites a specific historical path. They do not replace current qualifying evidence.

## Minimal Evidence Boundary

Default verification is claim-scoped, not repository-wide evidence archaeology.

Start from the user-visible claim, user-provided evidence or paths, current workspace source/diff/tests/check output relevant to that claim, current runtime/browser evidence when requested, and current installed cache or local `dist/` only when the claim concerns plugin install, cache, marketplace, package, or release readiness.

Do not default to `evals/baselines/`, `artifacts/`, `research/`, `examples/`, historical release notes, old handoffs, old runtime trials, or broad `docs/prd-v*` archaeology.

Apply shared evidence contracts only when the active claim needs them:

- `skills/_shared/NON-EXECUTOR-BOUNDARY.md` for execution, closeout, runtime, cache, release, UAT, customer, thread, subagent, worktree, handoff, branch deletion, or remote mutation claims.
- `skills/_shared/LIFECYCLE-PREFLIGHT.md` for lifecycle state, source truth, UAT/release, or closeout claims.
- `skills/_shared/EVIDENCE-BOUNDARY.md` for visual, role-separation, runtime/cache, wiki, release, or verify evidence boundaries.
- `skills/_shared/RUNTIME-CAPABILITY.md`, `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, `skills/_shared/ROLE-SEPARATION.md`, `skills/_shared/LLM-WIKI.md`, `skills/_shared/COGNITIVE-BUDGET.md`, or `skills/_shared/VISUAL-HANDOFF-PACKET.md` only when the branch depends on that evidence type.

## Required Output

Every final verification report starts with the complete six-field block from `SCOPE-EVIDENCE-TEMPLATE.md`. The first line is exactly:

```text
Verification Scope
```

Do not bold, decorate, translate, rename, or replace that opening block. Specialized payloads come after it.

Use this compact body unless a branch reference requires more:

```text
Verification Summary
- Lens:
- Verdict: pass / partial / fail / blocked
- Claimed Behavior:
- Claim / AC -> Evidence -> Result -> Gap -> Severity:
- Source Evidence:
- Test Evidence:
- Runtime / Browser Evidence:
- Data Readiness:
- Environment Readiness:
- Customer / UAT Readiness:
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

Risks
Unverified Claims
Next Action
```

Task-state recommendations come after the verification body: `triage closeout`, `gap closure`, `re-verify`, or `blocked needs-info`.

## Stop Conditions

- Stop before any verdict unless `Verification Scope` has concrete `Covered`, `Not Covered`, and `Evidence Sources` fields.
- Stop before claiming `pass`, readiness, UAT, release, or handoff confidence unless fresh in-scope evidence has been inspected or run.
- If only source, doc, diff, summary, or historical evidence is available, state that evidence boundary and do not upgrade it into runtime, browser, data, environment, UAT, release, or customer evidence.
- If evidence conflicts, name the conflict and separate source, diff, test, runtime, and user-provided claims before choosing a verdict.
- If checks cannot be run, mark them `unverified`; do not claim test-backed or runtime-backed behavior passed.

## Reference Loading Rules

Load only the reference matching the active branch.

- Scope-first / no-command / code-diff-only: `VERIFY-SCOPE.md` and `SCOPE-EVIDENCE-TEMPLATE.md`.
- QA failure or QA -> fix -> QA advice: `QA-FAILURE-BRANCH.md` and `QA-FIX-QA.md`.
- Runtime/model selector, capability, or mismatch claims: `RUNTIME-CAPABILITY-BRANCH.md` and `skills/_shared/RUNTIME-CAPABILITY.md`.
- Runtime/cache/release/UAT/customer/marketplace/installed-plugin readiness: `RELEASE-READINESS-BRANCH.md` and `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`.
- Native closeout, merge readiness, cleanup separation, or closeout git-boundary claims: `NATIVE-CLOSEOUT-BRANCH.md`.
- Browser-visible, responsive, interaction, visual, console, or network evidence: `UI-READINESS-BRANCH.md` and `UI-TOOL-ROUTER.md`.
- Fresh-context subagent review prompts: `SUBAGENT-REVIEW-BRANCH.md` and `skills/_shared/SUBAGENT-DELEGATION.md`.
- Frontend-facing contract documentation: `CONTRACT-DOC-REVIEW.md`.
- Lifecycle or named review lens selection: `LENSES.md`.
- Full branch workflow, failure handling, and optional lifecycle blocks: `VERIFY-ROUTER-BRANCHES.md`.

## Gate Rule

If verification would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, stop before execution and output `Proposed Action`, `Target`, `Risk`, `Rollback/Undo`, and `Approval Needed`.

Before git-boundary review, staging, or commit-related verification, follow `skills/_shared/GIT-BOUNDARY.md`. Never approve `git add .`.

## Artifact Rule

Write verification artifacts only when they are needed for UAT/SIT, release, review, or handoff. New or materially updated durable artifacts must follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`. Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows.
