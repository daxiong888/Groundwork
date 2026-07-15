# QA Fix QA Loop

Target Reader: Codex running `verify` or `implement` after a verification failure.
Reader Action Needed: Turn a failed check into a scoped fix loop without broadening the task.
Decision Supported: Whether the failure is understood enough to fix and what must be rechecked.
Artifact Type: shared workflow reference
Source of Truth: Groundwork issue #8 acceptance criteria, `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md`, `skills/_shared/SEVERITY.md`, and existing verify/implement contracts.
Scope: Verification failure reporting, minimal diagnosis, scoped fix planning, regression check, and re-QA.
Out of Scope: Broad refactors, speculative fixes, release approval, or unrelated bug sweeps.
Evidence Level: Groundwork issue #8 acceptance criteria and existing verify/implement contracts.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Verify Failure Report

When verification fails, or when the user asks for QA -> fix -> QA handling after a failure, first keep the verdict in this exact `Verification Scope` shape:

```text
Verification Scope
- Claim:
- Covered:
- Missing:

Verdict: fail | blocked
```

Then report the failure in this exact shape. `Verdict` belongs only to `Verification Scope`; never repeat it inside `QA Failure`:

```text
QA Failure
- Expected:
- Actual:
- Reproduction: command: <original-check>
- Severity: P0 / P1 / P2 / P3
- Minimal Diagnosis:
- Evidence Delta:
- Source / AC Change: unchanged / changed / unverified
- Implementation Authority: existing_and_sufficient / approval_required / missing / unverified
- Risk Change: unchanged_within_boundary / new_or_increased / unverified
- Fix Plan:
- Gap-Closure Admission: ready_for_implement / diagnose_before_edit / needs_info / product_or_contract_rework / human_decision / blocked
- Gap Closure Plan:
- Re-QA Required: command: <original-check>
- Regression Note:
- Scoped Next Action: route: implement / route: verify / route: to-prd / route: human_decision / route: triage / route: stop
```

Rules:

- Hard instruction: keep every field in the shape even when information is missing. Use `not provided` for absent prompt details and `unverified` for details not checked. Do not replace this block with a generic QA process.
- Keep diagnosis minimal and evidence-backed.
- If cause is uncertain, say what is confirmed and what is still hypothesis.
- Evidence delta states what new observation, failing check, source fact, or changed hypothesis distinguishes this iteration from the previous one. For the first observed failure, write `first observed failure`. Repeating the same action and result is not an evidence delta.
- Select exactly one `Verification Scope` verdict: `fail` or `blocked`. It remains unchanged while a `QA Failure` block is present, and a feedback admission never upgrades it. `Verdict` must appear exactly once in `Verification Scope` and must not appear in `QA Failure`.
- Field ownership is exact: `Claim`, `Covered`, `Missing`, and `Verdict` appear only in `Verification Scope`; every QA field appears only in `QA Failure`. Do not move a recognized field to the other block or a later section.
- Source / AC Change states whether accepted source truth, product decision, or acceptance criteria changed since the implementation became ready. `ready_for_implement` and `diagnose_before_edit` require `unchanged`; use `changed` or `unverified` to block implementation re-entry when appropriate.
- Implementation Authority uses only `existing_and_sufficient`, `approval_required`, `missing`, or `unverified`. Both ready admissions require `existing_and_sufficient`; `approval_required` routes to `human_decision` or `blocked`, `missing` routes to `blocked`, and `unverified` cannot enter implementation.
- Risk Change uses only `unchanged_within_boundary`, `new_or_increased`, or `unverified`. Both ready admissions require `unchanged_within_boundary`; `new_or_increased` routes to `human_decision` or `blocked`, and `unverified` cannot enter implementation.
- Do not skip `Expected`, `Actual`, or `Reproduction` for behavior failures.
- If the prompt does not provide concrete failure details, inspect the available fixture/checks when allowed. If details still cannot be confirmed, keep the field and write `not provided` or `unverified`; do not replace the report with a generic QA process.
- Do not hide severity in prose.
- Use `skills/_shared/SEVERITY.md`. `none` is invalid in `QA Failure` because this block is emitted only for failed or blocked verification. If no material failure remains, omit the `QA Failure` block and use a normal verification verdict instead.
- `Reproduction` and `Re-QA Required` must use one stable original-check identity: either `command: <exact direct check>` or `manual: <stable-slug>`. For `ready_for_implement` and `diagnose_before_edit`, the two complete values must be exactly identical. Do not use status placeholders, shell/evaluator wrappers, composite shell expressions, or inline interpreter snippets; examples include `echo ok`, `true`, `sh -c`, `timeout`, `xargs`, `python -c`, `node -e`, `manual: ok`, `manual: pass`, and `manual: success`.
- `Fix Plan` and `Gap Closure Plan` must name the minimum bounded proposal or evidence update needed before verdict can change. They must not claim that a fix was applied, deployed, released, completed, or made live, and must not contain an immediate execution instruction.
- Regression note must state the smallest adjacent behavior that should be rechecked, or `not identified` when there is no evidence yet.
- Do not update a failure verdict to pass until the original reproduction/check has been re-QA'd or the missing re-QA evidence is explicitly reported as unresolved.
- `Scoped Next Action` is a finite control field, not free prose. Use exactly `route: implement` for `ready_for_implement` or `diagnose_before_edit`; `route: verify` for `needs_info`; `route: to-prd` for `product_or_contract_rework`; `route: human_decision` for `human_decision`; and `route: stop` or `route: triage` for `blocked`. Do not append execution language to the token.

