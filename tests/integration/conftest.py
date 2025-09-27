from collections.abc import Callable, Generator
from typing import Any

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from alembic import command
from app.core.config import settings
from app.core.database import get_db
from app.main import app
from tests.utils import PasswordKind, build_password


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> None:
    app.dependency_overrides = {}


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:15") as container:
        container.start()
        yield container


@pytest.fixture(scope="session")
def test_engine(postgres_container: PostgresContainer) -> Generator[Engine]:
    db_url = postgres_container.get_connection_url()
    # Patch database component settings for Alembic and app
    url = make_url(db_url)
    settings.DATABASE_HOST = url.host or "localhost"
    if url.port is not None:
        settings.DATABASE_PORT = int(url.port)
    if url.username is not None:
        settings.DATABASE_USER = str(url.username)
    if url.password is not None:
        settings.DATABASE_PASSWORD = str(url.password)
    settings.DATABASE_NAME = str(url.database)
    # Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def user_data() -> dict[str, str]:
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": build_password(PasswordKind.VALID),
    }


@pytest.fixture
def login_and_get_tokens(
    client: TestClient,
    user_data: dict[str, str],
) -> Callable[[dict[str, str] | None], dict[str, Any]]:
    def _do_login(ud: dict[str, str] | None = None) -> dict[str, Any]:
        data = ud or user_data
        reg = client.post("/api/v1/users/register", json=data)
        assert reg.status_code in (201, 409)
        login = client.post(
            "/api/v1/users/login",
            json={"email": data["email"], "password": data["password"]},
        )
        assert login.status_code == 200
        return {
            "access_token": login.json().get("access_token"),
            "refresh_token": login.cookies.get("refresh_token"),
            "response": login,
            "user_data": data,
        }

    return _do_login
