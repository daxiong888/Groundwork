export function filterTasks(tasks, filters = {}) {
  const activityName = normalizeText(filters.activityName);
  const phone = normalizePhone(filters.phone);

  return tasks.filter((task) => {
    if (activityName && normalizeText(task.activityName) !== activityName) {
      return false;
    }

    if (phone && normalizePhone(task.phone) !== phone) {
      return false;
    }

    return true;
  });
}

export function findTaskByPhone(tasks, phone) {
  const expected = normalizePhone(phone);
  return tasks.find((task) => normalizePhone(task.phone) === expected);
}

function normalizeText(value) {
  return String(value ?? "").trim();
}

export function normalizePhone(value) {
  // BUG: supported spaces and hyphens are formatting, but remain significant.
  return String(value ?? "").trim();
}

// ROOT_CAUSE_SUFFICIENCY_FIXTURE_END
