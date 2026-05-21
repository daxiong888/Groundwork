export function filterTasks(tasks, filters = {}) {
  const activityName = normalize(filters.activityName);
  const phone = normalize(filters.phone);

  return tasks.filter((task) => {
    if (activityName && normalize(task.activityName) !== activityName) {
      return false;
    }

    if (phone && normalize(task.phone) !== phone) {
      return false;
    }

    return true;
  });
}

function normalize(value) {
  return String(value ?? "").trim();
}
