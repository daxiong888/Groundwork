# Prototype Annotation Fixture

This fixture separates prototype-originated review aids from product-owned content.

- Review annotation IDs: `review_arrows`, `debug_badges`, `design_notes`, and `help_explanation`.
- Product-owned content without an annotation ID: `validation_message`.
- `decision-source.md` records the complete selective-retention decision set used by handoff and verification rows.
- `visual-packet.md` carries that set through with stable per-ID anchors for exact downstream comparison.
- The fixture is static source evidence only. It is not browser, runtime, UAT, release, or readiness evidence.
