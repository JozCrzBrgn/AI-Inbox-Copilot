from unittest.mock import MagicMock, patch

from frontend.views.login_view import LoginView


def setup_ft_mocks(mock_ft):
    """Minimal reusable mockup for Flet"""
    mock_ft.TextField.return_value = MagicMock(value="test", password=True)
    mock_ft.Text.return_value = MagicMock()
    mock_ft.Container.return_value = MagicMock()
    mock_ft.Column.return_value = MagicMock()
    mock_ft.View.return_value = MagicMock()
    mock_ft.Stack.return_value = MagicMock()
    mock_ft.Icon.return_value = MagicMock()
    mock_ft.IconButton.return_value = MagicMock()
    mock_ft.GestureDetector.return_value = MagicMock()
    mock_ft.Alignment.return_value = MagicMock()
    mock_ft.Blur.return_value = MagicMock()
    mock_ft.FontWeight.BOLD = "bold"
    mock_ft.Colors.RED_400 = "red"
    mock_ft.Colors.BLUE_GREY_400 = "bg"
    mock_ft.TextAlign.CENTER = "center"
    mock_ft.CrossAxisAlignment.CENTER = "center"
    mock_ft.MouseCursor.CLICK = "click"
    mock_ft.Icons.PERSON = "person"
    mock_ft.Icons.LOCK = "lock"
    mock_ft.Icons.VISIBILITY = "vis"
    mock_ft.Icons.VISIBILITY_OFF = "vis_off"


@patch("frontend.views.login_view.show_snack")
@patch("frontend.views.login_view.login")
@patch("frontend.views.login_view.PrimaryButton")
@patch("frontend.views.login_view.ft")
def test_login_success(mock_ft, mock_primary_btn, mock_login, mock_snack):
    setup_ft_mocks(mock_ft)

    mock_page = MagicMock()
    mock_page.session = MagicMock()
    mock_login.return_value = "token123"

    captured = {}

    def mock_button(label, on_click):
        captured["login"] = on_click
        return MagicMock()

    mock_primary_btn.side_effect = mock_button

    on_login_success = MagicMock()

    LoginView(mock_page, on_login_success)

    # Run login
    captured["login"](None)

    assert mock_page.session.token == "token123"
    on_login_success.assert_called_once_with("token123")
    mock_snack.assert_not_called()


@patch("frontend.views.login_view.show_snack")
@patch("frontend.views.login_view.login")
@patch("frontend.views.login_view.PrimaryButton")
@patch("frontend.views.login_view.ft")
def test_login_fail(mock_ft, mock_primary_btn, mock_login, mock_snack):
    setup_ft_mocks(mock_ft)

    mock_page = MagicMock()
    mock_page.session = MagicMock()
    mock_login.return_value = None

    captured = {}

    def mock_button(label, on_click):
        captured["login"] = on_click
        return MagicMock()

    mock_primary_btn.side_effect = mock_button

    on_login_success = MagicMock()

    LoginView(mock_page, on_login_success)

    captured["login"](None)

    mock_snack.assert_called_once_with(mock_page, "Invalid credentials", "red")
    on_login_success.assert_not_called()


@patch("frontend.views.login_view.ft")
def test_toggle_password(mock_ft):
    setup_ft_mocks(mock_ft)

    mock_page = MagicMock()

    icon_button_instance = MagicMock()
    captured = {}

    def mock_icon_button(*args, **kwargs):
        captured["toggle"] = kwargs.get("on_click")
        return icon_button_instance

    mock_ft.IconButton.side_effect = mock_icon_button

    LoginView(mock_page, MagicMock())

    # Run toggle
    captured["toggle"](None)

    # Verify that update was called
    mock_page.update.assert_called()


@patch("frontend.views.login_view.asyncio.run_coroutine_threadsafe")
@patch("frontend.views.login_view.asyncio.get_event_loop")
@patch("frontend.views.login_view.ft")
def test_open_github(mock_ft, mock_loop, mock_run_async):
    setup_ft_mocks(mock_ft)

    mock_page = MagicMock()

    captured = {}

    def mock_gesture(*args, **kwargs):
        captured["tap"] = kwargs.get("on_tap")
        return MagicMock()

    mock_ft.GestureDetector.side_effect = mock_gesture

    LoginView(mock_page, MagicMock())

    captured["tap"](None)

    mock_run_async.assert_called_once()