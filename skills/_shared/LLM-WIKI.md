Target Reader: Groundwork wiki authors, skill authors, implementers, clean reviewers, verifiers, handoff authors, and maintainers handling project-level long-lived knowledge.
Reader Action Needed: Use before creating, ingesting, querying, auditing, updating, deprecating, archiving, or repairing a project LLM Wiki.
Decision Supported: Whether a wiki operation is source-cited, evidence-layered, stale-checkable, and bounded away from source-truth/readiness overclaims.
Artifact Type: shared artifact contract.
Source of Truth: `docs/prd-v0.5.2-public-wiki-skill.md` V052-002 and shared evidence boundaries.
Scope: Wiki storage modes, directory shape, page frontmatter, claim citation, evidence layers, stale/conflict handling, raw-source boundaries, external-tool boundaries, audit scope, and wiki update candidates.
Out of Scope: Runtime execution, installed-plugin behavior, marketplace publishing, release readiness, UAT readiness, customer acceptance, source mutation, auto-memory, graph/vector stores, MCP servers, hooks, or replacing public skills.
Evidence Level: Source-validation policy only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private URLs, cookies, tokens, raw production payloads, or sensitive logs.

# LLM Wiki Contract

## Core Rule

A Groundwork wiki is compiled orientation and claim inventory. It is not source truth, product truth, backend/API contract truth, implementation authority, verification evidence, release evidence, UAT evidence, customer readiness, marketplace evidence, installed-plugin evidence, browser evidence, runtime evidence, cache-refresh evidence, or selector enforcement.

```text
wiki synthesis != source truth
wiki source inventory != claim-level citation
wiki stale check != verification pass
wiki audit != release readiness
graph/search/index output != authority
```

## Storage And Shape

| Mode | Location | Use when | Must not become |
| --- | --- | --- | --- |
| `shared_project_wiki` | `wiki/` | long-lived team/project knowledge after acceptance | source truth or readiness evidence |
| `artifact_scoped_wiki` | `artifacts/wiki/` | project convention requires artifacts-only durable knowledge | feature issue map |
| `private_scratch_wiki` | `.groundwork/wiki/` | temporary personal exploration/onboarding | shared project truth |

Do not create wiki for one-time scratch, adopt parent/sibling roots silently, or promote `.groundwork/wiki/` without source and redaction review.

Default inner shape: `SCHEMA.md`, `index.md`, `log.md`, `error-book.md`, `raw/`, `concepts/`, `decisions/`, `contracts/`, `procedures/`, `summaries/`, `queries/`, `terms/`, `_archive/`, `reports/`.

## Page Frontmatter

```yaml
---
type: concept
status: draft
target_reader: "Project maintainers and future agent sessions"
reader_action: "Use for orientation only; inspect cited source before implementation or verification."
default_evidence_layer: unknown
confidence: low
sources: []
last_updated: 2026-06-26
stale_risk: medium
aliases: []
supersedes: []
superseded_by: []
contested_with: []
claim_policy: claim_level_citations_required
---
```

Allowed `type`: `concept | decision | contract | procedure | summary | query | term`.
Allowed `status`: `draft | active | contested | stale_suspected | deprecated | archived`.
Allowed `default_evidence_layer`: `glossary_only | PRD_truth | contract_truth | source_truth | runtime_evidence | user_confirmed | unknown`.
Allowed `confidence`: `high | medium | low`.
Allowed `stale_risk`: `low | medium | high`.

Page-level `sources` is an inventory only. Material claims require claim-level citation.

## Material Claims

Material claims can affect behavior, implementation, API/schema/DB/frontend-backend contracts, permissions, data correctness, verification, release, UAT, customer commitments, architecture, operations, or task routing.

Use a block, table row, or inline equivalent with: claim, evidence layer, source, last checked, stale risk, and promotion blocker. Mixed-evidence pages must label material claims individually. Missing, stale, contested, or uncited claims stay marked and must not be promoted.

Evidence layers:

