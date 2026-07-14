# Wiki Page Type Profiles

Target Reader: Wiki authors and reviewers creating typed pages from `page.md`.
Reader Action Needed: Select one page type, copy its frontmatter values, and use its exact body section order.
Decision Supported: Whether a generated wiki page preserves the type-specific reader, evidence, stale-risk, and section contract.
Artifact Type: wiki page authoring contract.
Source of Truth: `skills/_shared/LLM-WIKI.md`, `SCHEMA.md`, and `page.md`.
Scope: The seven supported page types, their frontmatter profiles, title prefixes, required sections, and type-specific boundaries.
Out of Scope: Wiki storage selection, source authority, readiness claims, external tools, and project-specific content.
Evidence Level: Source-validation authoring contract only.
Safe to Share / Redaction Notes: Safe to share as-is; authored pages still require project-specific redaction review.

Use one profile per page. Keep the common frontmatter and claim shape from `page.md`; replace every placeholder. Section names and order below are required unless the project schema explicitly defines a stricter compatible profile.

### `concept`

- Title prefix: `Concept`
- Target reader: `Project maintainers and future agent sessions`
- Reader action: `Use for orientation only; inspect cited source before implementation or verification.`
- Default evidence layer / stale risk: `unknown` / `medium`
- Section order: `Summary` -> `Material Claims` -> `Related Pages` -> `Open Gaps`

### `contract`

- Title prefix: `Contract`
- Target reader: `Project maintainers, implementers, reviewers, and future agent sessions`
- Reader action: `Use as claim inventory only; inspect cited contract or source evidence before implementation or verification.`
- Default evidence layer / stale risk: `unknown` / `high`
- Section order: `Boundary` -> `Confirmed Contract Claims` -> `Unknown or Contested Claims` -> `Do Not Assume` -> `Open Gaps`
- `Confirmed Contract Claims` uses the material-claim shape from `page.md`.

### `decision`

- Title prefix: `Decision`
- Target reader: `Project maintainers and future agent sessions`
- Reader action: `Use for orientation only; inspect cited source before implementation or verification.`
- Default evidence layer / stale risk: `unknown` / `medium`
- Section order: `Decision` -> `Rationale` -> `Material Claims` -> `Supersession` -> `Open Gaps`

### `procedure`

- Title prefix: `Procedure`
- Target reader: `Project maintainers, operators, implementers, and future agent sessions`
- Reader action: `Follow only after checking prerequisites, source links, and stale risk.`
- Default evidence layer / stale risk: `unknown` / `medium`
- Section order: `Prerequisites` -> `Steps` -> `Material Claims` -> `Failure Modes` -> `Open Gaps`
- `Steps` is an ordered list.

### `query`

- Title prefix: `Query`
- Target reader: `Project maintainers and future agent sessions`
- Reader action: `Reuse the answer only within the stated evidence boundary and inspect cited sources when the claim matters.`
- Default evidence layer / stale risk: `unknown` / `medium`
- Section order: `Answer Boundary` -> `Answer` -> `Material Claims` -> `Follow-up Wiki Updates`
- `Answer Boundary`: `wiki_synthesis_only | source_backed | insufficient | blocked`

### `summary`

- Title prefix: `Summary`
- Target reader: `Project maintainers and future agent sessions`
- Reader action: `Use for orientation only; inspect cited source before implementation, verification, or readiness claims.`
- Default evidence layer / stale risk: `unknown` / `medium`
- Section order: `Summary Boundary` -> `Summary` -> `Material Claims` -> `Source Inventory` -> `Open Gaps`
- `Summary Boundary`: `wiki_synthesis_only | source_backed | insufficient | blocked`

### `term`

- Title prefix: `Term`
- Target reader: `Project maintainers, PRD authors, implementers, reviewers, and future agent sessions`
- Reader action: `Use term alignment only within the stated evidence layer; inspect source or contract evidence before promoting.`
- Default evidence layer / stale risk: `glossary_only` / `medium`
- Section order: `Meaning` -> `Aliases and Homonyms` -> `Material Claims` -> `Promotion Boundary`
- Promotion boundary: Glossary-only alignment is not PRD truth, contract truth, source truth, runtime evidence, verification evidence, release evidence, UAT evidence, or customer readiness.
