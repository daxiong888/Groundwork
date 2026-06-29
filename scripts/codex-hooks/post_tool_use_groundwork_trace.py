#!/usr/bin/env python3
from groundwork_router_observability import handle_tool_event, run_handler


if __name__ == "__main__":
    raise SystemExit(run_handler(handle_tool_event, "PostToolUse"))
