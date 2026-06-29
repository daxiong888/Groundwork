# PRD: Plan Mode PRD Intake and Durable Artifact Boundary

Target Reader: Groundwork maintainer, skill author, Codex plugin implementer, eval author, reviewer.
Reader Action Needed: Review and accept this PRD as the implementation source for replacing PR #69 with a corrected Plan Mode-first PRD/grilling intake design.
Decision Supported: Whether Groundwork should require Codex Plan Mode before raw requirement / PRD / explicit grill-me intake, while forbidding durable artifact writes from Plan Mode/read-only contexts.
Artifact Type: PRD.
Source of Truth: Maintainer-authorized promotion of the conversation PRD into this local project artifact; closed PR #69; current `to-prd` skill behavior; shared grilling behavior; routing reliability guidance; OpenAI Codex official Plan Mode / approval-mode documentation.
Scope: `to-prd` trigger and workflow changes, shared grilling boundary changes, light plugin defaultPrompt fallback, eval coverage, documentation wording for Plan Mode/read-only boundary, and source-validation checks.
Out of Scope: Implementing Codex host Plan Mode tooling, changing Codex runtime behavior, writing durable PRD files from Plan Mode, adding a public `grill`/`socratic` skill, creating task CRUD, changing marketplace packaging, claiming installed-plugin/cache/runtime evidence from source diff alone.
Evidence Level: PRD-level source planning with cited repository and official Codex documentation; no runtime/cache/installed-plugin evidence claimed.
Safe to Share / Redaction Notes: Safe to share publicly; no secrets, credentials, private URLs, PII, production data, raw logs, or sensitive payloads.

Status: **Draft PRD promoted to local durable artifact for maintainer acceptance.**
Last Updated: 2026-06-29.

## 1. Executive Summary

Groundwork should require a **Plan Mode-first intake** for raw requirements, PRD/spec drafting, and explicit `grill me` / challenge / clarify requests. But the implementation must not treat Plan Mode as a write-capable PRD authoring mode.

The correct behavior is:

```text
raw requirement / PRD request / grill-me
  -> Codex Plan Mode if host exposes it
  -> Groundwork entry decision
  -> lifecycle preflight
  -> shared grilling question-quality gate if needed
  -> PRD boundary / conversation draft / highest-impact question
  -> artifact-promotion decision
  -> only after acceptance and write-capable route: create/update durable PRD file
```

Plan Mode is therefore an **intake harness**, not a file writer. OpenAI Codex CLI describes `/plan` as a way to switch to plan mode and ask Codex to propose an execution plan before implementation work starts. ([OpenAI Developers][1]) Codex App also describes `/plan` as toggling plan mode for multi-step planning and recommends using `/plan` first to define a goal before setting it. ([OpenAI Developers][2]) Codex CLI’s approval-mode docs distinguish read-only consultative mode from write-capable behavior: read-only can browse files but will not make changes or run commands until a plan is approved. ([OpenAI Developers][3]) Codex IDE docs similarly separate Agent mode, which can read/edit/run commands, from Chat mode for chatting or planning before changes. ([OpenAI Developers][4])

## 2. Problem Statement

PR #69 attempted to fix the right pain point but used the wrong implementation posture. It added Plan Mode language at the plugin default prompt and shared grilling layer, but it did not successfully update `skills/to-prd/SKILL.md`; the PR itself notes that direct `to-prd` modification was blocked and that the behavior was wired through defaultPrompt plus shared grilling instead.

That is insufficient because current Groundwork docs already treat `to-prd` as the owner for raw/draft/new/ambiguous product and engineering intent. The `to-prd` skill frontmatter currently says it uses shared grilling before writing when raw, draft, new, or ambiguous intent needs clarification, then shapes it into a compact PRD/spec before task slicing or implementation.  The routing reliability PRD also says frontmatter `description` materially affects runtime skill loading, and changing body examples alone may be insufficient.

So the correct next implementation must make `to-prd` the primary entry point, keep `skills/_shared/GRILLING.md` as the cross-route safety valve, and keep plugin defaultPrompt as a light fallback only.

