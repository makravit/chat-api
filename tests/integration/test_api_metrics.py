
# Standard library imports

# Third-party imports
from fastapi.testclient import TestClient

# Local application imports
from app.main import app


def test_metrics_endpoint_returns_prometheus_format():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    # Check for Prometheus HELP/TYPE lines in response
    assert "# HELP" in response.text
    assert "# TYPE" in response.text
