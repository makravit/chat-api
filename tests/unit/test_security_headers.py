from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_present_on_simple_route() -> None:
    client = TestClient(app)
    r = client.get("/live")
    assert r.status_code == 200
    headers = r.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "no-referrer"
    assert headers.get("Permissions-Policy") is not None
    assert headers.get("Content-Security-Policy") is not None
