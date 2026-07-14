"""Verify-related deterministic check constants."""

VERIFY_SCOPE_FIELDS = ["Claim", "Covered", "Missing"]
VERIFY_SCOPE_FIELD_ALIASES = {
    "Claim": ["Claim", "User-visible Claim Being Verified", "In Scope"],
    "Covered": ["Covered"],
    "Missing": ["Missing", "Not Covered"],
}


def missing_verify_scope_fields(text):
    lowered = str(text or "").lower()
    return [
        field
        for field, aliases in VERIFY_SCOPE_FIELD_ALIASES.items()
        if not any(f"{alias.lower()}:" in lowered for alias in aliases)
    ]
QA_FAILURE_FIELDS = [
    "Expected",
    "Actual",
    "Reproduction",
    "Severity",
    "Minimal Diagnosis",
    "Fix Plan",
    "Gap Closure Plan",
    "Re-QA Required",
    "Regression Note",
    "Scoped Next Action",
]
ARTIFACT_HEADER_FIELDS = [
    "Target Reader",
    "Reader Action Needed",
    "Artifact Type",
    "Source of Truth",
    "Safe to Share / Redaction Notes",
]
