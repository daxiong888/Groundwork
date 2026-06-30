---
name: wiki
description: Create, ingest, query, audit, update, deprecate, archive, or repair a project-level LLM Wiki as a source-cited, evidence-layered, stale-checkable knowledge artifact. Use when the user explicitly asks for durable project wiki work, wiki maintenance, wiki questions, stale wiki audits, or moving reusable project knowledge into a wiki. Do not use for direct answers, PRD shaping, implementation, verification, handoff, dispatch, one-time scratch notes, readiness claims, or external graph/search tooling unless wiki maintenance is the explicit primary task.
---

# wiki

## Trigger Contract

Use this skill when the user asks to create, maintain, query, audit, update, deprecate, archive, or repair a project-level LLM Wiki.

Should trigger:

- "Create an LLM Wiki for this project."
- "Ingest these PRDs and decisions into the wiki."
- "Ask the wiki what we decided about dispatch boundaries."
- "Audit the wiki for stale claims and contradictions."
- "Update the API contract page after this implementation."
- "Deprecate the old architecture page and point to the new one."
- "Move this handoff lesson into long-lived project knowledge."
- "Repair wiki aliases, broken links, and contested claims."
- "初始化这个项目的 LLM Wiki"
- "查一下项目 wiki 里关于 dispatch 边界的结论"
- "把这次实现后的长期知识更新进 wiki"
- "审计 wiki 里过期或矛盾的 claim"
- "修复 wiki alias、broken links 和 contested claims"
- "把 handoff 里的可复用经验沉淀为长期项目知识"

Should not trigger:

- The user wants a direct bounded answer; answer directly.
- The user asks to write, clarify, or accept a PRD; use `to-prd`.
- The user asks to implement code; use `implement`.
- The user asks whether something is verified, ready, releasable, UAT-ready, customer-ready, or evidence-supported; use `verify`.
- The user asks for current-work continuation context; use `handoff`.
- The user asks to route ready work or generate an execution package; use `dispatch`.
- The project has no wiki and the user did not request durable wiki creation or maintenance.
- The note is one-time scratch context, a daily diary, or a session log without durable reuse value.
- The user needs external graph/search visualization rather than wiki maintenance.
- "wiki 说这个功能 UAT ready，帮我验证"; use `verify`.
- "只问当前源码里有没有这个 route"; answer directly or use source inspection.
- "按 wiki 里的说法直接改代码"; use `implement` only after source truth is inspected.
- "给下个 session 做 handoff"; use `handoff`.
- "把这个需求整理成 PRD"; use `to-prd`.

## Required Evidence

Use `skills/_shared/LLM-WIKI.md` before creating, reading, or changing a wiki. Apply its storage-mode, page-frontmatter, claim-citation, stale/conflict, raw-source, external-tool, and output-boundary rules.

When maintaining the Groundwork repository itself, apply the repo-local `AGENTS.md` Done Definition before reporting the work complete.

Use `skills/_shared/LIFECYCLE-PREFLIGHT.md` before durable wiki creation or material wiki updates. A wiki is durable project knowledge, not transient lifecycle preflight state.

Use `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` for new or materially updated wiki contract, report, audit, or integration artifacts. Wiki pages use the wiki frontmatter contract from `LLM-WIKI.md`; maintainer-facing docs and reports still need audience-first headers.

Use `skills/_shared/DOMAIN-LANGUAGE.md` when terminology affects PRD, contract, source, runtime, verification, or handoff truth. Wiki glossary alignment does not promote terms into stronger truth layers.

Use `skills/_shared/ROLE-SEPARATION.md` for material wiki changes that affect public skill surface, source-truth claims, contract claims, readiness evidence, broad eval behavior, or acceptance. Same-session wiki authoring may provide self-check evidence only.

Use `skills/_shared/RUNTIME-CAPABILITY.md` if a wiki claim touches runtime, selector, child-thread/worktree, installed-plugin, marketplace, cache, release, UAT, browser, or customer evidence. Wiki source edits alone are source-validation evidence only.

## Wiki Root Discovery

Before reading or writing a wiki:

