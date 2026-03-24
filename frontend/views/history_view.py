import asyncio
import os
import threading

import flet as ft
import requests
from components.error_snack_bar import show_snack
from services.api import get_history
from views.login_view import LoginView

URL_GITHUB = os.getenv("URL_GITHUB", "https://github.com")

def HistoryView(page, go_to_main):
    # Redirigir si no está logueado
    token = getattr(page.session, "token", None)
    if not token:
        page.views.clear()
        page.views.append(LoginView(page, go_to_main))
        page.update()
        return

    loader = ft.ProgressRing(visible=False)

    columns = [
        ft.DataColumn(ft.Text("ID")),
        ft.DataColumn(ft.Text("Date")),
        ft.DataColumn(ft.Text("Customer")),
        ft.DataColumn(ft.Text("Intent")),
        ft.DataColumn(ft.Text("Priority")),
        ft.DataColumn(ft.Text("Sentiment")),
        ft.DataColumn(ft.Text("Summary")),
        ft.DataColumn(ft.Text("Reply")),
    ]

    table = ft.DataTable(
        columns=columns,
        rows=[],
        border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
        border_radius=10,
        vertical_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_800),
        horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_800),
        expand=True,
    )

    table_container = ft.Container(
        content=ft.Row([table], scroll=ft.ScrollMode.AUTO),
        expand=True,
    )

    def open_github(e):
        asyncio.run_coroutine_threadsafe(
            page.launch_url(URL_GITHUB),
            asyncio.get_event_loop()
        )

    def logout(e):
        if hasattr(page.session, "token"):
            delattr(page.session, "token")
        page.views.clear()
        page.views.append(LoginView(page, go_to_main))
        page.update()

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        page.update()

    def go_back(e):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    def load_history(e=None):
        loader.visible = True
        table.rows = []
        page.update()

        def task():
            try:
                res = get_history(getattr(page.session, "token", None))

                if res.status_code == 200:
                    data = res.json()
                    table.rows = [
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(row.get("id", "")))),
                            ft.DataCell(ft.Text(str(row.get("date", "")))),
                            ft.DataCell(ft.Text(str(row.get("customer_name", "")))),
                            ft.DataCell(ft.Text(str(row.get("intent", "")))),
                            ft.DataCell(ft.Text(str(row.get("priority", "")))),
                            ft.DataCell(ft.Text(str(row.get("sentiment", "")))),
                            ft.DataCell(ft.SelectionArea(content=ft.Text(str(row.get("summary", ""))))),
                            ft.DataCell(ft.SelectionArea(content=ft.Text(str(row.get("reply", ""))))),
                        ])
                        for row in data
                    ]
                    show_snack(page, "History loaded!", ft.Colors.GREEN_600)

                elif res.status_code == 401:
                    show_snack(page, "Session expired. Please login again.", ft.Colors.RED_400)
                    logout(None)

                elif res.status_code == 429:
                    show_snack(page, "Rate limit exceeded. Please wait a moment and try again.", ft.Colors.ORANGE_400)

                else:
                    show_snack(page, f"Error {res.status_code}: {res.text}", ft.Colors.RED_400)

            except requests.exceptions.ConnectionError:
                show_snack(page, "Cannot connect to backend server.", ft.Colors.RED_400)
            except Exception as ex:
                show_snack(page, f"Error: {ex}", ft.Colors.RED_400)
            finally:
                loader.visible = False
                page.update()

        threading.Thread(target=task).start()

    # Cargar historial al entrar
    load_history()

    return ft.View(
        route="/history",
        appbar=ft.AppBar(
            title=ft.Text("AI Inbox Copilot — History"),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
            actions=[
                ft.IconButton(icon=ft.Icons.REFRESH, on_click=load_history, tooltip="Refresh"),
                ft.IconButton(icon=ft.Icons.DARK_MODE, on_click=toggle_theme),
                ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout),
            ]
        ),
        controls=[
            ft.Column([
                loader,
                table_container,
                ft.Container(expand=True),
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
            ], expand=True, spacing=20)
        ],
        scroll=ft.ScrollMode.AUTO
    )