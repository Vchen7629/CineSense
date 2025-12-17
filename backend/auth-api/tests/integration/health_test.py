# Checks Health Endpoint
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/apihealth")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_check() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}