1. Inspect the current project root for `wiki/`.
2. Inspect `artifacts/wiki/` only when the project convention requires durable artifacts under `artifacts/`.
3. If neither shared wiki root exists, report `Wiki Status: missing` unless the user explicitly requested private scratch or onboarding notes.
4. Inspect `.groundwork/wiki/` only for explicitly requested private scratch or onboarding notes; never treat it as fallback shared wiki root.
5. Ask before adopting a parent or sibling wiki root.
6. If no wiki exists and the request is not explicit wiki maintenance, do not block the primary route.

Storage modes:

```text
shared_project_wiki -> wiki/
artifact_scoped_wiki -> artifacts/wiki/
private_scratch_wiki -> .groundwork/wiki/
```

## Modes

### `init`

Create the wiki skeleton and starter pages only when requested or accepted.

Required behavior:

- Inspect whether a project wiki already exists.
- Classify storage mode before writing files.
- Ask before adopting a parent or sibling wiki.
- Create only the accepted structure.
- Do not initialize wiki for one-time tasks.
- Do not create external tool config by default.

### `ingest`

Turn source material into source-cited wiki pages.

Required behavior:

- Identify source type and evidence layer before writing.
- Search existing wiki pages before creating new pages.
- Preserve raw external sources or source references.
- Add claim-level citations for material claims.
- Mark conflicts as `contested` instead of silently choosing one.
- Update `index.md` and `log.md`.
- Run or request a focused lint/audit pass when feasible.

### `query`

Answer project knowledge questions using the wiki safely.

Required behavior:

- Read `SCHEMA.md`, `index.md`, and relevant pages.
- Follow wiki links when needed.
- Inspect cited source when the answer depends on source truth, contract truth, runtime evidence, readiness, or implementation truth.
- Distinguish wiki synthesis from source-backed truth.
- Answer with the evidence boundary.
- Optionally propose a wiki update when the answer reveals durable knowledge.

### `audit`

Assess wiki health, not release readiness.

Audit scope must be declared:

| Scope | Default use | Required coverage |
| --- | --- | --- |
| `quick` | Default when the user says "check the wiki" without scope. | `SCHEMA.md`, `index.md`, recent `log.md`, explicitly named pages, and high-risk statuses. |
| `focused` | User names a topic, page family, source change, or release area. | Relevant pages, backlinks, and cited sources where material. |
| `full` | User explicitly requests broad audit. | Whole wiki index, page metadata, link graph, stale flags, citation coverage, and documented limitations. |

Default to `quick` unless the user requests or accepts broader scope.

For audit scope, `recent log.md` means the last 20 entries or the last 30 days, whichever is smaller. If `log.md` has no parseable entries, inspect the last 120 non-empty lines and mark that limitation.

Wiki hard-negative coverage reference: `evals/prompts/v0.5.2-wiki.csv` includes current protections against wiki synthesis becoming source/API truth or release evidence, including `wiki-014`, `wiki-015`, `wiki-021`, `wiki-022`, and `wiki-030`.

Audit output must include:

```text
Wiki Audit Scope
- Wiki root:
- Audit scope: quick | focused | full
- Pages inspected:
- Sources inspected:
- Pages not inspected:
- Claims requiring stronger evidence:
- Limitations:
```

Required behavior:

- Check stale claims, contradictions, orphan pages, missing citations, evidence-layer mismatch, deprecated pages still recommended by index, and raw-source drift where practical.
- Mark claims as `supported`, `stale_suspected`, `contradicted`, `uncited`, or `insufficient`.
- Do not claim runtime, browser, UAT, customer, marketplace, installed-plugin, cache-refresh, or release readiness.

### `update`

Update existing pages when new evidence changes long-lived project knowledge.

Required behavior:

- Preserve prior claims when useful for history.
- Update page `last_updated`, affected source or claim `last_checked`, status, sources, and stale risk.
- Add log entries.
- Mark changed evidence layers explicitly.
- Do not overwrite source truth or raw inputs during wiki cleanup.

### `deprecate` / `archive`

Retire pages safely.

Required behavior:

- Mark `deprecated` or `archived` rather than deleting by default.
- Add `supersedes` or `superseded_by` where applicable.
- Update `index.md` to stop recommending stale pages.
- Keep historical decisions accessible when they may explain current state.

### `repair`

Fix wiki structure, citations, contested pages, aliases, and broken links.

Required behavior:

