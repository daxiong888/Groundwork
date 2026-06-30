#!/usr/bin/env bash
set -euo pipefail

target="${1:-$(pwd)}"

if ! command -v codegraph >/dev/null 2>&1; then
  echo "codegraph command not found; install CodeGraph before indexing this worktree." >&2
  exit 127
fi

if [ ! -d "$target" ]; then
  echo "target directory does not exist: $target" >&2
  exit 2
fi

if [ ! -d "$target/.codegraph" ]; then
  codegraph init "$target"
else
  codegraph sync -q "$target"
fi
