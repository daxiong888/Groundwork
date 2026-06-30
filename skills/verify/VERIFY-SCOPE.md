# Verify Scope Branch

Target Reader: Codex running `verify` for scope-first verification, no-command evidence sufficiency, or code-diff-only readiness questions.
Reader Action Needed: Start the final verification body with the required scope block and keep missing evidence explicit.
Decision Supported: Whether a readiness or evidence-sufficiency claim is supported, partial, failed, blocked, or unverified.
Artifact Type: branch-specific verification reference
Source of Truth: `skills/verify/SCOPE-EVIDENCE-TEMPLATE.md` and `skills/verify/SKILL.md`.
Scope: Final-report opening, no-command handling, code-diff-only readiness, and minimal evidence-boundary rules.
Out of Scope: QA failure diagnosis, UI tool routing, release evidence claims, subagent package details, or contract-doc checklists.
Evidence Level: Source-validation rule only.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, private logs, or production payloads.

## Required Opening

Load `SCOPE-EVIDENCE-TEMPLATE.md` and copy its complete six-field `Verification Scope` block at the start of the final verification report body.

Rules:

- The first line of the final verification report body is exactly `Verification Scope`.
- Do not bold, decorate, translate, rename, or replace the opening line.
- Keep all six fields even when information is missing.
- Use `not provided` for absent prompt details and `unverified` for facts not checked.
- Brief progress or tool-use prefaces are allowed before the final report only when they do not contain a verdict, findings, specialized payload, contract conclusion, QA decision, UI tool recommendation, approval decision, or subagent prompt body.

## Code-Diff-Only / No-Command Branch

Questions that ask whether missing evidence is enough for readiness, including code-diff-only, no-runtime-evidence, no-browser-evidence, no-command, or "can this count as ready" prompts, are verification reports.

Do not answer them as a direct short judgment. Start with `Verification Scope`, put forbidden or unavailable checks under `Out of Scope` or `Not Covered`, and mark missing runtime/browser/test/data/environment/UAT evidence as `unverified`.

For code-diff-only rows, keep the labeled verdict line mechanically safe:

- Use `Verdict: fail`, `Verdict: partial`, or `Verdict: blocked`.
- Do not put `ready`, `readiness`, `pass`, `merge-ready`, `release-ready`, `ready for`, `approved`, or `green` on any line that begins with `Verdict`, `Result`, `Status`, `Recommendation`, `Conclusion`, or `readiness_verdict`.
- For `Claimed Behavior`, use a neutral label such as `code diff only sufficiency claim` or `see User-visible Claim Being Verified`; do not restate `ready`, `readiness`, `就绪`, `交付`, `验收`, `发布`, `合并`, or `通过` on that line.
- Do not write labeled lines such as `Verdict: fail for ready`, `Status: not ready`, `Conclusion: not ready`, `readiness_verdict: blocked`, or `Recommendation: not ready`.
- In labeled scope lines such as `Not Covered`, avoid Chinese positive fragments that can look like a readiness claim, such as `可见`, `可以`, or `可` near `验收`, `发布`, `UAT`, `联调`, `上线`, `合并`, or `通过`. Prefer neutral English nouns like `UI behavior`, `runtime behavior`, `release state`, and `UAT state`.
- Put readiness wording in clearly negated prose after the verdict, such as `Code diff alone cannot count as ready.`
- Prefer this safe shape:

```text
Verification Scope
- In Scope: whether code diff alone is sufficient evidence for the stated claim
- Out of Scope: command execution, source inspection, runtime execution, browser verification, release checks, UAT checks
- Covered: evidence sufficiency only
- Not Covered: concrete code correctness, runtime behavior, browser behavior, data state, environment state, release state, UAT state
- Evidence Sources: user-provided evidence boundary only
- User-visible Claim Being Verified: code diff without runtime or browser evidence can count as ready

Verdict: blocked
Claimed Behavior: code diff only sufficiency claim
Evidence Boundary: code diff alone cannot count as ready.
Next Action: run the narrowest relevant runtime/API/browser check, then re-verify.
```
