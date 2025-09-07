from __future__ import annotations
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql as psql
from .settings import settings
from .sql_loader import load_sql

_pool: SimpleConnectionPool | None = None


def _dsn(dbname: str) -> str:
    s = settings.db
    return f"host={s.HOST} port={s.PORT} dbname={dbname} user={s.USER} password={s.PASSWORD}"


def init_pool() -> None:
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(1, 10, dsn=_dsn(settings.db.NAME), cursor_factory=RealDictCursor)


def close_pool() -> None:
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None


@contextmanager
def get_conn():
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)


@contextmanager
def get_cursor():
    with get_conn() as conn:
        with conn.cursor() as cur:
            yield cur
            conn.commit()


def ensure_database_exists() -> None:
    """Create DB if missing (works only if role has CREATEDB). Safe to call always."""
    try:
        psycopg2.connect(dsn=_dsn(settings.db.NAME)).close()
        return
    except Exception:
        pass

    maint = psycopg2.connect(dsn=_dsn(settings.db.MAINTENANCE_DB))
    maint.autocommit = True
    with maint, maint.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.db.NAME,))
        if cur.fetchone():
            return
        cur.execute(psql.SQL("CREATE DATABASE {}").format(psql.Identifier(settings.db.NAME)))


def apply_schema() -> None:
    schema_sql = load_sql("schema.sql")
    with get_cursor() as cur:
        cur.execute(schema_sql)
