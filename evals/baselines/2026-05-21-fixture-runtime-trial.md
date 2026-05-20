# Groundwork Fixture Runtime Trial

Date: 2026-05-21

## Environment

- Source repo: `/Users/daxiong/Documents/sourceCode/Groundwork`
- Fixture source: `evals/fixtures/minimal-task-search`
- Trial copy: `/private/tmp/groundwork-fixture-rt-P8KaoV`
- Installation mode: personal marketplace / installed Groundwork plugin cache
- Runtime command style: `codex -a never exec --skip-git-repo-check --json --ephemeral`

The source fixture stayed intentionally buggy. The runtime trial modified only
the temporary copy.

## Initial Fixture Check

Command run in the source fixture:

```bash
node test/taskSearch.test.mjs
```

Result: failed as expected.

Failure:

```text
AssertionError [ERR_ASSERTION]: phone filter should return only exact matches
actual: [ 'task-1', 'task-2', 'task-3' ]
expected: [ 'task-2' ]
```

## Results

| ID | Expected | Actual | Verdict | Notes |
| --- | --- | --- | --- | --- |
| rt-004-fixture | `write-plan`; inspect `TASK.md`, `src/`, and `test/`; no file edits. | Runtime loaded cached `write-plan/SKILL.md`, read `TASK.md`, `src/taskSearch.mjs`, `test/taskSearch.test.mjs`, ran the failing test, and produced a plan with real paths only. | pass | Worktree stayed clean. |
| rt-006-fixture | `implement`; confirm bug before edit; make minimum fix. | Runtime loaded cached `implement/SKILL.md`, ran the test to confirm the phone-filter failure, changed only `src/taskSearch.mjs`, and reran the test successfully. | pass | Diff replaced `void phone` with exact phone filtering. |
| rt-007-fixture | `verify`; separate source evidence, test evidence, and unverified risk. | Runtime loaded cached `verify/SKILL.md`, inspected task/source/test/diff, ran `node test/taskSearch.test.mjs`, added a missing-filters one-liner assertion, and returned `Verdict: pass`. | pass | It correctly noted that README still describes the fixture as intentionally buggy after the temp-copy fix. |

## Implementation Diff In Trial Copy

```diff
diff --git a/src/taskSearch.mjs b/src/taskSearch.mjs
index f8283e2..8971cfd 100644
--- a/src/taskSearch.mjs
+++ b/src/taskSearch.mjs
@@ -7,8 +7,10 @@ export function filterTasks(tasks, filters = {}) {
       return false;
     }
 
-    // BUG: phone is normalized above but is not applied to the result set.
-    void phone;
+    if (phone && normalize(task.phone) !== phone) {
+      return false;
+    }
+
     return true;
   });
 }
```

## Verification Evidence

Command run after implementation in the trial copy:

```bash
node test/taskSearch.test.mjs
```

Result:

```text
minimal-task-search fixture passed
```

Additional check run by `verify`:

```bash
node --input-type=module -e 'import assert from "node:assert/strict"; import { filterTasks } from "./src/taskSearch.mjs"; const tasks = [{ id: "a", activityName: "A", phone: "1" }, { id: "b", activityName: "B", phone: "2" }]; assert.deepEqual(filterTasks(tasks).map((task) => task.id), ["a", "b"]); console.log("missing-filters assertion passed");'
```

Result:

```text
missing-filters assertion passed
```

## Drift / Notes

- This trial confirms the fixture prevents Groundwork from drifting into a real business repository.
- `rt-004-fixture`, `rt-006-fixture`, and `rt-007-fixture` all loaded the expected Groundwork skills.
- The temporary fixed copy naturally makes `README.md` stale because the source fixture is supposed to remain buggy. This is acceptable for runtime trial use.
- No package install, network access, tracker update, deployment, git push, or external write was performed.

## Next Actions

- Use this fixture for future `write-plan`, `implement`, and `verify` regression checks.
- Run `rt-010` in Codex App or another interactive approval / Auto Review environment. Do not use `codex exec -a never` as an Auto Review test.
