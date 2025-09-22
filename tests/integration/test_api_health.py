import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api import health
from app.main import app


def test_liveness() -> None:
    client = TestClient(app)
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_ok() -> None:
    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_health_check_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "error"]
    assert "db" in response.json()


def test_readiness_db_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate DB failure for /ready endpoint and expect 503."""
    client = TestClient(app)

    def broken_get_session_local() -> None:
        msg = "DB down"
        raise SQLAlchemyError(msg)

    monkeypatch.setattr(health, "get_session_local", broken_get_session_local)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not ready"


def test_health_check_db_down(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate DB failure for /health endpoint and expect error status."""
    client = TestClient(app)

    def broken_get_session_local() -> None:
        msg = "DB down"
        raise SQLAlchemyError(msg)

    monkeypatch.setattr(health, "get_session_local", broken_get_session_local)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["db"] == "down"
