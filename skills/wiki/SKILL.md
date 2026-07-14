---
name: wiki
description: Explicit project-level LLM Wiki create, ingest, query, audit, update, deprecate/archive, or repair. Not for direct answers, PRD shaping, slicing, implementation, verification, handoff, dispatch, or scratch notes.
---

# wiki

## Trigger Contract

Use for explicit project-level LLM Wiki init, ingest, query, audit, update, deprecate/archive, or repair.

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

Load only when material: `skills/_shared/LIFECYCLE-PREFLIGHT.md` for durable create/update; audience-first for reports/audits/contracts; domain language for truth-bearing terms; evidence/role/runtime/non-executor refs only for readiness/runtime/cache/release/UAT/customer claims.

Wiki synthesis is orientation unless claim-level citations and source checks support a stronger boundary.

## Wiki Root Discovery

Before wiki IO: inspect `wiki/`, then `artifacts/wiki/`; report `Wiki Status: missing` if absent; inspect `.groundwork/wiki/` only for explicit private scratch; ask before parent/sibling roots.

Storage modes: `shared_project_wiki -> wiki/`, `artifact_scoped_wiki -> artifacts/wiki/`, `private_scratch_wiki -> .groundwork/wiki/`.

## Modes

Allowed modes: `init`, `ingest`, `query`, `audit`, `update`, `deprecate/archive`, `repair`. Classify storage first; cite pages; label contested/stale claims; update `index.md`/`log.md` when pages change; do not overwrite raw source truth. Audit means wiki health only, not release readiness; default `quick`, use `focused`/`full` only when requested.

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

For missing wiki, source gaps, contested/stale/uncited claims, or route conflict, name requested action, affected page/claim, available evidence, answer boundary, fallback, promotion blocker, and next route.

## Output Shape

Default to `Wiki Summary` or `Wiki Query Answer` with the answer/change, cited pages or sources, material stale/conflict/gap boundary, and next action when needed. Add mode, root, checks, recommended update, or next route only when they affect the result.

For focused/full audits or machine-consumed reports, use the exact `Wiki Audit Scope` block before findings. A quick audit may state root, inspected pages, material limitations, and findings in compact prose.

## Stop Condition

Stop when complete, safely declined, or blocked with next source check. Final readiness belongs to `verify`; public skill approval belongs to independent clean review or maintainer acceptance.

## Artifact Rule

Follow `skills/_shared/LLM-WIKI.md` for pages/templates, audience/artifact policy for durable reports/contracts and placement. Redact secrets, credentials, PII, sensitive logs, screenshots, requests, database rows, private URLs, cookies, and tokens.
