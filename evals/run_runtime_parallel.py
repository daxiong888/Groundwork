#!/usr/bin/env python3
"""Compatibility entrypoint for bounded runtime evals.

The bounded scheduler, resource policy, per-case result files, summary, and
failure rerun logic now live in `evals/run_runtime.py`. This wrapper keeps the
older command path working without maintaining a second scheduler.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("GROUNDWORK_RUNTIME_ROOT", "/private/tmp/groundwork-runtime-v03-parallel")

import run_runtime

PARALLEL_COMPAT_CASE_TIMEOUT = "390"


def with_parallel_compat_defaults(argv):
    """Preserve the old wrapper's default child codex timeout."""
    args = list(argv)
    if any(arg == "--case-timeout" or arg.startswith("--case-timeout=") for arg in args):
        return args
    return ["--case-timeout", PARALLEL_COMPAT_CASE_TIMEOUT, *args]


if __name__ == "__main__":
    raise SystemExit(run_runtime.main(with_parallel_compat_defaults(sys.argv[1:])))