## Gap-Closure Admission

Use the named `qa_gap_closure` feedback gate before routing a failed verification to `implement`. It preserves or reasserts requirement state `implementation_ready`; it does not change the `fail`/`blocked` verdict and does not prove readiness.

Set `Gap-Closure Admission: ready_for_implement` only when all are true:

- the accepted source truth, product decision, and acceptance criteria are unchanged;
- expected, actual, severity, and the original check are present or were directly inspected;
- reproduction and re-QA name the same non-placeholder `command:` or `manual:` original-check identity;
- the defect and write scope are bounded enough for a focused fix;
- `Implementation Authority` is `existing_and_sufficient`;
- `Risk Change` is `unchanged_within_boundary`;
- this is the first observed failure, or the package contains new evidence or a changed hypothesis since the previous attempt.

Use `diagnose_before_edit` when source truth and ACs are unchanged, reproduction and re-QA name the same stable original-check identity, `Implementation Authority` is `existing_and_sufficient`, `Risk Change` is `unchanged_within_boundary`, and the cause is still unconfirmed. `implement` may inspect or reproduce under that branch, but must not make a speculative fix.

Use the remaining outcomes as hard routing boundaries:

| Admission | Route / Action |
| --- | --- |
| `needs_info` | `Scoped Next Action: route: verify`; obtain the missing expected/actual/reproduction/original check without inventing it |
| `product_or_contract_rework` | `Scoped Next Action: route: to-prd`; do not repair product truth in implementation |
| `human_decision` | `Scoped Next Action: route: human_decision`; pause for the named approval, scope, risk, or source-owner decision |
| `blocked` | `Scoped Next Action: route: stop` or `route: triage`; name the missing evidence, tool, authority, or safe path |

These non-ready outcomes may keep `Evidence Delta: unverified` or `not provided`; they must not invent evidence merely to satisfy the ready re-entry gate. Their finite `Scoped Next Action` token must match the table and must never use `route: implement`.

An unchanged failure with no evidence delta must not automatically retry. Record the exhausted action, change the hypothesis or evidence plan, or route to `triage`/human decision. Do not create or update `STATE.md` merely because one iteration failed; use lifecycle state only when its separate threshold is met.

## Implement Fix Loop

When `implement` receives a verify failure:

1. Confirm the failure report has expected, actual, severity, minimal diagnosis, evidence delta, source/AC change status, implementation authority, risk change, gap-closure admission, fix plan, and an exactly matching `command:` or `manual:` reproduction/re-QA identity.
2. Fix only the scoped failure.
3. Rerun the original failing check after the fix.
4. Add or update a focused regression test/check when feasible.
5. Report any unresolved gap back to `verify`.

Do not turn one failed check into broad cleanup or unrelated behavior changes.

## Clean Review Staleness

When the failed verification or QA finding follows a clean review:

- use `skills/_shared/REVIEW-LOOP.md` to preserve the review-loop state;
- if the fix changes material reviewed files, set the previous clean review to stale for the latest diff;
- report `findings_addressed`, the original failing check or reproduction rerun, and any checks not run;
- route back to fresh clean review before claiming `Clean Review Evidence: passed` for the fixed change;
- do not use the old clean-review pass as proof for verify/readiness after remediation.
