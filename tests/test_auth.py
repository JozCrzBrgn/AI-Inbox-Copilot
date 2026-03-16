from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_login_success(client):
    with patch('backend.routers.auth.authenticate_user') as mock_auth:
        mock_auth.return_value = {"username": "testuser"}
        with patch('backend.routers.auth.create_access_token') as mock_token:
            mock_token.return_value = "fake_token"
            response = client.post("/token", data={"username": "testuser", "password": "testpass"})
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


def test_login_failure(client):
    with patch('backend.routers.auth.authenticate_user') as mock_auth:
        mock_auth.return_value = False
        response = client.post("/token", data={"username": "wrong", "password": "wrong"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data