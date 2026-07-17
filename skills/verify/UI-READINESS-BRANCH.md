# UI Readiness Branch

Target Reader: Codex running `verify` for browser-visible, responsive, interaction, visual, console, network, or scripted UI evidence claims.
Reader Action Needed: Choose the right UI evidence tool, check prototype annotation decisions item by item, and avoid treating visual packets or prototypes as runtime/browser/UAT/release evidence by themselves.
Decision Supported: Whether UI-related readiness claims and annotation decision carry-through are observed, unsupported, mismatched, or still unverified.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/verify/UI-TOOL-ROUTER.md`, `skills/_shared/VISUAL-HANDOFF-PACKET.md`, `skills/prototype/DECISION-CAPTURE.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, `docs/prd-v0.5-prototype-first-skill-expansion.md` GW-PROT-ANNOT-001, and `artifacts/v0.5-prototype-first-skill-expansion/issue-map.md` GW-PROT-ANNOT-001.
Scope: UI tool choice, UI evidence report shape, visual packet evidence boundary, per-annotation carry-through, and mock/API contract separation.
Out of Scope: Implementing UI changes, installing browser tooling, bypassing security interstitials, or approving UAT/release.
Evidence Level: Source-validation policy only unless browser/runtime evidence is actually produced and named.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required References

- Load `SCOPE-EVIDENCE-TEMPLATE.md` first.
- Apply `EB-VISUAL-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` before using visual packets, screenshots, generated images, HTML packets, or prototype output.
- Load `UI-TOOL-ROUTER.md` for tool choice and `UI Evidence` shape.
- Load `skills/_shared/VISUAL-HANDOFF-PACKET.md` when the claim depends on a visual handoff packet, HTML packet, screenshot set, generated image, or prototype output.
- Load `skills/prototype/DECISION-CAPTURE.md` when the source prototype, visual packet, or handoff contains or references an `Annotation Presentation Decision`.
- Load the conditional `UAT Evidence Window` in `skills/_shared/RELEASE-EVIDENCE-CLAIM.md` when UI observations are attributed to a fix, artifact, deployed version, mutable shared environment, or redeploy/rerun chain.

## Branch Rules

- UI tool routing, frontend/backend contract review, and visual evidence reports still start with the `Verification Scope` block.
- Do not claim layout, color, responsiveness, hover/focus, animation, state-transition correctness, console health, or network behavior without matching browser/runtime/tool evidence.
- Reclassify visual packets, screenshots, generated images, HTML packets, and prototype outputs as communication artifact evidence unless a separate qualifying browser/runtime run is named.
- Do not treat mock fields from a visual packet or prototype as confirmed API/schema/source truth; classify them as `mock / illustrative / not backend contract` or `proposed contract hypothesis`.
- If the chosen UI tool does not cover the claim, mark the uncovered claim `unverified`.
- Do not claim browser/runtime/UAT/release evidence from a visual packet unless separately named qualifying evidence is inspected.
- When UI evidence supports a version-attributed UAT claim, bind it to the matching UAT evidence window or its canonical reference. If the relevant SUT fingerprint changes, partition or invalidate affected UI observations instead of combining them into one pass.

## Annotation Carry-through Check

When annotation decisions exist, enumerate the complete source `Annotation ID` set and produce one row per ID:

| Annotation ID | Purpose | Disposition | Required Conditional Field | Observed Target or Reference | Carry-through Verdict |
| --- | --- | --- | --- | --- | --- |
| `<stable ID>` | `<source purpose>` | `<source disposition>` | `none` / `Audience-facing Source: ...` / `Companion Reference: ...` | `<named artifact, section, UI evidence, or missing>` | `covered` / `gap` / `unverified` |

For a machine-consumed per-ID check, repeat this equivalent block instead of the table:

```text
Annotation Carry-through Check
- Annotation ID:
- Source Purpose:
- Source Disposition:
- Required Conditional Field: none | Audience-facing Source: ... | Companion Reference: ...
- Observed Target or Reference:
- Carry-through Verdict: covered | gap | unverified
```

Apply these checks:

1. The downstream inline blocks or cited canonical reference must cover the same ID set exactly once. A missing, duplicated, renamed, or unexplained additional ID is a `gap`.
2. Purpose and disposition must match the source decision unless a newer authoritative decision is named. An unreferenced rewrite is a `gap`, not a new canonical decision.
3. `retain_as_audience_content_candidate` requires the same-block `Audience-facing Source`, and its value must match the source decision unless a newer authoritative decision is named. A missing or mismatched value is a `gap`. Retention remains a content candidate and does not prove implementation, acceptance, browser/runtime behavior, UAT, release, or readiness.
4. `separate_review_companion` requires the same-block `Companion Reference`; its value must match the source decision unless a newer authoritative decision is named, and the reference must resolve to a separately named review or handoff companion. A missing, mismatched, or unresolved value is a `gap`. Confirming that the aid is absent from the target surface still requires matching artifact or browser evidence.
5. `remove_before_final` requires both conditional fields to be absent. Confirming actual removal from the target UI, export, screenshot, demo, or presentation requires matching artifact or browser evidence; otherwise the removal outcome remains `unverified` even when source carry-through is covered.
6. Keep the enclosing `Verification Scope` consistent with the per-ID verdicts: all `covered` means `Verdict: pass`; any `gap` means `Verdict: fail`; no gap with at least one `unverified` item means `Verdict: partial`. `Covered` lists only covered IDs, while `Missing` lists every gap or unverified ID.
