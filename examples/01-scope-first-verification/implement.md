# Implement Notes: Scope-First Verification

Target Reader: Groundwork maintainer reviewing how the `verify` hardening was implemented.
Reader Action Needed: Check the touched areas and understand why the change stayed focused on verification behavior.
Decision Supported: Whether the implementation matched the scope-first verification PRD.
Scope: Documentation and skill/eval changes from the v0.2.2/v0.2.3 `verify` hardening line.
Out of Scope: New public skills, new CLI commands, task CRUD, runtime daemon behavior, or application feature implementation.
Evidence Level: `CHANGELOG.md` v0.2.2/v0.2.3 plus the v0.2.3 runtime baseline.

## Scope

Harden `verify` behavior for readiness, UAT, release, contract review, UI routing, QA failure, git-boundary, and subagent-review prompts.

## Changed Areas

- `skills/verify/SKILL.md` requires every verification report body to start with the full `Verification Scope` block.
- `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md` defines the exact required six-field opening and verdict rules.
- `skills/verify/LENSES.md` keeps verification lenses explicit so a report can name which evidence path is being used.
- Runtime prompt rows in the guardrail suite exercised adjacent routing, contract review, and scope-block behavior.

## Implementation Summary

- Replaced findings-first readiness behavior with a required scope-first opening.
- Required all specialized verification branches to keep the same opening wrapper.
- Clarified that a code diff or implementation summary alone is not readiness evidence.
- Kept implementation conformance review and prototype contract-boundary review out of `verify` when no readiness claim is being checked.

## Recorded Checks

- v0.2.3 final targeted rerun passed rows `rel-002`, `gr-002`, `gr-005`, `gr-010`, and `gr-015`.
- The final targeted routing rerun passed 4/4 adjacent routing rows after the frontmatter patch.
- The v0.2.3 baseline records no timeouts or non-zero `codex exec` return codes in the relevant runs.

## Remaining Gaps

- The v0.2.3 report treated targeted reruns as closure evidence for the patched rows; it did not claim that every future verification prompt shape was exhaustively covered.
- Final readiness for downstream release still depends on the current repository state and fresh checks at the time of release.

