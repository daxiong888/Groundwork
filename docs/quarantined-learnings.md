# Quarantined Learning Proposals

Target Reader: Groundwork maintainer reviewing repeated fixture or runtime failures.
Reader Action Needed: Decide whether a proposed skill/doc/eval patch should stay quarantined, be accepted, be rejected, or be promoted.
Decision Supported: Controlled self-evolution without automatic repository mutation.
Scope: Proposal format, status lifecycle, promotion criteria, rollback requirements, and human decision recording.
Out of Scope: Auto-applying patches, committing `.groundwork/harness` runtime content, mutating `main`, opening PRs, or changing production systems.
Evidence Level: Groundwork issue #16 acceptance criteria and `docs/nightly-harness.md`.

## Purpose

A quarantined learning proposal captures a repeated Groundwork failure and a possible patch without applying it automatically. The proposal is evidence for a human decision, not a runtime instruction to mutate skills or docs.

## Proposal Format

```text
Quarantined Learning Proposal
- Observed Failure:
- Affected Skill:
- Regression Evidence:
- Proposed Patch:
- Risk:
- Rollback:
- Promotion Criteria:
- Human Decision:
- Status: quarantined / accepted / rejected / promoted
```

## Field Rules

- `Observed Failure`: name the fixture row, runtime prompt, command, or baseline where the failure occurred.
- `Affected Skill`: name one public skill or shared reference. If multiple skills are affected, create separate proposals or state the primary owner.
- `Regression Evidence`: cite the prompt id, expected behavior, forbidden behavior, actual behavior, and relevant command or runtime observation.
- `Proposed Patch`: describe the smallest skill/doc/eval change. Do not include an unreviewed broad rewrite.
- `Risk`: state how the patch could make skill selection, artifact writing, safety gates, or output shape worse.
- `Rollback`: state the file-level revert or removal path.
- `Promotion Criteria`: define what must pass before the proposal can become a normal issue or patch.
- `Human Decision`: record `accepted`, `rejected`, `needs-info`, or `defer`.
- `Status`: use `quarantined`, `accepted`, `rejected`, or `promoted`.

## Storage Boundary

- Runtime-generated learning drafts belong under ignored `.groundwork/harness/` by default.
- Do not commit `.groundwork/harness` learning contents unless the user explicitly approves a specific policy or report file.
- Durable policy belongs in `docs/`.
- Eval-backed accepted changes should land as ordinary scoped commits against `skills/`, `docs/`, or `evals/`.

## Promotion Criteria

A proposal can be promoted only when:

- the failure is reproducible from a fixture, baseline, or captured runtime trial
- the affected skill or doc owner is clear
- the proposed patch is smaller than the failure it fixes
- the patch does not add a new public skill unless an issue explicitly requires it
- the patch respects git boundary and artifact policy
- rollback is clear
- a human accepts the proposal or opens a scoped follow-up issue

## Rejection Criteria

Reject or keep quarantined when:

- the evidence is anecdotal or not reproducible
- the patch would broaden public skill surface without an issue
- the patch changes production systems, remote trackers, shared global skills, or runtime directories
- the patch depends on a tool or API not available in the target environment
- the patch duplicates an existing PRD, plan, or source artifact
