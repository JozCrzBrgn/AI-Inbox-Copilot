from unittest.mock import MagicMock, patch

import requests

from frontend.views.main_view import MainView


def make_ft_mocks(mock_ft):
    """Minimal reusable mockup for Flet"""
    mock_ft.TextField.return_value = MagicMock(value="email")
    mock_ft.ProgressRing.return_value = MagicMock(visible=False)
    mock_ft.Column.return_value = MagicMock()
    mock_ft.Row.return_value = MagicMock()
    mock_ft.Container.return_value = MagicMock()
    mock_ft.View.return_value = MagicMock()
    mock_ft.AppBar.return_value = MagicMock()
    mock_ft.IconButton.return_value = MagicMock()
    mock_ft.GestureDetector.return_value = MagicMock()
    mock_ft.ButtonStyle.return_value = MagicMock()
    mock_ft.Text.return_value = MagicMock()
    mock_ft.Colors.GREEN_600 = "green"
    mock_ft.Colors.BLUE_600 = "blue"
    mock_ft.Colors.WHITE = "white"
    mock_ft.Colors.BLUE_GREY_700 = "bg"
    mock_ft.Colors.BLUE_GREY_400 = "bg3"
    mock_ft.Colors.ORANGE_400 = "orange"
    mock_ft.Colors.RED_400 = "red"
    mock_ft.ThemeMode.DARK = "dark"
    mock_ft.TextAlign.CENTER = "center"
    mock_ft.MouseCursor.CLICK = "click"
    mock_ft.Icons.SEARCH = "search"
    mock_ft.Icons.HISTORY = "history"
    mock_ft.Icons.TABLE_CHART_OUTLINED = "history"
    mock_ft.Icons.DARK_MODE = "dark_mode"
    mock_ft.Icons.LOGOUT = "logout"


def make_fake_thread():
    def fake_thread(*args, **kwargs):
        obj = MagicMock()
        target = kwargs.get("target") or (args[0] if args else None)
        obj.start = lambda: target()
        return obj
    return fake_thread


def capture_analyze_button():
    btn = MagicMock()
    btn.on_click = None

    def capture(text, on_click):
        btn.on_click = on_click
        return MagicMock()

    return btn, capture


@patch("frontend.views.main_view.threading.Thread")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.show_snack")
@patch("frontend.views.main_view.get_priority_color")
@patch("frontend.views.main_view.result_card")
@patch("frontend.views.main_view.analyze")
@patch("frontend.views.main_view.ft")
def test_main_analysis_success(
    mock_ft,
    mock_analyze,
    mock_card,
    mock_color,
    mock_snack,
    mock_primary_btn,
    mock_thread,
):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "priority": "high",
        "sentiment": "positive",
        "summary": "summary",
        "suggested_subject": "subject",
        "suggested_reply": "reply"
    }

    mock_analyze.return_value = mock_res
    mock_thread.side_effect = make_fake_thread()
    make_ft_mocks(mock_ft)

    btn, capture = capture_analyze_button()
    mock_primary_btn.side_effect = capture

    MainView(mock_page, MagicMock())

    assert btn.on_click is not None
    btn.on_click(None)

    mock_snack.assert_called_with(mock_page, "Analysis complete!", "green")


@patch("frontend.views.main_view.threading.Thread")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.show_snack")
@patch("frontend.views.main_view.analyze")
@patch("frontend.views.main_view.ft")
def test_main_analysis_429(
    mock_ft,
    mock_analyze,
    mock_snack,
    mock_primary_btn,
    mock_thread,
):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")

    mock_res = MagicMock(status_code=429)
    mock_analyze.return_value = mock_res

    mock_thread.side_effect = make_fake_thread()
    make_ft_mocks(mock_ft)

    btn, capture = capture_analyze_button()
    mock_primary_btn.side_effect = capture

    MainView(mock_page, MagicMock())

    btn.on_click(None)

    mock_snack.assert_called_with(
        mock_page,
        "Rate limit exceeded. Please wait a moment and try again.",
        "orange"
    )


@patch("frontend.views.main_view.threading.Thread")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.show_snack")
@patch("frontend.views.main_view.analyze")
@patch("frontend.views.main_view.ft")
def test_main_connection_error(
    mock_ft,
    mock_analyze,
    mock_snack,
    mock_primary_btn,
    mock_thread,
):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")

    mock_analyze.side_effect = requests.exceptions.ConnectionError("fail")

    mock_thread.side_effect = make_fake_thread()
    make_ft_mocks(mock_ft)

    btn, capture = capture_analyze_button()
    mock_primary_btn.side_effect = capture

    MainView(mock_page, MagicMock())

    btn.on_click(None)

    mock_snack.assert_called()


