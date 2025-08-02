
# Standard library imports

# Third-party imports
from fastapi.testclient import TestClient

from app.core.config import Settings

# Local application imports
from app.main import app


def test_metrics_endpoint_returns_prometheus_format():
    client = TestClient(app)
    settings = Settings()
    response = client.get(
        "/metrics",
        auth=(settings.METRICS_USER, settings.METRICS_PASS)
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    # Check for Prometheus HELP/TYPE lines in response
    assert "# HELP" in response.text
    assert "# TYPE" in response.text
