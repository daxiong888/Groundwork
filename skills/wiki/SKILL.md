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

Load `skills/_shared/LLM-WIKI.md` before wiki IO; it owns storage, frontmatter, citations, stale/conflict handling, raw sources, external-tool boundary, and output shape.

For Groundwork repo maintenance, apply repo-local `AGENTS.md` before reporting complete.

Load only when material: lifecycle for durable creation/updates, audience-first for reports/audits/contracts, domain language for terms that affect truth, and evidence/role/runtime/non-executor refs only for stronger readiness/runtime/cache/release/UAT/customer claims.

Wiki synthesis is orientation unless claim-level citations and stronger source checks support a stronger boundary.

## Wiki Root Discovery

Before wiki IO: inspect `wiki/`, then artifact-scoped `artifacts/wiki/`; report `Wiki Status: missing` if absent; inspect `.groundwork/wiki/` only for explicit private scratch; ask before adopting parent/sibling roots.

Storage modes: `shared_project_wiki -> wiki/`, `artifact_scoped_wiki -> artifacts/wiki/`, `private_scratch_wiki -> .groundwork/wiki/`.

## Modes

`init`, `ingest`, `query`, `audit`, `update`, `deprecate/archive`, and `repair` are allowed. In every mode: classify storage first; cite source pages; keep contested/stale claims labeled; update `index.md`/`log.md` when pages change; do not overwrite raw source truth. Audit means wiki health only, not release readiness; default `quick`, use `focused`/`full` only when requested.

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
- Do not block normal `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` because a wiki is absent.
- Do not copy repo source wholesale into `wiki/raw/`, mutate raw source truth, or add diaries, memory, vector DBs, graphs, external config, hooks, or MCP servers by default.

## Failure Shapes

For missing wiki, source access gaps, contested/stale/uncited claims, or route conflict, name requested action, affected page/claim, available evidence, current answer boundary, safe fallback, promotion blocker, and next route.

## Output Shape

Use `Wiki Summary` or `Wiki Query Answer` with mode/question, root/pages/sources inspected, changes or answer, evidence boundary, checks, gaps/stale claims, recommended wiki update, and next route.

For audits, use the exact `Wiki Audit Scope` block before findings.

## Stop Condition

Stop when the scoped wiki operation is complete, safely declined as a route conflict/missing evidence, or blocked with the next source check. Final readiness belongs to `verify`; public skill approval belongs to independent clean review or maintainer acceptance.

## Artifact Rule

Follow `skills/_shared/LLM-WIKI.md` for wiki pages/templates, `skills/_shared/AUDIENCE-FIRST-ARTIFACT.md` for durable reports/contracts, and `skills/_shared/ARTIFACT-DIRECTORY-POLICY.md` for committed placement. Redact secrets, credentials, PII, sensitive logs, screenshots, requests, database rows, private URLs, cookies, and tokens.
