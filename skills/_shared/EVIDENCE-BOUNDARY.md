Target Reader: Groundwork skill authors, implementers, dispatchers, handoff authors, wiki maintainers, clean reviewers, verifiers, and release reviewers.
Reader Action Needed: Cite the numbered claim-boundary IDs instead of copying long evidence-boundary prose into public skills.
Decision Supported: Which evidence may support a claim, which stronger claims remain blocked, and which detailed shared reference owns the operational rules.
Artifact Type: shared guardrail and claim-boundary taxonomy.
Source of Truth: `skills/_shared/SKILL-AUDIT.md`, `skills/_shared/RUNTIME-CAPABILITY.md`, `skills/_shared/LLM-WIKI.md`, `skills/_shared/ROLE-SEPARATION.md`, `skills/_shared/REVIEW-LOOP.md`, `skills/_shared/VISUAL-HANDOFF-PACKET.md`, `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, and `docs/release-evidence-claim-boundary.md`.
Scope: Cross-skill evidence claim boundaries, short reusable IDs, owning references, and anti-duplication audit guidance.
Out of Scope: Replacing detailed runtime, wiki, role-separation, review-loop, visual packet, release-claim, verification, or output-shape contracts.
Evidence Level: Source-validation policy only. This taxonomy does not prove runtime behavior, cache/source equivalence, browser behavior, clean review, independent verification, UAT, release readiness, marketplace behavior, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private URLs, runtime logs, or production payloads.

# Evidence Boundary Taxonomy

## Core Rule

Public skills should cite these claim-boundary IDs and load the detailed shared reference only when the active branch needs operational detail.

Do not copy long "Do not claim X from Y" policy blocks into public skills. Keep public skill text to:

```text
Apply EB-<FAMILY>-<NNN> from `skills/_shared/EVIDENCE-BOUNDARY.md`.
Skill-specific delta: <only the behavior unique to this skill>.
```

If a boundary changes, update this taxonomy and the owning detailed reference first. Then update public skills only when their skill-specific delta changes.

## Claim Families

| ID | Boundary | Qualifying Evidence | Non-Evidence / Blocked Upgrade | Owning References |
| --- | --- | --- | --- | --- |
| `EB-RUNTIME-001` | Source diff, docs, prompt text, package text, model-menu seeds, and local source-validation checks are not runtime execution evidence. | Named command, adapter, browser/runtime tool, API, or runtime trial output for the specific claim, with scope and limitations. | Source diff, implementation summary, prompt preference, dispatch package, old note, local CSV parse, or fixture inspection. | `skills/_shared/RUNTIME-CAPABILITY.md`, `docs/release-evidence-claim-boundary.md` |
| `EB-CACHE-001` | Source checkout is not installed plugin cache, marketplace, cache refresh, or source/cache equivalence evidence. | Installed plugin root, local source root, refresh or equivalence method, run scope, commands or trials, and limitations. | Local checkout path, edited files, plugin manifest parse, fixture pass, or source-only eval. | `skills/_shared/RUNTIME-CAPABILITY.md`, `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, `docs/release-evidence-claim-boundary.md` |
| `EB-WIKI-001` | Wiki synthesis, wiki audit, page-level source inventory, and external graph/search/index output are orientation or claim inventory, not source truth or readiness evidence. | Cited source, accepted contract, inspected code/schema/API, test output, runtime/browser evidence, release evidence, or explicit scoped user confirmation. | Wiki page text, uncited claims, stale/contested pages, glossary-only entries, page-level source lists, graph/search/index summaries. | `skills/_shared/LLM-WIKI.md`, `skills/_shared/DOMAIN-LANGUAGE.md` |
| `EB-ROLE-001` | Self-check and same-session review are not clean review, independent verification, acceptance, release, UAT, customer, or final readiness evidence. | Fresh read-only clean review from an independent reviewer for clean-review claims; explicit-scope independent verification for verification claims. | Implementer self-review, self-run tests, same-session designer/implementer/verifier collapse, reviewer self-fix followed by pass. | `skills/_shared/ROLE-SEPARATION.md`, `skills/_shared/REVIEW-LOOP.md`, `skills/_shared/SKILL-AUDIT.md` |
| `EB-VERIFY-001` | Code diff, implementation summary, source-validation checks, or old evidence do not by themselves prove readiness. | Scope-first verification that maps covered and not-covered claims to current source, tests, runtime/browser/data/environment/UAT/release evidence as applicable. | Diff-only review, old test run, stale handoff, source-only checks, implementation conformance report, or missing-command/no-command assertion. | `skills/verify/SKILL.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, `skills/_shared/ROLE-SEPARATION.md` |
| `EB-VISUAL-001` | Screenshot, generated image, HTML packet, visual packet, static prototype, or prototype output is not browser runtime evidence, API/schema truth, release evidence, UAT evidence, customer readiness, or implementation authority by itself. | Browser/UI run with URL/context/action/observation/limitation for browser claims; named source/API/schema/runtime/UAT/release evidence for stronger claims. | Visual packet text, image appearance, mock field, prototype-only fixture, static HTML existence, screenshot without recorded browser context. | `skills/_shared/VISUAL-HANDOFF-PACKET.md`, `skills/prototype/CONTRACT-BOUNDARY.md`, `skills/verify/UI-TOOL-ROUTER.md` |
| `EB-RELEASE-001` | Clean review, fixture pass, PRD acceptance, issue-pack completion, source-validation checks, or package completeness are not release, UAT, customer, marketplace, runtime, or cache readiness. | `release_evidence_claim` or equivalent release claim object with named evidence, installed plugin/source details when relevant, run scope, limitations, missing evidence, and maintainer/customer/UAT evidence for that boundary. | Clean-looking UI, local diff, fixture pass, clean review pass, runtime recommendation, wiki audit, source-only CI, or package schema completeness. | `skills/_shared/RELEASE-EVIDENCE-CLAIM.md`, `docs/release-evidence-claim-boundary.md`, `skills/_shared/RUNTIME-CAPABILITY.md` |

## Skill Application Map

Use the narrowest applicable IDs:

- `to-prd`: apply `EB-WIKI-001` when wiki or external recall informs PRD shaping; apply `EB-VERIFY-001` when PRD intent is being mistaken for downstream readiness.
- `implement`: apply `EB-RUNTIME-001`, `EB-CACHE-001`, `EB-WIKI-001`, `EB-ROLE-001`, and `EB-RELEASE-001` when final reports discuss those evidence layers.
- `verify`: apply all IDs that match the claim under verification; `EB-VERIFY-001` is always in scope for readiness or evidence-sufficiency questions.
- `handoff`: apply `EB-ROLE-001`, `EB-VISUAL-001`, `EB-WIKI-001`, `EB-RUNTIME-001`, `EB-CACHE-001`, and `EB-RELEASE-001` when preserving continuation evidence or do-not-assume boundaries.
- `dispatch`: apply `EB-RUNTIME-001`, `EB-CACHE-001`, `EB-WIKI-001`, `EB-ROLE-001`, and `EB-RELEASE-001` when routing work or packaging result expectations.
- `wiki`: apply `EB-WIKI-001`; add `EB-RUNTIME-001`, `EB-CACHE-001`, `EB-ROLE-001`, and `EB-RELEASE-001` when wiki claims touch those stronger boundaries.

## Skill-Specific Delta Pattern

Public skills may add only the delta that changes action:

- `dispatch` may include wiki pages as orientation in `source_package`, but must label them non-authoritative and require downstream source inspection.
- `handoff` may preserve received evidence and `Do-Not-Assume` boundaries, but must not upgrade the evidence.
- `implement` may run self-checks and report source-validation checks, but clean review and readiness remain separate routes.
- `to-prd` may use wiki context to reduce repeated questions only when the material claim is source-backed or explicitly marked as needing clarification.
- `verify` may pass only the claim covered by current scoped evidence and must mark uncovered stronger claims unverified.
- `wiki` may store claim inventory and citations, but stronger claims remain blocked until their owning evidence is inspected.

## Grep-Based Audit Note

Use this review note during material skill changes to catch copied boundary blocks in public skills:

```bash
rg -n "Do not claim installed-plugin runtime behavior|Do not treat wiki synthesis as source truth|A code diff or implementation summary alone is not readiness evidence|A visual packet is a communication artifact|Release readiness is not inferred|Self-checks are useful implementation hygiene" skills/*/SKILL.md
```

Expected result: no matches in public `SKILL.md` files unless the line is a trigger example or a clearly necessary skill-specific delta. Prefer an `EB-*` citation plus a short delta over copied prose.

When a new boundary phrase appears repeatedly across public skills, add or extend an `EB-*` ID here before updating individual skills.
