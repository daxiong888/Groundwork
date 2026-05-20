# Groundwork Runtime Trial

Date: 2026-05-20
Environment: Codex CLI from `/Users/daxiong/Documents/sourceCode/Groundwork`; explicit smoke prompts also ran from `/private/tmp/groundwork-smoke-clean`
Installation mode: personal marketplace rooted at `/Users/daxiong`; lean package at `/Users/daxiong/.codex/plugins/groundwork`; Groundwork installed and enabled through Codex App UI
Runtime tested: smoke yes; representative prompts not yet

## Summary

- prompts run: 8 explicit invocation smoke prompts (`sx-001` to `sx-008`) plus 6 loader/package smoke prompts
- pass: 9 confirmed runtime/plugin-load passes (`loader-smoke-004`, `loader-smoke-005`, `loader-smoke-006`, `sx-001`, `sx-002`, `sx-003`, `sx-005`, `sx-007`, `sx-008`)
- partial: 2 (`sx-004`, `sx-006`) because the expected skill loaded and no edits occurred, but the run inspected broader local context than a smoke prompt should require
- fail: 0
- blocked: 3 early loader setup attempts before the final personal marketplace + UI install path

## Results

| ID | Expected | Actual | Verdict | Notes |
| --- | --- | --- | --- | --- |
| sx-001 | Loads `to-prd`; no file write by default. | After install, runtime injected `groundwork:to-prd`, produced `TRIAL_ID: sx-001`, followed `to-prd` output shape, and did not edit files. | pass | The agent read the cached `to-prd/SKILL.md` after injection and also read memory due global memory rules. This is environment noise, not a selection failure. |
| sx-002 | Loads `to-issues`; tracker-neutral issue slices. | Runtime injected `groundwork:to-issues`, produced `TRIAL_ID: sx-002`, and returned a `needs-info` issue because the original prompt referenced “这个 PRD” without providing a PRD. | pass with fixture drift | Skill selection passed, but the smoke prompt was not self-contained and caused unnecessary file/Chronicle probing. |
| sx-003 | Loads `triage`; readiness verdict before plan. | Produced `TRIAL_ID: sx-003`, classified the issue as `needs-info` / `HITL`, and did not edit files. | pass with environment drift | The output used prior memory to infer a likely project context. That is acceptable for normal Codex behavior but too broad for an isolated smoke fixture. |
| sx-004 | Loads `write-plan`; no invented exact paths before inspection. | Produced `TRIAL_ID: sx-004`, wrote a source-inspected plan, and did not edit files. | partial | The skill behaved as designed by inspecting before exact paths, but the prompt caused it to inspect a real external project. This validates skill behavior, not isolated smoke quality. |
| sx-005 | Loads `prototype`; prototype question and cleanup decision. | Produced `TRIAL_ID: sx-005`, answered with prototype question, decision, states, interactions, gaps, implementation implications, and cleanup decision. | pass | No prototype file was created. The output marked missing browser/runtime verification as not performed. |
| sx-006 | Loads `implement`; diagnose before edits. | Produced `TRIAL_ID: sx-006`, diagnosed before edits, and did not edit files. | partial | The run inspected an unrelated temporary UAT package under `/private/tmp/laihu-uat-package...`. This confirms the `implement` workflow tendency but shows the smoke prompt needs a clean fixture repo or stricter isolation. |
| sx-007 | Loads `verify`; skeptical evidence split. | Produced `TRIAL_ID: sx-007`, concluded code diff alone is insufficient for front-end integration or customer UAT readiness, and listed missing runtime/data/environment evidence. | pass | Reran from `/private/tmp/groundwork-smoke-clean`; output honored the prompt not to inspect files or memory. |
| sx-008 | Loads `handoff`; compact continuation. | Produced `TRIAL_ID: sx-008`, gave compact continuation state, evidence, risks, and next steps without repeating PRD/diff content. | pass | Reran from `/private/tmp/groundwork-smoke-clean`; output honored the prompt not to inspect files or memory. |
| loader-smoke-001 | Detect whether Groundwork is already loaded as a Codex plugin/skill without searching files. | Returned `GROUNDWORK_NOT_LOADED`. Runtime logs rejected repo marketplace `source.path: "./"` as an empty local plugin source path. | blocked | Repo marketplace cannot point at the marketplace root itself. |
| loader-smoke-002 | Detect whether Groundwork is already loaded after changing repo marketplace `source.path` to `./.`. | Returned `GROUNDWORK_NOT_LOADED`. Runtime logs rejected `source.path: "./."` because the local plugin source path must stay within the marketplace root. | blocked | `./.` is not a valid workaround for a plugin package located at the marketplace root. |
| loader-smoke-003 | Detect whether Groundwork is loaded after switching to personal marketplace rooted at `/Users/daxiong`. | Returned `GROUNDWORK_NOT_LOADED`. No Groundwork cache path or `groundwork@groundwork-personal` enabled state was created. | blocked | Marketplace registration succeeded, but CLI did not perform per-plugin install/enable. |
| loader-smoke-004 | Detect whether Groundwork is loaded after installing and restarting Codex App. | Returned `GROUNDWORK_LOADED`. Config contains `[plugins."groundwork@groundwork-personal"] enabled = true`, and cache exists at `/Users/daxiong/.codex/plugins/cache/groundwork-personal/groundwork/0.1.0`. | pass | Confirms real runtime plugin loading after UI install. |
| loader-smoke-005 | Detect whether Groundwork still loads after switching the personal marketplace to the lean package path. | Returned `GROUNDWORK_LOADED`; rebuilt cache size was about `320K`; no `.git/` or `refer/` directory was found in the cache. | pass | The personal marketplace now points to `./.codex/plugins/groundwork`, not the full source repository. |
| loader-smoke-006 | Detect whether Groundwork still loads after syncing the lean package into the installed cache. | Returned `GROUNDWORK_LOADED`; package and installed cache were both about `324K`; no `.git/` or `refer/` directory was found in either location. | pass | Confirms the active installed copy and the lean source package are aligned after the baseline/checklist update. |

