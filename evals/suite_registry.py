"""Canonical eval-suite selection shared by runners and coverage checks."""


DEFAULT_SUITES = (
    "smoke.csv",
    "safety.csv",
    "reliability.csv",
    "guardrails-regression.csv",
    "v0.5.2-wiki.csv",
    "lifecycle-state.csv",
    "lifecycle-preflight-regressions.csv",
    "routing-reliability.csv",
    "routing-blind.csv",
    "trace-first-verify-review.csv",
)
