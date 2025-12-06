import os

# Force Testcontainers to use the reliable bridge network
# os.environ["TESTCONTAINERS_DOCKER_NETWORK"] = "bridge"
os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from src.api.api import app
from pgvector.psycopg2 import register_vector
from src.database.database_service import get_db
from src.database.models import Base
from fastapi.testclient import TestClient
from src.database import database_service
from contextlib import contextmanager

@pytest.fixture(scope="session")
def db_engine():
    """
    1. SPIN UP THE CONTAINER
    Scope='session' guarantees this only happens ONCE per test run.
    This is where you 'pay' the 5-second startup cost.
    """
    # We use the official pgvector docker image
    with PostgresContainer("pgvector/pgvector:pg16", driver="psycopg2") as postgres:
        # Adjust the internal container port handling if necessary, 
        # but usually defaults work fine.
        
        database_url = postgres.get_connection_url()
        engine = create_engine(database_url)

        # 2. SETUP THE DB
        # Enable the vector extension inside the container
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext")) # <--- ADD THIS
            conn.commit()

        # Register your pgvector listener (from your app logic)
        event.listen(engine, "connect", register_vector)

        # Create all tables once
        Base.metadata.create_all(bind=engine)

        yield engine
        
    # When the test session ends, the 'with' block exits and 
    # the container is destroyed automatically.


@pytest.fixture(name="session")
def session_fixture(db_engine):
    """
    3. RUN FAST TESTS
    This fixture runs for EVERY test function.
    It wraps the test in a transaction and rolls it back at the end.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to this specific connection/transaction
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    @contextmanager
    def get_db_context_override():
        yield session

    # yield session
    # We save the original function so we can restore it later
    original_context = database_service.get_db_context
    
    # We overwrite the function in the module with our override
    database_service.get_db_context = get_db_context_override

    yield session
    database_service.get_db_context = original_context

    # 4. CLEANUP
    session.close()
    transaction.rollback() # Everything you did in the test is undone here
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session):
    """
    Override the dependency with the rolled-back session.
    """
    def get_db_override():
        yield session

    app.dependency_overrides[get_db] = get_db_override
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()