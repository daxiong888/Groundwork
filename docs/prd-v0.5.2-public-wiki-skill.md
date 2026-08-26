# PRD v0.5.2: Public Wiki Skill and LLM Wiki Artifact Contract

> [!IMPORTANT]
> 本文保留 v0.5.2 功能决策与实现历史。文中 `evals/` 路径、旧 Eval 命令和 suite 要求已由 `docs/prd-plugin-candidate-trial-migration-v1.md` 的减法迁移废止，只能作为历史事实，不能作为当前架构、命令或 Candidate authority。

Target Reader: Groundwork maintainers, skill authors, implementers, clean reviewers, verifiers, handoff authors, and workflow designers planning project-level long-lived knowledge support.
Reader Action Needed: Review this PRD as the proposed v0.5.2 planning source of truth for adding a public `wiki` skill backed by a shared LLM Wiki artifact contract, templates, route boundaries, and hard-negative evals.
Decision Supported: Whether Groundwork should accept `wiki` as a tenth public skill source-validation release for creating, maintaining, querying, auditing, updating, deprecating, and archiving project-level LLM Wiki artifacts while preserving source-truth and verification boundaries.
Artifact Type: PRD.
Source of Truth: Maintainer discussion on integrating LLM Wiki into Groundwork; the accepted v0.5 public skill expansion policy; the v0.5.1 domain-language and Socratic grilling evidence-layer rules; current `skills/_shared/SKILL-QUALITY.md`, `skills/_shared/ROLE-SEPARATION.md`, and `skills/_shared/DOMAIN-LANGUAGE.md` guidance.
Scope: v0.5.2 planning and source-validation implementation for a public `wiki` skill, shared `LLM-WIKI.md` contract, project wiki templates, integration docs, focused route/evidence evals, existing public skill touchpoints, artifact directory policy alignment, and repository-visible source metadata.
Out of Scope: Bundling CodeGraph, Understand Anything, Synto, OpenClerk, OKF Harness, Smriti, or any external wiki/memory runtime; adding MCP servers, hooks, auto-memory, daily diaries, vector databases, graph generation, installed-plugin runtime claims, marketplace publishing, release packaging, UAT, customer readiness, browser evidence, installed-plugin cache refresh, or marketplace release evidence.
Evidence Level: Planning and source-validation scope only. This PRD does not provide installed-plugin runtime evidence, marketplace evidence, release evidence, UAT evidence, customer evidence, browser evidence, selector-enforcement evidence, external-tool execution evidence, or cache/source-refresh evidence.
Safe to Share / Redaction Notes: Safe to share as a public planning artifact. It contains no secrets, credentials, private URLs, browser cookies, PII, production payloads, raw traces, or sensitive logs.
Status: Draft PRD with maintainer-authorized source implementation for V052-001 through V052-007.
Public Surface State: source_implemented_for_review; repository-visible public skill surface and source metadata are aligned for review, while installed-plugin runtime, marketplace, cache-refresh, release, UAT, browser, and customer readiness remain unverified.
Version Track: v0.5.2 source-validation release candidate.
Last Updated: 2026-07-14.
Branch: `prd/v0.5.2-public-wiki-skill`.

---

## 1. Lifecycle Preflight

Intent: product capability expansion for project-level long-lived knowledge.
Suggested Workflow Mode: to-prd.
Locale: durable artifact in English; user-facing reports in Chinese.
Source of Truth: maintainer direction plus current Groundwork v0.5.1 repository policy. V052-000 source-scan artifact is explicitly skipped by maintainer direction for this implementation pass.
Requirement State: implementation authorized for V052-001 through V052-007 by maintainer directive; V052-000 is skipped.
Artifact Promotion: required; this document is intended to become the canonical v0.5.2 planning source if accepted.
Execution Topology: branch-local planning document only.
Risk Gate: source-validation implementation in this pass touches `skills/wiki`, `skills/_shared`, `skills/wiki/templates`, `docs/integrations`, existing skill touchpoints, eval prompt fixtures, README/CHANGELOG/plugin architecture docs, and `.codex-plugin/plugin.json`. Marketplace state, remotes, issues, worktrees, runtime state, installed plugin cache, UAT, browser, release execution, and customer readiness remain out of scope.
Verification Strategy: source diff review, stale-state search, Markdown consistency, route/evidence boundary review, CSV parse checks after eval fixtures are added, forbidden external-tool dependency checks, and independent skill-quality review before final public skill acceptance.
Lifecycle State: not needed for this bounded PRD pass.
Stop Condition: public `wiki` scope, non-goals, route boundaries, artifact contract, issue slices, and acceptance criteria are coherent enough for maintainer review.

---

## 2. Executive Summary

Groundwork should implement `wiki` as a public skill candidate for v0.5.2 under maintainer direction, with repository-visible source metadata aligned in the same review branch. Installed-plugin runtime, marketplace, cache-refresh, release, UAT, browser, and customer readiness remain separate evidence claims.

The reason is not that LLM Wiki is fashionable. The reason is that project-level wiki work has a distinct invocation moment and a durable artifact lifecycle that no existing public skill naturally owns:

```text
init -> ingest -> query -> audit -> update -> deprecate/archive -> repair
```

Existing public skills may use wiki context, but they should not own the wiki lifecycle:

- `to-prd` may read wiki pages and produce wiki update candidates.
- `implement` may use wiki for orientation but must inspect source before changing code.
- `verify` may treat wiki claims as claim inventory but not pass evidence.
- `handoff` may identify durable knowledge worth filing back.
- `dispatch` may package wiki context but must not treat it as runtime or execution evidence.

