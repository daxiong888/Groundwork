"""Artifact-oriented deterministic checks."""

from .common import has_required_field
from .results import checker_result

MISSING_TARGET_READER_CHECKER_ID = "artifact.missing_target_reader"


def check_missing_target_reader(text):
    if not has_required_field(text, "Target Reader"):
        return checker_result(
            MISSING_TARGET_READER_CHECKER_ID,
            "fail",
            severity="p2",
            fix_locus="artifact_policy",
            notes=["artifact header missing Target Reader"],
        )
    return checker_result(MISSING_TARGET_READER_CHECKER_ID, "pass")