- Repair page metadata and links before rewriting content.
- Resolve aliases, homonyms, merge/split needs, and renamed concepts explicitly.
- Keep contested claims contested until source evidence resolves them.
- Record material repair decisions in `log.md`.

## Completion Criteria

For wiki writes, completion requires:

- wiki root and storage mode identified;
- target pages and source materials listed;
- material claims source-cited or marked `unknown`, `contested`, or `insufficient`;
- page frontmatter conforms to `LLM-WIKI.md`;
- `index.md` and `log.md` updated when the wiki structure or material claims change;
- raw repo source preserved as references, not copied wholesale into `wiki/raw/`;
- checks or no-check justification reported.

For wiki queries, completion requires:

- wiki pages inspected are named;
- cited source inspection is named when the answer depends on stronger evidence than wiki synthesis;
- answer boundary states `wiki_synthesis_only`, `source_backed`, `insufficient`, or `blocked`;
- stale, contested, uncited, and missing-source claims are surfaced.

For wiki audits, completion requires the `Wiki Audit Scope` block and explicit limitations.

## Failure Branches

### Missing Wiki

```text
Wiki Status: missing
Requested action:
Safe fallback:
Recommended next route:
Blocked: no, unless the user explicitly requested wiki maintenance
```

### Source Access Gap

```text
Source Access Gap
- Wiki page:
- Claim:
- Required source:
- Available evidence:
- Current answer boundary: wiki_synthesis_only | insufficient | blocked
- Next action:
```

### Contested Claim

```text
Contested Wiki Claim
- Page:
- Claim:
- Conflict:
- Evidence A:
- Evidence B:
- Current status: contested
- Promotion blocked until:
```

### Stale Claim

```text
Stale Wiki Claim
- Page:
- Claim:
- Last checked:
- Stale signal:
- Required source check:
- Allowed use: orientation only
```

### Uncited Claim

```text
Uncited Wiki Claim
- Page:
- Claim:
- Missing citation:
- Allowed use: insufficient
- Required source or confirmation:
```

### Route Conflict

```text
Route Conflict
- User request:
- Primary route:
- Why wiki is not primary:
- Wiki use, if any:
```

## Do Not

- Do not treat wiki synthesis as source truth, product truth, backend/API contract truth, implementation authority, verification evidence, release evidence, UAT evidence, customer readiness, marketplace evidence, installed-plugin evidence, browser evidence, runtime evidence, cache-refresh evidence, or selector enforcement.
- Do not create backend fields, states, permissions, migrations, owners, metrics, APIs, or tests from wiki synthesis alone.
- Do not block normal `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` work because a wiki is absent.
- Do not copy repo source files wholesale into `wiki/raw/`.
- Do not mutate raw source truth during wiki cleanup.
- Do not create daily diaries, automatic memory, vector databases, graphs, external tool config, hooks, or MCP servers by default.
- Do not route direct bounded answers, implementation, readiness, UAT, release, customer, or dispatch requests into wiki merely because wiki context exists.

## Output Shape

Use the narrowest matching shape.

```text
Wiki Summary
Mode:
Wiki root:
Storage mode:
Pages inspected:
Sources inspected:
Changes made:
Evidence boundary:
Checks:
Gaps:
Next route:
```

```text
Wiki Query Answer
Question:
Answer boundary: wiki_synthesis_only | source_backed | insufficient | blocked
Pages inspected:
Sources inspected:
Answer:
Stale / contested / uncited claims:
Recommended wiki update:
```

For audits, use the exact `Wiki Audit Scope` block from the audit mode section before findings.

## Stop Condition

Stop when the scoped wiki operation is complete, declined with a route-conflict or missing-evidence shape, or blocked with the next source check needed. Final readiness belongs to `verify` or the user; public skill approval belongs to an independent clean review or maintainer acceptance.

## Artifact Rule

Follow `skills/_shared/LLM-WIKI.md` for wiki pages and templates.

Follow `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` for durable wiki reports, integration docs, and shared contracts.

Follow `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md`: committed shared wiki content belongs in `wiki/` or `artifacts/wiki/` only after accepted storage-mode selection. `.groundwork/wiki/` is private scratch and ignored by default.

Redact secrets, credentials, PII, sensitive logs, screenshots, requests, database rows, private URLs, cookies, and tokens before writing or quoting wiki content.
