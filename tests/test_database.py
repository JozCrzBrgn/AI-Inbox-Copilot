from unittest.mock import MagicMock, patch

import pytest

from backend.services.database import (
    get_all_emails,
    get_connection,
    init_database,
    save_email,
)


@patch("backend.services.database.psycopg2.connect")
def test_get_connection(mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    conn = get_connection()

    assert conn == mock_conn
    mock_connect.assert_called_once()


@patch("backend.services.database.psycopg2.connect")
def test_init_database(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    init_database()

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("backend.services.database.psycopg2.connect")
def test_save_email(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    save_email("Juan", "complaint", "high", "negative", "summary", "reply")

    mock_cursor.execute.assert_called_once()

    args, kwargs = mock_cursor.execute.call_args

    assert "INSERT INTO emails" in args[0]
    assert args[1] == ("Juan", "complaint", "high", "negative", "summary", "reply")

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("backend.services.database.psycopg2.connect")
def test_get_all_emails(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    mock_date = MagicMock()
    mock_date.isoformat.return_value = "2024-01-01T00:00:00"

    mock_cursor.fetchall.return_value = [
        (1, mock_date, "Juan", "complaint", "high", "negative", "summary", "reply")
    ]

    result = get_all_emails()

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["date"] == "2024-01-01T00:00:00"
    assert result[0]["customer_name"] == "Juan"


@patch("backend.services.database.psycopg2.connect")
def test_get_all_emails_date_none(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        (1, None, "Juan", "complaint", "high", "negative", "summary", "reply")
    ]

    result = get_all_emails()

    assert result[0]["date"] is None


@patch("backend.services.database.psycopg2.connect")
def test_save_email_exception(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    mock_cursor.execute.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        save_email("Juan", "intent", "high", "neg", "sum", "reply")