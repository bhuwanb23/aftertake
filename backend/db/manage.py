"""CLI to manage the AfterTake SQLite database.

Usage (from the repo root, using the backend venv's python):

    python -m backend.db.manage init      # create tables if missing (idempotent)
    python -m backend.db.manage reset     # drop all tables, then re-init
    python -m backend.db.manage inspect   # list tables + row counts
    python -m backend.db.manage path      # print the resolved DB file path

The schema itself lives in backend/db/schema.sql — edit it there, then run
`init` (existing tables are untouched) or `reset` (fresh start).
"""
import argparse
import sys

try:
    from . import database
except ImportError:  # allow `python backend/db/manage.py` as a fallback
    from backend.db import database

# Tables created by schema.sql. Used by reset/inspect.
TABLES = [
    "source_videos",
    "creator_profiles",
    "opportunities",
    "scripts",
    "thumbnails",
    "metadata",
    "quality_scores",
    "decision_log",
    "generated_assets",
    "pipeline_runs",
]


def cmd_init(_args):
    conn = database.init_db()
    count = len([r for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")])
    print(f"DB ready at {database.database_path()} — {count} tables present.")
    conn.close()


def cmd_reset(_args):
    conn = database.get_connection()
    print(f"Dropping all tables in {database.database_path()} ...")
    for t in TABLES:
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
    conn.close()
    cmd_init(_args)


def cmd_inspect(_args):
    conn = database.get_connection()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    if not rows:
        print(f"No tables yet at {database.database_path()} - run `init` first.")
    for r in rows:
        t = r["name"]
        n = conn.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()["c"]
        print(f"  {t:<24} {n} rows")
    conn.close()


def cmd_path(_args):
    print(database.database_path())


def main():
    parser = argparse.ArgumentParser(prog="manage", description="Manage the AfterTake SQLite database.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="create tables if missing (idempotent)")
    sub.add_parser("reset", help="drop all tables, then re-init from schema.sql")
    sub.add_parser("inspect", help="list tables and row counts")
    sub.add_parser("path", help="print the resolved DB file path")
    args = parser.parse_args()
    {"init": cmd_init, "reset": cmd_reset, "inspect": cmd_inspect, "path": cmd_path}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
