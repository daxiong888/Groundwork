#!/usr/bin/env python3
"""Bounded maintainer evidence CLI. Uses no model API, subprocess, or network."""

import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys

from rsi.control import policy_feedback, recover, source_feedback
from rsi.engine import ingest, prepare, status
from rsi.schema import RSIError, result
from rsi.security import read_json, within
from rsi.store import Store


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=str(Path.cwd()))
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--scope", required=True)
    p.add_argument("--output")
    p.add_argument("--run-context", help="Private JSON containing actual native heartbeat identity, when available")
    p = commands.add_parser("ingest")
    p.add_argument("--attempt", required=True)
    p.add_argument("--result", required=True)
    p = commands.add_parser("feedback")
    p.add_argument("--scope")
    p.add_argument("--candidate")
    p.add_argument("--revision", type=int)
    p.add_argument("--record", required=True)
    p = commands.add_parser("status")
    p.add_argument("--scope", required=True)
    p.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    os.umask(0o077)
    store = None
    def output(value):
        print(json.dumps(value, ensure_ascii=False, sort_keys=True), flush=True)
    try:
        store = Store(args.project)
        recover(store)
        if args.command == "prepare":
            context = read_json(within(args.run_context, store.root), 4096) if args.run_context else None
            prepare(store, args.scope, args.output, output, run_context=context)
        elif args.command == "ingest":
            analysis = read_json(within(args.result, store.root), 24576)
            ingest(store, args.attempt, analysis, output)
        elif args.command == "status":
            status(store, args.scope, output)
        else:
            record = read_json(within(args.record, store.root), 32768)
            scope = args.scope or record.get("scope")
            if record.get("kind") == "policy":
                response = policy_feedback(store, scope, record)
            elif record.get("kind") == "source":
                response = source_feedback(store, scope, record)
            else:
                from rsi.feedback import handle_feedback
                response = handle_feedback(store, scope, args.candidate, args.revision, record)
            output(response)
        return 0
    except (RSIError, OSError, sqlite3.Error, ValueError, TypeError, KeyError) as exc:
        # Never export source paths, raw payloads or SQLite exception contents.
        output(result(exc.reason if isinstance(exc, RSIError) else "local_io_or_invalid_input", action="pause_automation_if_storage_unwritable" if isinstance(exc, (OSError, sqlite3.Error)) else "inspect_contract"))
        return 2
    finally:
        if store:
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
