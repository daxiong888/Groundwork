#!/usr/bin/env python3
import os
import sys

try:
    from groundwork_router_telemetry import handle_permission_event, run_handler
except Exception as exc:  # Hooks must not break normal Codex use during plugin cache refresh.
    if os.environ.get("GROUNDWORK_ROUTER_OBSERVABILITY_DEBUG"):
        print(f"Groundwork router observability entrypoint unavailable: {exc}", file=sys.stderr)
    raise SystemExit(0)


if __name__ == "__main__":
    raise SystemExit(run_handler(handle_permission_event))
