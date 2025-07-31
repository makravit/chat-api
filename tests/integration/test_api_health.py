
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
