#!/usr/bin/env python3
"""Compatibility wrapper for the skill-bundled child Goal prompt linter."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    linter = Path(__file__).resolve().parents[1] / "skills" / "_shared" / "tools" / "lint_child_goal_prompt.py"
    runpy.run_path(str(linter), run_name="__main__")
