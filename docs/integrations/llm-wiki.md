Target Reader: Groundwork maintainers, skill authors, and project leads deciding whether and how to create a project LLM Wiki.
Reader Action Needed: Use this guide to decide wiki placement, creation timing, skill interaction, evidence boundaries, and page retirement rules before authoring or reviewing wiki artifacts.
Decision Supported: Whether a project should maintain an LLM Wiki, where the wiki should live, how public skills may use it, what evidence claims it can support, and how to deprecate or archive pages safely.
Artifact Type: maintainer integration guide.
Source of Truth: `docs/prd-v0.5.2-public-wiki-skill.md`, `skills/wiki/SKILL.md`, `skills/_shared/LLM-WIKI.md`, and `skills/wiki/templates/`.
Scope: Source-validation guidance for project wiki creation, storage modes, skill integration, claim boundaries, maintenance, deprecation, archive, and review.
Out of Scope: Runtime execution, installed-plugin behavior, marketplace publishing, release readiness, UAT readiness, customer acceptance, browser evidence, cache/source refresh, selector enforcement, MCP servers, hooks, graph/vector stores, or external wiki tools.
Evidence Level: Source-validation guidance only. This guide does not prove runtime, marketplace, installed-plugin, cache-refresh, browser, UAT, release, selector, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private URLs, cookies, tokens, raw production payloads, or sensitive logs.

# LLM Wiki Integration Guide

## When to Create a Wiki

Create or propose a project wiki only when the knowledge is durable, reusable, and project-level.

Good fit:

- recurring project terms, aliases, and term conflicts;
- long-lived architecture or workflow decisions;
- stable API, schema, or frontend/backend contract summaries that cite source;
- procedures future sessions will repeat;
- error-book entries with source-backed diagnosis and mitigation;
- reusable Q&A that would otherwise be rediscovered across sessions.

Not a good fit:

- one-off session notes;
- daily diaries or chronological status logs;
- raw implementation summaries without source review;
- prototype-only labels not confirmed by source or contract;
- runtime, release, UAT, marketplace, installed-plugin, cache-refresh, or selector claims without separate evidence.

> [!IMPORTANT]
> A wiki is orientation and claim inventory. It is not source truth, product truth, implementation authority, verification pass evidence, release evidence, UAT evidence, marketplace evidence, installed-plugin evidence, or cache-refresh evidence.

## Storage Decision

Use the storage modes from `skills/_shared/LLM-WIKI.md`:

| Mode | Location | Use when |
| --- | --- | --- |
| `shared_project_wiki` | `wiki/` | The team accepts project-level durable knowledge in the repository. |
| `artifact_scoped_wiki` | `artifacts/wiki/` | The project requires all durable knowledge under `artifacts/`. |
| `private_scratch_wiki` | `.groundwork/wiki/` | The work is temporary personal exploration and should not be committed by default. |

Default to `wiki/` only after the user asks for durable project wiki creation or accepts the proposal. Do not silently adopt parent or sibling wiki roots.

## Starter Files

Use `skills/wiki/templates/` as the starter set:

- `SCHEMA.md`
- `index.md`
- `log.md`
- `error-book.md`
- `page.md`, the shared typed-page base
- `PAGE-TYPES.md`, the type-profile and exact section-order contract

Copy only the files required by the accepted storage mode. For each authored page, start from `page.md`, apply one profile from `PAGE-TYPES.md`, replace every date/profile placeholder, and update sources, status, stale risk, aliases, and evidence layers for the actual project.

## Skill Interaction

`wiki` owns project wiki lifecycle: init, ingest, query, audit, update, deprecate, archive, and repair. Other skills may use wiki context only inside their primary route.

