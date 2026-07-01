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

RUNTIME_PACKAGE_ENTRIES = {
    ".codex-plugin": ".codex-plugin",
    "skills": "skills",
    "hooks": "hooks",
    "scripts/codex-hooks": "scripts/codex-hooks",
    "README.runtime.md": "README.md",
    "LICENSE": "LICENSE",
}

RUNTIME_HOOK_FILES = {
    "hooks.json",
}

RUNTIME_CODEX_HOOK_FILES = {
    "groundwork_route_detection.py",
    "groundwork_router_observability.py",
    "permission_request_groundwork_trace.py",
    "post_tool_use_groundwork_trace.py",
    "pre_tool_use_groundwork_trace.py",
    "stop_groundwork_score.py",
    "user_prompt_submit_groundwork_entry.py",
}

FORBIDDEN_PACKAGE_ROOTS = {
    ".git",
    ".github",
    ".codegraph",
    ".groundwork",
    ".trellis",
    "AGENTS.md",
    "CHANGELOG.md",
    "PROJECT.md",
    ".gitignore",
    ".worktreeinclude.example",
    "artifacts",
    "docs",
    "evals",
    "examples",
    "research",
    "schemas",
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
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        return
    shutil.copy2(source, destination)


def file_set(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def validate_hooks_config(plugin_root: Path) -> list[str]:
    hooks_path = plugin_root / "hooks" / "hooks.json"
    if not hooks_path.is_file():
        return ["Runtime package hook config is missing: hooks/hooks.json"]
    try:
        manifest = json.loads(hooks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"Runtime package hook config is invalid JSON: {exc}"]
    if set(manifest) != {"hooks"}:
        return ["Runtime package hook config must contain only the top-level `hooks` field."]
    if not isinstance(manifest.get("hooks"), dict):
        return ["Runtime package hook config `hooks` field must be an object."]
    return []


def assert_runtime_package_boundary(plugin_root: Path) -> None:
    expected_roots = sorted({destination.split("/", 1)[0] for destination in RUNTIME_PACKAGE_ENTRIES.values()})
    observed_roots = sorted(path.name for path in plugin_root.iterdir())
    missing = [root for root in expected_roots if not (plugin_root / root).exists()]
    unexpected = [root for root in observed_roots if root not in expected_roots]
    leaked = [root for root in sorted(FORBIDDEN_PACKAGE_ROOTS) if (plugin_root / root).exists()]
    hook_files = file_set(plugin_root / "hooks")
    script_entries = sorted(path.name for path in (plugin_root / "scripts").iterdir()) if (plugin_root / "scripts").exists() else []
    codex_hook_files = file_set(plugin_root / "scripts" / "codex-hooks")

    errors = []
    if missing:
        errors.append("Runtime package is missing required paths:\n" + "\n".join(f"- {path}" for path in missing))
    if unexpected:
        errors.append("Runtime package contains unexpected top-level paths:\n" + "\n".join(f"- {path}" for path in unexpected))
    if leaked:
        errors.append("Runtime package contains forbidden repo-only paths:\n" + "\n".join(f"- {path}" for path in leaked))
    if hook_files != RUNTIME_HOOK_FILES:
        extra = sorted(hook_files - RUNTIME_HOOK_FILES)
        missing_hooks = sorted(RUNTIME_HOOK_FILES - hook_files)
        details = []
        if missing_hooks:
            details.append("missing:\n" + "\n".join(f"- hooks/{path}" for path in missing_hooks))
        if extra:
            details.append("unexpected:\n" + "\n".join(f"- hooks/{path}" for path in extra))
        errors.append("Runtime package hook manifest files are not exact:\n" + "\n\n".join(details))
    if script_entries != ["codex-hooks"]:
        errors.append(
            "Runtime package scripts/ must contain only codex-hooks/:\n"
            + "\n".join(f"- scripts/{path}" for path in script_entries)
        )
    if codex_hook_files != RUNTIME_CODEX_HOOK_FILES:
        extra = sorted(codex_hook_files - RUNTIME_CODEX_HOOK_FILES)
        missing_hooks = sorted(RUNTIME_CODEX_HOOK_FILES - codex_hook_files)
        details = []
        if missing_hooks:
            details.append("missing:\n" + "\n".join(f"- scripts/codex-hooks/{path}" for path in missing_hooks))
        if extra:
            details.append("unexpected:\n" + "\n".join(f"- scripts/codex-hooks/{path}" for path in extra))
        errors.append("Runtime package codex hook files are not exact:\n" + "\n\n".join(details))
    errors.extend(validate_hooks_config(plugin_root))
    if errors:
        raise SystemExit("\n\n".join(errors))


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
    for source_relative, destination_relative in RUNTIME_PACKAGE_ENTRIES.items():
        source = ROOT / source_relative
        if not source.exists():
            raise SystemExit(f"Package path does not exist: {source_relative}")
        copy_path(source, plugin_root / destination_relative)
        if source_relative == destination_relative:
            copied.append(source_relative)
        else:
            copied.append(f"{source_relative} -> {destination_relative}")

    assert_runtime_package_boundary(plugin_root)

    write_marketplace_manifest(output)
    print(f"Built Groundwork local marketplace: {output}")
    print(f"Plugin package root: {plugin_root}")
    print("Packaged runtime entries:")
    for relative in copied:
        print(f"- {relative}")
    print("Forbidden package roots:")
    for relative in sorted(FORBIDDEN_PACKAGE_ROOTS):
        print(f"- {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
