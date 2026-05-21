---
name: verify
description: Skeptically verify readiness evidence for code, tests, runtime behavior, data, environment, UAT/SIT, or release confidence.
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

Should not trigger:

- The user asks to implement code; use `implement`.
- The user asks to write a plan before edits; use `write-plan`.
- The user asks whether an issue is ready to start; use `triage`.
- The user asks for only PRD wording; use `to-prd`.
- The user asks for compact continuation context; use `handoff`.

## Required Evidence

Use source evidence, test output, runtime/browser evidence, data readiness, environment readiness, and UAT/customer evidence as applicable. If a check cannot be run, mark it `unverified`. A code diff or implementation summary alone is not readiness evidence.

## Workflow

1. State claimed behavior before judging it.
2. Inspect source/diff/test evidence.
3. Run or report relevant checks when available.
4. Use browser/runtime inspection when visual or interaction claims matter.
5. Separate data, environment, and customer/UAT readiness.
6. Mark missing checks as `unverified`.
7. Keep any customer-facing summary optional and secondary to engineering readiness.
8. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.

## Output Shape

```text
Verification Summary
- Verdict: pass / partial / fail / blocked
- Claimed Behavior
- Source Evidence
- Test Evidence
- Runtime / Browser Evidence
- Data Readiness
- Environment Readiness
- Customer / UAT Readiness
- Risks
- Unverified Claims
- Next Action
```

## Stop Condition

Stop when evidence supports a verdict or the blocking missing evidence is explicit.

## Gate Rule

If verification would require or is paired with push, deploy, publish, migration, destructive command, data write, remote tracker mutation, or shared skill mutation, stop before execution and output Proposed Action, Target, Risk, Rollback/Undo, and Approval Needed. Do not execute until explicit user approval.

## Artifact Rule


Follow `skills/_shared/ARTIFACT-POLICY.md`: every new or materially updated durable artifact must include the audience-first header, and local artifacts must follow the shared directory policy under `.groundwork/tasks/<task-id>/` or `.groundwork/shared/` unless the user specifies another target.
Write verification artifacts only when they are needed for UAT/SIT, release, review, or handoff.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, and database rows before writing or quoting artifacts.
