#!/usr/bin/env python3
"""Approximate static budget checks for public Groundwork SKILL.md entry files."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MAX_ENTRY_LINES = {
    "skills/verify/SKILL.md": 140,
    "skills/implement/SKILL.md": 140,
    "skills/dispatch/SKILL.md": 130,
    "skills/handoff/SKILL.md": 120,
}

DEFAULT_MAX_INLINE_EXAMPLE_LINES = 40
FULL_YAML_SCHEMA_MARKERS = {
    "schemaVersion",
    "result_package:",
    "dispatch_package:",
    "clean_review_package:",
    "properties:",
    "required:",
}
YAML_SCHEMA_EXEMPTION = "token-budget: allow-full-yaml-schema"
MAX_MARKDOWN_FENCE_INDENT = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail when public skill entry files drift beyond lightweight runtime budgets."
    )
    parser.add_argument(
        "--max-inline-example-lines",
        type=int,
        default=DEFAULT_MAX_INLINE_EXAMPLE_LINES,
        help=f"Maximum lines allowed inside any fenced SKILL.md example. Default: {DEFAULT_MAX_INLINE_EXAMPLE_LINES}.",
    )
    return parser.parse_args()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def fenced_blocks(lines: list[str]) -> list[tuple[int, int, str, list[str]]]:
    blocks: list[tuple[int, int, str, list[str]]] = []
    in_block = False
    start = 0
    language = ""
    body: list[str] = []

    for number, line in enumerate(lines, start=1):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent <= MAX_MARKDOWN_FENCE_INDENT and stripped.startswith("```"):
            if not in_block:
                in_block = True
                start = number
                language = stripped[3:].strip().lower()
                body = []
            else:
                blocks.append((start, number, language, body))
                in_block = False
            continue
        if in_block:
            body.append(line)
    return blocks


def check_entry_lines(path: Path, errors: list[str]) -> None:
    rel = relative(path)
    limit = MAX_ENTRY_LINES.get(rel)
    if limit is None:
        return
    line_count = len(path.read_text(encoding="utf-8").splitlines())
    if line_count > limit:
        errors.append(f"{rel} has {line_count} lines; max is {limit}.")


def check_inline_examples(path: Path, errors: list[str], max_lines: int) -> None:
    rel = relative(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    for start, end, _language, body in fenced_blocks(lines):
        body_lines = len(body)
        if body_lines > max_lines:
            errors.append(
                f"{rel}:{start}-{end} has an inline fenced example with {body_lines} lines; "
                f"max is {max_lines}. Move long examples to a lazy-loaded reference file."
            )


def check_full_yaml_schema(path: Path, errors: list[str]) -> None:
    rel = relative(path)
    text = path.read_text(encoding="utf-8")
    if YAML_SCHEMA_EXEMPTION in text:
        return
    for start, end, language, body in fenced_blocks(text.splitlines()):
        body_text = "\n".join(body)
        marker_hits = [marker for marker in FULL_YAML_SCHEMA_MARKERS if marker in body_text]
        if len(marker_hits) >= 3:
            errors.append(
                f"{rel}:{start}-{end} appears to inline a full YAML package schema "
                f"({', '.join(marker_hits[:4])}). Move schemas to references or add an explicit exemption."
            )


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))

    for path in skill_files:
        check_entry_lines(path, errors)
        check_inline_examples(path, errors, args.max_inline_example_lines)
        check_full_yaml_schema(path, errors)

    if errors:
        raise SystemExit("\n\n".join(errors))

    print(
        "skill entry budget ok: "
        f"{len(skill_files)} SKILL.md files checked; inline example max {args.max_inline_example_lines} lines"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
