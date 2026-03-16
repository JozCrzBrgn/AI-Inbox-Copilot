import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_info(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "created_by" in data
    assert "description" in data
    assert "version" in data