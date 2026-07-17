Target Reader: Maintainers and eval runners inspecting the prototype-annotation fixture.
Reader Action Needed: Use the per-ID decisions below as the canonical source state for downstream carry-through checks.
Decision Supported: Which prototype-originated annotations are removed and which one may remain as an audience-content candidate.
Artifact Type: prototype annotation decision-source fixture
Source of Truth: `index.html` for annotation identity and purpose; `user_instruction:final_help_copy` for the `help_explanation` retention decision.
Scope: The four annotation IDs in this fixture and their presentation dispositions.
Out of Scope: Production implementation, browser behavior, runtime behavior, UAT, release, customer readiness, and API/schema truth.
Evidence Level: Source-only fixture evidence.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, logs, or private payloads.

<a id="prototype-annotation-decision-source"></a>
# Prototype Annotation Decision Source

## Annotation Presentation Decision

- Annotation ID: review_arrows
- Annotation Purpose: internal flow explanation
- Presentation Disposition: remove_before_final

## Annotation Presentation Decision

- Annotation ID: debug_badges
- Annotation Purpose: internal state debugging
- Presentation Disposition: remove_before_final

## Annotation Presentation Decision

- Annotation ID: design_notes
- Annotation Purpose: designer review rationale
- Presentation Disposition: remove_before_final

## Annotation Presentation Decision

- Annotation ID: help_explanation
- Annotation Purpose: candidate audience help copy
- Presentation Disposition: retain_as_audience_content_candidate
- Audience-facing Source: user_instruction:final_help_copy

## Prototype Evidence Boundary

This file records source-only fixture decisions. It does not prove that the retained candidate is implemented or accepted in a product surface, and it provides no browser, runtime, UAT, release, customer-readiness, or API/schema evidence.
