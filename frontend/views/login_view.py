import asyncio
import os

import flet as ft
from components.error_snack_bar import show_snack
from components.ui_system import BG_DARK, TEXT_SECONDARY, GlassContainer, PrimaryButton
from services.api import login

URL_GITHUB = os.getenv("URL_GITHUB", "https://github.com")

def LoginView(page, on_login_success):

    show_password = False

    def toggle_password(e):
        nonlocal show_password
        show_password = not show_password
        password.password = not show_password

        toggle_btn.icon = ft.Icons.VISIBILITY if show_password else ft.Icons.VISIBILITY_OFF

        page.update()

    toggle_btn = ft.IconButton(
        icon=ft.Icons.VISIBILITY_OFF,
        on_click=toggle_password
    )

    username = ft.TextField(
        label="Username", 
        width=300, 
        prefix_icon=ft.Icons.PERSON
    )

    password = ft.TextField(
        label="Password",
        password=True,
        width=300,
        prefix_icon=ft.Icons.LOCK,
        suffix=toggle_btn
    )

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

    # Card
    card = GlassContainer(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.MAIL_OUTLINE, size=50, color="#8B5CF6"),
                ft.Text("AI Inbox Copilot", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Smart Email Management", color=TEXT_SECONDARY),

                username,
                password,

                PrimaryButton("Login", handle_login),

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
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
    )

    # Blobs
    blob1 = ft.Container(
        width=250,
        height=250,
        bgcolor="#3B82F6",
        blur=ft.Blur(120, 120),
        border_radius=200,
        top=-80,
        left=-80,
        opacity=0.35
    )

    blob2 = ft.Container(
        width=200,
        height=200,
        bgcolor="#8B5CF6",
        blur=ft.Blur(120, 120),
        border_radius=150,
        bottom=-60,
        right=-60,
        opacity=0.35
    )

    # Container Card
    card_container = ft.Container(
        width=380,
        content=card
    )

    return ft.View(
        route="/login",
        bgcolor=BG_DARK,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Stack(
                            width=380,
                            height=420,
                            controls=[
                                blob1,
                                blob2,
                                card_container
                            ]
                        )
                    )
                ]
            )
        ]
    )