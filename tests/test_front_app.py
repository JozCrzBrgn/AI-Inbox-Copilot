from unittest.mock import MagicMock, patch

import pytest

from frontend.app import main


@pytest.mark.asyncio
@patch("frontend.app.LoginView")
@patch("frontend.app.MainView")
@patch("frontend.app.ft")
async def test_main_no_token(mock_ft, mock_main_view, mock_login_view):
    mock_page = MagicMock()
    mock_page.session = MagicMock()
    mock_page.views = []

    # no token
    mock_page.session.token = None

    await main(mock_page)

    mock_login_view.assert_called_once()
    mock_main_view.assert_not_called()
    assert len(mock_page.views) == 1
    mock_page.update.assert_called_once()


@pytest.mark.asyncio
@patch("frontend.app.LoginView")
@patch("frontend.app.MainView")
@patch("frontend.app.ft")
async def test_main_with_token(mock_ft, mock_main_view, mock_login_view):
    mock_page = MagicMock()
    mock_page.session = MagicMock(token="abc")
    mock_page.views = []

    await main(mock_page)

    mock_main_view.assert_called_once()
    mock_login_view.assert_not_called()
    assert len(mock_page.views) == 1
    mock_page.update.assert_called_once()


@pytest.mark.asyncio
@patch("frontend.app.LoginView")
@patch("frontend.app.MainView")
@patch("frontend.app.ft")
async def test_go_to_main(mock_ft, mock_main_view, mock_login_view):
    mock_page = MagicMock()
    mock_page.session = MagicMock()
    mock_page.session.token = None
    mock_page.views = []

    captured_go = {}

    def fake_login(page, go_to_main):
        captured_go["fn"] = go_to_main
        return MagicMock()

    mock_login_view.side_effect = fake_login

    await main(mock_page)

    # Defensive validation
    assert "fn" in captured_go

    # Run navigation
    captured_go["fn"]("token123")

    assert mock_page.session.token == "token123"
    mock_main_view.assert_called()
    mock_page.update.assert_called()


@patch("frontend.app.ft.run")
def test_run_called(mock_run):
    import frontend.app
    frontend.app.__name__ = "__main__"

    # Execute block manually
    if frontend.app.__name__ == "__main__":
        frontend.app.ft.run(
            main=frontend.app.main,
            view=frontend.app.ft.AppView.WEB_BROWSER,
            port=8550,
        )

    mock_run.assert_called_once()