# Handoff: Prototype Contract Boundary Example

Target Reader: Future Groundwork maintainer updating or reviewing this example.
Reader Action Needed: Continue from the recorded evidence without rediscovering the v0.2.x prototype boundary context.
Decision Supported: Whether the example can remain a formal real maintenance case study.
Scope: Public documentation and example files for the prototype contract-boundary case.
Out of Scope: Backend API approval, frontend UI approval, runtime reruns, or modifying `prototype` behavior.
Evidence Level: Static repository evidence plus recorded v0.2.2/v0.2.3 runtime baseline results.

## Current State

The example is ready as a documentation case study. It uses repository evidence from real prototype boundary hardening and does not invent PR numbers, backend contracts, or runtime results.

## Source Artifacts

| Artifact | Role |
| --- | --- |
| `README.md` | Case overview and maintainer value |
| `prd.md` | Problem, goal, acceptance criteria, and non-goals |
| `implement.md` | What changed and what checks were recorded |
| `verify.md` | Claim-to-evidence mapping |

## Evidence

- Code truth: `skills/prototype/SKILL.md`, `skills/prototype/CONTRACT-BOUNDARY.md`.
- Release notes: `CHANGELOG.md` v0.2.2.
- Runtime records: `evals/baselines/2026-05-22-v0.2.2-runtime-baseline.md` and `evals/baselines/2026-05-25-v0.2.3-runtime-baseline.md`.
- Runtime rows: `gr-002` and `rel-008` in v0.2.2, plus targeted `gr-002` in v0.2.3.

## Open Risks

| Risk | Severity | Next Check |
| --- | --- | --- |
| Example can become stale if `prototype` behavior changes later | P3 | Compare this example against current `skills/prototype/*` before the next release |
| Readers may treat prototype classification as backend approval | P2 | Keep the not-backend-contract wording in README and PRD |

## Do Not Assume

- Prototype display fields exist in backend responses.
- Client-derived logic is approved product behavior.
- A visual prototype is integration-ready without browser/runtime evidence.

## Next Action

Keep this example linked from `README.md` and `docs/maintainer-workflows.md`. Refresh it only when prototype contract-boundary behavior or runtime evidence materially changes.

