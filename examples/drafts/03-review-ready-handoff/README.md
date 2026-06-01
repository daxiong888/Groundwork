# Draft Preview: Review-Ready Handoff Package

Target Reader: Groundwork maintainer deciding whether a future handoff case has enough evidence to become a formal example.
Reader Action Needed: Treat this as a preview only and wait for complete source, implementation, verification, and handoff evidence before promoting it.
Decision Supported: Whether the future `handoff` example is ready to move from draft preview to real maintenance case study.
Scope: Intended future example for a release or PR where `handoff` produces a compact review package.
Out of Scope: Claiming this as a completed real example, creating supporting `prd.md`, `implement.md`, `verify.md`, or `handoff.md`, or changing `handoff` behavior.
Evidence Level: Preview based on existing `handoff` design intent and runtime rows, but not yet backed by a complete end-to-end release or PR case package.

This is a draft preview, not a formal real example.

The intended future case will show a release or PR where `handoff` produces a compact review package with:

- source artifacts and their roles
- code, test, runtime, UAT, contract, and git-boundary evidence when available
- open risks and gaps
- next action
- allowed and disallowed files when file boundary matters
- do-not-assume notes
- redaction notes

Do not add `prd.md`, `implement.md`, `verify.md`, or `handoff.md` here until the repository has complete end-to-end evidence for the case. When that evidence exists, promote this directory out of `examples/drafts/` and update `examples/README.md`.

