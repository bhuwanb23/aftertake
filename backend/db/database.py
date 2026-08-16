"""SQLite connection + schema management for AfterTake.

Plain SQL only (no ORM) per Phase 0 Step 3c / Step 4.
The schema lives in db/sql/*.sql — one file per table (Phase 0 Step 9),
applied in sorted filename order. DDL is never embedded in Python code.
"""
import json
import os
import sqlite3
from pathlib import Path

try:  # python-dotenv may not be installed yet; fall back to real env vars + defaults
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # repo root
SCHEMA_DIR = Path(__file__).resolve().parent / "sql"


def database_path() -> Path:
    """Resolve the SQLite file path from DATABASE_PATH (relative to repo root)."""
    raw = os.getenv("DATABASE_PATH", "./aftertake.db")
    p = Path(raw)
    return p if p.is_absolute() else BASE_DIR / p


def get_connection(db_path=None) -> sqlite3.Connection:
    """Open a connection to the AfterTake database. Creates parent dirs if needed."""
    path = Path(db_path) if db_path else database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None) -> sqlite3.Connection:
    """Apply every *.sql file in db/sql/ (sorted by name). Idempotent —
    all DDL uses CREATE TABLE IF NOT EXISTS. Returns a connection."""
    conn = get_connection(db_path)
    for sql_file in sorted(SCHEMA_DIR.glob("*.sql")):
        conn.executescript(sql_file.read_text(encoding="utf-8"))
    conn.commit()
    return conn


def dumps(obj) -> str:
    """Serialize a nested object to a JSON text column."""
    return json.dumps(obj, ensure_ascii=False)


def loads(raw):
    """Deserialize a JSON text column back to a Python object."""
    if raw is None:
        return None
    return json.loads(raw) if isinstance(raw, str) else raw


def rows_to_dicts(rows):
    """Convert sqlite3.Row results to plain dicts (for API responses)."""
    return [dict(r) for r in rows]
