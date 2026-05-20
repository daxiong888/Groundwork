export function filterTasks(tasks, filters = {}) {
  const activityName = normalize(filters.activityName);
  const phone = normalize(filters.phone);

  return tasks.filter((task) => {
    if (activityName && normalize(task.activityName) !== activityName) {
      return false;
    }

    // BUG: phone is normalized above but is not applied to the result set.
    void phone;
    return true;
  });
}

function normalize(value) {
  return String(value ?? "").trim();
}