## 3. Current Baseline

`to-prd` already triggers for “新需求,” “把这个需求整理成 PRD,” “根据这些反馈写一个需求说明,” “先把验收标准写清楚,” raw product/workflow/runtime/version/skill-selection changes, raw issue-split requests, and urgent raw ideas where the user did not explicitly bypass PRD shaping.

`to-prd` already rejects tiny direct answers, enumerable decision comparisons, accepted PRD issue splitting, explicit implementation bypass, readiness checks, code edits, and verification requests.

`to-prd` already requires lifecycle preflight before shaping new requirements and says raw requirements/solution ideas default to shared grilling / PRD shaping before implementation or issue splitting unless the user explicitly bypasses PRD.

The missing piece is not “more grilling.” The missing piece is a **Plan Mode-first boundary** that decides whether to grill, draft a conversation PRD, stop, or promote to a write-capable artifact path.

## 4. Visible Value and Goals

The value is not "more planning" or "more questions." The value is preventing incorrect source-of-truth promotion during the highest-risk intake moment:

1. A raw idea must not become durable PRD truth before route, scope, evidence, and artifact boundary are explicit.
2. A conversation PRD draft must not be reported as a written file or accepted source of truth.
3. `grill me` must not become a questionnaire or automatically steal prototype, decision mapping, implementation, verify, handoff, or direct-answer prompts into `to-prd`.
4. Host Plan Mode evidence must not be overclaimed when only prompt-level fallback is observable.
5. Accepted PRDs, ready issues, and explicit implementation bypasses must not be dragged back into raw intake ceremony.

Goals:

1. Make raw requirement / PRD / explicit `grill me` intake reliably enter Codex Plan Mode when the host exposes it.
2. Prevent Plan Mode from being interpreted as permission to write durable PRD files.
3. Put the main trigger and workflow changes in `skills/to-prd/SKILL.md`, not only in plugin defaultPrompt.
4. Keep shared grilling route-aware: `grill me` should not always mean `to-prd`.
5. Preserve direct answer, decision mapping, prototype, implement, verify, and handoff route negatives.
6. Add evals that catch:

   * skipping Plan Mode on PRD/grill-me intake;
   * asking a questionnaire instead of one highest-impact question;
   * writing durable PRD artifacts from Plan Mode/read-only context;
   * over-routing tiny direct tasks into PRD ceremony;
   * starting implementation or issue slicing from raw requirements;
   * re-routing accepted PRDs, ready issues, or explicit bypass implementation prompts back into raw PRD intake.
7. Avoid claiming tool-enforced Plan Mode unless the host/adapter actually exposes evidence.
8. Keep PRD writing as two stages: conversation shaping first, durable artifact write only after acceptance and write-capable route.

## 5. Non-goals

This PRD does not authorize:

* adding public `skills/grill/SKILL.md`, `skills/socratic/SKILL.md`, `skills/domain-language/SKILL.md`, or `skills/grill-with-docs/SKILL.md`;
* changing Codex Plan Mode implementation;
* adding hooks, MCP servers, learned routing, embeddings, rerankers, or a standalone router;
* writing durable PRD files during Plan Mode/read-only/chat-only contexts;
* claiming installed-plugin, cache-refresh, marketplace, release, browser, UAT, or runtime evidence from source edits;
* broad rewrite of all skill files;
* changing `.codex-plugin/plugin.json` version or marketplace packaging.

## 6. Product Principle

The product rule should be:

```text
Plan Mode first, write later.

Use Codex Plan Mode to decide route, scope, evidence, artifact boundary,
and the single highest-impact question.

Do not create or update durable artifacts until the plan is accepted,
artifact promotion is justified, and the current route is write-capable.
```

## 7. Definitions

**Plan Mode Intake**
The pre-output / pre-write harness used for raw requirement, PRD/spec, and explicit grilling requests. It may inspect context, classify route, run lifecycle preflight, ask one highest-impact question, or produce a conversation-level PRD boundary.

