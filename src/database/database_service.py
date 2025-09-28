from __future__ import annotations
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql as psql
from src.settings import settings
from src.database.sql_loader import load_sql

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
        print("Checking if database exists...   settings.db.NAME =", settings.db.NAME)
        # First, try to connect to the target database. If it works, we're done.
        psycopg2.connect(dsn=_dsn(settings.db.NAME)).close()
        print("Database exists.")
        return True
    except psycopg2.OperationalError:
        # This is expected if the database doesn't exist yet.
        print("Database does not exist --- OPERATIONAL ERROR.")
    
    except Exception as e:
        # Handle other potential exceptions
        print(f"An unexpected error occurred: {e}")
        raise

    # Connect to the maintenance database (e.g., 'postgres')
    maint_conn = psycopg2.connect(dsn=_dsn(settings.db.MAINTENANCE_DB))
    
    # **THIS IS THE FIX**: Set the connection to autocommit mode
    maint_conn.autocommit = True

    try:
        with maint_conn.cursor() as cur:
            # Check if the database already exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.db.NAME,))
            if cur.fetchone():
                return # Database exists, nothing to do.

            # If it doesn't exist, create it
            print(f"Database '{settings.db.NAME}' not found. Creating it now...")
            cur.execute(psql.SQL("CREATE DATABASE {}").format(psql.Identifier(settings.db.NAME)))
            print("Database created successfully.")
    finally:
        # Always close the maintenance connection
        maint_conn.close()


def apply_schema() -> None:
    schema_sql = load_sql("schema.sql")
    with get_cursor() as cur:
        cur.execute(schema_sql)
