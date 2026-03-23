import asyncio
import os

import flet as ft
from components.error_snack_bar import show_snack
from services.api import login

URL_GITHUB = os.getenv("URL_GITHUB", "https://github.com")


def LoginView(page, on_login_success):
    username = ft.TextField(label="Username", width=300, prefix_icon=ft.Icons.PERSON)
    password = ft.TextField(label="Password", password=True, width=300, prefix_icon=ft.Icons.LOCK)

    page.theme_mode = ft.ThemeMode.DARK
    page.update()

    def open_github(e):
        asyncio.run_coroutine_threadsafe(
            page.launch_url(URL_GITHUB),
            asyncio.get_event_loop()
        )

    def handle_login(e):
        token = login(username.value, password.value)
        if token:
            page.session.token = token
            on_login_success(token)
        else:
            show_snack(page, "Invalid credentials", ft.Colors.RED_400)

    card = ft.Container(
        content=ft.Column([
            ft.Text("AI Inbox Copilot", size=24, weight=ft.FontWeight.BOLD),
            username,
            password,
            ft.ElevatedButton("Login", on_click=handle_login, width=300),
            ft.Divider(color=ft.Colors.BLUE_GREY_700),
            ft.GestureDetector(
                on_tap=open_github,
                content=ft.Text(
                    "Made with ❤️ by Josue Cruz",
                    size=12,
                    color=ft.Colors.BLUE_GREY_400,
                    text_align=ft.TextAlign.CENTER
                ),
                mouse_cursor=ft.MouseCursor.CLICK
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=30,
        border_radius=15,
        bgcolor=ft.Colors.BLUE_GREY_900,
        width=350
    )

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [card],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0)
            )
        ]
    )