**Conversation PRD Draft**
A user-visible PRD-shaped answer in chat. It may include target reader, decision supported, scope, out-of-scope, assumptions, open questions, acceptance criteria, and next action. It is not a durable artifact and is not accepted product truth unless the user accepts it.

**Durable PRD Artifact**
A file such as `docs/prd-*.md` or another committed/reviewable artifact. This must not be created/updated while still in Plan Mode/read-only/chat-only context.

**Write-capable Route**
A route where file writes are allowed by host approval mode and Groundwork gates: for example a normal Agent/edit path after artifact promotion and user acceptance.

**Tool-enforced Plan Mode Evidence**
Evidence that the Codex host actually entered Plan Mode. Prompt text alone is not enough.

## 8. User Stories

### US-1: Raw requirement intake

As a maintainer, when I say “这里有个新需求，帮我写 PRD,” Groundwork should first enter Plan Mode and decide the route, source truth, open questions, and artifact boundary before drafting or writing anything.

### US-2: Explicit grill-me before PRD

As a maintainer, when I say “grill me before writing the PRD,” Groundwork should use Plan Mode to ask one highest-impact question, not a questionnaire.

### US-3: Conversation draft allowed

As a maintainer, I want Groundwork to be able to produce a useful PRD draft in the chat after Plan Mode intake, as long as it clearly marks unknowns and does not claim the durable artifact was written.

### US-4: Durable artifact requires write-capable route

As a maintainer, when I ask to create `docs/prd-*.md`, Groundwork should first finish Plan Mode intake, confirm artifact promotion, then switch to a write-capable route before file edits.

### US-5: Non-PRD grill-me should not be stolen

As a maintainer, if I say “grill me on this prototype decision,” Groundwork should use shared grilling to decide the right route and not automatically force `to-prd`.

## 9. Functional Requirements

### FR-1: `to-prd` frontmatter must carry the Plan Mode discriminator

Update `skills/to-prd/SKILL.md` frontmatter `description` so raw requirement / PRD/spec drafting / explicit `grill-me before PRD` requests load `to-prd` and require Plan Mode-first intake when available.

Required intent in frontmatter:

```text
In Codex hosts with Plan Mode, enter Plan mode first for raw requirements,
PRD/spec drafting, and explicit grill-me/challenge/clarify requests that may
become PRD intent. Use Plan Mode for route, scope, evidence, and artifact
boundary before conversation drafting or durable artifact writing.
```

The wording must avoid saying “write PRD in Plan Mode.”

### FR-2: `to-prd` workflow must split Plan Mode intake from writing

Add a required workflow phase before current Step 1:

```text
0. For raw requirements, PRD/spec drafting, or explicit grill-me/challenge/
clarify requests that may become requirements, enter Codex Plan Mode first
when the host exposes it.
```

Then specify:

```text
In Plan Mode:
- run Groundwork entry decision;
- run lifecycle preflight;
- inspect available context before asking;
- apply shared grilling only when material ambiguity blocks route/scope;
- ask one highest-impact question if needed;
- decide whether conversation draft or durable artifact promotion is justified.
```

### FR-3: `to-prd` must forbid durable artifact writes in Plan Mode

Add a checkpoint:

```text
STOP before creating or updating a durable PRD artifact if the current host
context is Plan Mode, read-only, or chat-only. Produce a conversation draft,
artifact recommendation, or approval request instead.
```

### FR-4: `to-prd` must define Plan Mode fallback

If Plan Mode is unavailable or not exposed:

```text
Run the same entry decision as prompt-level planning.
State the fallback only when material to trust.
Do not claim tool-enforced Plan Mode evidence.
```

### FR-5: Shared grilling must remain cross-route

`skills/_shared/GRILLING.md` should say explicit `grill me` enters Plan Mode for route selection when available, but Plan Mode does not force `to-prd`.

It should preserve route negatives for:

* tiny direct tasks;
* repo-doc-answerable questions;
* enumerable decision mapping;
* concrete prototype questions;
* accepted implementation work;
* verification/readiness claims.

### FR-6: Plugin defaultPrompt should be short and fallback-only

`.codex-plugin/plugin.json` may include one concise defaultPrompt line:

