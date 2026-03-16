import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.dependencies import get_current_user


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: "testuser"
    yield TestClient(app)
    app.dependency_overrides = {}


def test_production(client):
    response = client.post("/v1/production")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["message"] == "Todo ok"