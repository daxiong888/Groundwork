"""Stable checker result helpers."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class CheckerResult:
    checker_id: str
    verdict: str
    severity: str = "none"
    fix_locus: Optional[str] = None
    notes: Tuple[str, ...] = ()

    def to_score_dict(self):
        result = {
            "checker_id": self.checker_id,
            "verdict": self.verdict,
            "severity": self.severity,
            "notes": list(self.notes),
        }
        if self.fix_locus is not None:
            result["fix_locus"] = self.fix_locus
        return result


def checker_result(checker_id, verdict, *, severity="none", fix_locus=None, notes=None):
    return CheckerResult(
        checker_id=checker_id,
        verdict=verdict,
        severity=severity,
        fix_locus=fix_locus,
        notes=tuple(notes or ()),
    ).to_score_dict()
