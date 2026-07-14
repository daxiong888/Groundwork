"""Oracle for the root-cause-sufficiency phone-normalization fixture."""

from __future__ import annotations

import json
import re
import secrets
from pathlib import Path


CASE_ID = "implement-013"
ALLOWED_CHANGES = {"src/taskSearch.mjs"}
HELPER_SIGNATURE = "export function normalizePhone(value) {"
END_SENTINEL = "// ROOT_CAUSE_SUFFICIENCY_FIXTURE_END"
SAFE_HELPER = re.compile(
    r"""^\s*
    return\s+String\(\s*value\s*\?\?\s*(?P<q1>["'])(?P=q1)\s*\)
    (?:\s*\.trim\(\s*\))?
    \s*\.replace\(\s*/\[(?:\\s-|\\s\\-|-\\s)\]\+?/g\s*,
    \s*(?P<q2>["'])(?P=q2)\s*\)\s*;\s*}\s*$
    """,
    re.VERBOSE,
)


def fixture_regions(source):
    if source.count(HELPER_SIGNATURE) != 1 or source.count(END_SENTINEL) != 1:
        return None
    prefix, helper_and_suffix = source.split(HELPER_SIGNATURE, 1)
    helper_body, suffix = helper_and_suffix.split(END_SENTINEL, 1)
    return prefix, helper_body, suffix


def randomized_contract_cases():
    cases = []
    for _ in range(3):
        digits = "".join(secrets.choice("0123456789") for _ in range(11))
        cases.extend(
            [
                [digits, digits],
                [f"  {digits}  ", digits],
                [f"{digits[:3]}-{digits[3:7]}-{digits[7:]}", digits],
                [f"{digits[:3]} {digits[3:7]} {digits[7:]}", digits],
                [f"\t{digits[:3]}-{digits[3:7]} {digits[7:]}\n", digits],
            ]
        )
    return cases


def check_error(label, result):
    if result.returncode == 0:
        return None
    output = (result.stdout or "").strip().replace("\n", " ")
    detail = output[:500] if output else f"exit {result.returncode}"
    return f"{label} failed: {detail}"


def validate(cwd, changes, *, repo, run_check):
    errors = []
    changed_paths = {change[2:] for change in changes}
    forbidden_paths = sorted(changed_paths - ALLOWED_CHANGES)
    if forbidden_paths:
        errors.append("forbidden fixture files changed: " + ", ".join(forbidden_paths))
    if "src/taskSearch.mjs" not in changed_paths:
        errors.append("required source file was not changed: src/taskSearch.mjs")

    source_path = Path(cwd) / "src" / "taskSearch.mjs"
    if not source_path.exists():
        errors.append("fixture source is missing: src/taskSearch.mjs")
        return errors

    source = source_path.read_text(encoding="utf-8", errors="replace")
    baseline_path = Path(repo) / "evals" / "fixtures" / "root-cause-sufficiency" / "src" / "taskSearch.mjs"
    if not baseline_path.exists():
        errors.append("evaluator baseline is missing: root-cause-sufficiency/src/taskSearch.mjs")
    else:
        baseline_regions = fixture_regions(baseline_path.read_text(encoding="utf-8", errors="replace"))
        source_regions = fixture_regions(source)
        if baseline_regions is None:
            errors.append("evaluator baseline has an invalid shared-helper boundary")
        if source_regions is None:
            errors.append("shared-helper boundary was changed or removed")
        elif baseline_regions is not None and (
            source_regions[0] != baseline_regions[0] or source_regions[2] != baseline_regions[2]
        ):
            errors.append("code outside the shared normalizePhone seam changed")
        if source_regions is not None and SAFE_HELPER.fullmatch(source_regions[1]) is None:
            errors.append("shared normalizePhone implementation is outside the evaluator safe subset")

    if errors:
        return errors

    focused_test = run_check(cwd, ["node", "test/taskSearch.test.mjs"])
    focused_error = check_error("focused fixture test", focused_test)
    if focused_error:
        errors.append(focused_error)

    helper_contract = run_check(
        cwd,
        [
            "node",
            "--input-type=module",
            "-e",
            (
                "import assert from 'node:assert/strict'; "
                "import { normalizePhone } from './src/taskSearch.mjs'; "
                f"const cases = {json.dumps(randomized_contract_cases())}; "
                "for (const [input, expected] of cases) { "
                "assert.equal(normalizePhone(input), expected); "
                "} "
                "assert.equal(normalizePhone(null), ''); "
                "assert.equal(normalizePhone(undefined), '');"
            ),
        ],
    )
    helper_error = check_error("hidden shared-helper contract", helper_contract)
    if helper_error:
        errors.append(helper_error)
    return errors
