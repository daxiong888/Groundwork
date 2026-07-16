# UI Readiness Branch

Target Reader: Codex running `verify` for browser-visible, responsive, interaction, visual, console, network, or scripted UI evidence claims.
Reader Action Needed: Choose the right UI evidence tool and avoid treating visual packets or prototypes as runtime/browser/UAT/release evidence by themselves.
Decision Supported: Whether UI-related readiness claims are observed, unsupported, or still unverified.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/verify/UI-TOOL-ROUTER.md`, `skills/_shared/VISUAL-HANDOFF-PACKET.md`, and `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`.
Scope: UI tool choice, UI evidence report shape, visual packet evidence boundary, and mock/API contract separation.
Out of Scope: Implementing UI changes, installing browser tooling, bypassing security interstitials, or approving UAT/release.
Evidence Level: Source-validation policy only unless browser/runtime evidence is actually produced and named.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required References

- Load `SCOPE-EVIDENCE-TEMPLATE.md` first.
- Apply `EB-VISUAL-001` from `skills/_shared/EVIDENCE-BOUNDARY.md` before using visual packets, screenshots, generated images, HTML packets, or prototype output.
- Load `UI-TOOL-ROUTER.md` for tool choice and `UI Evidence` shape.
- Load `skills/_shared/VISUAL-HANDOFF-PACKET.md` when the claim depends on a visual handoff packet, HTML packet, screenshot set, generated image, or prototype output.
- Load the conditional `UAT Evidence Window` in `skills/_shared/RELEASE-EVIDENCE-CLAIM.md` when UI observations are attributed to a fix, artifact, deployed version, mutable shared environment, or redeploy/rerun chain.

## Branch Rules

- UI tool routing, frontend/backend contract review, and visual evidence reports still start with the `Verification Scope` block.
- Do not claim layout, color, responsiveness, hover/focus, animation, state-transition correctness, console health, or network behavior without matching browser/runtime/tool evidence.
- Reclassify visual packets, screenshots, generated images, HTML packets, and prototype outputs as communication artifact evidence unless a separate qualifying browser/runtime run is named.
- Do not treat mock fields from a visual packet or prototype as confirmed API/schema/source truth; classify them as `mock / illustrative / not backend contract` or `proposed contract hypothesis`.
- If the chosen UI tool does not cover the claim, mark the uncovered claim `unverified`.
- Do not claim browser/runtime/UAT/release evidence from a visual packet unless separately named qualifying evidence is inspected.
- When UI evidence supports a version-attributed UAT claim, bind it to the matching UAT evidence window or its canonical reference. If the relevant SUT fingerprint changes, partition or invalidate affected UI observations instead of combining them into one pass.
