
# Standard library imports

# Third-party imports
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

# Local application imports
from app.main import app
from app.api import health


def test_health_check_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}

def test_health_check_db_down(monkeypatch):
    # Patch get_db to raise SQLAlchemyError
    def fail_db():
        raise SQLAlchemyError("Simulated DB down")

    monkeypatch.setattr(health, "get_db", lambda: fail_db())
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "error", "db": "down"}