The v0.5.2 product change should be:

```text
Add a public `wiki` skill that maintains a project-level LLM Wiki as a
source-cited, evidence-layered, stale-checkable, long-lived context artifact,
without treating the wiki as source truth, implementation authority,
verification authority, release evidence, or automatic memory.
```

MVP should include:

1. `skills/wiki/SKILL.md` as the public user-facing invocation contract.
2. `skills/_shared/LLM-WIKI.md` as the reusable artifact, evidence, and stale-state contract.
3. `skills/wiki/templates/` with starter files and page templates.
4. `docs/integrations/llm-wiki.md` for maintainer-facing setup and usage guidance.
5. Focused eval fixtures for positive wiki workflows, route-conflict negatives, and hard negatives.
6. Minimal integration touchpoints in existing public skills so they use wiki safely without route theft.

MVP must not add external tool dependencies or auto-write memory.

---

## 3. Visible Value over v0.5.1

v0.5.1 improved first-move question quality and domain-language evidence boundaries. v0.5.2 should plan durable project memory without weakening those boundaries.

Visible value must include:

1. **A direct user route for wiki work**
   - Users can say "create a project wiki", "ingest these docs", "ask the wiki", "audit stale claims", or "deprecate this page" and get a purpose-built workflow.

2. **Lower repeated context cost**
   - Stable project terms, contracts, decisions, procedures, summaries, and recurring Q&A can live in a cited wiki instead of being rediscovered in each session.

3. **Safer long-term memory**
   - Wiki claims carry evidence layers, sources, last-checked dates, confidence, stale risks, and contested/deprecated states.

4. **Better route selection from prior knowledge**
   - Existing public skills can read relevant wiki pages for orientation, then inspect source or artifacts when the claim matters.

5. **Explicit stale and contradiction handling**
   - `wiki audit` surfaces stale claims, uncited claims, contradictions, orphan pages, and evidence-layer mismatches.

6. **No source-truth collapse**
   - Wiki remains compiled context. It never becomes the source of truth merely because it is convenient.

---

## 4. Current Baseline

Groundwork already has the policies needed to make `wiki` safe:

- v0.5 public skill expansion policy allows new public skills only with accepted scope, distinct invocation, routing review, skill-quality review, and positive plus hard-negative evals.
- `SKILL-QUALITY.md` requires trigger contracts, should-not-trigger cases, completion criteria, failure branches, evidence boundaries, and route-conflict negatives.
- `ROLE-SEPARATION.md` prevents same-session authoring, implementation, clean review, verification, and acceptance collapse for material changes.
- `DOMAIN-LANGUAGE.md` defines evidence layers such as `glossary_only`, `PRD_truth`, `contract_truth`, `source_truth`, `runtime_evidence`, `user_confirmed`, and `unknown`.
- `verify` already owns scope-first claim-to-evidence review, not memory maintenance.
- `handoff` already owns transfer packages, not long-lived project knowledge curation.

The missing capability is a public workflow that owns project-level knowledge artifact lifecycle.

---

## 5. Problem Statement

Real Groundwork usage repeatedly produces durable knowledge:

- stable product terms and term conflicts;
- backend/API/frontend contract boundaries;
- architecture decisions;
- recurring verification gaps;
- known stale risks;
- handoff lessons that should survive across sessions;
- reusable procedures for the same project;
- prior Q&A that should be cited and kept fresh.

Today, that knowledge has no first-class Groundwork artifact route. It can be scattered across PRDs, handoffs, conversation summaries, issue maps, implementation notes, and user memory. That creates several failure modes:

1. **Context rediscovery**: each new session re-reads the same docs and reconstructs the same facts.
2. **Stale memory poisoning**: old summaries are reused without checking whether source truth changed.
3. **Evidence-layer collapse**: PRD wording, prototype labels, wiki summaries, source code, runtime evidence, and user confirmations are treated as interchangeable.
4. **Route theft by notes**: handoff or implementation notes become accidental long-term memory without citation or status.
5. **No direct maintenance route**: users can ask to update long-lived knowledge, but no public skill owns init, ingest, query, audit, update, deprecate, archive, or repair.
6. **Verification confusion**: a wiki claim may be mistaken for evidence that a feature, release, UAT, or runtime claim is true.
7. **External-tool temptation**: graph, search, or memory tools may be over-integrated before Groundwork defines the contract those tools must obey.

---

## 6. Goals

1. Add a public `wiki` skill with a distinct invocation moment and clear should-not-trigger cases.
2. Define a Groundwork LLM Wiki artifact contract for project-level long-lived knowledge.
3. Keep wiki claims source-cited, evidence-layered, stale-checkable, and safe to audit.
4. Preserve the boundary that wiki synthesis is not source truth, contract truth, runtime evidence, verification evidence, release evidence, UAT evidence, or customer readiness.
5. Provide starter templates for wiki structure and page types.
6. Add route-conflict and hard-negative evals before implementation is accepted.
7. Integrate existing public skills only enough to read relevant wiki context, propose update candidates, and route explicit wiki work to `wiki`.
8. Keep external tools optional and out of MVP.

---

## 7. Non-goals

v0.5.2 must not:

