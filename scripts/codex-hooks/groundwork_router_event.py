#!/usr/bin/env python3
"""Low-cost, fail-open entrypoint for all Groundwork observability hooks."""

import json
import os
import sys
from pathlib import Path


SUPPORTED_EVENTS = {"PermissionRequest", "PostToolUse", "PreToolUse", "Stop", "UserPromptSubmit"}


def _preflight_enabled(event):
    """Check opt-in without importing the telemetry module or classifier.

    The telemetry module revalidates this config before writing. This preflight
    exists only to keep the default disabled path cheap and fail-closed.
    """

    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY") == "1":
        return True
    cwd = Path(event.get("cwd") or os.getcwd()).resolve()
    path = cwd / ".groundwork" / "harness" / "router-observability" / "config.json"
    current = cwd
    for part in path.relative_to(cwd).parts:
        current /= part
        if current.is_symlink():
            return False
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    if not isinstance(config, dict):
        return False
    if any(
        field in config and not isinstance(config[field], bool)
        for field in ("enabled", "raw_capture", "snippet_capture")
    ) or ("mode" in config and not isinstance(config["mode"], str)):
        return False
    return config.get("enabled") is True


def _dispatch(event_name, event):
    from groundwork_router_telemetry import handle_permission_event, handle_stop, handle_tool_event, handle_user_prompt_submit

    if event_name == "UserPromptSubmit":
        return handle_user_prompt_submit(event)
    if event_name in {"PreToolUse", "PostToolUse"}:
        return handle_tool_event(event, event_name)
    if event_name == "PermissionRequest":
        return handle_permission_event(event)
    return handle_stop(event)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        if len(args) != 1 or args[0] not in SUPPORTED_EVENTS:
            raise ValueError("expected one supported hook event name")
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
        if not _preflight_enabled(event):
            return 0
        output = _dispatch(args[0], event)
        if output is not None:
            print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    except Exception as exc:  # Hooks must not break normal Codex use.
        if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG"):
            print(f"Groundwork router telemetry hook failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