@patch("frontend.views.main_view.LoginView")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.ft")
def test_main_logout(mock_ft, mock_primary_btn, mock_login_view):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")
    mock_page.views = []

    btn_logout = MagicMock()

    def mock_icon(*args, **kwargs):
        if kwargs.get("on_click"):
            btn_logout.on_click = kwargs["on_click"]
        return MagicMock()

    mock_ft.IconButton.side_effect = mock_icon
    make_ft_mocks(mock_ft)

    MainView(mock_page, MagicMock())

    btn_logout.on_click(None)

    assert not hasattr(mock_page.session, "token")
    mock_login_view.assert_called()


@patch("frontend.views.main_view.threading.Thread")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.show_snack")
@patch("frontend.views.main_view.analyze")
@patch("frontend.views.main_view.ft")
def test_main_analysis_other_error(
    mock_ft,
    mock_analyze,
    mock_snack,
    mock_primary_btn,
    mock_thread,
):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")

    mock_res = MagicMock(status_code=500, text="server error")
    mock_analyze.return_value = mock_res

    mock_thread.side_effect = make_fake_thread()
    make_ft_mocks(mock_ft)

    btn, capture = capture_analyze_button()
    mock_primary_btn.side_effect = capture

    MainView(mock_page, MagicMock())

    btn.on_click(None)

    mock_snack.assert_called_with(
        mock_page,
        "Error 500: server error",
        "red"
    )


@patch("frontend.views.main_view.threading.Thread")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.show_snack")
@patch("frontend.views.main_view.analyze")
@patch("frontend.views.main_view.ft")
def test_main_generic_exception(
    mock_ft,
    mock_analyze,
    mock_snack,
    mock_primary_btn,
    mock_thread,
):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")

    mock_analyze.side_effect = Exception("boom")

    mock_thread.side_effect = make_fake_thread()
    make_ft_mocks(mock_ft)

    btn, capture = capture_analyze_button()
    mock_primary_btn.side_effect = capture

    MainView(mock_page, MagicMock())

    btn.on_click(None)

    mock_snack.assert_called()


@patch("frontend.views.main_view.HistoryView")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.ft")
def test_go_to_history(mock_ft, mock_primary_btn, mock_history_view):
    mock_page = MagicMock()
    mock_page.views = [MagicMock(route="/history"), MagicMock(route="/other")]

    btn_history = MagicMock()

    def mock_icon(*args, **kwargs):
        if kwargs.get("icon") == mock_ft.Icons.TABLE_CHART_OUTLINED:
            btn_history.on_click = kwargs.get("on_click")
        return MagicMock()

    mock_ft.IconButton.side_effect = mock_icon
    make_ft_mocks(mock_ft)

    MainView(mock_page, MagicMock())

    assert btn_history.on_click is not None
    btn_history.on_click(None)

    mock_history_view.assert_called()
    assert mock_page.update.called


@patch("frontend.views.main_view.asyncio.run_coroutine_threadsafe")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.asyncio.get_event_loop")
@patch("frontend.views.main_view.ft")
def test_open_github(mock_ft, mock_loop, mock_primary_btn, mock_async):
    mock_page = MagicMock()

    gesture = MagicMock()

    def mock_gesture(*args, **kwargs):
        gesture.on_tap = kwargs.get("on_tap")
        return MagicMock()

    mock_ft.GestureDetector.side_effect = mock_gesture
    make_ft_mocks(mock_ft)

    MainView(mock_page, MagicMock())

    gesture.on_tap(None)

    mock_async.assert_called()


@patch("frontend.views.main_view.threading.Thread")
@patch("frontend.views.main_view.PrimaryButton")
@patch("frontend.views.main_view.show_snack")
@patch("frontend.views.main_view.analyze")
@patch("frontend.views.main_view.ft")
def test_main_missing_fields(
    mock_ft,
    mock_analyze,
    mock_snack,
    mock_primary_btn,
    mock_thread,
):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {}

    mock_analyze.return_value = mock_res
    mock_thread.side_effect = make_fake_thread()
    make_ft_mocks(mock_ft)

    btn, capture = capture_analyze_button()
    mock_primary_btn.side_effect = capture

    MainView(mock_page, MagicMock())

    btn.on_click(None)

    mock_snack.assert_called_with(mock_page, "Analysis complete!", "green")