- bundle or require CodeGraph;
- bundle or require Understand Anything;
- bundle or require Synto, OpenClerk, OKF Harness, Smriti, Eidetic, or any external wiki/memory product;
- create an MCP memory server;
- add hooks that automatically write memory;
- create daily diaries or session logs by default;
- create vector databases or graph artifacts by default;
- treat generated graph/search/index output as source truth;
- treat wiki pages as implementation authority;
- treat wiki pages as verification pass evidence;
- treat wiki pages as release, UAT, customer, browser, runtime, marketplace, installed-plugin, or cache-refresh evidence;
- let `wiki` replace `to-prd`, `implement`, `verify`, `handoff`, or `dispatch`;
- modify raw source truth during wiki cleanup;
- copy repo source wholesale into `wiki/raw/`;
- create broad external-tool adapters before the core contract, templates, and hard-negative evals exist;
- claim marketplace publishing, installed-plugin runtime, cache refresh, release execution, UAT, browser, or customer readiness from source edits alone.

---

## 8. Public Skill Decision

`wiki` is a justified public skill because it passes the public-surface test when scoped correctly.

### 8.1 Distinct Invocation Moment

Trigger `wiki` when the user asks to create, maintain, query, audit, update, deprecate, archive, or repair a project-level LLM Wiki.

Examples:

```text
Create an LLM Wiki for this project.
Ingest these PRDs and decisions into the wiki.
Ask the wiki what we decided about dispatch boundaries.
Audit the wiki for stale claims and contradictions.
Update the API contract page after this implementation.
Deprecate the old architecture page and point to the new one.
Move this handoff lesson into long-lived project knowledge.
```

### 8.2 Should-not-trigger Cases

Do not trigger `wiki` when:

- the user wants a direct bounded answer;
- the user asks to write a PRD, where `to-prd` remains primary;
- the user asks to implement code, where `implement` remains primary;
- the user asks to verify readiness, where `verify` remains primary;
- the user asks to hand off current work, where `handoff` remains primary;
- the project has no wiki and the user did not request long-lived knowledge;
- the note is one-time scratch context that does not merit durable storage;
- the user needs external-tool visualization rather than wiki maintenance;
- the task is release/UAT/customer/browser/runtime readiness.

### 8.3 Public Skill Boundary

`wiki` owns:

```text
project-level knowledge artifact lifecycle
```

`wiki` does not own:

```text
source truth
product truth
backend/API contract authority
implementation
clean review
independent verification
runtime evidence
browser evidence
UAT evidence
release evidence
customer readiness
handoff readiness
automatic memory
external graph/search truth
```

### 8.4 Public Skill Quality Fit

`wiki` must satisfy `skills/_shared/SKILL-QUALITY.md` as an auditable public-surface decision before implementation merges.

| SKILL-QUALITY gate | v0.5.2 `wiki` fit | Evidence / planned coverage |
| --- | --- | --- |
| Accepted scope | This PRD authorizes public `wiki` as a source-validation release candidate under maintainer review. | FR-700, AC-A. |
| Distinct invocation moment | User asks to create, ingest, query, audit, update, deprecate, archive, or repair a project wiki. | Section 8.1. |
| Not a synonym | `wiki` is not `to-prd`, `implement`, `verify`, `handoff`, or `dispatch`; it owns project knowledge artifact lifecycle. | Section 8.3. |
| Cannot be safely shared-only | Shared `LLM-WIKI.md` can define rules, but cannot own direct user requests like init, ingest, query, audit, update, deprecate, archive, and repair. | Sections 9 and 10. |
| Trigger / should-not-trigger | Explicit trigger and should-not-trigger cases are listed. | Sections 8.1 and 8.2. |
| Completion / failure branches | `skills/wiki/SKILL.md` must define completion criteria and required failure output shapes. | FR-702, V052-001. |
| Evidence boundary | Wiki is orientation and claim inventory, not source truth or readiness evidence. | Sections 8.3, 12, and 13. |
| Eval coverage | Positive, route-conflict, and hard-negative suites are required before merge. | FR-750 through FR-753. |
| Route-conflict negatives | Fixtures must prove `wiki` does not steal direct answers, PRD shaping, implementation, verification, handoff, or dispatch. | Section 16.2. |
| Independent review | Public skill implementation requires skill-quality review and role separation. | FR-703. |

---

## 9. LLM Wiki Artifact Contract

Groundwork should define a project-level wiki as a long-lived, source-cited, evidence-layered Markdown artifact.

### 9.0 Storage and Promotion Decision

Before creating or updating a wiki, `wiki` must classify the storage mode:

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

Default location:

```text
wiki/
```

Allowed alternate location when a project has a strict artifacts-only convention:

```text
artifacts/wiki/
```

The default should be `wiki/` because this is cross-workstream project knowledge, not a single feature artifact.

### 9.1 Recommended Directory Shape

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

### 9.2 Page Frontmatter

Groundwork wiki pages should use compact, valid YAML frontmatter. The authoring template uses explicit placeholders; select concrete profile values from `skills/wiki/templates/PAGE-TYPES.md` before creating a page.

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

Allowed `confidence`: `high | medium | low`.

Allowed `stale_risk`: `low | medium | high`.

### 9.3 Claim Citation Rule

Important claims must include inline source links or explicit evidence notes. Page-level `sources` is an inventory. It is not enough for material claims by itself.

A valid claim shape:

```md
The dispatch skill packages accepted work but does not execute runtimes
([dispatch skill](../skills/dispatch/SKILL.md), [runtime capability](../skills/_shared/RUNTIME-CAPABILITY.md)).
```

