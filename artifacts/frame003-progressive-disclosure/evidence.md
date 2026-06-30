# FRAME-003 Progressive Disclosure Evidence

Target Reader: Groundwork maintainers reviewing FRAME-003 source changes for public skill progressive disclosure.
Reader Action Needed: Use this evidence map to distinguish source/self-check/clean-review/targeted-runtime coverage from broader release, UAT, marketplace, and customer-readiness claims.
Decision Supported: Whether the FRAME-003 source changes satisfy the first-pass progressive disclosure requirements for `dispatch` and `verify`, including targeted installed-plugin runtime rows.
Artifact Type: evidence map
Source of Truth: `skills/_shared/SKILL-AUDIT.md`, `skills/dispatch/SKILL.md`, `skills/verify/SKILL.md`, new referenced branch files under `skills/dispatch/` and `skills/verify/`, local validation output, clean-review session results, installed plugin cache `/Users/daxiong/.codex/plugins/cache/groundwork-frame003/groundwork/0.5.2`, and targeted runtime output under `/private/tmp/groundwork-runtime-v03/20260630T043805Z`.
Scope: FRAME-003 first-pass split of `skills/dispatch/SKILL.md` and `skills/verify/SKILL.md`; self-check evidence; clean-review evidence; local source/schema/test validation; targeted runtime rows for verify opening/code-diff/QA-failure and dispatch package-only boundaries.
Out of Scope: Full-suite runtime behavior, release readiness, UAT, customer readiness, marketplace publication, production install behavior outside `groundwork-frame003`, or broad public skill redesign outside `dispatch` and `verify`.
Evidence Level: Source-validation, self-check, clean-review, and targeted installed-plugin runtime evidence. This is not release, UAT, marketplace, or customer readiness.
Safe to Share / Redaction Notes: Safe to share as-is; contains no secrets, credentials, PII, raw runtime logs, or private payloads.

## Requirement Map

| Requirement | Source Evidence | Self-check Evidence | Clean Review Evidence | Runtime/Cache Evidence |
|---|---|---|---|---|
| `dispatch/SKILL.md` no longer inlines long YAML examples | `skills/dispatch/SKILL.md` references `skills/dispatch/EXAMPLES.md`; `skills/dispatch/EXAMPLES.md` contains the moved package examples | `evals/test_progressive_disclosure.py::test_dispatch_skill_loads_examples_on_demand` checks that `SKILL.md` has no fenced YAML and that examples live in `EXAMPLES.md` | Fresh read-only reviewer found no remaining source-level issue after remediation | `sx-009` passed in `/private/tmp/groundwork-runtime-v03/20260630T043805Z`, expected/actual `dispatch`, verdict `pass` |
| `verify/SKILL.md` no longer always-loads all branch templates | `skills/verify/SKILL.md` keeps the final opening rule, shared references, minimal output shape, and Branch Index; branch payloads live in `VERIFY-SCOPE.md`, `QA-FAILURE-BRANCH.md`, `RELEASE-READINESS-BRANCH.md`, `RUNTIME-CAPABILITY-BRANCH.md`, `NATIVE-CLOSEOUT-BRANCH.md`, `UI-READINESS-BRANCH.md`, and `SUBAGENT-REVIEW-BRANCH.md`; only `SCOPE-EVIDENCE-TEMPLATE.md` is required before every verification report body; non-scope branch files do not reference `VERIFY-SCOPE.md` | `evals/test_progressive_disclosure.py::test_verify_skill_routes_branch_templates_to_references` checks that branch files are referenced, removed payload markers are absent from `SKILL.md`, and `VERIFY-SCOPE.md` is not globally loaded before every report body; `test_verify_scope_branch_is_not_loaded_by_other_branch_files` checks that non-scope branch files do not load `VERIFY-SCOPE.md` | Clean review found and remediation addressed native closeout reachability, runtime capability payload, and two `VERIFY-SCOPE.md` over-eager-load issues | `sx-007`, `tf-vr-001`, `tf-vr-002`, and `tf-vr-003` passed in `/private/tmp/groundwork-runtime-v03/20260630T043805Z`, expected/actual `verify`, verdict `pass` |
| New referenced files are durable artifacts with audience-first headers | All added branch/example files include the required audience-first fields | `evals/test_progressive_disclosure.py::test_branch_references_have_audience_first_headers` validates the header fields | Fresh read-only reviewer did not report artifact-header gaps | Not applicable |
| `SKILL-AUDIT.md` progressive disclosure rule is addressed | `skills/_shared/SKILL-AUDIT.md` says public `SKILL.md` should keep universal invocation rules and move branch-specific procedures, templates, detailed checklists, examples, and long domain references into referenced files loaded only when needed | This evidence map plus the progressive disclosure unit test map the changed source files to the audit rule | Clean review covered whether the split still left source-level branch-template gaps; second review reported no findings | Not covered |
| Runtime rows do not regress, especially verify opening block and dispatch package-only boundary | Rows remain in `evals/prompts/smoke.csv` (`sx-007`, `sx-009`) and `evals/prompts/trace-first-verify-review.csv` (`tf-vr-001`, `tf-vr-002`, `tf-vr-003`) | Local source/schema checks passed before runtime execution | Clean review did not substitute for runtime evidence | Targeted installed-plugin runtime run `/private/tmp/groundwork-runtime-v03/20260630T043805Z`: 5 rows, counts `pass: 5`, failures `[]` |

