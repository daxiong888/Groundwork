"""Common deterministic check helpers."""

import re


def missing_required_fields(text, fields):
    return [field for field in fields if not has_required_field(text, field)]


def has_required_field(text, field):
    pattern = re.compile(
        r"^\s*(?:#{1,6}\s*)?(?:[-*]\s*)?(?:\*\*)?"
        + re.escape(field)
        + r"(?:\*\*)?\s*:",
        re.IGNORECASE | re.MULTILINE,
    )
    return bool(pattern.search(text))