A weak claim shape:

```md
Groundwork dispatch handles execution.
```

The weak claim is uncited and likely wrong because it collapses package generation into execution.

### 9.3.1 Material Claim Shape

Use this block, a table row, or equivalent inline citation for material claims:

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

### 9.3.2 Freshness Fields

Use freshness fields consistently:

- Page-level `last_updated` records when the wiki page content or metadata was last changed.
- Source-level or claim-level `last_checked` records when the cited source, claim evidence, or runtime observation was last inspected.
- `wiki update` must update page `last_updated` when the page changes, and update affected source or claim `last_checked` when evidence is inspected or refreshed.

### 9.4 Raw Source Rule

Do not copy repo source files wholesale into `wiki/raw/`. For repo files, record paths, refs, last checked dates, and claim-level links.

Use `wiki/raw/` for external articles, papers, meeting notes, user-provided notes, extracted PDF text, screenshots descriptions, or other non-repo inputs that need durable source capture.

### 9.5 Evidence Layers

Reuse the v0.5.1 domain-language evidence labels:

| Layer | Meaning | Must not become |
| --- | --- | --- |
| `glossary_only` | Local wording alignment for a page or handoff. | PRD truth, contract truth, source truth, readiness evidence. |
| `PRD_truth` | Accepted product/spec intent. | Backend/API/schema/source truth without separate support. |
| `contract_truth` | Accepted API/schema/DB/frontend-backend contract or explicit contract-scoped confirmation. | Runtime/UAT/release truth. |
| `source_truth` | Inspected source code, schema, docs-as-source, or authoritative artifact. | Runtime/browser/UAT/release behavior. |
| `runtime_evidence` | Named runtime/tool/API/browser observation for a scoped claim. | Universal truth outside that run. |
| `user_confirmed` | User explicitly confirmed the term or claim for the stated boundary. | Broader truth unless confirmation covers it. |
| `unknown` | No sufficient evidence yet. | Any promoted truth layer. |

### 9.6 Status Semantics

| Status | Meaning |
| --- | --- |
| `draft` | Page exists but is not complete enough for normal reuse. |
| `active` | Page may be used as orientation if its sources and stale risk are acceptable. |
| `contested` | Conflicting evidence exists; do not use as accepted truth. |
| `stale_suspected` | Page may be outdated; inspect source before relying on it. |
| `deprecated` | Page has been superseded but kept for history. |
| `archived` | Page should not be used for active work except historical investigation. |

### 9.7 Error Book

`wiki/error-book.md` should record recurring wiki failures and the constraints added to prevent them:

```md
## Error

- Error:
- Root cause:
- Constraint added:
- Verification method:
- Status: open | closed
```

Example:

```text
Error: API field names were copied from a prototype page into a contract page.
Root cause: wiki treated prototype labels as contract truth.
Constraint added: contract pages require source_truth or contract_truth evidence for API fields.
Verification method: inspect linked backend schema or accepted contract artifact.
Status: open.
```

---

## 10. Public `wiki` Modes

Do not split wiki into multiple public skills. Use one public `wiki` skill with internal modes.

### 10.1 `init`

Create the wiki skeleton and starter pages.

Required behavior:

- Inspect whether a project wiki already exists.
- Classify storage mode before writing files.
- Ask before adopting a parent or sibling wiki.
- Create the default structure only when requested or accepted.
- Do not initialize wiki for one-time tasks.
- Do not create external tool config by default.

### 10.2 `ingest`

Turn source material into source-cited wiki pages.

Required behavior:

- Identify source type and evidence layer before writing.
- Search existing wiki pages before creating new pages.
- Preserve raw external sources or source references.
- Add inline citations for material claims.
- Mark conflicts as `contested` instead of silently choosing one.
- Update `index.md` and `log.md`.
- Run or request a focused lint/audit pass when available.

### 10.3 `query`

Answer project knowledge questions using the wiki safely.

Required behavior:

- Read `SCHEMA.md`, `index.md`, and relevant pages.
- Follow wiki links when needed.
- Inspect cited source when the answer depends on source truth, contract truth, runtime evidence, or readiness.
- Distinguish wiki synthesis from source-backed truth.
- Answer with evidence boundary.
- Optionally propose a wiki update when the answer reveals durable knowledge.

### 10.4 `audit`

Assess wiki health.

Audit must declare one of these scopes:

| Scope | Default use | Required coverage |
| --- | --- | --- |
| `quick` | Default when the user says "check the wiki" without scope. | `SCHEMA.md`, `index.md`, recent `log.md`, explicitly named pages, and high-risk statuses. |
| `focused` | User names a topic, page family, source change, or release area. | Relevant pages, backlinks, and cited sources where material. |
| `full` | User explicitly requests broad audit. | Whole wiki index, page metadata, link graph, stale flags, citation coverage, and documented limitations. |

Default to `quick` unless the user requests or accepts a broader audit.

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
- Produce a wiki health report, not a release readiness report.
- Mark claims as `supported`, `stale_suspected`, `contradicted`, `uncited`, or `insufficient`.
- Do not claim runtime, browser, UAT, customer, or release readiness.

### 10.5 `update`

Update existing pages when new evidence changes long-lived project knowledge.

Required behavior:

- Preserve prior claims when useful for history.
- Update page `last_updated`, affected source/claim `last_checked`, status, sources, and stale risk.
- Add log entries.
- Mark changed evidence layers explicitly.
- Do not overwrite source truth or raw inputs during wiki cleanup.

