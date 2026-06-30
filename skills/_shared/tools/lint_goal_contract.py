#!/usr/bin/env python3
"""Lightweight Goal Contract linter.

This intentionally scans the full Markdown text, including fenced code blocks.
It supports lightweight block values after a field label, but does not perform
full Markdown AST validation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


FIELD_ALIASES = {
    "Goal Command": ("Goal Command", "目标命令"),
    "Outcome": ("Outcome", "结果", "目标结果"),
    "Source Truth": ("Source Truth", "事实源", "来源事实"),
    "Acceptance Criteria Mapping": ("Acceptance Criteria Mapping", "验收标准映射", "验收映射"),
    "Verification": ("Verification", "验证"),
    "Constraints": ("Constraints", "约束"),
    "Boundaries": ("Boundaries", "边界"),
    "Iteration Policy": ("Iteration Policy", "迭代策略"),
    "Stop When": ("Stop When", "完成条件", "停止条件"),
    "Pause If": ("Pause If", "暂停条件"),
    "Non-goals": ("Non-goals", "Non-goals", "非目标"),
    "Risk / Gate": ("Risk / Gate", "Risk/Gate", "风险 / 门禁", "风险/门禁"),
    "Preferred Runtime": ("Preferred Runtime", "首选运行时"),
    "Result Package Expected": ("Result Package Expected", "预期结果包"),
}

PLACEHOLDERS = (
    "[Outcome]",
    "[Verification]",
    "TODO",
    "TBD",
    "待定",
)

GOAL_COMMAND_PLACEHOLDER_PATTERNS = (
    r"^/goal\s*$",
    r"^/goal\b.*<[^>]+>",
    r"^/goal\b.*\[[^\]]+\]",
    r"^/goal\b.*\{[^}]+\}",
    r"^/goal\s+(?:one executable task|todo|tbd|待定)\s*$",
)

VAGUE_PHRASES = (
    ("Verification", "make sure it works", "verification must name concrete evidence"),
    ("Constraints", "随便改", "constraints cannot allow arbitrary edits"),
    ("Boundaries", "edit anything", "boundaries cannot allow broad edits"),
    ("Iteration Policy", "keep trying", "iteration policy must be bounded"),
)

VAGUE_VERIFICATION_PATTERNS = (
    r"\bmake sure (it|this) works\b",
    r"\bverify it works\b",
    r"\bcheck it works\b",
    r"\bworks as expected\b",
    r"确认.*可用",
    r"验证.*可用",
)

BROAD_BOUNDARY_PATTERNS = (
    r"\bedit anything\b",
    r"\bchange anything\b",
    r"\bmodify anything\b",
    r"\bany file\b",
    r"随便改",
    r"任意修改",
)

UNBOUNDED_ITERATION_PATTERNS = (
    r"\bkeep trying\b",
    r"\bretry until (it )?works\b",
    r"\btry until (it )?passes\b",
    r"一直重试",
    r"不断重试",
)

CONCRETE_VERIFICATION_HINTS = (
    "python",
    "pytest",
    "npm",
    "pnpm",
    "yarn",
    "cargo",
    "go test",
    "mvn",
    "gradle",
    "git diff --check",
    "screenshot",
    "browser",
    "log",
    "runtime output",
    "artifact",
    "review checklist",
    "command",
    "检查",
    "命令",
    "测试",
    "截图",
    "日志",
    "产物",
    "清单",
)


def label_pattern(label: str) -> str:
    escaped = re.escape(label).replace(r"\ ", r"\s+")
    return escaped.replace(r"\/", r"\s*/\s*")


def find_label(text: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
    for alias in aliases:
        pattern = re.compile(
            rf"(?im)^\s*(?:[-*]\s+|\d+\.\s+|#+\s+|\|\s*)?"
            rf"{label_pattern(alias)}[ \t]*(?:[:：]|\||$)"
        )
        match = pattern.search(text)
        if match:
            return match
    return None


def find_field_line_value(line: str, aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        pattern = re.compile(
            rf"^\s*(?:[-*]\s+|\d+\.\s+|#+\s+|\|\s*)?"
            rf"{label_pattern(alias)}[ \t]*[:：][ \t]*(?P<value>.*)$",
            re.IGNORECASE,
        )
        match = pattern.match(line)
        if match:
            return match.group("value").strip()
    return None


def is_known_field_label(line: str) -> bool:
    return any(find_field_line_value(line, aliases) is not None for aliases in FIELD_ALIASES.values())


def extract_field_value(text: str, aliases: tuple[str, ...]) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        first_value = find_field_line_value(line, aliases)
        if first_value is None:
            continue

        values = [first_value] if first_value else []
        for follow in lines[index + 1 :]:
            if is_known_field_label(follow):
                break
            if re.match(r"^\s*#{1,6}\s+\S", follow):
                break
            if not re.match(r"^\s+\S", follow):
                break
            stripped = follow.strip()
            if stripped:
                values.append(stripped)
        return "\n".join(values).strip()
    return ""


def has_non_empty_field_value(text: str, aliases: tuple[str, ...]) -> bool:
    return bool(extract_field_value(text, aliases))


def contains_any(patterns: tuple[str, ...], value: str) -> bool:
    return any(re.search(pattern, value, re.IGNORECASE) for pattern in patterns)


def first_non_empty_line(value: str) -> str:
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def lint(text: str) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []

    for field, aliases in FIELD_ALIASES.items():
        if not find_label(text, aliases):
            findings.append((field, "missing required label"))
        elif not has_non_empty_field_value(text, aliases):
            findings.append((field, "required field must have non-empty content"))

    goal_command = extract_field_value(text, FIELD_ALIASES["Goal Command"])
    goal_command_first_line = first_non_empty_line(goal_command)
    if goal_command and not goal_command_first_line.startswith("/goal"):
        findings.append(("Goal Command", "Goal Command must start with /goal"))
    elif goal_command_first_line and contains_any(GOAL_COMMAND_PLACEHOLDER_PATTERNS, goal_command_first_line):
        findings.append(("Goal Command", "Goal Command must be executable, not a placeholder"))

    for placeholder in PLACEHOLDERS:
        if placeholder in text:
            findings.append(("Placeholder", f"placeholder is not allowed: {placeholder}"))

    lowered = text.lower()
    for field, phrase, reason in VAGUE_PHRASES:
        if phrase.lower() in lowered:
            findings.append((field, reason))

    verification = extract_field_value(text, FIELD_ALIASES["Verification"])
    if verification:
        verification_lower = verification.lower()
        has_hint = any(hint in verification_lower for hint in CONCRETE_VERIFICATION_HINTS)
        if contains_any(VAGUE_VERIFICATION_PATTERNS, verification) or not has_hint:
            findings.append(("Verification", "verification is too vague; name concrete checks or evidence"))

    boundaries = extract_field_value(text, FIELD_ALIASES["Boundaries"])
    if boundaries and contains_any(BROAD_BOUNDARY_PATTERNS, boundaries):
        findings.append(("Boundaries", "boundaries are too broad"))

    iteration_policy = extract_field_value(text, FIELD_ALIASES["Iteration Policy"])
    if iteration_policy and contains_any(UNBOUNDED_ITERATION_PATTERNS, iteration_policy):
        findings.append(("Iteration Policy", "iteration policy is unbounded"))

    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 skills/_shared/tools/lint_goal_contract.py <goal-contract-file>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("Goal Contract Lint: fail")
        print("Findings:")
        print(f"- file: unable to read {path}: {exc}")
        return 1

    findings = lint(text)
    if not findings:
        print("Goal Contract Lint: pass")
        return 0

    print("Goal Contract Lint: fail")
    print("Findings:")
    for field, reason in findings:
        print(f"- {field}: {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
