import asyncio

import flet as ft
from components.error_snack_bar import show_snack
from components.ui_system import GlassContainer


async def copy_to_clipboard(e, page, text):
    clipboard = ft.Clipboard()
    await clipboard.set(text)
    e.control.icon = ft.Icons.CHECK
    e.control.update()
    show_snack(page, "Copied!", ft.Colors.GREEN_600)


def copyable_block(page, title, text):

    async def handle_copy(e):
        await copy_to_clipboard(e, page, text)
        await asyncio.sleep(1)
        e.control.icon = ft.Icons.COPY
        e.control.update()

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text(title, weight="bold", size=18),
                    ft.IconButton(
                        icon=ft.Icons.COPY,
                        tooltip="Copy",
                        icon_color="#94A3B8",
                        on_click=handle_copy
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            GlassContainer(
                padding=15,
                content=ft.SelectionArea(
                    content=ft.Text(text, color="#CBD5E1")
                )
            )
        ],
        spacing=10
    )