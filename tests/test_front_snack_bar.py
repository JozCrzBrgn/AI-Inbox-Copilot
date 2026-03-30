from unittest.mock import MagicMock, patch

from frontend.components.error_snack_bar import show_snack


@patch("frontend.components.error_snack_bar.ft")
def test_show_snack(mock_ft):

    mock_text = MagicMock()
    mock_ft.Text.return_value = mock_text

    mock_snack = MagicMock()
    mock_ft.SnackBar.return_value = mock_snack

    mock_page = MagicMock()
    mock_page.overlay = []

    # Run function
    show_snack(mock_page, "Error message", color="red")

    # Validations
    mock_ft.Text.assert_called_once_with("Error message")
    mock_ft.SnackBar.assert_called_once_with(
        content=mock_text,
        bgcolor="red",
        duration=3000
    )

    # Verify that it was added to the overlay
    assert mock_snack in mock_page.overlay

    # Check that the snack bar is open
    assert mock_snack.open is True

    # Verify that update was called
    mock_page.update.assert_called_once()