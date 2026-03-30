import asyncio
import os
import threading

import flet as ft
import requests
from components.copyable import copyable_block
from components.error_snack_bar import show_snack
from components.result_card import get_priority_color, result_card
from components.ui_system import GlassContainer, PrimaryButton
from services.api import analyze
from views.history_view import HistoryView
from views.login_view import LoginView

URL_GITHUB = os.getenv("URL_GITHUB", "https://github.com")


def MainView(page, go_to_main):
    email_input = ft.TextField(
                    hint_text="Paste the email content here...",
                    multiline=True, min_lines=5, max_lines=5,
                    border=ft.InputBorder.NONE,
                    color="white",
                    expand=True
                )

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

    def run_analysis(e):
        loader.visible = True
        results.visible = False
        page.update()

        def task():
            try:
                token = getattr(page.session, "token", None)
                res = analyze(email_input.value, token)

                if res.status_code == 200:

                    data = res.json()
                    sentiment = data.get("sentiment", "")
                    priority = data.get("priority", "")

                    sentiment_emoji = {
                        "positive": "😊",
                        "neutral": "😐", 
                        "negative": "😞"
                    }.get(sentiment.lower(), "")
                    sentiment_text = f"{sentiment_emoji} {sentiment.capitalize()}" if sentiment_emoji else sentiment
                    
                    priority_emoji = {
                        "low": "🟢",
                        "medium": "🟡", 
                        "high": "🔴"
                    }.get(priority.lower(), "")
                    priority_text = f"{priority_emoji} {priority.capitalize()}" if priority_emoji else priority.capitalize()

                    results.controls = [
                        ft.Row(
                            [
                                result_card("Priority", priority_text, get_priority_color(priority)),
                                result_card("Sentiment", sentiment_text, get_priority_color(priority)),
                                result_card("Summary", data.get("summary", ""), get_priority_color(priority)),
                            ], 
                            spacing=20,
                            expand=True,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START
                        ),
                        ft.Row(
                            [
                                copyable_block(page, "Suggested Subject", data.get("suggested_subject", "")),
                                copyable_block(page, "Suggested Reply", data.get("suggested_reply", ""))
                            ],
                            spacing=50,
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.START
                        )
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

        threading.Thread(target=task).start()

    return ft.View(
        route="/main",
        bgcolor="#0F172A",
        controls=[
            ft.Row([
                # Sidebar
                ft.Container(
                    width=90,
                    bgcolor="#1E293B",
                    border_radius=20,
                    content=ft.Column([
                        ft.IconButton(
                            icon=ft.Icons.ANALYTICS_OUTLINED,
                            icon_size=40,
                            icon_color="#8B5CF6",
                            on_click=lambda e: None
                        ),
                        ft.IconButton(
                            icon=ft.Icons.TABLE_CHART_OUTLINED,
                            icon_size=40,
                            on_click=go_to_history
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_size=40,
                            on_click=logout
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20)
                ),

                ft.Container(
                    expand=True,
                    padding=30,
                    content=ft.Column([
                        ft.Text("Email Intelligence", size=28, weight="bold"),

                        ft.Container(height=20),

                        GlassContainer(
                            content=ft.Column([
                                email_input,
                                ft.Row([
                                    PrimaryButton("Analyze with AI", run_analysis),
                                ], 
                                alignment=ft.MainAxisAlignment.START)
                            ])
                        ),

                        ft.Container(height=20),

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
                    ],
                    spacing=20)
                )
            ], expand=True)
        ]
    )