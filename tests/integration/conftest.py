
# Standard library imports

# Third-party imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from alembic import command
from alembic.config import Config
from app.core.config import settings

# Local application imports
from app.core.database import get_db
from app.main import app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as container:
        container.start()
        yield container

@pytest.fixture(scope="session")
def test_engine(postgres_container):
    db_url = postgres_container.get_connection_url()
    # Patch DATABASE_URL for Alembic and app using settings object
    settings.DATABASE_URL = db_url
    # Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(db_url)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