| Layer | Meaning | Must not become |
| --- | --- | --- |
| `glossary_only` | local wording alignment | PRD/contract/source/readiness truth |
| `PRD_truth` | accepted product/spec intent | backend/API/source truth |
| `contract_truth` | accepted API/schema/DB/frontend-backend contract | runtime/UAT/release truth |
| `source_truth` | inspected source/schema/docs-as-source/authoritative artifact | runtime/browser/UAT/release behavior |
| `runtime_evidence` | scoped runtime/tool/API/browser observation | universal truth |
| `user_confirmed` | explicit confirmation for stated boundary | broader truth |
| `unknown` | insufficient evidence | promoted truth |

## Freshness And Status

`last_updated` changes when the page changes. Claim/source `last_checked` changes only when the cited evidence is re-inspected. Do not update `last_checked` for a page edit alone.

Status semantics: `draft` incomplete; `active` orientation; `contested` conflicting evidence; `stale_suspected` inspect source before reuse; `deprecated` superseded history; `archived` historical only.

## Boundaries

- Do not copy repo source wholesale into `wiki/raw/`; record paths, refs, dates, and claim-level links.
- Use `wiki/raw/` for external articles, papers, meeting notes, user notes, extracted PDF text, screenshot descriptions, or non-repo inputs needing durable capture.
- Never mutate raw source truth during wiki cleanup.
- External search/graph/index/memory tools are recall aids only until tied back to sources.
- Do not add graph/vector stores, hooks, MCP servers, or auto-memory as wiki MVP dependencies.

## Wiki Update Candidate

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

Advisory only unless the current user request explicitly includes wiki maintenance. Do not update wiki from implementation self-summary alone when source, contract, runtime, or verification evidence is required. Do not create wiki diary entries.

## Existing Skill Use

- `to-prd`: wiki context may reduce questions but never proves PRD acceptance; stale/contested/uncited/page-level-only claims require source inspection or clarification.
- `implement`: wiki can orient likely paths; code changes still require source/contracts/tests/authoritative artifacts and must not invent fields/APIs/states/permissions/migrations/owners/metrics/tests.
- `verify`: wiki is claim inventory only; inspect cited source/test/runtime/browser/release/cache/UAT evidence for the claim.
- `handoff`: wiki is orientation or update candidate, not clean review, verification, runtime, release, UAT, marketplace, installed-plugin, or cache-refresh evidence.
- `dispatch`: wiki context is non-authoritative orientation; downstream source inspection remains required.

Absence of a wiki must not block normal `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` unless wiki maintenance was requested.

## Audit Scope

| Scope | Default use | Required coverage |
| --- | --- | --- |
| `quick` | unspecified wiki check | `SCHEMA.md`, `index.md`, recent `log.md`, named pages, high-risk statuses |
| `focused` | topic/page/source/release area named | relevant pages, backlinks, material cited sources |
| `full` | explicit broad audit | whole index, metadata, links, stale flags, citations, limitations |

Recent `log.md` means last 20 entries or 30 days; if unparseable, inspect last 120 non-empty lines and mark limitation.

Audit output:

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

## Failure Shapes

```text
Wiki Status: missing
Requested action:
Safe fallback:
Recommended next route:
Blocked: no, unless the user explicitly requested wiki maintenance
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

```text
Stale Wiki Claim
- Page:
- Claim:
- Last checked:
- Stale signal:
- Required source check:
- Allowed use: orientation only
```

```text
Uncited Wiki Claim
- Page:
- Claim:
- Missing citation:
- Allowed use: insufficient
- Required source or confirmation:
```

## Template Set

Starter templates live under `skills/wiki/templates/`: `SCHEMA.md`, `index.md`, `log.md`, `error-book.md`, `page-concept.md`, `page-decision.md`, `page-contract.md`, `page-procedure.md`, `page-summary.md`, `page-query.md`, `page-term.md`. Copy only after selecting storage mode; update dates, sources, and statuses.
