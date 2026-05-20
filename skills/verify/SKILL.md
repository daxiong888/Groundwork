---
name: verify
description: Skeptically verify code tests runtime data environment UAT SIT and release readiness with concrete evidence or explicit unverified claims. Use when the user asks to 验证一下, check readiness, UAT, SIT, release confidence, or whether work can be handed to frontend or customers.
---

# verify

## Trigger Contract

Use this skill when the user asks for readiness, evidence, UAT/SIT, runtime behavior, release confidence, or customer/front-end handoff verification.

Should trigger:

- "验证一下能不能给前端验"
- "这个可以给客户 UAT 吗"
- "检查一下 release readiness"
- "跑一遍证据链"
- "确认这次实现是否真的生效"

Should not trigger:

- The user asks to implement code; use `implement`.
- The user asks to write a plan before edits; use `write-plan`.
- The user asks whether an issue is ready to start; use `triage`.
- The user asks for only PRD wording; use `to-prd`.
- The user asks for compact continuation context; use `handoff`.

## Required Evidence

Use source evidence, test output, runtime/browser evidence, data readiness, environment readiness, and UAT/customer evidence as applicable. If a check cannot be run, mark it `unverified`.

## Workflow

1. State claimed behavior before judging it.
2. Inspect source/diff/test evidence.
3. Run or report relevant checks when available.
4. Use browser/runtime inspection when visual or interaction claims matter.
5. Separate data, environment, and customer/UAT readiness.
6. Mark missing checks as `unverified`.
7. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.

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

## Artifact Rule

Write verification artifacts only when they are needed for UAT/SIT, release, review, or handoff. Redact sensitive logs, requests, screenshots, database rows, and credentials.
