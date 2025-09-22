from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app


def test_metrics_endpoint_returns_prometheus_format() -> None:
    client = TestClient(app)
    settings = Settings()
    response = client.get(
        "/metrics",
        auth=(settings.METRICS_USER, settings.METRICS_PASS),
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    # Check for Prometheus HELP/TYPE lines in response
    assert "# HELP" in response.text
    assert "# TYPE" in response.text


def test_metrics_endpoint_unauthorized() -> None:
    client = TestClient(app)
    # Missing auth
    r1 = client.get("/metrics")
    assert r1.status_code in (401, 403)
    # Wrong basic auth
    r2 = client.get("/metrics", auth=("wrong", "creds"))
    assert r2.status_code in (401, 403)
