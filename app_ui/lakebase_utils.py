"""Lakebase (managed Postgres) connection for the Lumora marketplace app.

When deployed as a Databricks App with a Lakebase resource attached, the
platform injects PGHOST/PGPORT/PGDATABASE/PGUSER/PGSSLMODE automatically; the
Postgres password is the app service principal's OAuth token. This is the
low-latency serving layer for the vendor tiles.
"""

import os
import time
import threading
import uuid

import psycopg
from databricks.sdk import WorkspaceClient

LAKEBASE_INSTANCE = os.environ.get("LAKEBASE_INSTANCE", "lumora-marketplace-db")

_lock = threading.Lock()
_cached = {"token": None, "exp": 0}


def _db_credential() -> str:
    """A Lakebase-valid Postgres credential (NOT the raw OAuth token), cached ~50 min."""
    now = time.time()
    with _lock:
        if _cached["token"] and now < _cached["exp"]:
            return _cached["token"]
    cred = WorkspaceClient().database.generate_database_credential(
        request_id=str(uuid.uuid4()), instance_names=[LAKEBASE_INSTANCE]
    )
    with _lock:
        _cached.update(token=cred.token, exp=now + 3000)
    return cred.token


def _conn():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ.get("PGPORT", "5432")),
        dbname=os.environ.get("PGDATABASE", "databricks_postgres"),
        user=os.environ["PGUSER"],
        password=_db_credential(),
        sslmode=os.environ.get("PGSSLMODE", "require"),
        connect_timeout=15,
    )


def query(sql: str, params=None):
    """Run a read query against Lakebase; return (columns, rows)."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            cols = [d.name for d in cur.description] if cur.description else []
            rows = [list(r) for r in cur.fetchall()]
            return cols, rows
