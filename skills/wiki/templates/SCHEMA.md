---
type: contract
status: draft
target_reader: "Project maintainers, wiki authors, clean reviewers, and future agent sessions"
reader_action: "Use this schema before adding or changing pages in this project wiki."
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

# LLM Wiki Schema

Target Reader: Project maintainers, wiki authors, clean reviewers, and future agent sessions.
Reader Action Needed: Use this schema before adding or changing pages in this project wiki.
Decision Supported: Whether a wiki page has valid metadata, source citation, evidence boundaries, freshness fields, and stale/conflict handling.
Artifact Type: wiki schema.
Source of Truth: `skills/_shared/LLM-WIKI.md` and this project's accepted wiki storage decision.
Scope: Page types, statuses, frontmatter, evidence layers, citation policy, freshness fields, and audit expectations for this wiki.
Out of Scope: Source-truth approval, implementation authority, verification pass evidence, release readiness, UAT readiness, customer readiness, runtime evidence, browser evidence, marketplace evidence, installed-plugin evidence, cache-refresh evidence, graph stores, vector stores, hooks, and external memory runtimes.
Evidence Level: Wiki schema and source-validation guidance only.
Safe to Share / Redaction Notes: Review project-specific entries for secrets, credentials, PII, sensitive logs, private URLs, cookies, tokens, and raw production payloads before sharing.

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

## Material Claim Shape

```md
- Claim:
  Evidence layer:
  Source:
  Last checked:
  Stale risk:
  Promotion blocked until:
```

Page-level `sources` is an inventory. Material claims still need inline source links, evidence notes, or the material claim shape above.

## Source Rules

- Repo source files are referenced by path, ref, and last checked date; do not copy them wholesale into `raw/`.
- External articles, papers, meeting notes, user notes, extracted PDF text, or screenshot descriptions may be preserved under `raw/` after redaction review.
- Search, graph, index, and external-tool outputs are recall aids, not authority.

## Audit Scope

Every audit must declare `quick`, `focused`, or `full` and list pages and sources inspected, pages not inspected, claims requiring stronger evidence, and limitations.