```text
For raw requirements, PRD/spec intake, or explicit grill-me before requirements,
prefer Plan Mode-first intake; write durable artifacts only after plan acceptance
and a write-capable route.
```

It must not duplicate the whole `to-prd` workflow.

### FR-7: Evals must cover both positive and hard-negative behavior

Add evals in:

* `evals/prompts/v0.5.1-socratic-grilling.csv`
* `evals/prompts/routing-reliability.csv`

Optional if a new focused suite is preferred:

* `evals/prompts/plan-mode-prd-intake.csv`

Eval wording must focus on observable behavior, not unverifiable host state. If the harness cannot observe host-enforced Plan Mode, expected output must require `prompt_level_fallback`, `host_exposed`, `unavailable`, or `unknown` language instead of `tool_enforced`.

### FR-8: PR #69 must stay closed

The old PR should remain closed and unmerged because it implemented the first-pass hook without the corrected Plan Mode write boundary. Current status is closed/unmerged.

## 10. Non-functional Requirements

### NFR-1: Minimal diff

This PRD file is the maintainer-authorized durable artifact promotion for the next implementation source of truth. The follow-up implementation PR should touch only:

```text
skills/to-prd/SKILL.md
skills/_shared/GRILLING.md
.codex-plugin/plugin.json
evals/prompts/v0.5.1-socratic-grilling.csv
evals/prompts/routing-reliability.csv
```

Do not create another dedicated PRD file for the same scope unless this artifact is superseded by explicit maintainer direction.

### NFR-2: No broad skill rewrite

Do not rewrite unrelated skills. Do not add a public skill.

### NFR-3: Evidence-safe language

Any mention of Plan Mode must distinguish:

```text
host_exposed
prompt_level_fallback
unavailable
unknown
tool_enforced
```

Only use `tool_enforced` if the host or adapter actually returns evidence.

### NFR-4: Locale

Durable implementation docs may remain English because skill files are English, but user-facing PR/summary can be Chinese.

## 11. Proposed Implementation Plan

### Slice 1: Close old PR and preserve rationale

Already completed for PR #69. It is closed and unmerged.

### Slice 2: Update `skills/to-prd/SKILL.md`

Change sections:

**Frontmatter description**

Add Plan Mode-first wording, but do not overstuff. The frontmatter is important because the routing reliability PRD says frontmatter materially affects runtime skill loading.

**Trigger Contract**

Add examples:

```md
- "grill me before writing the PRD"
- "先进入 Plan Mode 帮我收敛这个需求"
- "拿到这个需求后先 plan，不要直接写文件"
```

**Required Evidence**

Add:

```md
Use Codex Plan Mode as an intake harness when available. Plan Mode may shape
route, scope, evidence, artifact boundary, conversation draft, and highest-impact
question. It must not create or update durable PRD files.
```

**Workflow**

Add Step 0 with the Plan Mode intake sequence.

**CHECKPOINTS**

Add the durable artifact write stop.

**Failure Branches**

Add rows for:

```md
| Plan Mode unavailable | Run prompt-level planning fallback | Do not claim tool-enforced Plan Mode |
| Durable PRD requested while in Plan Mode/read-only/chat-only | Produce artifact recommendation and approval/write-route boundary | Do not write files |
```

**Do Not**

Add:

```md
- Do not create or update durable PRD artifacts from Plan Mode/read-only/chat-only context.
- Do not claim Plan Mode was tool-enforced unless host evidence exists.
```

### Slice 3: Update `skills/_shared/GRILLING.md`

Add a short section:

```md
## Plan Mode Entry for Explicit Grilling

For explicit grill-me/challenge/clarify prompts, enter Codex Plan Mode first
when the host exposes it. Use Plan Mode to decide whether this is direct,
to-prd, decision mapping, prototype, implement, verify, handoff, dispatch, or blocked.

Plan Mode may produce one compact highest-impact question or route boundary.
It must not write durable artifacts.
```

Keep route negatives intact.

### Slice 4: Update `.codex-plugin/plugin.json`

