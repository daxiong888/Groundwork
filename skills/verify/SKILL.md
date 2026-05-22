---
name: verify
description: Skeptically verify scope-first readiness evidence using review lenses for PRD docs contracts code UI UAT git boundary or release confidence.
---

# verify

## Trigger Contract

Use this skill when the user asks for readiness, evidence, UAT/SIT, runtime behavior, release confidence, or customer/front-end handoff verification.

Should trigger:

- "验证一下能不能给前端验"
- "这个可以给客户 UAT 吗"
- "检查一下 release readiness"
- "发布前确认证据链是否完整"
- "跑一遍证据链"
- "确认这次实现是否真的生效"
- "review 这个 PRD 的验收是否够清楚"
- "做一次 git boundary review"
- "验证这份前端联调文档是否符合后端事实"

Should not trigger:

- The user asks to implement code; use `implement`.
- The user asks to write a plan before edits; use `write-plan`.
- The user asks whether an issue is ready to start; use `triage`.
- The user asks for only PRD wording; use `to-prd`.
- The user asks for compact continuation context; use `handoff`.

## Required Evidence

Start with `SCOPE-EVIDENCE-TEMPLATE.md`. Use source evidence, test output, runtime/browser evidence, data readiness, environment readiness, and UAT/customer evidence as applicable. Select the narrowest matching named lens from `LENSES.md` when the user asks for PRD review, document review, contract review, implementation review, UAT review, UI review, or git boundary review. If a check cannot be run, mark it `unverified`. A code diff or implementation summary alone is not readiness evidence.

## Workflow

1. Start with the exact `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`.
2. State the named lens or lenses being used.
3. State claimed behavior before judging it.
4. Inspect source/diff/test evidence.
5. Run or report relevant checks when available.
6. Use browser/runtime inspection when visual or interaction claims matter.
7. Separate data, environment, and customer/UAT readiness.
8. Map `Claim / AC -> Evidence -> Result -> Gap -> Severity`.
9. Mark missing checks as `unverified`.
10. Keep any customer-facing summary optional and secondary to engineering readiness.
11. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.

## Output Shape

```text
Verification Summary
- Verification Scope
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
- Risks
- Unverified Claims
- Next Action
```

## Stop Condition

Stop when evidence supports a verdict or the blocking missing evidence is explicit.

## Gate Rule

If verification would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, stop before execution and output Proposed Action, Target, Risk, Rollback/Undo, and Approval Needed. Do not execute until explicit user approval.

Before git-boundary review, staging, or commit-related verification, follow `skills/_shared/GIT-BOUNDARY.md`. Never approve `git add .`; require explicit pathspec staging and a statement of unrelated modified, untracked, or ignored files.

## Artifact Rule


Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md`: every new or materially updated durable artifact must include the required audience-first header fields exactly.
Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: local artifact placement must follow the directory policy, and `.groundwork/*` runtime directories are ignored by default and not committed unless explicitly approved.
Write verification artifacts only when they are needed for UAT/SIT, release, review, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
