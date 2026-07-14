#!/usr/bin/env python3
"""Validate managed-worktree child Goal Mode prompt shape."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLACEHOLDER_GOAL_PATTERNS = (
    r"^/goal\s*$",
    r"^/goal\b.*<[^>]+>",
    r"^/goal\b.*\[[^\]]+\]",
    r"^/goal\b.*\{[^}]+\}",
    r"^/goal\s+(?:one executable task|todo|tbd|待定)\s*$",
)
TEMPLATE_GOAL_TOKEN = "{goal_contract.goal_command}"
GOAL_COMMAND_PATTERN = re.compile(r"^/goal(?:\s|$)")


def first_non_empty_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def is_goal_command(line: str) -> bool:
    return GOAL_COMMAND_PATTERN.match(line) is not None


def prompt_template_block(text: str) -> str:
    pattern = re.compile(r"(?ms)^```[a-zA-Z0-9_-]*[ \t]*\n(?P<body>.*?)\n```")
    for match in pattern.finditer(text):
        body = match.group("body")
        first = first_non_empty_line(body)
        if first == TEMPLATE_GOAL_TOKEN or is_goal_command(first):
            return body
    return ""


def is_placeholder_goal(line: str) -> bool:
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in PLACEHOLDER_GOAL_PATTERNS)


def lint_rendered_prompt(text: str) -> list[str]:
    first = first_non_empty_line(text)
    if not first:
        return ["prompt is empty"]
    findings = []
    if first.startswith("```"):
        findings.append("rendered child prompt must not wrap /goal in a fenced code block")
    if not is_goal_command(first):
        findings.append("first non-empty line must start with /goal")
    elif is_placeholder_goal(first):
        findings.append("goal command must be executable, not a placeholder")
    return findings


def lint_template(text: str) -> list[str]:
    body = prompt_template_block(text)
    if not body:
        return ["template must contain a fenced prompt body"]
    findings = []
    first = first_non_empty_line(body)
    if first != TEMPLATE_GOAL_TOKEN and not is_goal_command(first):
        findings.append(
            f"first non-empty line of the prompt body must be {TEMPLATE_GOAL_TOKEN} or a literal /goal command"
        )
    if is_goal_command(first) and is_placeholder_goal(first):
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
    parser.add_argument("--template", action="store_true", help="Validate a Markdown prompt template.")
    parser.add_argument("path", help="Rendered child prompt or Markdown template path.")
    args = parser.parse_args(argv[1:])
    path = Path(args.path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings = [f"file: unable to read {path}: {exc}"]
    else:
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
