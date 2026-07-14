#!/usr/bin/env python3
"""Build a small local Codex marketplace for Groundwork."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

try:
    from check_runtime_package_boundary import (
        BUDGETS,
        CONTRACT_PATH,
        COPY_ENTRIES,
        FORBIDDEN_RUNTIME_ROOTS,
        PLUGIN_NAME,
        PROVENANCE_SCHEMA_VERSION,
        content_inventory,
        sha256_bytes,
        validate_package,
    )
except ImportError:  # Package import used by tests.
    from scripts.check_runtime_package_boundary import (
        BUDGETS,
        CONTRACT_PATH,
        COPY_ENTRIES,
        FORBIDDEN_RUNTIME_ROOTS,
        PLUGIN_NAME,
        PROVENANCE_SCHEMA_VERSION,
        content_inventory,
        sha256_bytes,
        validate_package,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "groundwork-local-marketplace"
DIST_ROOT = (ROOT / "dist").resolve()
OUTPUT_MARKER = ".groundwork-marketplace-output"


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
    if ROOT in resolved.parents and DIST_ROOT not in resolved.parents:
        raise SystemExit("Refusing to use a repository source directory as output; use a dist/ child.")
    if resolved == DIST_ROOT:
        raise SystemExit("Refusing to replace the repository dist root; use a named dist/ child.")
    return resolved


def reset_owned_output(output: Path) -> None:
    if not output.exists():
        return
    marker = output / OUTPUT_MARKER
    if not output.is_dir() or not marker.is_file():
        raise SystemExit(
            f"Refusing to replace an existing directory not owned by this builder: {output}"
        )
    shutil.rmtree(output)


def copy_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        return
    shutil.copy2(source, destination)


def write_runtime_manifest(plugin_root: Path) -> None:
    inventory = content_inventory(plugin_root)
    plugin_metadata = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "plugin_name": plugin_metadata.get("name"),
        "plugin_version": plugin_metadata.get("version"),
        "contract_sha256": sha256_bytes(CONTRACT_PATH.read_bytes()),
        "content_file_count": len(inventory),
        "content_inventory_sha256": sha256_bytes(
            json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
        "readme_sha256": sha256_bytes((plugin_root / "README.md").read_bytes()),
        "budgets": BUDGETS,
    }
    (plugin_root / ".codex-plugin" / "runtime-manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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

    reset_owned_output(output)
    output.mkdir(parents=True)
    (output / OUTPUT_MARKER).write_text(
        "Groundwork local marketplace build output.\n",
        encoding="utf-8",
    )
    plugin_root.mkdir(parents=True)

    copied = []
    for source_relative, destination_relative in COPY_ENTRIES.items():
        source = ROOT / source_relative
        if not source.exists():
            raise SystemExit(f"Package path does not exist: {source_relative}")
        copy_path(source, plugin_root / destination_relative)
        if source_relative == destination_relative:
            copied.append(source_relative)
        else:
            copied.append(f"{source_relative} -> {destination_relative}")

    write_runtime_manifest(plugin_root)

    validate_package(plugin_root, report=False)

    write_marketplace_manifest(output)
    print(f"Built Groundwork local marketplace: {output}")
    print(f"Plugin package root: {plugin_root}")
    print("Packaged runtime entries:")
    for relative in copied:
        print(f"- {relative}")
    print("Forbidden package roots:")
    for relative in sorted(FORBIDDEN_RUNTIME_ROOTS):
        print(f"- {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
