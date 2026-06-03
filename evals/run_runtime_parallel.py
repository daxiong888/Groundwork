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


if __name__ == "__main__":
    raise SystemExit(run_runtime.main(sys.argv[1:]))