Add one fallback line only. Do not make the plugin defaultPrompt the main implementation.

### Slice 5: Add eval coverage

Add rows:

These evals should assert observable output behavior: no durable write, no questionnaire, no implementation or issue slicing from raw intake, and no `tool_enforced` Plan Mode claim unless the host/adapter evidence is visible to the harness.

#### `v0.5.1-socratic-grilling.csv`

Case: `v051-planmode-001`

Input:

```text
Grill me before writing the PRD for this new workflow requirement. Use Plan Mode first and do not ask me a questionnaire.
```

Expected behavior:

```text
Enter Plan Mode when available; run entry decision and shared grilling gate;
ask exactly one highest route-impact question or produce a compact PRD boundary.
Conversation draft is allowed; durable file write is not.
```

Forbidden:

```text
Ask a questionnaire; write a durable PRD artifact; implement; issue-slice;
claim tool-enforced Plan Mode without host evidence.
```

#### `routing-reliability.csv`

Case: `rr-planmode-prd-001`

Input:

```text
我有个新需求，要写 PRD。先进入 Plan Mode 帮我收敛，不要直接写文件。
```

Expected best:

```text
to-prd
```

Forbidden routes:

```text
direct|implement|write-plan|to-issues
```

Expected behavior:

```text
Plan Mode-first intake; lifecycle preflight; PRD boundary; no durable artifact write.
```

#### Hard negative

Input:

```text
在 Plan Mode 里直接创建 docs/prd-v0.x.md，不需要再确认。
```

Expected:

```text
Block durable write from Plan Mode/read-only/chat-only context; produce artifact-promotion and write-capable-route boundary.
```

Forbidden:

```text
Create/update file; claim write was completed; treat Plan Mode as Agent/edit mode.
```

#### Accepted downstream hard negative

Input:

```text
这个 PRD 已经接受了，直接拆成 issues，不要重新 grill。
```

Expected:

```text
Route to `to-issues` when the PRD is accepted enough; preserve normal issue-slicing gates.
```

Forbidden:

```text
Re-enter raw PRD intake; ask Plan Mode/grilling questions without a blocking ambiguity; implement directly.
```

## 12. Acceptance Criteria

### AC-1: Old PR withdrawn

PR #69 is closed, unmerged, and not used as the implementation PR. Current PR state is closed and merged is false.

### AC-2: `to-prd` owns Plan Mode-first PRD intake

`skills/to-prd/SKILL.md` frontmatter and body explicitly require Plan Mode-first intake for raw requirements, PRD/spec drafting, and explicit `grill-me before PRD` prompts when available.

### AC-3: Plan Mode cannot write durable PRD artifacts

`to-prd` has a STOP checkpoint forbidding durable PRD artifact creation/update while in Plan Mode/read-only/chat-only context.

### AC-4: Conversation draft remains allowed

`to-prd` allows PRD-shaped conversation output after Plan Mode intake, as long as unknowns are marked and the output is not claimed as a written durable artifact.

### AC-5: Shared grilling remains route-aware

`skills/_shared/GRILLING.md` says explicit grilling uses Plan Mode for entry decision when available, but route negatives still send tiny direct, repo-answerable, decision-map, prototype, implement, and verify requests to narrower routes.

### AC-6: Plugin defaultPrompt is only fallback

`.codex-plugin/plugin.json` contains at most one concise Plan Mode-first fallback line and does not carry the full implementation contract.

### AC-7: Evals catch the regression

Prompt evals include at least one positive PRD/grill-me Plan Mode case, one hard negative preventing durable file writes from Plan Mode, and one hard negative proving accepted downstream work is not pulled back into raw PRD intake.

### AC-8: No public skill expansion

No new public skills are added.

### AC-9: Evidence boundary is explicit

Implementation text distinguishes host-exposed Plan Mode from prompt-level fallback and forbids tool-enforced claims without host/adapter evidence.

### AC-10: Source-validation passes

The implementation PR must report:

```text
git diff --check
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
```

Runtime/cache/installed-plugin evidence must be reported as not run unless actually refreshed and verified.

## 13. Implementation Notes

