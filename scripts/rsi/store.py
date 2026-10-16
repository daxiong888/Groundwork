"""One SQLite authority; short write transactions also serialize publication."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import time

from .schema import RSIError, canonical, require
from .security import normalized, parent_fd


DDL = """
CREATE TABLE IF NOT EXISTS scopes (
 id TEXT PRIMARY KEY, generation INTEGER NOT NULL, state TEXT NOT NULL,
 policy TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
 projection TEXT NOT NULL DEFAULT 'pending', cleanup TEXT NOT NULL DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS sources (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, kind TEXT NOT NULL, path TEXT,
 config TEXT NOT NULL, generation TEXT, offset INTEGER NOT NULL DEFAULT 0,
 skipping INTEGER NOT NULL DEFAULT 0, signature TEXT, status TEXT NOT NULL DEFAULT 'new',
 updated REAL NOT NULL, snapshot TEXT);
CREATE TABLE IF NOT EXISTS facts (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, source TEXT NOT NULL, generation TEXT NOT NULL,
 position TEXT NOT NULL, identity TEXT, fingerprint TEXT NOT NULL, work_id TEXT,
 body TEXT, created REAL NOT NULL, expires REAL NOT NULL,
 UNIQUE(source,generation,position));
CREATE TABLE IF NOT EXISTS work (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, kind TEXT NOT NULL, revision INTEGER NOT NULL,
 state TEXT NOT NULL, updated REAL NOT NULL, body TEXT, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS attempts (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, work_id TEXT NOT NULL, evidence_revision INTEGER NOT NULL,
 policy_generation INTEGER NOT NULL, state TEXT NOT NULL, created REAL NOT NULL,
 expires REAL NOT NULL, packet TEXT, payload_digest TEXT, result TEXT,
 failures INTEGER NOT NULL DEFAULT 0, failure_reason TEXT, supplement INTEGER NOT NULL DEFAULT 0,
 freshness_reserved INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS candidates (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, merge_key TEXT NOT NULL,
 revision INTEGER NOT NULL, state TEXT NOT NULL, proposal_digest TEXT NOT NULL,
 body TEXT, work_id TEXT NOT NULL, evidence_revision INTEGER NOT NULL,
 created REAL NOT NULL, updated REAL NOT NULL, expires REAL NOT NULL,
 notified_revision INTEGER NOT NULL DEFAULT 0, result_digest TEXT, adoption TEXT,
 UNIQUE(scope,merge_key));
CREATE TABLE IF NOT EXISTS candidate_history (
 candidate TEXT NOT NULL, revision INTEGER NOT NULL, body TEXT,
 proposal_digest TEXT NOT NULL, created REAL NOT NULL, expires REAL NOT NULL,
 PRIMARY KEY(candidate,revision));
CREATE TABLE IF NOT EXISTS feedback (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, candidate TEXT, revision INTEGER,
 kind TEXT NOT NULL, payload_digest TEXT NOT NULL, body TEXT, result TEXT,
 created REAL NOT NULL, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS usage (
 scope TEXT NOT NULL, day TEXT NOT NULL, bytes INTEGER NOT NULL DEFAULT 0,
 records INTEGER NOT NULL DEFAULT 0, packets INTEGER NOT NULL DEFAULT 0,
 packet_bytes INTEGER NOT NULL DEFAULT 0, ready INTEGER NOT NULL DEFAULT 0,
 reserved INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(scope,day));
CREATE TABLE IF NOT EXISTS exports (
 path TEXT PRIMARY KEY, scope TEXT NOT NULL, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS messages (
 ref TEXT PRIMARY KEY, scope TEXT NOT NULL, source TEXT NOT NULL, generation TEXT NOT NULL,
 position INTEGER NOT NULL, turn_id TEXT NOT NULL, body TEXT, expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS maintenance_invocations (
 scope TEXT NOT NULL, wake_id TEXT NOT NULL, thread_ref TEXT NOT NULL,
 turn_ref TEXT NOT NULL, kind TEXT NOT NULL, observed REAL NOT NULL,
 PRIMARY KEY(scope,wake_id));
CREATE TABLE IF NOT EXISTS diagnostics (
 id INTEGER PRIMARY KEY, scope TEXT NOT NULL, source TEXT, reason TEXT NOT NULL,
 count INTEGER NOT NULL DEFAULT 1, created REAL NOT NULL, updated REAL NOT NULL,
 notified INTEGER NOT NULL DEFAULT 0, UNIQUE(scope,source,reason));
CREATE INDEX IF NOT EXISTS facts_work ON facts(work_id,created);
CREATE INDEX IF NOT EXISTS attempts_scope ON attempts(scope,state);
"""


class Store:
    def __init__(self, project, clock=time.time):
        self.project = normalized(project)
        self.root = self.project / ".groundwork/harness/rsi/v1"
        self.clock = clock
        path = self.root / "state.sqlite3"
        with parent_fd(path, create=True) as (fd, name):
            descriptor = os.open(name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            os.close(descriptor)
        os.chmod(self.root, 0o700)
        for suffix in ("", "-wal", "-shm", "-journal"):
            normalized(str(path) + suffix)
        self.db = sqlite3.connect(path, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA secure_delete=ON")
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.executescript(DDL)

    def close(self):
        self.db.close()

    def now(self):
        return self.clock()

    @contextmanager
    def tx(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield self.db
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def scope(self, scope, generation=None, active=True):
        row = self.db.execute("SELECT * FROM scopes WHERE id=?", (scope,)).fetchone()
        require(row is not None, "scope_missing")
        if active:
            require(row["state"] == "active", "policy_inactive")
            require(json.loads(row["policy"])["expires_at"] > self.now(), "policy_expired")
        if generation is not None:
            require(row["generation"] == generation, "policy_generation_changed")
        return row

    def usage(self, scope):
        day = datetime.fromtimestamp(self.now(), timezone.utc).strftime("%Y-%m-%d")
        self.db.execute("INSERT OR IGNORE INTO usage(scope,day) VALUES(?,?)", (scope, day))
        return self.db.execute("SELECT * FROM usage WHERE scope=? AND day=?", (scope, day)).fetchone()

    def charge(self, scope, **values):
        row = self.usage(scope)
        require(values.keys() <= {"bytes", "records", "packets", "packet_bytes", "ready", "reserved"}, "invalid_budget")
        if values:
            sql = ",".join(f"{key}={key}+?" for key in values)
            self.db.execute(f"UPDATE usage SET {sql} WHERE scope=? AND day=?", (*values.values(), scope, row["day"]))

    def release_attempt(self, attempt):
        day = datetime.fromtimestamp(attempt["created"], timezone.utc).strftime("%Y-%m-%d")
        self.db.execute("UPDATE usage SET reserved=MAX(0,reserved-?) WHERE scope=? AND day=?", (attempt["freshness_reserved"], attempt["scope"], day))
        self.db.execute("UPDATE attempts SET freshness_reserved=0 WHERE id=?", (attempt["id"],))

    def diagnostic(self, scope, reason, source=""):
        self.db.execute("""INSERT INTO diagnostics(scope,source,reason,created,updated) VALUES(?,?,?,?,?)
            ON CONFLICT(scope,source,reason) DO UPDATE SET count=count+1,updated=excluded.updated""",
                        (scope, source, reason, self.now(), self.now()))

    def size(self):
        total = 0
        for base, directories, files in os.walk(self.root, followlinks=False):
            directories[:] = [name for name in directories if not (Path(base) / name).is_symlink()]
            for name in files:
                path = Path(base) / name
                if not path.is_symlink():
                    total += path.stat().st_size
        locators = self.project / ".groundwork/harness/router-observability/semantic-locators"
        if locators.is_dir() and not locators.is_symlink():
            for path in locators.iterdir():
                if path.is_file() and not path.is_symlink():
                    total += path.stat().st_size
        return total

    def feedback_replay(self, record):
        from .schema import digest
        row = self.db.execute("SELECT * FROM feedback WHERE id=?", (record["id"],)).fetchone()
        if row:
            require(row["payload_digest"] == digest(record), "idempotency_conflict")
            return json.loads(row["result"])
        return None

    def save_feedback(self, scope, record, response, candidate=None, revision=None):
        from .schema import digest
        policy = json.loads(self.scope(scope, active=False)["policy"])
        self.db.execute("INSERT INTO feedback VALUES(?,?,?,?,?,?,?,?,?,?)", (
            record["id"], scope, candidate, revision, record["kind"], digest(record),
            canonical(record), canonical(response), self.now(),
            self.now() + policy["budgets"]["facts_days"] * 86400,
        ))
