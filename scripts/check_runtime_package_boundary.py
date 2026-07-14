#!/usr/bin/env python3
"""Validate the Groundwork runtime package boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "scripts" / "runtime_package_manifest.json"
PACKAGE_CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
PLUGIN_NAME = PACKAGE_CONTRACT["plugin_name"]
COPY_ENTRIES = PACKAGE_CONTRACT["copy_entries"]
ALLOWED_RUNTIME_ROOTS = {destination.split("/", 1)[0] for destination in COPY_ENTRIES.values()}
EXPECTED_EXACT_FILES = {key: set(value) for key, value in PACKAGE_CONTRACT["exact_files"].items()}
FORBIDDEN_RUNTIME_ROOTS = set(PACKAGE_CONTRACT["forbidden_roots"])
BUDGETS = PACKAGE_CONTRACT["budgets"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or inspect the Groundwork runtime package and fail on repo-only leaks."
    )
    parser.add_argument(
        "--package-root",
        type=Path,
        help="Existing plugins/groundwork package root to inspect. Defaults to a fresh temp build.",
    )
    return parser.parse_args()


def build_package(temp_root: Path) -> Path:
    marketplace_root = temp_root / "marketplace"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_local_marketplace.py"),
            "--output",
            str(marketplace_root),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            "Failed to build local marketplace for boundary check.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return marketplace_root / "plugins" / PLUGIN_NAME


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def file_set(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def content_inventory(package_root: Path) -> list[dict[str, str]]:
    generated = ".codex-plugin/runtime-manifest.json"
    return [
        {"path": path.relative_to(package_root).as_posix(), "sha256": sha256_bytes(path.read_bytes())}
        for path in sorted(package_root.rglob("*"))
        if path.is_file() and path.relative_to(package_root).as_posix() != generated
    ]


def line_count(paths) -> int:
    total = 0
    for path in paths:
        if not path.is_file():
            continue
        try:
            total += len(path.read_text(encoding="utf-8").splitlines())
        except UnicodeDecodeError:
            continue
    return total


def skill_reference_depth(skills_root: Path) -> int:
    markdown = list(skills_root.rglob("*.md"))
    nodes = {path.resolve() for path in markdown}
    edges = {node: set() for node in nodes}
    for path in markdown:
        for reference in re.findall(r"`([^`]+\.md)`", path.read_text(encoding="utf-8")):
            if reference.startswith("skills/"):
                candidate = skills_root.parent / reference
            elif "/" in reference:
                root_candidate = skills_root.parent / reference
                candidate = root_candidate if root_candidate.exists() else path.parent / reference
            else:
                candidate = path.parent / reference
            resolved = candidate.resolve()
            if resolved in nodes:
                edges[path.resolve()].add(resolved)

    maximum = 0

    def visit(node: Path, seen: set[Path]) -> None:
        nonlocal maximum
        maximum = max(maximum, len(seen))
        for target in edges[node]:
            if target not in seen:
                visit(target, seen | {target})

    for node in nodes:
        visit(node, {node})
    return maximum


def validate_runtime_provenance(package_root: Path, errors: list[str]) -> None:
    manifest_path = package_root / ".codex-plugin" / "runtime-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        plugin = json.loads((package_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"Runtime provenance manifest is missing or invalid: {exc}")
        return
    inventory = content_inventory(package_root)
    inventory_hash = sha256_bytes(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    require(manifest.get("plugin_name") == plugin.get("name"), errors, "Runtime manifest plugin_name mismatch.")
    require(manifest.get("plugin_version") == plugin.get("version"), errors, "Runtime manifest plugin_version mismatch.")
    require(
        manifest.get("contract_sha256") == sha256_bytes(CONTRACT_PATH.read_bytes()),
        errors,
        "Runtime manifest package contract hash mismatch.",
    )
    require(manifest.get("content_file_count") == len(inventory), errors, "Runtime manifest content_file_count mismatch.")
    require(manifest.get("content_inventory_sha256") == inventory_hash, errors, "Runtime manifest content hash mismatch.")
    require(
        manifest.get("readme_sha256") == sha256_bytes((package_root / "README.md").read_bytes()),
        errors,
        "Runtime manifest README hash mismatch.",
    )
    require(manifest.get("budgets") == BUDGETS, errors, "Runtime manifest budget contract mismatch.")


def validate_complexity_budgets(package_root: Path, errors: list[str]) -> dict[str, int]:
    runtime_files = [path for path in package_root.rglob("*") if path.is_file()]
    generated_manifest = package_root / ".codex-plugin" / "runtime-manifest.json"
    runtime_lines = line_count(path for path in runtime_files if path != generated_manifest)
    skill_files = [path for path in (package_root / "skills").rglob("*") if path.is_file()]
    hook_files = [path for path in (package_root / "scripts" / "codex-hooks").rglob("*") if path.is_file()]
    metrics = {
        "runtime_files": len(runtime_files),
        "runtime_lines_excluding_generated_manifest": runtime_lines,
        "skill_files": len(skill_files),
        "skill_lines": line_count(skill_files),
        "codex_hook_files": len(hook_files),
        "codex_hook_lines": line_count(hook_files),
        "skill_reference_depth": skill_reference_depth(package_root / "skills"),
    }
    pairs = {
        "runtime_files": "max_runtime_files",
        "runtime_lines_excluding_generated_manifest": "max_runtime_lines_excluding_generated_manifest",
        "skill_files": "max_skill_files",
        "skill_lines": "max_skill_lines",
        "codex_hook_files": "max_codex_hook_files",
        "codex_hook_lines": "max_codex_hook_lines",
        "skill_reference_depth": "max_skill_reference_depth",
    }
    for metric, budget in pairs.items():
        require(
            metrics[metric] <= BUDGETS[budget],
            errors,
            f"Runtime complexity budget exceeded: {metric}={metrics[metric]} > {budget}={BUDGETS[budget]}",
        )
    return metrics


def validate_hooks_config(package_root: Path, errors: list[str]) -> None:
    hooks_path = package_root / "hooks" / "hooks.json"
    if not hooks_path.is_file():
        errors.append("Runtime package hook config is missing: hooks/hooks.json")
        return
    try:
        manifest = json.loads(hooks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Runtime package hook config is invalid JSON: {exc}")
        return
    require(
        set(manifest) == {"hooks"},
        errors,
        "Runtime package hook config must contain only the top-level `hooks` field.",
    )
    require(
        isinstance(manifest.get("hooks"), dict),
        errors,
        "Runtime package hook config `hooks` field must be an object.",
    )


def validate_package(package_root: Path) -> None:
    package_root = package_root.expanduser().resolve()
    errors: list[str] = []

    require(package_root.is_dir(), errors, f"Package root does not exist: {package_root}")
    if errors:
        raise SystemExit("\n".join(errors))

    observed_roots = {path.name for path in package_root.iterdir()}
    unexpected_roots = sorted(observed_roots - ALLOWED_RUNTIME_ROOTS)
    missing_roots = sorted(ALLOWED_RUNTIME_ROOTS - observed_roots)
    forbidden_roots = sorted(root for root in FORBIDDEN_RUNTIME_ROOTS if (package_root / root).exists())

    require(
        not unexpected_roots,
        errors,
        "Runtime package contains unexpected top-level roots:\n"
        + "\n".join(f"- {root}" for root in unexpected_roots),
    )
    require(
        not missing_roots,
        errors,
        "Runtime package is missing required top-level roots:\n"
        + "\n".join(f"- {root}" for root in missing_roots),
    )
    require(
        not forbidden_roots,
        errors,
        "Runtime package contains forbidden repo-only roots:\n"
        + "\n".join(f"- {root}" for root in forbidden_roots),
    )
    require(
        (package_root / ".codex-plugin" / "plugin.json").is_file(),
        errors,
        "Runtime package must contain .codex-plugin/plugin.json.",
    )
    require((package_root / "skills").is_dir(), errors, "Runtime package must contain skills/.")
    require((package_root / "hooks" / "hooks.json").is_file(), errors, "Runtime package must contain hooks/hooks.json.")
    require(
        (package_root / "scripts" / "codex-hooks").is_dir(),
        errors,
        "Runtime package must contain scripts/codex-hooks/.",
    )
    require((package_root / "README.md").is_file(), errors, "Runtime package must contain README.md.")

    hook_files = file_set(package_root / "hooks")
    require(
        hook_files == EXPECTED_EXACT_FILES["hooks"],
        errors,
        "Runtime package hooks/ files must be exact:\n"
        + "\n".join(f"- hooks/{path}" for path in sorted(hook_files)),
    )

    script_entries = sorted(path.name for path in (package_root / "scripts").iterdir()) if (package_root / "scripts").exists() else []
    require(
        script_entries == ["codex-hooks"],
        errors,
        "Runtime package scripts/ must contain only codex-hooks/:\n"
        + "\n".join(f"- scripts/{path}" for path in script_entries),
    )

    codex_hook_files = file_set(package_root / "scripts" / "codex-hooks")
    require(
        codex_hook_files == EXPECTED_EXACT_FILES["scripts/codex-hooks"],
        errors,
        "Runtime package scripts/codex-hooks/ files must be exact:\n"
        + "\n".join(f"- scripts/codex-hooks/{path}" for path in sorted(codex_hook_files)),
    )
    plugin_metadata_files = file_set(package_root / ".codex-plugin")
    require(
        plugin_metadata_files == EXPECTED_EXACT_FILES[".codex-plugin"],
        errors,
        "Runtime package .codex-plugin/ files must be exact:\n"
        + "\n".join(f"- .codex-plugin/{path}" for path in sorted(plugin_metadata_files)),
    )
    validate_hooks_config(package_root, errors)
    validate_runtime_provenance(package_root, errors)
    metrics = validate_complexity_budgets(package_root, errors)

    if errors:
        raise SystemExit("\n\n".join(errors))

    print(f"runtime package boundary ok: {package_root}")
    print("runtime complexity metrics: " + json.dumps(metrics, sort_keys=True))


def main() -> int:
    args = parse_args()
    if args.package_root:
        validate_package(args.package_root)
    else:
        with tempfile.TemporaryDirectory(prefix="groundwork-runtime-boundary-") as temp_name:
            validate_package(build_package(Path(temp_name)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
