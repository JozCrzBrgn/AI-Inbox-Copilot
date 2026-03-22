from unittest.mock import MagicMock, patch

import pytest

from backend.services.slack import send_slack_alert


@pytest.fixture
def mock_result():
    """Result Base Fixture"""
    return {
        "customer_name": "Juan Pérez",
        "intent": "complaint",
        "sentiment": "negative",
        "summary": "El cliente está molesto por el retraso",
        "suggested_reply": "Lamentamos el retraso, lo revisaremos"
    }


@patch("backend.services.slack.requests.post")
@patch("backend.services.slack.cnf")
def test_send_slack_alert_success(mock_cnf, mock_post, mock_result):
    mock_cnf.slack.slack_webhook_url = "fake-slack-url"
    
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = send_slack_alert(mock_result)

    assert result is True
    mock_post.assert_called_once()


@patch("backend.services.slack.cnf")
def test_send_slack_alert_no_webhook(mock_cnf, mock_result):
    mock_cnf.slack.slack_webhook_url = None

    result = send_slack_alert(mock_result)

    assert result is False


@patch("backend.services.slack.requests.post")
@patch("backend.services.slack.cnf")
def test_send_slack_alert_http_error(mock_cnf, mock_post, mock_result):
    mock_cnf.slack.slack_webhook_url = "fake-slack-url"
    
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_post.return_value = mock_response

    result = send_slack_alert(mock_result)

    assert result is False


@patch("backend.services.slack.requests.post")
@patch("backend.services.slack.cnf")
def test_send_slack_alert_request_exception(mock_cnf, mock_post, mock_result):
    mock_cnf.slack.slack_webhook_url = "fake-slack-url"
    
    mock_post.side_effect = Exception("Connection error")

    result = send_slack_alert(mock_result)

    assert result is False


@patch("backend.services.slack.requests.post")
@patch("backend.services.slack.cnf")
def test_send_slack_alert_payload_content(mock_cnf, mock_post, mock_result):
    mock_cnf.slack.slack_webhook_url = "fake-slack-url"
    
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    send_slack_alert(mock_result)

    args, kwargs = mock_post.call_args

    assert "json" in kwargs
    payload = kwargs["json"]

    assert "Juan Pérez" in payload["text"]
    assert "complaint" in payload["text"]
    assert payload["username"] == "AI Inbox Copilot"
    assert payload["icon_emoji"] == ":robot_face:"