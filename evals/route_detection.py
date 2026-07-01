"""Eval compatibility wrapper for the runtime-safe hook classifier."""

import importlib.util
import sys
from pathlib import Path


CLASSIFIER_SOURCE_PATH = str(
    Path(__file__).resolve().parents[1] / "scripts" / "codex-hooks" / "groundwork_route_detection.py"
)


def _load_shared_classifier():
    spec = importlib.util.spec_from_file_location("groundwork_route_detection_for_evals", CLASSIFIER_SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load route detection classifier: {CLASSIFIER_SOURCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


_shared = _load_shared_classifier()

for _name in _shared.__all__:
    globals()[_name] = getattr(_shared, _name)

CLASSIFIER_SOURCE_PATH = _shared.CLASSIFIER_SOURCE_PATH
__all__ = list(_shared.__all__)