## Validation Commands

Source and structural checks run during FRAME-003:

```text
python3 -m unittest evals.test_progressive_disclosure
git diff --check
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -c "import csv, pathlib; [list(csv.DictReader(open(p, newline=''))) for p in pathlib.Path('evals/prompts').glob('*.csv')]; print('csv ok')"
python3 -m unittest discover evals
python3 evals/run_runtime.py --all-prompts --validate-schema
codex plugin add groundwork@groundwork-frame003 --json
python3 -B evals/run_runtime.py --suite smoke.csv --suite trace-first-verify-review.csv --serial --case-timeout 240 sx-007 sx-009 tf-vr-001 tf-vr-002 tf-vr-003
```

The `--validate-schema` runner command above is schema/source validation only. The final targeted runtime command exercised Codex runtime behavior against the refreshed `groundwork-frame003` installed plugin cache.

## Clean Review Evidence

Clean review was performed by fresh read-only reviewer sessions separate from the implementation work:

- First clean review found two source-level issues: native closeout rules were not reachable after being moved under release readiness, and runtime capability output shape was underspecified.
- Remediation added `skills/verify/NATIVE-CLOSEOUT-BRANCH.md` and `skills/verify/RUNTIME-CAPABILITY-BRANCH.md`, then updated `skills/verify/SKILL.md` and `evals/test_progressive_disclosure.py`.
- Second clean review reported no findings at source level and identified the remaining gap as installed-plugin runtime/cache validation.
- Final clean review then found one remaining P2: `verify/SKILL.md` still globally loaded `VERIFY-SCOPE.md`, which contained code-diff-only and no-command branch detail. Remediation changed the global load requirement to `SCOPE-EVIDENCE-TEMPLATE.md` only and added a regression assertion in `evals/test_progressive_disclosure.py`.
- A follow-up clean review found the same over-eager-load pattern inside non-scope branch files. Remediation changed QA failure, runtime capability, native closeout, UI readiness, and subagent review branch references to load only `SCOPE-EVIDENCE-TEMPLATE.md`, removed a remaining code-diff-only verdict detail from public `verify/SKILL.md`, and added regression assertions that non-scope branch files do not reference `VERIFY-SCOPE.md` and that branch-specific code-diff verdict detail does not return to the public skill body.

This is clean-review evidence for the source split, not release, UAT, marketplace, or customer readiness.

## Cache And Runtime Evidence

Installed plugin root used for runtime execution:

```text
/Users/daxiong/.codex/plugins/cache/groundwork-frame003/groundwork/0.5.2
```

Source root:

```text
/Users/daxiong/.codex/worktrees/16fa/Groundwork
```

Marketplace source used for refresh:

```text
/private/tmp/groundwork-frame003-marketplace/plugins/groundwork
```

Refresh method:

```text
codex plugin add groundwork@groundwork-frame003 --json
```

The CLI reported:

```text
installedPath: /Users/daxiong/.codex/plugins/cache/groundwork-frame003/groundwork/0.5.2
version: 0.5.2
```

Source/cache equivalence method for runtime-affecting files:

- Synchronized the FRAME-003 runtime-affecting skill and eval files into `/private/tmp/groundwork-frame003-marketplace/plugins/groundwork`.
- Ran the supported `codex plugin add groundwork@groundwork-frame003 --json` refresh.
- Compared the runtime-affecting files between source root and installed plugin root with `diff -q`; the final comparison before the targeted runtime run returned no differences for those files.
- `artifacts/frame003-progressive-disclosure/evidence.md` is the repository closeout evidence map. It is not loaded by the runtime rows and was updated after the runtime run to record final evidence; it is intentionally not used as proof of runtime cache equivalence.

Targeted runtime result:

```text
run_root: /private/tmp/groundwork-runtime-v03/20260630T043805Z
suites: smoke.csv, trace-first-verify-review.csv
ids: sx-007, sx-009, tf-vr-001, tf-vr-002, tf-vr-003
rows: 5
counts: pass 5
failures: []
```

Boundary:

- This proves targeted installed-plugin runtime behavior only for the listed rows.
- It does not prove full-suite runtime behavior.
- It does not prove release, UAT, marketplace, or customer readiness.

## Runtime Iteration Notes

After refreshing `groundwork-frame003`, targeted runtime rows initially produced:

- `smoke.csv`: `sx-007` pass and `sx-009` pass.
- `trace-first-verify-review.csv`: `tf-vr-001` pass, `tf-vr-003` pass, and `tf-vr-002` fail.

The first `tf-vr-002` failure was a code-diff-only behavior checker match caused by the generated `Not Covered` line using Chinese text with `可见` near `发布/UAT`. `VERIFY-SCOPE.md` was updated with a safer code-diff-only skeleton that uses neutral English nouns such as `UI behavior`, `release state`, and `UAT state` in labeled scope lines.

A later full targeted run still failed `tf-vr-002` because `Claimed Behavior` restated the prompt as a ready-state judgment. `VERIFY-SCOPE.md` was tightened again so code-diff-only rows use a neutral `Claimed Behavior: code diff only sufficiency claim` line and avoid ready/readiness terms on that label.

The final targeted runtime set passed all five rows against the refreshed cache at `/private/tmp/groundwork-runtime-v03/20260630T043805Z`.