| Skill | Allowed wiki use | Required boundary |
| --- | --- | --- |
| `to-prd` | Read pages as orientation; follow cited sources for material facts; propose durable update candidates. | Wiki is not PRD acceptance or product truth. |
| `implement` | Use wiki to find likely files, concepts, decisions, or stale-risk areas. | Inspect source, contracts, tests, or authoritative artifacts before code changes. |
| `verify` | Treat wiki pages as claim inventory. | Inspect claim-specific source, test, runtime, release, cache/source, browser, UAT, or customer evidence before passing a claim. |
| `handoff` | Cite wiki as orientation; propose a candidate for reusable knowledge. | Do not turn handoffs into wiki diaries or readiness evidence. |
| `dispatch` | Package wiki context as orientation for accepted work. | Do not treat wiki context as runtime execution, verification, clean review, selector, release, UAT, marketplace, installed-plugin, or cache-refresh evidence. |

If a project has no wiki, normal `to-prd`, `implement`, `verify`, `handoff`, and `dispatch` work continues unless the user explicitly requested wiki maintenance.

## Wiki Update Candidate

Existing skills should not update wiki pages unless the user explicitly includes wiki maintenance in the current request. They may emit this advisory shape:

```text
Wiki Update Candidate
- Candidate action: create | update | deprecate | archive | repair
- Proposed page:
- Durable knowledge:
- Evidence source:
- Evidence layer:
- Suggested status:
- Stale risk:
- Why this is reusable:
- Must not auto-apply because:
- Recommended next route: wiki
```

Use a candidate when durable reusable knowledge appears during PRD shaping, implementation, verification, handoff, or dispatch. Do not emit candidates for one-time notes, chat history, raw logs, or implementation self-summaries that still need source review.

## Claim Rules

Material claims need claim-level evidence. Page-level `sources` is only an inventory.

Material claims include anything that could affect:

- product behavior;
- implementation;
- API, schema, DB, permissions, or frontend/backend contract;
- data correctness;
- verification;
- release, UAT, customer commitments, or readiness;
- architecture, operational procedures, or future task routing.

If a claim is stale, contested, uncited, page-level-source-only, glossary-only, or source-inaccessible, keep it as orientation and mark the stronger claim as insufficient or blocked until source evidence is inspected.

## Query and Audit Boundaries

`wiki query` may answer from wiki synthesis only when the requested answer does not require stronger evidence. If the answer depends on source truth, contract truth, runtime behavior, implementation, release, UAT, marketplace, installed-plugin, cache-refresh, browser behavior, or selector enforcement, inspect the cited evidence or report the gap.

`wiki audit` reports wiki health only. It must declare `quick`, `focused`, or `full` scope and name limitations. A wiki audit does not prove release readiness, runtime behavior, UAT readiness, customer readiness, marketplace state, installed-plugin behavior, or cache/source refresh.

## Deprecate and Archive

Prefer status changes over deletion:

- `deprecated`: page is superseded but may explain current state.
- `archived`: page should not guide active work except historical investigation.

When deprecating or archiving:

1. Update page status.
2. Add `supersedes` or `superseded_by` links where applicable.
3. Update `index.md` so active readers do not follow obsolete pages by default.
4. Add a `log.md` entry.
5. Keep contested or historical claims visible when they explain a decision.

Do not rewrite raw source truth during cleanup. For repo files, record paths, refs, and claim-level links instead of copying source files wholesale into `wiki/raw/`.

## Review Checklist

Before accepting a wiki change:

- Storage mode and root are explicit.
- Page frontmatter follows `skills/_shared/LLM-WIKI.md`.
- Material claims have claim-level citations or are marked insufficient.
- Stale, contested, uncited, deprecated, and archived states are visible.
- `index.md` and `log.md` are updated when structure or material claims changed.
- No secrets, credentials, PII, private URLs, cookies, tokens, raw production payloads, or sensitive logs were copied.
- No runtime, UAT, release, marketplace, installed-plugin, cache-refresh, selector, or customer readiness claim is made without separate named evidence.

## References

- `skills/wiki/SKILL.md`
- `skills/_shared/LLM-WIKI.md`
- `skills/_shared/SKILL-QUALITY.md`
- `skills/_shared/DOMAIN-LANGUAGE.md`
- `skills/_shared/ROLE-SEPARATION.md`
- `skills/_shared/RUNTIME-CAPABILITY.md`
- `skills/wiki/templates/`
