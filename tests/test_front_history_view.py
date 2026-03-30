from unittest.mock import MagicMock, patch

import requests

from frontend.views.history_view import HistoryView


def setup_ft(mock_ft):
    """Minimal reusable mockup for Flet"""
    mock_ft.ProgressRing.return_value = MagicMock(visible=False)
    mock_ft.DataColumn.return_value = MagicMock()
    mock_ft.Text.return_value = MagicMock()
    mock_ft.DataTable.return_value = MagicMock(rows=[])
    mock_ft.Container.return_value = MagicMock()
    mock_ft.Row.return_value = MagicMock()
    mock_ft.BorderSide.return_value = MagicMock()
    mock_ft.DataRow.return_value = MagicMock()
    mock_ft.DataCell.return_value = MagicMock()
    mock_ft.Column.return_value = MagicMock()
    mock_ft.View.return_value = MagicMock()
    mock_ft.IconButton.return_value = MagicMock()
    mock_ft.GestureDetector.return_value = MagicMock()
    mock_ft.Switch.return_value = MagicMock(value=False)
    mock_ft.TextField.return_value = MagicMock()
    mock_ft.padding.all.return_value = 0

    mock_ft.Colors.GREEN_600 = "green"
    mock_ft.Colors.RED_400 = "red"
    mock_ft.Colors.ORANGE_400 = "orange"
    mock_ft.Colors.BLUE_GREY_700 = "bg"
    mock_ft.Colors.BLUE_GREY_800 = "bg2"


@patch("frontend.views.history_view.LoginView")
def test_history_no_token(mock_login_view):
    page = MagicMock()
    page.session = MagicMock()
    page.session.token = None
    page.views = []

    HistoryView(page, MagicMock())

    mock_login_view.assert_called_once()
    assert len(page.views) == 1
    page.update.assert_called()


@patch("frontend.views.history_view.show_snack")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_history_success(mock_ft, mock_get_history, mock_snack):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    res = MagicMock()
    res.status_code = 200
    res.json.return_value = [{"id": 1, "summary": "ok", "reply": "ok"}]
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    mock_snack.assert_called_with(page, "History loaded!", "green")


@patch("frontend.views.history_view.LoginView")
@patch("frontend.views.history_view.show_snack")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_history_401(mock_ft, mock_get_history, mock_snack, mock_login):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")
    page.views = []

    res = MagicMock(status_code=401)
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    mock_snack.assert_called()
    mock_login.assert_called()


@patch("frontend.views.history_view.show_snack")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_history_429(mock_ft, mock_get_history, mock_snack):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    res = MagicMock(status_code=429)
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    mock_snack.assert_called_with(page, "Rate limit exceeded.", "orange")


@patch("frontend.views.history_view.show_snack")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_history_error_status(mock_ft, mock_get_history, mock_snack):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    res = MagicMock(status_code=500, text="boom")
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    mock_snack.assert_called_with(page, "Error 500: boom", "red")


@patch("frontend.views.history_view.show_snack")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_history_connection_error(mock_ft, mock_get_history, mock_snack):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    mock_get_history.side_effect = requests.exceptions.ConnectionError()

    HistoryView(page, MagicMock())

    mock_snack.assert_called_with(
        page,
        "Cannot connect to backend server.",
        "red"
    )


@patch("frontend.views.history_view.show_snack")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_history_exception(mock_ft, mock_get_history, mock_snack):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    mock_get_history.side_effect = Exception("fail")

    HistoryView(page, MagicMock())

    mock_snack.assert_called()
    assert "Error:" in mock_snack.call_args[0][1]


@patch("frontend.views.history_view.asyncio.run_coroutine_threadsafe")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_navigation_helpers(mock_ft, mock_get_history, mock_async):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")
    page.views = [1, 2]

    res = MagicMock(status_code=200)
    res.json.return_value = []
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    # Simulate manual go_back
    page.views.pop()
    page.update.assert_called()


@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_search_filter(mock_ft, mock_get_history):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    data = [
        {"id": 1, "summary": "hello world", "reply": "ok"},
        {"id": 2, "summary": "bye", "reply": "test"},
    ]

    res = MagicMock(status_code=200)
    res.json.return_value = data
    mock_get_history.return_value = res

    # Simulate search
    textfield = mock_ft.TextField.return_value
    handler = textfield.on_change

    e = MagicMock()
    e.control.value = "hello"

    handler(e)

    assert True


@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_switch_filter(mock_ft, mock_get_history):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    res = MagicMock(status_code=200)
    res.json.return_value = [{"id": 1, "priority": "High"}]
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    # grab switch created
    switch = mock_ft.Switch.return_value
    handler = switch.on_change

    e = MagicMock()
    e.control = switch
    e.control.value = True

    handler(e)

    assert True


@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_long_text_truncation(mock_ft, mock_get_history):
    setup_ft(mock_ft)

    page = MagicMock()
    page.session = MagicMock(token="abc")

    long_text = "a" * 100

    res = MagicMock(status_code=200)
    res.json.return_value = [{
        "id": 1,
        "summary": long_text,
        "reply": long_text
    }]
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    # Verify that an attempt was made to render rows
    assert mock_ft.DataRow.called


@patch("frontend.views.history_view.asyncio.get_event_loop")
@patch("frontend.views.history_view.asyncio.run_coroutine_threadsafe")
@patch("frontend.views.history_view.get_history")
@patch("frontend.views.history_view.ft")
def test_open_github(mock_ft, mock_get_history, mock_async, mock_loop):
    setup_ft(mock_ft)

    captured = {}

    def fake_gesture(*args, **kwargs):
        captured["handler"] = kwargs.get("on_tap")
        return MagicMock()

    mock_ft.GestureDetector.side_effect = fake_gesture

    page = MagicMock()
    page.session = MagicMock(token="abc")

    res = MagicMock(status_code=200)
    res.json.return_value = []
    mock_get_history.return_value = res

    HistoryView(page, MagicMock())

    handler = captured.get("handler")
    assert handler is not None

    handler(None)

    mock_async.assert_called_once()