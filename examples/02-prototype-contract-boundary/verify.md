# Verification Report: Prototype Contract Boundary

Target Reader: Groundwork maintainer validating the prototype contract-boundary case study.
Reader Action Needed: Review the claim-to-evidence mapping and decide whether the example is supported by repository evidence.
Decision Supported: Whether this is a real maintenance example rather than a hypothetical prototype policy.
Scope: Evidence already recorded in repository files for prototype contract-boundary behavior.
Out of Scope: Re-running runtime evals, inspecting a live frontend, or approving any backend contract.
Evidence Level: Static repository evidence from prototype skill files, changelog, and v0.2.2/v0.2.3 runtime baselines.

## Verification Scope

- In Scope: prototype contract-boundary classification and recorded baseline evidence.
- Out of Scope: backend source-truth verification, UI visual verification, current plugin installation state, and release approval.
- Covered: source docs, skill rules, changelog summary, and recorded runtime rows.
- Not Covered: a fresh runtime rerun for this example directory.
- Evidence Sources: `skills/prototype/SKILL.md`, `skills/prototype/CONTRACT-BOUNDARY.md`, `CHANGELOG.md`, `evals/baselines/2026-05-22-v0.2.2-runtime-baseline.md`, and `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`.
- User-visible Claim Being Verified: Groundwork has a real example where prototype outputs avoid inventing backend contract.

## Claim Evidence Matrix

| Claim / AC | Evidence | Result | Gap | Severity |
| --- | --- | --- | --- | --- |
| AC-1: backend contract candidates are classified | `CONTRACT-BOUNDARY.md` defines backend contract candidates and proposed hypotheses | pass | Fresh runtime is not rerun in this example | none |
| AC-2: mock fields are labeled not backend contract | `CONTRACT-BOUNDARY.md` requires `mock / illustrative / not backend contract` | pass | None for static evidence | none |
| AC-3: client-derived logic is labeled not backend contract | `CONTRACT-BOUNDARY.md` requires `derived / illustrative / not backend contract` | pass | None for static evidence | none |
| AC-4: output includes contract status fields | `skills/prototype/SKILL.md` requires `Contract Status`, field classes, and `Contract Impact` | pass | None for static evidence | none |
| AC-5: prototype is not frontend contract by default | `skills/prototype/SKILL.md` states prototype output is not frontend contract unless claims are source-backed or explicitly confirmed | pass | None for static evidence | none |
| Runtime evidence exists | v0.2.2 `gr-002` and `rel-008` passed; v0.2.3 targeted `gr-002` passed after routing fix | pass | Recorded evidence is historical | P3 |

## Verdict

pass for repository-backed example status.

The example is supported as a historical Groundwork maintenance case. It does not prove a current backend contract or current visual behavior.

## Unverified Claims

- Current installed plugin cache behavior is not checked by this example.
- Visual behavior of any static prototype needs separate browser/runtime evidence.

