from unittest.mock import MagicMock, patch

from frontend.components.result_card import get_priority_color, result_card


@patch("frontend.components.result_card.ft")
def test_get_priority_color_high(mock_ft):
    mock_ft.Colors.RED_400 = "red"
    assert get_priority_color("high") == "red"


@patch("frontend.components.result_card.ft")
def test_get_priority_color_medium(mock_ft):
    mock_ft.Colors.ORANGE_400 = "orange"
    assert get_priority_color("medium") == "orange"


@patch("frontend.components.result_card.ft")
def test_get_priority_color_default(mock_ft):
    mock_ft.Colors.GREEN_400 = "green"
    assert get_priority_color("anything") == "green"


@patch("frontend.components.result_card.GlassContainer")
@patch("frontend.components.result_card.ft")
def test_result_card(mock_ft, mock_glass):
    # internal mocks
    mock_text1 = MagicMock()
    mock_text2 = MagicMock()
    mock_column = MagicMock()
    mock_glass_instance = MagicMock()

    mock_ft.Text.side_effect = [mock_text1, mock_text2]
    mock_ft.Column.return_value = mock_column
    mock_glass.return_value = mock_glass_instance

    # run
    result = result_card("Title", "Value", "blue")

    # assert return
    assert result == mock_glass_instance

    # verify texts
    mock_ft.Text.assert_any_call(
        "Title",
        size=12,
        color="#94A3B8",
        weight="w500"
    )

    mock_ft.Text.assert_any_call(
        "Value",
        size=20,
        color="blue",
        weight="bold"
    )

    # verify column
    mock_ft.Column.assert_called_once_with(
        [mock_text1, mock_text2],
        spacing=5
    )

    # verify GlassContainer
    mock_glass.assert_called_once_with(
        padding=15,
        content=mock_column
    )