Target Reader: Groundwork wiki authors, skill authors, implementers, clean reviewers, verifiers, handoff authors, and maintainers handling project-level long-lived knowledge.
Reader Action Needed: Use this contract before creating, ingesting, querying, auditing, updating, deprecating, archiving, or repairing a project LLM Wiki.
Decision Supported: Whether a wiki artifact operation is safe, source-cited, evidence-layered, stale-checkable, and bounded away from source-truth or readiness overclaims.
Artifact Type: shared artifact contract.
Source of Truth: `docs/prd-v0.5.2-public-wiki-skill.md` V052-002 and the shared evidence boundaries in `skills/_shared/DOMAIN-LANGUAGE.md`, `skills/_shared/SKILL-QUALITY.md`, `skills/_shared/ROLE-SEPARATION.md`, and `skills/_shared/RUNTIME-CAPABILITY.md`.
Scope: Project-level wiki storage modes, directory shape, page frontmatter, claim citation, evidence layers, stale/conflict handling, raw-source boundaries, external-tool boundaries, audit scope, and wiki update candidates.
Out of Scope: Runtime execution, installed-plugin behavior, marketplace publishing, release readiness, UAT readiness, customer acceptance, source mutation, auto-memory, graph/vector stores, MCP servers, hooks, or replacing public skills.
Evidence Level: Source-validation policy only. This contract does not prove runtime, browser, UAT, release, marketplace, installed-plugin, cache-refresh, selector-enforcement, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private URLs, cookies, tokens, raw production payloads, or sensitive logs.

# LLM Wiki Contract

## Core Rule

A Groundwork wiki is compiled project orientation and claim inventory. It is not source truth, product truth, backend/API contract truth, implementation authority, verification evidence, release evidence, UAT evidence, customer readiness, marketplace evidence, installed-plugin evidence, browser evidence, runtime evidence, cache-refresh evidence, or selector enforcement.

```text
wiki synthesis != source truth
wiki source inventory != claim-level citation
wiki stale check != verification pass
wiki audit != release readiness
graph/search/index output != authority
```

## Storage Mode

Before creating or updating a wiki, classify the storage mode:

| Mode | Location | Commit default | Use when | Must not be treated as |
| --- | --- | --- | --- | --- |
| `shared_project_wiki` | `wiki/` | may be committed after maintainer acceptance | Long-lived team/project knowledge. | Source truth or readiness evidence. |
| `artifact_scoped_wiki` | `artifacts/wiki/` | may be committed after review | The project requires all durable knowledge under `artifacts/`. | A feature-specific issue map. |
| `private_scratch_wiki` | `.groundwork/wiki/` | ignored by default | Personal exploration or temporary onboarding. | Shared project truth. |

Rules:

- Do not create any wiki for one-time scratch context.
- Do not adopt parent or sibling wiki roots silently.
- Do not promote `.groundwork/wiki/` content into a committed wiki without source review and redaction review.
- Recommend `wiki/` only when the user asks for durable project-level knowledge or accepts the wiki proposal.

## Directory Shape

Default shared project wiki:

```text
wiki/
  SCHEMA.md
  index.md
  log.md
  error-book.md
  raw/
    articles/
    papers/
    notes/
    meetings/
    assets/
  concepts/
  decisions/
  contracts/
  procedures/
  summaries/
  queries/
  terms/
  _archive/
  reports/
    lint/
    stale-claims.md
    contradictions.md
```

Use `artifacts/wiki/` with the same inner shape only when the project has an artifacts-only durable knowledge convention.

Use `.groundwork/wiki/` only for private scratch and do not commit it by default.

## Page Frontmatter

Wiki pages must use compact, valid YAML frontmatter:

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

Page-level `sources` is an inventory. It does not replace claim-level citations for material claims.

## Material Claims

Material claims are statements that could affect product behavior, implementation, API/schema/DB/frontend-backend contracts, permissions, data correctness, verification, release, UAT, customer commitments, architecture, operational procedures, or future task routing.

Use this block, a table row, or equivalent inline citation:

```md
- Claim:
  Evidence layer:
  Source:
  Last checked:
  Stale risk:
  Promotion blocked until:
```

Rules:

- Page-level `default_evidence_layer` is only a fallback.
- Material claims override page-level defaults.
- A page with mixed claims must label claim-level evidence.
- `contract_truth`, `source_truth`, and `runtime_evidence` claims require specific source links or named runtime evidence.
- Missing, stale, contested, or uncited claims must be marked as such instead of promoted.

## Evidence Layers

Reuse the shared domain-language labels:

| Layer | Meaning | Must not become |
| --- | --- | --- |
| `glossary_only` | Local wording alignment for a page or handoff. | PRD truth, contract truth, source truth, readiness evidence. |
| `PRD_truth` | Accepted product/spec intent. | Backend/API/schema/source truth without separate support. |
| `contract_truth` | Accepted API/schema/DB/frontend-backend contract or explicit contract-scoped confirmation. | Runtime/UAT/release truth. |
| `source_truth` | Inspected source code, schema, docs-as-source, or authoritative artifact. | Runtime/browser/UAT/release behavior. |
| `runtime_evidence` | Named runtime/tool/API/browser observation for a scoped claim. | Universal truth outside that run. |
| `user_confirmed` | User explicitly confirmed the term or claim for the stated boundary. | Broader truth unless confirmation covers it. |
| `unknown` | No sufficient evidence yet. | Any promoted truth layer. |

