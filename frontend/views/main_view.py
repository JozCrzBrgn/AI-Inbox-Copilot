import asyncio
import os
import threading

import flet as ft
import requests
from components.error_snack_bar import show_snack
from components.result_card import get_priority_color, result_card
from services.api import analyze
from views.history_view import HistoryView
from views.login_view import LoginView

URL_GITHUB = os.getenv("URL_GITHUB", "https://github.com")


def MainView(page, go_to_main):
    email_input = ft.TextField(multiline=True, min_lines=8, expand=True)

    loader = ft.ProgressRing(visible=False)

    results = ft.Column(visible=False, spacing=20)

    def open_github(e):
        asyncio.run_coroutine_threadsafe(
            page.launch_url(URL_GITHUB),
            asyncio.get_event_loop()
        )

    def go_to_history(e):
        page.views[:] = [v for v in page.views if getattr(v, "route", None) != "/history"]
        page.views.append(HistoryView(page, go_to_main))
        page.update()

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

    def run_analysis(e):
        # Show loader
        loader.visible = True
        results.visible = False
        page.update()

        def task():
            try:
                token = getattr(page.session, "token", None)
                res = analyze(email_input.value, token)

                if res.status_code == 200:
                    data = res.json()
                    priority = data.get("priority", "")

                    results.controls = [
                        ft.Row([
                            result_card("Priority", priority, get_priority_color(priority)),
                            result_card("Sentiment", data.get("sentiment", ""))
                        ], spacing=20),
                        result_card("Summary", data.get("summary", "")),
                        result_card("Suggested Subject", data.get("suggested_subject", "")),
                        result_card("Suggested Reply", data.get("suggested_reply", "")),
                    ]

                    results.visible = True
                    show_snack(page, "Analysis complete!", ft.Colors.GREEN_600)

                elif res.status_code == 429:
                    show_snack(page, "Rate limit exceeded. Please wait a moment and try again.", ft.Colors.ORANGE_400)
                
                else:
                    show_snack(page, f"Error {res.status_code}: {res.text}", ft.Colors.RED_400)
            
            except requests.exceptions.ConnectionError as e: 
                show_snack(page, f"Cannot connect to backend server: {e}", ft.Colors.RED_400)
            except Exception as ex:
                show_snack(page, f"Error: {ex}", ft.Colors.RED_400)
            finally:
                loader.visible = False
                page.update()

        # Run in a separate thread
        threading.Thread(target=task).start()

    return ft.View(
        route="/main",
        appbar=ft.AppBar(
            title=ft.Text("AI Inbox Copilot"),
            actions=[
                ft.IconButton(icon=ft.Icons.DARK_MODE, on_click=toggle_theme),
                ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)
            ]
        ),
        controls=[
            ft.Column([
                email_input,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Analyze",
                            on_click=run_analysis,
                            icon=ft.Icons.SEARCH,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE
                            )
                        ),
                        ft.ElevatedButton(
                            "History",
                            on_click=go_to_history,
                            icon=ft.Icons.HISTORY,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_GREY_700,
                                color=ft.Colors.WHITE
                            )
                        ),
                    ], 
                    spacing=15
                ),
                loader,
                results,
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
            ], spacing=25, expand=True)
        ]
    )