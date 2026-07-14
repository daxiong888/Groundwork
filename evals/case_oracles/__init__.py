"""Fixture-owned evaluator oracles keyed by case id."""

from . import implement_root_cause


ORACLES = {
    implement_root_cause.CASE_ID: implement_root_cause.validate,
}


def validate_case(row, cwd, changes, *, repo, run_check):
    oracle = ORACLES.get(str(row.get("id") or ""))
    if oracle is None:
        return []
    return oracle(cwd, changes, repo=repo, run_check=run_check)