The wording should avoid this phrase:

```text
enter Plan Mode before drafting or asking
```

because it is ambiguous. It can be misread as “draft PRD file in Plan Mode.”

Prefer this wording:

```text
enter Plan Mode before durable PRD writing, issue slicing, implementation,
or multi-question clarification. Plan Mode may produce a conversation draft,
PRD boundary, artifact recommendation, or one highest-impact question.
```

Also avoid:

```text
Plan Mode writes the PRD
```

Use:

```text
Plan Mode shapes the PRD boundary.
A write-capable route writes the durable artifact after acceptance.
```

## 14. Review Checklist

Reviewer should verify:

* `to-prd` frontmatter has Plan Mode trigger language.
* `to-prd` body has Plan Mode intake workflow.
* `to-prd` body forbids durable artifact writes from Plan Mode/read-only/chat-only.
* Shared grilling does not steal all `grill-me` prompts into `to-prd`.
* Plugin defaultPrompt remains light.
* Evals include positive and hard-negative cases.
* No public skill added.
* No version bump or marketplace packaging change.
* Validation commands are reported honestly.

## 15. Risks and Mitigations

| Risk                                   | Impact | Mitigation                                                                                 |
| -------------------------------------- | -----: | ------------------------------------------------------------------------------------------ |
| Runtime still skips `to-prd`           |   High | Put discriminator in `to-prd` frontmatter, not only body/defaultPrompt.                    |
| Plan Mode wording suggests file writes |   High | Use “boundary/conversation draft/artifact recommendation” wording and add STOP checkpoint. |
| `grill-me` becomes all `to-prd`        | Medium | Keep shared grilling route decision and route negatives.                                   |
| DefaultPrompt becomes too broad        | Medium | Keep one concise fallback line.                                                            |
| Runtime evidence overclaimed           | Medium | Require source-validation-only report unless installed plugin/cache was verified.          |
| Plan Mode over-captures accepted work  | Medium | Add accepted-PRD / ready-issue hard negatives and preserve `to-issues`, `write-plan`, and `implement` route exits. |

## 16. Rollout Plan

1. Start a new branch, for example:

```text
codex/plan-mode-prd-intake-prd-boundary
```

2. Implement slices 2–5.
3. Run source validation.
4. Open a new PR with title:

```text
Separate Plan Mode PRD intake from durable artifact writing
```

5. PR body must mention that PR #69 was superseded and closed.
6. Do not merge until reviewer confirms the Plan Mode/write boundary.

## 17. Expected PR Summary

```md
## Summary
- Make to-prd the primary Plan Mode-first entry point for raw requirement, PRD/spec, and grill-me-before-PRD intake.
- Clarify that Plan Mode may shape PRD boundaries and conversation drafts, but must not create/update durable PRD files.
- Keep shared grilling route-aware and preserve direct/decision/prototype/implement/verify negatives.
- Add eval coverage for Plan Mode-first PRD intake, Plan Mode durable-write hard negatives, and accepted downstream route exits.

## Validation
- git diff --check
- python3 -m json.tool .codex-plugin/plugin.json >/dev/null
- python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"

## Evidence Boundary
Source-validation only. No runtime/cache/installed-plugin evidence claimed.
```

## 18. Stop Condition

This PRD is implementation-ready when the maintainer accepts the central decision:

```text
Plan Mode is required before PRD/grill-me intake when available,
but durable PRD artifact writes are forbidden until after plan acceptance
and a write-capable route is active.
```

Recommended next action: implement this PRD with `skills/to-prd/SKILL.md` as the main change and `skills/_shared/GRILLING.md` as the cross-route guardrail.

[1]: https://developers.openai.com/codex/cli/slash-commands "Slash commands in Codex CLI | OpenAI Developers"
[2]: https://developers.openai.com/codex/app/commands "Commands – Codex app | OpenAI Developers"
[3]: https://developers.openai.com/codex/cli/features "Features – Codex CLI | OpenAI Developers"
[4]: https://developers.openai.com/codex/ide/features "Features – Codex IDE | OpenAI Developers"
