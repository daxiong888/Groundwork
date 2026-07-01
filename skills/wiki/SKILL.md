---
name: wiki
description: Use only when the user explicitly asks to create, ingest, query, audit, update, deprecate/archive, or repair a project-level LLM Wiki. Not for direct answers, PRD shaping, slicing, implementation, verification, handoff, dispatch, or scratch notes unless wiki maintenance is primary.
---

# wiki

## Trigger Contract

Use for explicit project-level LLM Wiki creation, ingestion, query, audit, update, deprecation/archive, or repair.

Route away:

- Direct bounded answer -> answer directly.
- PRD/spec shaping -> `to-prd`.
- Code edits -> `implement`.
- Readiness, release, UAT, customer, runtime, cache, or evidence proof -> `verify`.
- Continuation context -> `handoff`.
- Runtime/package routing -> `dispatch`.
- One-time scratch, diary, or session log -> do not use wiki unless durable reuse is requested.

## Required Evidence

Load `skills/_shared/LLM-WIKI.md` before creating, reading, or changing a wiki. It owns storage mode, frontmatter, citations, stale/conflict handling, raw sources, external-tool boundary, and output boundary.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Load only when material:

- `skills/_shared/LIFECYCLE-PREFLIGHT.md` for durable wiki creation or material updates.
- `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` for wiki reports, audits, integration docs, or shared contracts; wiki pages use `LLM-WIKI.md` frontmatter.
- `skills/_shared/DOMAIN-LANGUAGE.md` when terminology affects PRD, contract, source, runtime, verification, or handoff truth.
- `skills/_shared/EVIDENCE-BOUNDARY.md`, `ROLE-SEPARATION.md`, `RUNTIME-CAPABILITY.md`, and `NON-EXECUTOR-BOUNDARY.md` for public skill surface, source/contract/readiness/runtime/cache/release/UAT/customer claims.

Wiki synthesis is orientation unless claim-level citations and stronger source checks support a stronger boundary.

## Wiki Root Discovery

Before wiki IO:

1. Inspect current project root for `wiki/`.
2. Inspect `artifacts/wiki/` only when project convention uses artifact-scoped wiki.
3. If neither exists, report `Wiki Status: missing` unless explicit wiki creation/private scratch was requested.
4. Inspect `.groundwork/wiki/` only for explicit private scratch/onboarding notes; never as shared fallback.
5. Ask before adopting parent or sibling wiki roots.

Storage modes: `shared_project_wiki -> wiki/`, `artifact_scoped_wiki -> artifacts/wiki/`, `private_scratch_wiki -> .groundwork/wiki/`.

## Modes

- `init`: create accepted skeleton only after root/storage classification; no external tool config by default.
- `ingest`: source-cited pages; search existing pages first; mark conflicts `contested`; update `index.md` and `log.md`.
- `query`: read `SCHEMA.md`, `index.md`, relevant pages, and cited sources when stronger truth is needed; distinguish wiki synthesis from source-backed truth.
- `audit`: assess wiki health, not release readiness. Default `quick`; use `focused` or `full` only when requested. Include the exact audit scope block below.
- `update`: update page metadata, `last_checked`, evidence layer, status, citations, and `log.md`; do not overwrite raw source truth.
- `deprecate` / `archive`: mark page status, maintain supersedes/superseded_by, update index, keep historical decisions accessible.
- `repair`: fix metadata, links, aliases, contested claims, and split/merge issues; keep contested claims contested until source evidence resolves them.

## Audit Scope Block

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

Quick audit means `SCHEMA.md`, `index.md`, recent `log.md` (last 20 entries or 30 days, else last 120 non-empty lines), named pages, and high-risk statuses.

## Hard Stops

- Do not promote wiki synthesis beyond `EB-WIKI-001`.
- Do not create backend fields, states, permissions, migrations, owners, metrics, APIs, tests, runtime/cache/release/UAT/customer readiness, or task execution from wiki synthesis alone.
- Do not block normal `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` work because a wiki is absent.
- Do not copy repo source wholesale into `wiki/raw/`.
- Do not mutate raw source truth; route source changes to the correct implementation owner.
- Do not create daily diaries, automatic memory, vector databases, graphs, external tool config, hooks, or MCP servers by default.

## Failure Shapes

```text
Wiki Status: missing
Requested action:
Safe fallback:
Recommended next route:
Blocked: no, unless explicit wiki maintenance requires a wiki
```

```text
Source Access Gap
- Wiki page:
- Claim:
- Required source:
- Available evidence:
- Current answer boundary: wiki_synthesis_only | insufficient | blocked
- Next action:
```

For contested, stale, or uncited claims, name page, claim, evidence gap/conflict, allowed use, and promotion blocker.

## Output Shape

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

For audits, use the exact `Wiki Audit Scope` block before findings.

## Stop Condition

Stop when the scoped wiki operation is complete, safely declined as a route conflict/missing evidence, or blocked with the next source check. Final readiness belongs to `verify`; public skill approval belongs to independent clean review or maintainer acceptance.

## Artifact Rule

Follow `skills/_shared/LLM-WIKI.md` for wiki pages/templates, `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` for durable reports/contracts, and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md` for committed placement. Redact secrets, credentials, PII, sensitive logs, screenshots, requests, database rows, private URLs, cookies, and tokens.
