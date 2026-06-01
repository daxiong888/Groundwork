# Handoff: Scope-First Verification Example

Target Reader: Future Groundwork maintainer updating or reviewing this example.
Reader Action Needed: Continue from the recorded evidence without rediscovering the v0.2.x verification hardening context.
Decision Supported: Whether the example can remain a formal real maintenance case study.
Scope: Public documentation and example files for the scope-first verification case.
Out of Scope: Runtime reruns, release approval, or modifying `verify` behavior.
Evidence Level: Static repository evidence plus recorded v0.2.3 runtime baseline results.

## Current State

The example is ready as a documentation case study. It uses repository evidence from the real `verify` hardening line and does not invent PR numbers, release claims, or runtime results.

## Source Artifacts

| Artifact | Role |
| --- | --- |
| `README.md` | Case overview and maintainer value |
| `prd.md` | Problem, goal, acceptance criteria, and non-goals |
| `implement.md` | What changed and what checks were recorded |
| `verify.md` | Claim-to-evidence mapping |

## Evidence

- Code truth: `skills/verify/SKILL.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, `skills/verify/LENSES.md`.
- Release notes: `CHANGELOG.md` v0.2.2 and v0.2.3.
- Runtime record: `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`.
- Targeted rows: `rel-002`, `gr-002`, `gr-005`, `gr-010`, and `gr-015` passed in the v0.2.3 targeted rerun.

## Open Risks

| Risk | Severity | Next Check |
| --- | --- | --- |
| Example can become stale if `verify` behavior changes later | P3 | Compare this example against current `skills/verify/*` before the next release |
| Recorded runtime evidence is historical | P3 | Run the relevant eval subset before treating it as release-gating |

## Do Not Assume

- This example proves current runtime behavior without a fresh rerun.
- A scope-first report alone proves UAT readiness.
- A diff summary is enough readiness evidence.

## Next Action

Keep this example linked from `README.md` and `docs/maintainer-workflows.md`. Refresh it only when `verify` behavior or runtime evidence materially changes.

