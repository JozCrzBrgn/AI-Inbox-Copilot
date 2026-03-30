from unittest.mock import MagicMock, patch

from frontend.services.api import analyze, get_history, login


@patch("frontend.services.api.requests.post")
def test_login_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "abc123"}

    mock_post.return_value = mock_response

    token = login("user", "pass")

    assert token == "abc123"

    mock_post.assert_called_once_with(
        "http://test:8000/token",
        data={"username": "user", "password": "pass"}
    )


@patch("frontend.services.api.requests.post")
def test_login_fail(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 401

    mock_post.return_value = mock_response

    token = login("user", "wrong")

    assert token is None


@patch("frontend.services.api.requests.post")
def test_analyze(mock_post):
    mock_response = MagicMock()
    mock_post.return_value = mock_response

    result = analyze("email content", "token123")

    assert result == mock_response

    mock_post.assert_called_once_with(
        "http://test:8000/v1/analyze",
        json={"email_content": "email content"},
        headers={"Authorization": "Bearer token123"}
    )


@patch("frontend.services.api.requests.get")
def test_get_history(mock_get):
    mock_response = MagicMock()
    mock_get.return_value = mock_response

    result = get_history("token123")

    assert result == mock_response

    mock_get.assert_called_once_with(
        "http://test:8000/v1/emails",
        headers={"Authorization": "Bearer token123"}
    )