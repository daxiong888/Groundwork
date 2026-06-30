# Verify Router Branches

Target Reader: Codex running `verify` after selecting `verify-lite`, `verify-standard`, or `verify-strict`.
Reader Action Needed: Apply branch-specific workflow, failure handling, gates, and optional output blocks without loading them in the active `SKILL.md` entry.
Decision Supported: Whether a verification claim is supported, partial, failed, blocked, or unverified, and what next task-state route is appropriate.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/verify/SKILL.md`, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, and shared evidence-boundary contracts.
Scope: Verify branch workflow, failure handling, optional lifecycle/task-state blocks, and output expansion rules.
Out of Scope: Implementation fixes, runtime execution, remote mutation, or replacing branch-specific references.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Branch Workflows

1. Start the final verification report with the complete six-field `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`.
2. State the named lens or branch being used.
3. State the claimed behavior before judging it.
4. Run lifecycle preflight when `STATE.md`, task-state, source-truth, UAT/release, or closeout claims are in scope.
5. Choose `verify-lite`, `verify-standard`, or `verify-strict` and apply the Evidence Search Boundary before expanding reads.
6. Inspect source, diff, test, runtime, browser, data, environment, or user-provided evidence only as needed for the active claim.
7. Load only the matching Branch Index file from `SKILL.md`.
8. Separate data, environment, customer/UAT, runtime/browser, and source/test evidence.
9. Map `Claim / AC -> Evidence -> Result -> Gap -> Severity`.
10. Mark missing checks as `unverified`.
11. Give a verdict: `pass`, `partial`, `fail`, or `blocked`.
12. Add a task-state recommendation after the verification body.
13. Add a lifecycle state note only when lifecycle-state thresholds are met.

## Failure Branches

| Trigger | Action | Output Requirement |
|---|---|---|
| Evidence is missing | Mark the claim `unverified` or `blocked`. | Put the missing evidence in `Not Covered`, `Gap`, or `Unverified Claims`; no `pass`. |
| Evidence conflicts | Name the conflict and separate source, diff, test, runtime, and user-provided claims. | Do not choose a readiness verdict until the canonical source is clear. |
| Tests were not run | Report tests as not run. | Do not claim test-backed behavior passed. |
| UI tool choice does not match the claim | Use `UI-TOOL-ROUTER.md` or mark UI evidence `unverified`. | Do not claim visual, responsive, interaction, console, or network evidence from the wrong tool. |
| UAT/customer readiness is claimed without runtime evidence | Separate source, test, runtime/browser, data, environment, and UAT/customer readiness. | Do not give UAT/customer `pass` without required runtime and readiness evidence. |
| Visual packet output is treated as browser/runtime/UAT/release evidence | Apply `EB-VISUAL-001`. | Mark stronger claims `unverified` unless actual evidence is produced and named. |
| Mock fields from a visual packet are treated as confirmed API/schema truth | Reclassify them as `mock / illustrative / not backend contract`. | Route source/API/schema confirmation to source inspection or mark the claim `unverified`. |

## Optional Blocks

Task-state recommendation:

```text
Task State Recommendation
- Next Task-State Action: triage closeout / gap closure / re-verify / blocked needs-info
- Reason:
- Evidence Needed Before Closeout:
- Suggested Triage Input:
```

Lifecycle state update, only when thresholds are met:

```text
Lifecycle State Update
- Needed: yes / no
- Target: artifacts/<workstream-slug>/STATE.md
- Current Gap Closure:
- Re-verify Required:
- State Freshness Risk:
```

## Do Not

- Do not use a user summary, implementation summary, changelog, issue comment, or old handoff as evidence unless it is explicitly labeled as the claim being checked.
- Do not issue a verdict before declaring scope, coverage, and evidence sources.
- Do not hide source/doc-only or no-command boundaries in prose after the verdict.
- Do not turn historical evidence into current runtime, browser, data, UAT, release, or customer evidence.
