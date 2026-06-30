#!/usr/bin/env python3
"""Build a small local Codex marketplace for Groundwork."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "groundwork-local-marketplace"
PLUGIN_NAME = "groundwork"

PACKAGE_PATHS = (
    ".codex-plugin",
    ".github",
    ".gitignore",
    ".worktreeinclude.example",
    "AGENTS.md",
    "CHANGELOG.md",
    "LICENSE",
    "PROJECT.md",
    "README.md",
    "artifacts",
    "docs",
    "evals",
    "examples",
    "hooks",
    "research",
    "schemas",
    "scripts",
    "skills",
)

EXCLUDED_ROOTS = {
    ".git",
    ".codegraph",
    ".groundwork",
    ".trellis",
    "dist",
    "refer",
    "node_modules",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a trimmed local marketplace package for the Groundwork Codex plugin."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Marketplace output directory. Default: {DEFAULT_OUTPUT}",
    )
    return parser.parse_args()


def ensure_safe_output(output: Path) -> Path:
    resolved = output.expanduser().resolve()
    if resolved == ROOT:
        raise SystemExit("Refusing to use the repository root as output.")
    if resolved in ROOT.parents:
        raise SystemExit("Refusing to use a parent of the repository root as output.")
    return resolved


def copy_path(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        return
    shutil.copy2(source, destination)


def write_marketplace_manifest(output: Path) -> None:
    manifest = {
        "name": "groundwork",
        "interface": {
            "displayName": "Groundwork Local",
        },
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": f"./plugins/{PLUGIN_NAME}",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Productivity",
            }
        ],
    }
    manifest_path = output / ".agents" / "plugins" / "marketplace.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output = ensure_safe_output(args.output)
    plugin_root = output / "plugins" / PLUGIN_NAME

    if output.exists():
        shutil.rmtree(output)
    plugin_root.mkdir(parents=True)

    copied = []
    for relative in PACKAGE_PATHS:
        top_level = relative.split("/", 1)[0]
        if top_level in EXCLUDED_ROOTS:
            raise SystemExit(f"Refusing to package excluded path: {relative}")
        source = ROOT / relative
        if not source.exists():
            raise SystemExit(f"Package path does not exist: {relative}")
        copy_path(source, plugin_root / relative)
        copied.append(relative)

    write_marketplace_manifest(output)
    print(f"Built Groundwork local marketplace: {output}")
    print(f"Plugin package root: {plugin_root}")
    print("Packaged paths:")
    for relative in copied:
        print(f"- {relative}")
    print("Excluded roots:")
    for relative in sorted(EXCLUDED_ROOTS):
        print(f"- {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
