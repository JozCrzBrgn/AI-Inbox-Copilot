from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from frontend.components.copyable import copy_to_clipboard, copyable_block


@pytest.mark.asyncio
@patch("frontend.components.copyable.show_snack")
@patch("frontend.components.copyable.ft.Clipboard")
async def test_copy_to_clipboard(mock_clipboard_class, mock_show_snack):
    # Mock clipboard
    mock_clipboard = AsyncMock()
    mock_clipboard_class.return_value = mock_clipboard

    # Mock event y control
    mock_control = MagicMock()
    mock_event = MagicMock()
    mock_event.control = mock_control

    mock_page = MagicMock()
    text = "test text"

    await copy_to_clipboard(mock_event, mock_page, text)

    # Assertions
    mock_clipboard.set.assert_awaited_once_with(text)
    assert mock_control.icon is not None
    mock_control.update.assert_called_once()
    mock_show_snack.assert_called_once()


def test_copyable_block_structure():
    page = object()
    title = "My Title"
    text = "My text"

    result = copyable_block(page, title, text)

    # It is a Column
    assert result is not None
    assert hasattr(result, "controls")

    # It has 2 elements: Row + GlassContainer
    assert len(result.controls) == 2


@pytest.mark.asyncio
@patch("frontend.components.copyable.asyncio.sleep", new_callable=AsyncMock)
@patch("frontend.components.copyable.copy_to_clipboard", new_callable=AsyncMock)
async def test_handle_copy(mock_copy, mock_sleep):
    page = MagicMock()
    title = "Title"
    text = "Text"

    column = copyable_block(page, title, text)

    # Get button
    row = column.controls[0]
    button = row.controls[1]

    # Event mock
    mock_control = MagicMock()
    event = MagicMock()
    event.control = mock_control

    # Run handler
    await button.on_click(event)

    # Assertions
    mock_copy.assert_awaited_once()
    mock_sleep.assert_awaited_once_with(1)
    assert mock_control.icon is not None
    mock_control.update.assert_called()