import assert from "node:assert/strict";
import { filterTasks } from "../src/taskSearch.mjs";

const tasks = [
  { id: "task-1", activityName: "Safety Check", phone: "13800000001" },
  { id: "task-2", activityName: "Safety Check", phone: "13800000002" },
  { id: "task-3", activityName: "Meter Reading", phone: "13900000003" },
];

assert.deepEqual(
  filterTasks(tasks, {}).map((task) => task.id),
  ["task-1", "task-2", "task-3"],
  "empty filters should return all tasks",
);

assert.deepEqual(
  filterTasks(tasks, { activityName: "Safety Check" }).map((task) => task.id),
  ["task-1", "task-2"],
  "activityName filter should keep existing behavior",
);

assert.deepEqual(
  filterTasks(tasks, { phone: "13800000002" }).map((task) => task.id),
  ["task-2"],
  "phone filter should return only exact matches",
);

assert.deepEqual(
  filterTasks(tasks, { activityName: "Safety Check", phone: "13800000001" }).map((task) => task.id),
  ["task-1"],
  "combined filters should apply activityName and phone",
);

console.log("minimal-task-search fixture passed");