## Freshness Fields

- Page-level `last_updated` records when the wiki page content or metadata last changed.
- Source-level or claim-level `last_checked` records when the cited source, claim evidence, or runtime observation was last inspected.
- `wiki update` must update page `last_updated` when the page changes.
- `wiki update` must update affected source or claim `last_checked` when evidence is inspected or refreshed.
- Do not update `last_checked` merely because a page was edited without rechecking the source.

## Status Semantics

| Status | Meaning |
| --- | --- |
| `draft` | Page exists but is not complete enough for normal reuse. |
| `active` | Page may be used as orientation if its sources and stale risk are acceptable. |
| `contested` | Conflicting evidence exists; do not use as accepted truth. |
| `stale_suspected` | Page may be outdated; inspect source before relying on it. |
| `deprecated` | Page has been superseded but kept for history. |
| `archived` | Page should not be used for active work except historical investigation. |

## Raw Source Boundary

Do not copy repo source files wholesale into `wiki/raw/`.

For repo files, record paths, refs, last checked dates, and claim-level links.

Use `wiki/raw/` only for external articles, papers, meeting notes, user-provided notes, extracted PDF text, screenshot descriptions, or other non-repo inputs that need durable source capture.

Never mutate raw source truth during wiki cleanup.

## External Tool Boundary

External search, graph, index, memory, or visualization tools may be used only as recall aids when available and approved by the task context. Their output is derived material until tied back to a source.

Do not add CodeGraph, Understand Anything, Synto, OpenClerk, OKF Harness, Smriti, vector stores, graph stores, hooks, MCP servers, or auto-memory as a wiki MVP dependency.

## Wiki Update Candidate

Existing public skills may emit this advisory shape when durable knowledge should be maintained by `wiki`:

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

Rules:

- A `Wiki Update Candidate` is advisory unless the current user request explicitly includes wiki maintenance.
- Do not update wiki from an implementation self-summary alone when source, contract, runtime, or verification evidence is required.
- Do not create wiki updates for one-off session diary content.

## Existing Skill Use

Existing public skills may use a project wiki only within their own primary route:

- `to-prd`: may read wiki pages before drafting when project context is material. It must not treat wiki as PRD acceptance. Source-backed facts can reduce repeated questions; `draft`, `contested`, `stale_suspected`, `deprecated`, `archived`, glossary-only, uncited, or page-level-source-only claims require source inspection or clarification before promotion. It may emit a `Wiki Update Candidate` when PRD shaping creates durable project knowledge.
- `implement`: may use wiki pages for orientation and likely source paths. It must inspect source, contracts, tests, or authoritative artifacts before code changes and must not create fields, APIs, states, permissions, migrations, owners, metrics, or tests from wiki synthesis alone. It may emit a `Wiki Update Candidate` when implementation reveals durable architecture, contract, procedure, or error-book knowledge.
- `verify`: may treat wiki pages as claim inventory only. It must inspect the cited source, artifact, test, runtime, browser, release, cache/source refresh, or UAT evidence required for the claim. Stale, contested, uncited, page-level-source-only, or source-inaccessible wiki claims remain unverified or insufficient.
- `handoff`: may cite wiki pages as orientation and propose a `Wiki Update Candidate` for reusable knowledge. It must not turn every handoff into a wiki diary or treat wiki pages as clean review, independent verification, runtime, release, UAT, marketplace, installed-plugin, or cache-refresh evidence.
- `dispatch`: may package wiki context as orientation or claim inventory for accepted work. It must label wiki context as non-authoritative and require downstream source inspection. It must not treat wiki context as runtime execution, implementation, verification, clean review, selector-enforcement, release, UAT, marketplace, installed-plugin, or cache-refresh evidence.

Absence of a wiki must not block normal `to-prd`, `implement`, `verify`, `handoff`, or `dispatch` work unless the user explicitly requested wiki maintenance.

## Audit Scope

Wiki audit must declare one of these scopes:

| Scope | Default use | Required coverage |
| --- | --- | --- |
| `quick` | Default when the user says "check the wiki" without scope. | `SCHEMA.md`, `index.md`, recent `log.md`, explicitly named pages, and high-risk statuses. |
| `focused` | User names a topic, page family, source change, or release area. | Relevant pages, backlinks, and cited sources where material. |
| `full` | User explicitly requests broad audit. | Whole wiki index, page metadata, link graph, stale flags, citation coverage, and documented limitations. |

Default to `quick` unless the user requests or accepts broader scope.

For audit scope, `recent log.md` means the last 20 entries or the last 30 days, whichever is smaller. If `log.md` has no parseable entries, inspect the last 120 non-empty lines and mark that limitation.

Hard-negative coverage reference: `evals/prompts/v0.5.2-wiki.csv` includes source-truth and release-evidence guards such as `wiki-014`, `wiki-015`, `wiki-021`, `wiki-022`, and `wiki-030`.

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

## Failure Output Shapes

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

## Template Set

The starter template set lives under `skills/wiki/templates/`:

- `SCHEMA.md`
- `index.md`
- `log.md`
- `error-book.md`
- `page-concept.md`
- `page-decision.md`
- `page-contract.md`
- `page-procedure.md`
- `page-summary.md`
- `page-query.md`
- `page-term.md`

Copy templates only after selecting a storage mode. Update dates, sources, and statuses to match the actual wiki operation.