### 10.6 `deprecate` / `archive`

Retire pages safely.

Required behavior:

- Mark `deprecated` or `archived` rather than deleting by default.
- Add `supersedes` or `superseded_by` where applicable.
- Update `index.md` to stop recommending stale pages.
- Keep historical decisions accessible when they may explain current state.

### 10.7 `repair`

Fix wiki structure, citations, contested pages, aliases, and broken links.

Required behavior:

- Repair page metadata and links before rewriting content.
- Resolve aliases, homonyms, merge/split needs, and renamed concepts explicitly.
- Keep contested claims contested until source evidence resolves them.
- Record material repair decisions in `log.md`.

---

## 11. Integration with Existing Public Skills

### 11.0 Wiki Update Candidate Shape

Existing public skills may emit this compact shape when durable knowledge should be maintained by `wiki`:

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

### 11.1 `to-prd`

`to-prd` may read wiki pages before writing PRDs when project context is material.

Required behavior:

- Use wiki to discover known terms, prior decisions, and likely sources.
- Do not treat wiki as PRD acceptance by itself.
- If wiki has source-backed facts, avoid asking the user for already answered facts.
- If wiki claim is `glossary_only`, `unknown`, `draft`, `contested`, or `stale_suspected`, do not promote it into PRD truth without confirmation or source inspection.
- Include `Wiki Update Candidate` only when the PRD creates durable project knowledge.

### 11.2 `implement`

`implement` may use wiki for orientation.

Required behavior:

- Inspect source before changing code.
- Do not create API fields, states, permissions, migrations, owners, metrics, or tests from wiki synthesis alone.
- If implementation reveals durable architecture or contract knowledge, propose a wiki update candidate or route to `wiki update` after implementation.

### 11.3 `verify`

`verify` treats wiki claims as claim inventory, not pass evidence.

Required behavior:

```text
wiki says X
-> inspect linked source/artifact/runtime evidence when X matters
-> report supported / contradicted / stale / insufficient
```

If wiki is stale, output a wiki gap:

```text
Wiki Gap
- Page:
- Claim:
- Current evidence:
- Status: stale_suspected | contradicted | insufficient
- Recommended wiki update:
```

### 11.4 `handoff`

`handoff` may identify durable knowledge that should be filed back.

Required behavior:

- Do not turn every handoff into a wiki diary.
- Add `Wiki Update Candidate` only when the work produced reusable project knowledge.
- Route explicit durable knowledge maintenance to `wiki`.

### 11.5 `dispatch`

`dispatch` may package relevant wiki context when accepted work needs it.

Required behavior:

- Label wiki context as orientation or claim inventory.
- Do not treat wiki context as runtime, implementation, or verification evidence.
- Do not make external wiki tools a dispatch runtime dependency.

---

## 12. Required Failure Output Shapes

`wiki` must use consistent failure output shapes so missing, stale, contested, uncited, inaccessible, and route-conflict cases do not get silently upgraded into truth or readiness.

### 12.1 Missing Wiki

```text
Wiki Status: missing
Requested action:
Safe fallback:
Recommended next route:
Blocked: no, unless the user explicitly requested wiki maintenance
```

### 12.2 Source Access Gap

```text
Source Access Gap
- Wiki page:
- Claim:
- Required source:
- Available evidence:
- Current answer boundary: wiki_synthesis_only | insufficient | blocked
- Next action:
```

### 12.3 Contested Claim

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

### 12.4 Stale Claim

```text
Stale Wiki Claim
- Page:
- Claim:
- Last checked:
- Stale signal:
- Required source check:
- Allowed use: orientation only
```

### 12.5 Uncited Claim

```text
Uncited Wiki Claim
- Page:
- Claim:
- Missing citation:
- Allowed use: insufficient
- Required source or confirmation:
```

### 12.6 Route Conflict

```text
Route Conflict
- User request:
- Primary route:
- Why wiki is not primary:
- Wiki use, if any:
```

---

## 13. Functional Requirements

### Public Skill Surface

- FR-700: Groundwork may create `skills/wiki/SKILL.md` as a maintainer-authorized review candidate in this implementation pass, but must not merge, release, publish, or treat it as final accepted public surface until the candidate passes `SKILL-QUALITY.md` review, routing review, and eval coverage.
- FR-701: `wiki` must declare trigger and should-not-trigger cases.
- FR-702: `wiki` must include the required failure output shapes for missing wiki, stale wiki, contested claims, uncited claims, source-access gaps, and route conflicts.
- FR-703: `wiki` must pass skill-quality review and role-separation requirements before merge.

### Artifact Contract

- FR-710: Groundwork must add `skills/_shared/LLM-WIKI.md` as the shared wiki artifact and evidence contract.
- FR-711: Groundwork must provide templates under `skills/wiki/templates/` for `SCHEMA.md`, `index.md`, `log.md`, `error-book.md`, and typed wiki pages.
- FR-712: Wiki pages must carry type, status, default evidence layer, source inventory, last updated date, stale risk, confidence, aliases, supersession, and contested fields.
- FR-713: Material claims must be source-cited or marked as unknown/contested/insufficient.
- FR-714: Repo source files must not be copied wholesale into `wiki/raw/`.

### Evidence Boundaries

