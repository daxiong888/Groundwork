#!/usr/bin/env python3
"""Validate the Groundwork runtime package boundary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "groundwork"

ALLOWED_RUNTIME_ROOTS = {
    ".codex-plugin",
    "hooks",
    "skills",
    "scripts",
    "README.md",
    "LICENSE",
}

EXPECTED_RUNTIME_HOOK_FILES = {
    "hooks.json",
}

EXPECTED_RUNTIME_CODEX_HOOK_FILES = {
    "groundwork_router_observability.py",
    "permission_request_groundwork_trace.py",
    "post_tool_use_groundwork_trace.py",
    "pre_tool_use_groundwork_trace.py",
    "stop_groundwork_score.py",
    "user_prompt_submit_groundwork_entry.py",
}

FORBIDDEN_RUNTIME_ROOTS = {
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
        hook_files == EXPECTED_RUNTIME_HOOK_FILES,
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
        codex_hook_files == EXPECTED_RUNTIME_CODEX_HOOK_FILES,
        errors,
        "Runtime package scripts/codex-hooks/ files must be exact:\n"
        + "\n".join(f"- scripts/codex-hooks/{path}" for path in sorted(codex_hook_files)),
    )
    validate_hooks_config(package_root, errors)

    runtime_readme = ROOT / "README.runtime.md"
    if (package_root / "README.md").is_file() and runtime_readme.is_file():
        require(
            (package_root / "README.md").read_text(encoding="utf-8")
            == runtime_readme.read_text(encoding="utf-8"),
            errors,
            "Runtime package README.md must be generated from README.runtime.md.",
        )
    else:
        require(runtime_readme.is_file(), errors, "Source README.runtime.md is missing.")

    if errors:
        raise SystemExit("\n\n".join(errors))

    print(f"runtime package boundary ok: {package_root}")


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
