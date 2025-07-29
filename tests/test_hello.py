from fastapi.testclient import TestClient
from app.main import app

def test_hello_world():
    client = TestClient(app)
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}