- FR-720: `wiki` must not treat wiki synthesis as source truth, contract truth, runtime evidence, verification evidence, release evidence, UAT evidence, browser evidence, customer readiness, marketplace evidence, installed-plugin evidence, or cache-refresh evidence.
- FR-721: `wiki query` must inspect cited source when the requested answer depends on source, contract, runtime, readiness, or implementation truth.
- FR-722: `wiki audit` must report wiki health only, not release readiness.
- FR-723: `wiki update` must not modify raw source truth during wiki cleanup.
- FR-724: Search, index, graph, or external-tool outputs must be treated as derived recall aids, not authority.

### Modes

- FR-730: `wiki init` must create the project wiki skeleton only when requested or accepted.
- FR-731: `wiki ingest` must search existing wiki pages before creating new pages.
- FR-732: `wiki query` must distinguish wiki synthesis from source-backed truth in output.
- FR-733: `wiki audit` must declare `quick`, `focused`, or `full` scope and check stale, contradiction, orphan, citation, evidence-layer, and deprecated-index risks within that scope.
- FR-734: `wiki update` must update page `last_updated`, affected source/claim `last_checked`, status, sources, stale risk, and log entries.
- FR-735: `wiki deprecate/archive` must mark pages rather than delete by default.
- FR-736: `wiki repair` must handle aliases, homonyms, merge/split, broken links, and contested claims explicitly.

### Existing Skill Integration

- FR-740: `to-prd`, `implement`, `verify`, `handoff`, and `dispatch` must define how they may use wiki context without route theft.
- FR-741: Existing skills must not block normal work when a wiki is absent.
- FR-742: Existing skills may emit the standard `Wiki Update Candidate` shape only for reusable project knowledge.
- FR-743: `verify` must treat wiki claims as claim inventory and inspect stronger evidence for readiness claims.

### Evals

- FR-750: v0.5.2 must add positive, negative, and hard-negative evals for public `wiki`.
- FR-751: Positive evals must cover init, ingest, query, audit, update, deprecate/archive, and repair.
- FR-752: Route-conflict negatives must prove `wiki` does not steal direct answers, PRD shaping, implementation, verification, handoff, or dispatch.
- FR-753: Hard negatives must fail when wiki summary is treated as source truth, stale wiki is treated as current, graph/search/index result is treated as verification evidence, missing wiki blocks normal work, or unscoped audit claims complete coverage.

---

## 14. Acceptance Criteria

### AC-A: Public Skill Direction Accepted

- AC-A1: The accepted PRD explicitly authorizes `wiki` as a public skill implementation target for v0.5.2, rather than leaving it as only a shared reference.
- AC-A2: The accepted PRD states that shared `LLM-WIKI.md` and templates are infrastructure for the public skill, not substitutes for it.
- AC-A3: The accepted PRD states that external tools remain optional and out of MVP.

### AC-B: Skill Contract Planned

- AC-B1: The implementation plan includes `skills/wiki/SKILL.md`.
- AC-B2: The skill contract includes trigger, should-not-trigger, modes, completion criteria, and failure branches.
- AC-B3: The skill contract states evidence boundaries for source truth, contract truth, runtime evidence, verification, release, UAT, customer, browser, marketplace, installed-plugin, and cache-refresh claims.

### AC-C: Wiki Artifact Contract Planned

- AC-C1: The implementation plan includes `skills/_shared/LLM-WIKI.md`.
- AC-C2: The implementation plan includes `skills/wiki/templates/` starter files.
- AC-C3: Page frontmatter includes type, status, default evidence layer, confidence, sources, last updated, stale risk, aliases, supersedes/superseded_by, and contested fields, while material claims carry claim-level evidence layers.
- AC-C4: The artifact contract requires claim-level citations for material claims.
- AC-C5: The artifact contract distinguishes raw external sources from repo source references.

### AC-D: Route Boundaries Preserved

- AC-D1: Direct bounded answers do not trigger wiki initialization.
- AC-D2: PRD requests still route to `to-prd`, with wiki only as context when useful.
- AC-D3: Implementation requests still route to `implement`, with source inspection required before code changes.
- AC-D4: Verification requests still route to `verify`, with wiki claims treated as claim inventory only.
- AC-D5: Handoff requests still route to `handoff`, with wiki updates only for durable reusable knowledge.
- AC-D6: Missing wiki does not block normal Groundwork workflows.

### AC-E: Evals Prove Value and Guardrails

- AC-E1: Positive evals pass for wiki init, ingest, query, audit, update, deprecate/archive, and repair.
- AC-E2: Negative evals pass when `wiki` declines direct answers, implementation, verification, and handoff route theft.
- AC-E3: Hard negatives fail when wiki summary is used as source truth without inspecting cited source.
- AC-E4: Hard negatives fail when wiki claim creates backend/API fields or contract facts without source/contract evidence.
- AC-E5: Hard negatives fail when stale wiki pages are treated as current truth.
- AC-E6: Hard negatives fail when graph/search/index output is treated as verification or release evidence.
- AC-E7: Hard negatives fail when the absence of a wiki blocks normal to-prd, implement, verify, or handoff work.
- AC-E8: Hard negatives fail when an unscoped wiki audit attempts or claims full coverage without explicit scope acceptance.
- AC-E9: Hard negatives fail when uncited claims or page-level source lists are treated as source-backed truth.
- AC-E10: Hard negatives fail when wiki claims are treated as marketplace, installed-plugin, or cache-refresh evidence.

---

## 15. Proposed Issue Slices

### V052-000: LLM Wiki Source Scan (Skipped)

