import assert from "node:assert/strict";
import { filterTasks, findTaskByPhone } from "../src/taskSearch.mjs";

const tasks = [
  { id: "task-1", activityName: "Safety Check", phone: "13800000001" },
  { id: "task-2", activityName: "Safety Check", phone: "13800000002" },
  { id: "task-3", activityName: "Meter Reading", phone: "13900000003" },
];

assert.deepEqual(
  filterTasks(tasks, { phone: "138-0000-0002" }).map((task) => task.id),
  ["task-2"],
  "phone filtering should ignore supported hyphen formatting",
);

assert.deepEqual(
  filterTasks(tasks, { activityName: "Safety Check", phone: "138 0000 0001" }).map(
    (task) => task.id,
  ),
  ["task-1"],
  "combined filtering should preserve activityName behavior",
);

assert.equal(
  findTaskByPhone(tasks, "139-0000-0003")?.id,
  "task-3",
  "exact lookup should use the same phone normalization contract",
);

console.log("root-cause-sufficiency fixture passed");
