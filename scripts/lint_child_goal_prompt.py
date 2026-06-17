#!/usr/bin/env python3
"""Validate managed-worktree child Goal Mode prompt shape.

Rendered child prompts must start with /goal on the first non-empty line.
Markdown templates may be checked with --template; the first fenced prompt body
must start with {goal_contract.goal_command}, which must be rendered to /goal
before delivery.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLACEHOLDER_GOAL_PATTERNS = (
    r"^/goal\s*$",
    r"^/goal\s*<[^>]+>\s*$",
    r"^/goal\s*\[[^\]]+\]\s*$",
    r"^/goal\s*\{[^}]+\}\s*$",
    r"^/goal\s+(?:one executable task|todo|tbd|待定)\s*$",
)

TEMPLATE_GOAL_TOKEN = "{goal_contract.goal_command}"


def first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def fenced_blocks(text: str) -> list[str]:
    return [match.group("body") for match in re.finditer(r"(?ms)^```[a-zA-Z0-9_-]*[ \t]*\n(?P<body>.*?)\n```", text)]


def prompt_template_block(text: str) -> str:
    for body in fenced_blocks(text):
        first = first_non_empty_line(body)
        if first == TEMPLATE_GOAL_TOKEN or first.startswith("/goal"):
            return body
    return ""


def is_placeholder_goal(line: str) -> bool:
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in PLACEHOLDER_GOAL_PATTERNS)


def lint_rendered_prompt(text: str) -> list[str]:
    findings: list[str] = []
    first = first_non_empty_line(text)
    if not first:
        return ["prompt is empty"]
    if first.startswith("```"):
        findings.append("rendered child prompt must not wrap /goal in a fenced code block")
    if not first.startswith("/goal"):
        findings.append("first non-empty line must start with /goal")
    elif is_placeholder_goal(first):
        findings.append("goal command must be executable, not a placeholder")
    return findings


def lint_template(text: str) -> list[str]:
    findings: list[str] = []
    body = prompt_template_block(text)
    if not body:
        return ["template must contain a fenced prompt body"]
    first = first_non_empty_line(body)
    if first != TEMPLATE_GOAL_TOKEN and not first.startswith("/goal"):
        findings.append(
            f"first non-empty line of the prompt body must be {TEMPLATE_GOAL_TOKEN} or a literal /goal command"
        )
    if first.startswith("/goal") and is_placeholder_goal(first):
        findings.append("template goal command must be executable, not a placeholder")
    lowered = text.lower()
    mentions_fence_rule = "fenced code block" in lowered or "markdown fences" in lowered
    if "do not prepend" not in lowered or not mentions_fence_rule:
        findings.append("template must document that rendered prompts cannot prepend prose or fence /goal")
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Lint Goal Mode child prompts so /goal is the first non-empty rendered line."
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Validate a Markdown prompt template whose first fenced prompt body starts with {goal_contract.goal_command}.",
    )
    parser.add_argument("path", help="Rendered child prompt or THREAD-PROMPT-TEMPLATE.md when --template is set.")
    args = parser.parse_args(argv[1:])

    path = Path(args.path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("Child Goal Prompt Lint: fail")
        print("Findings:")
        print(f"- file: unable to read {path}: {exc}")
        return 1

    findings = lint_template(text) if args.template else lint_rendered_prompt(text)
    if not findings:
        print("Child Goal Prompt Lint: pass")
        return 0

    print("Child Goal Prompt Lint: fail")
    print("Findings:")
    for finding in findings:
        print(f"- {finding}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
