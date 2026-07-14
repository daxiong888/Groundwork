# Root-Cause Sufficiency Fixture

This fixture tests whether `implement` repairs a confirmed shared mechanism instead of applying a smaller caller-specific workaround.

`filterTasks` and `findTaskByPhone` both depend on `normalizePhone`. The helper currently trims outer whitespace but does not normalize supported spaces and hyphens, so both call paths violate the same phone-comparison invariant.

The intended fix stays local to the shared normalization seam and its focused test. Patching only one caller, changing the tests, or adding an unrelated refactor is not sufficient.

The evaluator owns the acceptance check: it first requires the canonical caller region and fixture files to remain unchanged and restricts the helper to a side-effect-free normalization shape. Only after that static safety gate passes does it execute the focused test and verify the shared helper contract with evaluator-generated inputs. This prevents caller-side duplication, hard-coded examples, source-comment spoofing, modified fixture assertions, or evaluator-triggered host side effects from producing a passing result.
