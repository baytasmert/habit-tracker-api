"""Testcontainers configuration for isolated PostgreSQL testing"""
import os
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import factory

# Disable Testcontainers Ryuk for Windows compatibility
os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

from src.database import Base
from tests.factories import HabitFactory, HabitLogFactory

# Testcontainers PostgreSQL setup for isolation
postgres_container = None
test_engine = None
TestingSessionLocal = None


@pytest.fixture(scope="session")
def testcontainers_postgres():
    """Start isolated PostgreSQL container for entire test session"""
    global postgres_container, test_engine, TestingSessionLocal

    postgres_container = PostgresContainer("postgres:16")
    postgres_container.start()

    # Create connection string
    db_url = postgres_container.get_connection_url()

    # Create engine and tables
    test_engine = create_engine(db_url)
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    yield test_engine

    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    postgres_container.stop()


@pytest.fixture
def testcontainers_db(testcontainers_postgres):
    """Database session with Testcontainers"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Set factory session for this test
    factory.Factory._meta.sqlalchemy_session = session
    HabitFactory._meta.sqlalchemy_session = session
    HabitLogFactory._meta.sqlalchemy_session = session

    yield session

    session.close()
    transaction.rollback()
    connection.close()
