
# Standard library imports

# Third-party imports
from fastapi.testclient import TestClient

# Local application imports
from app.main import app

def test_liveness():
    client = TestClient(app)
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_ok():
    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_health_check_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "error"]
    assert "db" in response.json()


def test_readiness_db_failure(monkeypatch):
    """Simulate DB failure for /ready endpoint and expect 503."""
    client = TestClient(app)
    # Patch get_db to raise an exception
    from app.api import health
    def broken_get_db():
        raise Exception("DB down")
    monkeypatch.setattr(health, "get_db", broken_get_db)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not ready"


def test_health_check_db_down(monkeypatch):
    """Simulate DB failure for /health endpoint and expect error status."""
    client = TestClient(app)
    from app.api import health
    def broken_get_db():
        raise Exception("DB down")
    monkeypatch.setattr(health, "get_db", broken_get_db)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["db"] == "down"
