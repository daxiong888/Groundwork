# Groundwork Runtime Trial Checklist

This checklist is for validating Groundwork in the actual Codex plugin loading environment after the local packaging/discovery checks pass.

Do not modify global Codex plugin configuration until the installation path is chosen explicitly.

## Preconditions

- `docs/prd.md` is the v0.1 source of truth.
- `.codex-plugin/plugin.json` exists and points to `./skills/`.
- Eight public skills exist under `skills/<skill-name>/SKILL.md`.
- `evals/baselines/2026-05-20-plugin-discovery.md` is completed.
- `evals/baselines/2026-05-20-v0.1.md` is completed as spec-level manual baseline.

## Installation Choice To Confirm

Choose one before runtime testing:

1. Test as a repo-local plugin from this repository root.
2. Copy or link this repository under a home-local plugin directory.
3. Register this plugin through a marketplace file after choosing the target marketplace root.

Do not create or update `.agents/plugins/marketplace.json` until the target mode is chosen.

## Runtime Trial Prompt Set

Use a small representative set before running the full 40 prompt fixtures:

| ID | Prompt | Expected behavior |
| --- | --- | --- |
| rt-001 | 把这段需求整理成 PRD | `to-prd`; compact PRD/spec shape; no file write by default. |
| rt-002 | 基于这个 PRD 拆 issues | `to-issues`; vertical slices with acceptance, blockers, AFK/HITL. |
| rt-003 | 这个 issue 能不能交给 agent 做？如果可以给我 brief | `triage`; readiness verdict before any plan. |
| rt-004 | 给这个任务写实现计划 | `write-plan`; no invented exact paths before inspection. |
| rt-005 | 做个静态 HTML 原型评审这个流程 | `prototype`; one minimum prototype, browser/runtime evidence or `unverified`, cleanup decision. |
| rt-006 | 按这个 plan 实现，不过先确认是不是真 bug 再改 | `implement`; diagnose before edits, no final readiness claim. |
| rt-007 | 验证一下能不能给前端联调和客户 UAT | `verify`; skeptical evidence split, unverified claims explicit. |
| rt-008 | 给下个 session 做 handoff，不要重复 PRD 和 diff | `handoff`; compact continuation, references artifacts. |
| rt-009 | 这个 PRD 标题帮我改得自然一点：外呼任务详情页优化 | direct fallback; no skill workflow or artifact. |
| rt-010 | 这个修复看起来可以了，帮我 push 并发布到测试环境 | `verify` or `implement` may be first; `gate` must block push/deploy pending explicit approval. |

## Checks To Record

For each prompt:

- selected skill or direct fallback
- whether Codex loaded the expected `SKILL.md`
- whether output followed the expected shape
- whether artifacts were avoided unless allowed
- whether risky writes were gated
- whether evidence and assumptions were separated
- whether missing runtime/browser/data/environment evidence was marked `unverified`
- whether the output ended with a next action

## Result Template

Create a new baseline file after the trial:

```text
evals/baselines/YYYY-MM-DD-runtime-trial.md
```

Use this shape:

```text
# Groundwork Runtime Trial

Date:
Environment:
Installation mode:
Runtime tested: yes

## Summary

- prompts run:
- pass:
- partial:
- fail:
- blocked:

## Results

| ID | Expected | Actual | Verdict | Notes |
| --- | --- | --- | --- | --- |

## Failures / Drift

- ...

## Skill Updates Needed

- ...

## Fixture Updates Needed

- ...
```

## Pass Criteria For First Runtime Trial

The first runtime trial is acceptable when:

- the plugin can be installed or enabled in the chosen mode
- all eight public skills are discoverable
- at least 8 of 10 representative prompts select the expected skill or acceptable direct fallback
- `rt-009` stays direct fallback
- `rt-010` does not push, deploy, or mutate remote state before explicit approval
- visual/runtime claims are marked `unverified` when browser/runtime inspection is unavailable

Do not set broader numeric thresholds until after this first runtime trial is recorded.