## Failures / Drift

- The CLI path used for the trial was `codex -a never exec --json --ephemeral -C . -s read-only "Use to-prd for this: ..."` after an earlier argument-order correction.
- The first sandboxed run failed before the trial because Codex needed to write its own local state outside the workspace. The command was rerun with approval.
- The current `codex plugin --help` path exposed `marketplace` management, but no direct local `plugin install <path>` command was observed.
- The repo-local `.codex-plugin/plugin.json` was not enough to produce observable plugin-load evidence in `codex exec -C .`.
- The spawned agent searched the repository for `to-prd` and `PRD`, then read `skills/to-prd/SKILL.md` directly. That can validate the skill file content, but it does not validate runtime plugin selection.
- The spawned agent also ran `find .. -name AGENTS.md -print`, which scanned sibling repositories and local reference snapshots. This introduced unrelated context and high token usage.
- Codex emitted warnings about unrelated cached marketplace/plugin manifests under `~/.codex/.tmp`. These warnings are environment noise unless they later block plugin loading.
- `codex plugin marketplace add /Users/daxiong/Documents/sourceCode/Groundwork` succeeded as marketplace registration, but runtime rejected the repo-root plugin source shape.
- `codex plugin marketplace remove groundwork-local` removed the invalid repo-root marketplace registration.
- A personal marketplace was created at `/Users/daxiong/.agents/plugins/marketplace.json` with `source.path: "./Documents/sourceCode/Groundwork"`, then `codex plugin marketplace add /Users/daxiong` succeeded.
- Even after personal marketplace registration, CLI smoke runs did not generate `/Users/daxiong/.codex/plugins/cache/groundwork-personal/groundwork/local` or a `groundwork@groundwork-personal` enabled config entry.
- Computer Use cannot operate the Codex App UI directly in this environment; it returned that `com.openai.codex` is not allowed for safety reasons.
- After manual install and Codex App restart, the plugin cache existed under `/Users/daxiong/.codex/plugins/cache/groundwork-personal/groundwork/0.1.0`, and config contained `[plugins."groundwork@groundwork-personal"] enabled = true`.
- The first installed cache was about 386 MB and included `.git/` and `refer/`, because the personal marketplace pointed at the full source repository.
- The personal marketplace was then updated to point at `/Users/daxiong/.codex/plugins/groundwork`, a lean package synced from the repository while excluding `.git/` and `refer/`.
- The old cache was removed and rebuilt from the lean package. The rebuilt cache was about 320 KB and contained no `.git/` or `refer/` directory.
- After the baseline/checklist update, the lean package was synced into the installed cache; both package and cache measured about 324 KB and still contained no `.git/` or `refer/`.
- `sx-001` and `sx-002` both showed `codex.skill.injected` events for `groundwork:<skill>`. Telemetry also emitted a non-blocking warning because tag values with `:` contain invalid characters.
- The original `sx-002` prompt used “这个 PRD” without a PRD body, so the agent searched `/private/tmp`, read unrelated temporary UAT package docs, and checked Chronicle status before returning `needs-info`.
- `sx-003`, `sx-004`, and `sx-006` show that behavior-oriented smoke prompts can still trigger memory or filesystem discovery. That is normal for real task execution, but too noisy for a pure explicit-invocation smoke test.
- `sx-007` and `sx-008` were rerun from a clean temporary directory with explicit “do not inspect files or memory” instructions and stayed within the prompt-provided context.

## Docs Checked

- Official Codex plugin docs say local plugin testing should use a repo or personal marketplace entry, and that `.codex-plugin/plugin.json` plus a skill folder is only the plugin package shape before marketplace installation.
- Official docs also state that Codex resolves a marketplace `source.path` relative to the marketplace root, and that the path must start with `./` and stay inside that root.
- Source: https://developers.openai.com/codex/plugins/build

## Skill Updates Needed

- None from the explicit smoke result. The observed drift is fixture/environment design, not a blocking skill-design failure.
- Do not weaken `write-plan` or `implement` just to make smoke prompts quieter; their inspection-first behavior is part of the intended workflow.

## Fixture Updates Needed

- Keep explicit smoke prompts self-contained. Avoid “这个 PRD”, “这个 issue”, “这个任务”, or “这个流程” unless the prompt also includes the source text.
- For pure skill-loading checks, add “Do not inspect files or memory” and run from a clean temporary directory.
- For `write-plan` and `implement`, prefer a tiny fixture repository over an empty directory. These skills are expected to inspect before producing exact paths or diagnosing a bug.
- Keep smoke prompts focused on skill loading and minimum behavior; use the representative `rt-*` prompts for real workflow quality.

## Next Actions

- Run the representative `rt-001` to `rt-010` prompts next.
- Treat `rt-009` and `rt-010` as non-negotiable gates: `rt-009` must remain direct fallback, and `rt-010` must not push, deploy, or mutate remote state before explicit approval.
- After representative prompts, decide whether to add a tiny fixture repo for `write-plan` / `implement` smoke stability.

## Follow-up Setup

- A repo-scoped marketplace entry was attempted after this partial trial, but it was removed because the repository root is also the plugin package root.
- Runtime rejected `source.path: "./"` as an empty local plugin source path.
- Runtime rejected `source.path: "./."` because the local plugin source path must stay within the marketplace root as a child path.
- The final setup path for this trial is a personal marketplace rooted at `/Users/daxiong`, with `source.path: "./.codex/plugins/groundwork"` pointing to the lean local package.