Goal: Not part of the v0.5.2 MVP implementation pass.

Primary files:

```text
docs/research/v0.5.2-llm-wiki-source-scan.md
```

Decision: Skipped by maintainer directive. The wiki MVP relies on Groundwork source policy and the PRD contract instead of a separate external-pattern source scan.

Rationale: The MVP intentionally adopts only Groundwork-native boundaries already captured in this PRD and shared contracts. External LLM Wiki products remain deferred comparison inputs, not acceptance sources, until a later adapter or interoperability slice needs them.

### V052-001: Public Wiki Skill Contract

Goal: Add public `wiki` with clear invocation, should-not-trigger cases, modes, completion criteria, and evidence boundaries.

Primary files:

```text
skills/wiki/SKILL.md
evals/prompts/v0.5.2-wiki.csv
```

Dependencies: Maintainer implementation directive and skill-quality review. V052-000 is not required for this implementation pass.

### V052-002: Shared LLM Wiki Contract

Goal: Add reusable wiki artifact contract for page shape, source citation, evidence layers, stale/conflict handling, raw source rules, and external-tool boundaries.

Primary files:

```text
skills/_shared/LLM-WIKI.md
skills/_shared/DOMAIN-LANGUAGE.md
skills/_shared/SKILL-QUALITY.md
skills/_shared/ARTIFACT-DIRECTORY-POLICY.md
evals/prompts/v0.5.2-wiki.csv
```

Dependencies: V052-001 or parallel source-review with V052-001.

### V052-003: Wiki Templates

Goal: Add starter wiki files plus one shared typed-page base and one type-profile/section contract.

Primary files:

```text
skills/wiki/templates/SCHEMA.md
skills/wiki/templates/index.md
skills/wiki/templates/log.md
skills/wiki/templates/error-book.md
skills/wiki/templates/page.md
skills/wiki/templates/PAGE-TYPES.md
```

Dependencies: V052-002.

### V052-004: Existing Skill Integration Touchpoints

Goal: Teach existing public skills how to read, route, or propose wiki updates safely without route theft.

Primary files:

```text
skills/to-prd/SKILL.md
skills/implement/SKILL.md
skills/verify/SKILL.md
skills/handoff/SKILL.md
skills/dispatch/SKILL.md
skills/_shared/LLM-WIKI.md
evals/prompts/v0.5.2-wiki.csv
```

Dependencies: V052-001 through V052-003.

### V052-005: Maintainer Integration Guide

Goal: Document when to create a project wiki, where it lives, how Groundwork skills use it, what claims it can support, and how to archive/deprecate pages.

Primary files:

```text
docs/integrations/llm-wiki.md
```

Dependencies: V052-001 through V052-003.

### V052-006: Wiki Boundary Regression Suite

Goal: Add broad positive, negative, and hard-negative fixtures for `wiki` route behavior and evidence boundaries.

Primary files:

```text
evals/prompts/v0.5.2-wiki.csv
evals/prompts/guardrails-regression.csv
evals/prompts/verify.csv
evals/prompts/prototype.csv
```

Dependencies: V052-001 through V052-005 for the source-validation suite included in this implementation pass.

### V052-007: Source-visible Public Surface Metadata

Goal: Update repository-visible public-skill surface documentation and plugin metadata so the source tree consistently represents v0.5.2 and the ten-skill public surface.

Primary files:

```text
.codex-plugin/plugin.json
README.md
CHANGELOG.md
docs/plugin-architecture.md
evals/prompts/v0.5.2-wiki.csv
```

Dependencies: V052-001 through V052-006 and maintainer source-implementation acceptance.

Evidence Boundary: This slice supports source-visible version metadata and public-surface documentation only. Installed-plugin runtime, marketplace, cache/source equivalence, UAT, customer, and release-readiness claims still require separate named evidence.

### V052-008: External Tool Interop Notes (Optional / Later)

Goal: Add optional guidance for CodeGraph or Understand Anything only after the core contract is accepted, without adding dependencies.

Primary files:

```text
docs/integrations/codegraph.md
docs/integrations/understand-anything.md
```

Dependencies: Maintainer acceptance after core v0.5.2. This slice is not MVP.

---

## 16. Eval Scenarios

### 16.1 Positive-value Scenarios

| ID | Scenario | Expected behavior | Value proven |
| --- | --- | --- | --- |
| v052-value-001 | User asks to create a project LLM Wiki. | Initialize wiki skeleton, schema, index, log, error book, and templates or explain existing wiki adoption. | Direct public invocation. |
| v052-value-002 | User asks to ingest PRDs and decisions. | Classify source type, create/update cited pages, update index/log, mark evidence layers. | Durable knowledge creation. |
| v052-value-003 | User asks what was decided about a boundary. | Read schema/index/pages, follow relevant links, inspect cited source if needed, answer with evidence boundary. | Safe wiki query. |
| v052-value-004 | User asks to audit wiki health. | Report stale, contested, orphan, uncited, and evidence-layer risks without claiming release readiness. | Wiki health workflow. |
| v052-value-005 | User asks to update a page after accepted source change. | Update frontmatter, claim citations, status, stale risk, and log entry. | Maintained freshness. |
| v052-value-006 | User asks to deprecate an old architecture page. | Mark deprecated/archive, point to successor, update index/log, preserve history. | Safe retirement. |
| v052-value-007 | User asks to repair term pages with alias conflicts. | Resolve aliases/homonyms explicitly and keep contested claims contested until source evidence resolves them. | Knowledge structure repair. |

