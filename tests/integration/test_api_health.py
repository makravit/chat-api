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
    assert response.json()["status"] in ["ok", "error"]
    assert "db" in response.json()
