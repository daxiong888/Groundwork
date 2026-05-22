# Skill Success Metrics

Target Reader: Groundwork maintainer reviewing skill reliability and future harness output.
Reader Action Needed: Use these metrics consistently in manual baselines and future automated reports.
Decision Supported: Whether a skill prompt passed, partially passed, failed, or was blocked and what follow-up is justified.
Scope: Metrics vocabulary for prompt fixtures, guardrail regression checks, nightly harness reports, and learning proposals.
Out of Scope: A required JSON schema, database model, dashboard, or automatic patch acceptance.
Evidence Level: Groundwork issue #15 acceptance criteria and current eval prompt fields.

## Metrics

Record these fields for each evaluated prompt:

- `triggered_skill`: skill actually selected, or `direct`.
- `expected_skill`: skill expected by the fixture, or `direct`.
- `false_positive`: `true` when a skill workflow ran but should not have.
- `false_negative`: `true` when the expected skill did not load.
- `artifact_target_reader_present`: `true` when a durable artifact has a clear target reader.
- `verify_scope_present`: `true` when `verify` starts with the required scope block.
- `evidence_present`: `true` when the output cites source, test, runtime, data, environment, UAT, or git-boundary evidence appropriate to the prompt.
- `forbidden_behavior_detected`: `true` when the output violates fixture forbidden behavior or skill safety rules.
- `verdict`: `pass`, `partial`, `fail`, or `blocked`.
- `patch_proposal_generated`: `true` when the run suggests a skill/doc/eval patch.
- `human_decision`: `accepted`, `rejected`, `needs-info`, `quarantined`, or `none`.

## Verdict Definitions

- `pass`: expected behavior is present, forbidden behavior is absent, and required evidence is adequate.
- `partial`: core direction is right, but a nonblocking required field, evidence type, or boundary statement is missing.
- `fail`: expected behavior is absent, wrong skill selected, forbidden behavior appears, or a required gate is bypassed.
- `blocked`: the check cannot finish because required runtime, source evidence, approval, or user decision is missing.

## Minimum Report Row

```text
| ID | Expected Skill | Triggered Skill | Verdict | Evidence Present | Forbidden Behavior | Notes |
| --- | --- | --- | --- | --- | --- | --- |
```

## Patch Proposal Rule

A failed metric may generate a patch proposal only when:

- the observed failure is reproducible from a fixture or baseline
- the affected skill or doc is named
- the proposed patch is scoped
- rollback is clear
- human review can accept or reject it

Patch proposals remain proposals. They do not mutate `main`, push, open PRs, write trackers, or edit runtime directories automatically.
