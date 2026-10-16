"""Directory-fd anchored regular-file access and conservative text filtering."""

import json
import os
from pathlib import Path
import re
import stat
import uuid
from contextlib import contextmanager

from .schema import RSIError, require


class ReadMeter:
    """Charge before bounded I/O; exceptions and crashes cannot refund a read."""
    def __init__(self, store, scope, limit, parent=None):
        self.store, self.scope, self.limit, self.used = store, scope, max(0, limit), 0
        self.parent = parent

    @property
    def remaining(self):
        available = max(0, self.limit - self.used)
        return min(available, self.parent.remaining) if self.parent else available

    def available(self):
        policy = json.loads(self.store.scope(self.scope)["policy"])
        usage = self.store.usage(self.scope)
        return max(0, min(self.remaining, policy["budgets"]["daily_bytes"] - usage["bytes"] - usage["reserved"]))

    def child(self, limit):
        return ReadMeter(self.store, self.scope, limit, parent=self)

    def read(self, stream, size, line=False):
        require(not self.store.db.in_transaction, "metered_io_inside_transaction")
        requested = size
        size = max(0, min(size, self.remaining))
        require(size > 0 or requested == 0, "read_budget_exhausted")
        with self.store.tx():
            row = self.store.scope(self.scope)
            policy = json.loads(row["policy"])
            usage = self.store.usage(self.scope)
            available = policy["budgets"]["daily_bytes"] - usage["bytes"] - usage["reserved"]
            size = max(0, min(size, available))
            require(size > 0 or requested == 0, "read_budget_exhausted")
            self.store.charge(self.scope, bytes=size)
        meters, current = [], self
        while current is not None:
            meters.append(current)
            current.used += size
            current = current.parent
        data = stream.readline(size) if line else stream.read(size)
        # Only a completed read returns unused allocation. Mid-read failure is conservative.
        with self.store.tx():
            self.store.charge(self.scope, bytes=len(data) - size)
        for meter in meters:
            meter.used += len(data) - size
        return data

    def wrap(self, stream):
        meter = self
        class Reader:
            def read(self, size):
                return meter.read(stream, size)
            def readline(self, size):
                return meter.read(stream, size, line=True)
            def __getattr__(self, name):
                return getattr(stream, name)
        return Reader()


def normalized(path):
    candidate = Path(os.path.abspath(path))
    require(".." not in Path(path).parts, "path_denied")
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current /= part
        require(not current.is_symlink(), "symlink_denied")
    return candidate


def within(path, root):
    candidate, base = normalized(path), normalized(root)
    require(candidate.is_relative_to(base), "path_denied")
    return candidate


@contextmanager
def parent_fd(path, create=False):
    candidate = normalized(path)
    fd = os.open(candidate.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in candidate.parts[1:-1]:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        yield fd, candidate.name
    finally:
        os.close(fd)


@contextmanager
def open_regular(path):
    with parent_fd(path) as (parent, name):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            require(stat.S_ISREG(os.fstat(fd).st_mode), "regular_file_required")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                yield stream
        finally:
            os.close(fd)


def read_bytes(path, limit):
    with open_regular(path) as stream:
        data = stream.read(limit + 1)
        require(len(data) <= limit, "over_limit")
        return data


def read_json(path, limit=65536):
    try:
        return json.loads(read_bytes(path, limit))
    except (UnicodeError, json.JSONDecodeError):
        raise RSIError("invalid_json") from None


def atomic_write(path, data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    with parent_fd(path, create=True) as (parent, name):
        temporary = ".rsi-" + uuid.uuid4().hex
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
            os.fsync(parent)
        finally:
            try:
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass


def remove(path):
    try:
        with parent_fd(path) as (parent, name):
            os.unlink(name, dir_fd=parent)
    except FileNotFoundError:
        # An export can be registered before its first filesystem publication.
        # Missing parent directories therefore also mean there is nothing to erase.
        pass


SECRET = re.compile(
    r"(?:\b(?:password|passwd|token|api[_-]?key|client[_-]?secret|cookie)\s*[\"']?\s*[:=]"
    r"|Authorization\s*:|\b(?:ghp_|github_pat_|xox[baprs]-|sk-)[\w-]{10,}"
    r"|\bAKIA[0-9A-Z]{16}\b|-----BEGIN .*PRIVATE KEY|https?://[^\s/@]+:[^\s/@]+@)", re.I)
BLOCKS = re.compile(r"<(environment_context|instructions|system|developer|user_instructions|skills_instructions|app-context|codex_delegation)\b[^>]*>.*?</\1>", re.S | re.I)


def filtered_text(text, limit, *, asset=False):
    require(isinstance(text, str), "unsupported_content")
    require(not SECRET.search(text), "secret_pattern_denied")
    filtered = text if asset else BLOCKS.sub("", text)
    if not asset:
        require(not re.search(r"</?(?:environment_context|instructions|system|developer|user_instructions|skills_instructions|app-context|codex_delegation)\b", filtered, re.I), "ambiguous_block_denied")
        require(not filtered.lstrip().startswith(("# AGENTS.md", "<permissions instructions>")), "instruction_block_denied")
    data = filtered.encode("utf-8")
    return data[:limit].decode("utf-8", errors="ignore"), ["role_and_record_type", "embedded_blocks", "secret_patterns", "utf8_limit"]
