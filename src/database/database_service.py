from __future__ import annotations
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql as psql
from src.settings import settings
from src.database.sql_loader import load_sql


def check_database_exists() -> None:
    """Create DB if missing (works only if role has CREATEDB). Safe to call always."""
    try:
        with psycopg2.connect(settings.database_url) as conn:
            pass
        print("✓ Database exists")
        return True
    except psycopg2.OperationalError as e:
        print('error', e)
        if "does not exist" in str(e):
            print("✗ Database does not exist")
            return False
        else:
            print(f"✗ Connection error: {e}")
            raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from pgvector.psycopg2 import register_vector

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=settings.db_pool_size,
    max_overflow=10,
    echo=settings.db_echo
)

@event.listens_for(engine, "connect")
def register_vector_type(dbapi_conn, connection_record):
    """Register pgvector type on each new connection."""
    register_vector(dbapi_conn)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# FastAPI dependency
def get_db():
    """
    Dependency for FastAPI endpoints.
    Automatically closes session after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Context manager for scripts/services
@contextmanager
def get_db_context():
    """
    Context manager for non-FastAPI code.
    Use in scripts, background tasks, etc.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()