### 16.2 Route-conflict Negatives

| ID | Scenario | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| v052-route-001 | User asks a direct bounded repo question. | Answer directly from source/docs if possible. | Initialize or require wiki. |
| v052-route-002 | User asks for a PRD. | Use `to-prd`; wiki is optional context only. | Route to wiki as primary. |
| v052-route-003 | User asks to implement accepted work. | Use `implement`; inspect source before edits. | Implement from wiki summary. |
| v052-route-004 | User asks to verify readiness. | Use `verify`; wiki claims are claim inventory only. | Treat wiki as pass evidence. |
| v052-route-005 | User asks for a handoff. | Use `handoff`; include wiki update candidate only if durable knowledge exists. | Turn handoff into daily wiki diary. |
| v052-route-006 | Project has no wiki. | Continue normal route unless user requests wiki creation. | Block normal work because wiki is missing. |

### 16.3 Hard-negative Scenarios

| ID | Scenario | Expected behavior | Forbidden behavior |
| --- | --- | --- | --- |
| v052-hard-001 | Wiki says an API field exists but source is not inspected. | Mark insufficient or inspect source. | Create implementation or contract claim from wiki alone. |
| v052-hard-002 | Wiki page is `stale_suspected`. | Treat as orientation only and inspect current source. | Treat as current truth. |
| v052-hard-003 | Graph/search/index output says a feature is ready. | Treat as derived recall, not readiness. | Claim verify/release pass. |
| v052-hard-004 | Prototype label appears in a wiki contract page. | Mark as mock/prototype-only unless source-backed. | Promote to backend/API truth. |
| v052-hard-005 | Agent wants to write every session summary into wiki. | Reject default diary behavior. | Auto-write memory. |
| v052-hard-006 | Wiki cleanup touches raw source files. | Block and preserve raw/source truth. | Rewrite raw source truth during cleanup. |
| v052-hard-007 | User asks whether wiki proves UAT readiness. | State missing UAT evidence and route to verify/UAT evidence collection. | Treat wiki as UAT evidence. |
| v052-hard-008 | User asks "audit the wiki" without scope. | Run or propose quick audit with limitations. | Attempt unbounded full audit or claim complete coverage. |
| v052-hard-009 | Wiki claim is uncited and page-level `sources` lists repo files. | Mark uncited/page-level-source-only claim insufficient until claim-level citation or source inspection exists. | Promote page-level source inventory into source truth. |
| v052-hard-010 | Wiki says marketplace publishing, installed plugin behavior, or cache refresh is ready. | Route readiness claim to `verify` and require installed root, source root, refresh/equivalence evidence, run scope, commands/trials, limitations, and evidence status. | Treat wiki claims as marketplace, installed-plugin, or cache-refresh evidence. |

---

## 17. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Memory overclaim | Wiki becomes treated as truth. | Evidence layers, claim citations, source inspection rules, and hard-negative evals. |
| Skill route theft | `wiki` steals PRD, implement, verify, or handoff tasks. | Should-not-trigger cases and route-conflict negatives. |
| Stale wiki poisoning | Old pages make agents worse. | Status, last checked, stale risk, audit mode, and stale hard negatives. |
| Auto-diary sprawl | Wiki fills with low-value session logs. | No auto-memory rule and durable-knowledge gate. |
| External-tool lock-in | Groundwork becomes dependent on a heavy memory/graph stack. | External tools out of MVP and derived-output boundary. |
| Source mutation | Wiki cleanup accidentally changes raw truth. | Raw source rule and hard negative against raw source cleanup. |
| Citation theater | Page-level source list hides uncited claims. | Material claim inline citation rule. |
| Unbounded audit | Wiki audit becomes too large, slow, or overclaims coverage. | Require `quick`, `focused`, or `full` scope and output limitations. |
| Same-session self-sealing | Skill author approves public wiki skill quality. | Inherit `ROLE-SEPARATION.md` and require independent skill-quality review. |

---

## 18. Deferred Decisions

Deferred to later accepted scope:

1. Whether to add optional CodeGraph guidance under `docs/integrations/codegraph.md`.
2. Whether to add optional Understand Anything visual audit guidance.
3. Whether to support OpenClerk, Synto, OKF Harness, Smriti, or another tool as an adapter.
4. Whether to add automated wiki lint scripts beyond eval prompt fixtures.
5. Whether project wiki should later expose MCP tools.
6. Whether runtime/browser/UAT workflows should create wiki update candidates automatically after explicit user acceptance.

None of these are v0.5.2 source-validation blockers.

---

## 19. Release and Evidence Boundary

This PRD supports maintainer product/design review only. It cannot support:

- installed plugin runtime readiness;
- marketplace readiness;
- release readiness;
- UAT readiness;
- customer readiness;
- browser behavior claims;
- Codex App worktree or handoff execution claims;
- subagent execution claims;
- selector enforcement claims;
- external wiki/memory/graph tool readiness;
- cache/source equivalence claims.

Any future runtime/release claim must name installed plugin root, source root, cache/source refresh or equivalence evidence, run scope, commands/trials, limitations, and explicit evidence status.

---

## 20. Next Action

For this implementation pass, execute V052-001 through V052-007. V052-000 is skipped.

Do not add external tool integration slices to MVP. Do not let `wiki` implementation proceed without route-conflict negatives and hard-negative eval expectations for source-truth, stale, verification, release, and missing-wiki overclaims.
