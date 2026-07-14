Target Reader: wiki authors, skill authors, implementers, clean reviewers, verifiers, handoff authors, and maintainers handling long-lived project knowledge.
Reader Action Needed: use before creating, ingesting, querying, auditing, updating, deprecating, archiving, or repairing a project LLM Wiki.
Decision Supported: whether wiki work is cited, evidence-layered, stale-checkable, and bounded away from source-truth/readiness overclaims.
Artifact Type: shared artifact contract.
Source of Truth: `docs/prd-v0.5.2-public-wiki-skill.md` V052-002 and shared evidence boundaries.
Scope: storage modes, page shape, citations, evidence layers, stale/conflict handling, raw-source/external-tool boundaries, audit scope, update candidates.
Out of Scope: runtime execution, installed-plugin behavior, marketplace publishing, release/UAT/customer readiness, source mutation, auto-memory, graph/vector stores, MCP servers, hooks, or replacing public skills.
Evidence Level: source-validation policy only.

# LLM Wiki Contract

## Core Rule

A Groundwork wiki is compiled orientation and claim inventory. It is not source truth, product truth, backend/API contract truth, implementation authority, verification evidence, release/UAT/customer readiness, marketplace evidence, installed-plugin evidence, browser/runtime evidence, cache-refresh evidence, or selector enforcement.

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
| `shared_project_wiki` | `wiki/` | accepted long-lived team/project knowledge | source truth/readiness evidence |
| `artifact_scoped_wiki` | `artifacts/wiki/` | project convention requires artifacts-only durable knowledge | feature issue map |
| `private_scratch_wiki` | `.groundwork/wiki/` | temporary personal exploration/onboarding | shared project truth |

Do not create wiki for one-time scratch, adopt parent/sibling roots silently, or promote `.groundwork/wiki/` without source/redaction review.

Default inner shape: `SCHEMA.md`, `index.md`, `log.md`, `error-book.md`, `raw/`, `concepts/`, `decisions/`, `contracts/`, `procedures/`, `summaries/`, `queries/`, `terms/`, `_archive/`, `reports/`.

## Page Frontmatter

Create typed pages from `skills/wiki/templates/page.md` and apply the selected profile and exact section order from `skills/wiki/templates/PAGE-TYPES.md`.

```yaml
---
type: "<concept | decision | contract | procedure | summary | query | term>"
status: draft
target_reader: "<from PAGE-TYPES.md>"
reader_action: "<from PAGE-TYPES.md>"
default_evidence_layer: "<from PAGE-TYPES.md>"
confidence: low
sources: []
last_updated: "<YYYY-MM-DD>"
stale_risk: "<from PAGE-TYPES.md>"
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
Allowed `confidence`: `high | medium | low`; `stale_risk`: `low | medium | high`.

Page-level `sources` is inventory only. Material claims require claim-level citation.

## Material Claims

Material claims affect behavior, implementation, API/schema/DB/frontend-backend contracts, permissions, data correctness, verification, release, UAT, customer commitments, architecture, operations, or routing.

Each material claim needs claim, evidence layer, source, last checked, stale risk, and promotion blocker. Mixed-evidence pages label material claims individually. Missing, stale, contested, or uncited claims stay marked and must not be promoted.

| Layer | Meaning | Must not become |
| --- | --- | --- |
| `glossary_only` | wording alignment | PRD/contract/source/readiness truth |
| `PRD_truth` | accepted product/spec intent | backend/API/source truth |
| `contract_truth` | accepted API/schema/DB/frontend-backend contract | runtime/UAT/release truth |
| `source_truth` | inspected source/schema/docs-as-source/authoritative artifact | runtime/browser/UAT/release behavior |
| `runtime_evidence` | scoped runtime/tool/API/browser observation | universal truth |
| `user_confirmed` | explicit confirmation for stated boundary | broader truth |
| `unknown` | insufficient evidence | promoted truth |

`last_updated` changes when page changes; claim/source `last_checked` changes only when cited evidence is re-inspected. Status: `draft` incomplete, `active` orientation, `contested` conflict, `stale_suspected` inspect before reuse, `deprecated` superseded history, `archived` historical only.

## Boundaries

- Do not copy repo source wholesale into `wiki/raw/`; record paths, refs, dates, and claim-level links.
- Use `wiki/raw/` for external articles, papers, meeting/user notes, extracted PDF text, screenshot descriptions, or non-repo inputs needing durable capture.
- Never mutate raw source truth during wiki cleanup.
- External search/graph/index/memory tools are recall aids until tied back to sources.
- Do not add graph/vector stores, hooks, MCP servers, or auto-memory as MVP dependencies.

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
- Why reusable:
- Must not auto-apply because:
- Recommended next route: wiki
```

Advisory only unless the user explicitly requested wiki maintenance. Do not update wiki from implementation self-summary alone when source, contract, runtime, or verification evidence is required. Do not create wiki diaries.

## Existing Skill Use

- `to-prd`: wiki context may reduce questions but never proves PRD acceptance.
- `implement`: wiki can orient paths; code changes still require source/contracts/tests/authoritative artifacts and must not invent fields/APIs/states/permissions/migrations/owners/metrics/tests.
- `verify`: wiki is claim inventory; inspect cited source/test/runtime/browser/release/cache/UAT evidence.
- `handoff`: wiki is orientation/update candidate, not clean review, verification, runtime, release, UAT, marketplace, installed-plugin, or cache-refresh evidence.
- `dispatch`: wiki is non-authoritative orientation; downstream source inspection remains required.

Absence of a wiki must not block normal `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` unless wiki maintenance was requested.

## Audit Scope

| Scope | Default use | Required coverage |
| --- | --- | --- |
| `quick` | unspecified wiki check | `SCHEMA.md`, `index.md`, recent `log.md`, named pages, high-risk statuses |
| `focused` | topic/page/source/release area named | relevant pages, backlinks, material cited sources |
| `full` | explicit broad audit | whole index, metadata, links, stale flags, citations, limitations |

Recent `log.md` means last 20 entries or 30 days; if unparseable, inspect last 120 non-empty lines and mark limitation.

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

Use compact blocks for:

- `Wiki Status: missing`: requested action, safe fallback, next route, and blocked status.
- `Source Access Gap`: page, claim, required source, available evidence, answer boundary, next action.
- `Contested Wiki Claim`: page, claim, conflict, Evidence A/B, status, promotion blocker.
- `Stale Wiki Claim`: page, claim, last checked, stale signal, required source check, allowed use.
- `Uncited Wiki Claim`: page, claim, missing citation, allowed use, required source/confirmation.

## Template Set

Starter templates live under `skills/wiki/templates/`: `SCHEMA.md`, `index.md`, `log.md`, `error-book.md`, the shared `page.md` base, and `PAGE-TYPES.md` type-profile/section contract. Copy only after selecting storage mode; replace date and profile placeholders, then update sources and statuses.
