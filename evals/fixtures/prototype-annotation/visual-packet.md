Target Reader: Maintainers, handoff authors, and verification reviewers using the prototype-annotation fixture.
Reader Action Needed: Carry or compare every annotation decision per stable ID without changing its purpose, disposition, or disposition-specific field.
Decision Supported: Whether a downstream visual packet preserves the complete selective-retention decision set.
Artifact Type: source-only visual handoff packet fixture
Source of Truth: [`decision-source.md`](decision-source.md)
Scope: Inline carry-through for `review_arrows`, `debug_badges`, `design_notes`, and `help_explanation`.
Out of Scope: Production implementation, browser behavior, runtime behavior, UAT, release, customer readiness, and API/schema truth.
Evidence Level: Source-only fixture evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, screenshots, or private payloads.

# Prototype Annotation Visual Packet

The blocks below carry the canonical decision-source fields through unchanged. Stable per-ID anchors support handoff references and verification comparisons.

## <a id="review_arrows"></a>`review_arrows`

### Annotation Presentation Decision

- Annotation ID: review_arrows
- Annotation Purpose: internal flow explanation
- Presentation Disposition: remove_before_final

## <a id="debug_badges"></a>`debug_badges`

### Annotation Presentation Decision

- Annotation ID: debug_badges
- Annotation Purpose: internal state debugging
- Presentation Disposition: remove_before_final

## <a id="design_notes"></a>`design_notes`

### Annotation Presentation Decision

- Annotation ID: design_notes
- Annotation Purpose: designer review rationale
- Presentation Disposition: remove_before_final

## <a id="help_explanation"></a>`help_explanation`

### Annotation Presentation Decision

- Annotation ID: help_explanation
- Annotation Purpose: candidate audience help copy
- Presentation Disposition: retain_as_audience_content_candidate
- Audience-facing Source: user_instruction:final_help_copy

## Prototype Evidence Boundary

This packet is source-only communication evidence. Its field carry-through does not prove implementation, acceptance, browser or runtime behavior, UAT, release, customer readiness, or API/schema truth; those claims require separately named qualifying evidence.
