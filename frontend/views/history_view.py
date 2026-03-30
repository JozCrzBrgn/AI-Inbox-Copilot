import asyncio
import os

import flet as ft
import requests
from components.copyable import copy_to_clipboard
from components.error_snack_bar import show_snack
from components.ui_system import GlassContainer
from services.api import get_history
from views.login_view import LoginView

URL_GITHUB = os.getenv("URL_GITHUB", "https://github.com")


def HistoryView(page: ft.Page, go_to_main):

    token = getattr(page.session, "token", None)
    if not token:
        page.views.clear()
        page.views.append(LoginView(page, go_to_main))
        page.update()
        return ft.View(route="/history", controls=[])

    # State
    all_data      = []
    active_filter = {"field": None, "value": None}
    search_query  = {"text": ""}

    # Table
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Customer")),
            ft.DataColumn(ft.Text("Intent")),
            ft.DataColumn(ft.Text("Priority")),
            ft.DataColumn(ft.Text("Sentiment")),
            ft.DataColumn(ft.Text("Summary")),
            ft.DataColumn(ft.Text("Reply")),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
        border_radius=10,
        vertical_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_800),
        horizontal_lines=ft.BorderSide(1, ft.Colors.BLUE_GREY_800),
        expand=True,
    )

    table_container = GlassContainer(
        content=ft.Column(
            [ft.Row([table], scroll=ft.ScrollMode.AUTO)],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
    )

    loader = ft.ProgressRing(visible=False)

    def apply_filters():
        filtered = all_data[:]

        # Text filter
        q = search_query["text"].strip().lower()
        if q:
            filtered = [
                r for r in filtered
                if any(q in str(v).lower() for v in r.values())
            ]

        # Field filter
        field = active_filter["field"]
        value = active_filter["value"]
        if field and value:
            filtered = [
                r for r in filtered
                if str(r.get(field, "")).lower() == value.lower()
            ]

        table.rows = []

        for r in filtered:
            row_id = r.get("id")

            summary_text = str(r.get("summary", ""))
            reply_text   = str(r.get("reply", ""))

            summary_short = summary_text[:60] + "…" if len(summary_text) > 60 else summary_text
            reply_short   = reply_text[:60]   + "…" if len(reply_text)   > 60 else reply_text

            combined = f"Summary:\n{summary_text}\n\nReply:\n{reply_text}"

            async def handle_copy(e, text=combined):
                await copy_to_clipboard(e, page, text)
                await asyncio.sleep(1)
                e.control.icon = ft.Icons.COPY_ALL_OUTLINED
                e.control.update()

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Text(str(row_id), size=12),
                                ft.IconButton(
                                    icon=ft.Icons.COPY_ALL_OUTLINED,
                                    icon_size=16,
                                    tooltip="Copy Summary and Reply",
                                    on_click=handle_copy,
                                    padding=ft.padding.all(0),
                                ),
                            ], spacing=2, tight=True)
                        ),
                        ft.DataCell(ft.Text(str(r.get("date", "")))),
                        ft.DataCell(ft.Text(str(r.get("customer_name", "")))),
                        ft.DataCell(ft.Text(str(r.get("intent", "")))),
                        ft.DataCell(ft.Text(str(r.get("priority", "")))),
                        ft.DataCell(ft.Text(str(r.get("sentiment", "")))),
                        ft.DataCell(ft.Text(summary_short)),
                        ft.DataCell(ft.Text(reply_short)),
                    ],
                )
            )
        page.update()

    # Searcher
    def on_search(e):
        search_query["text"] = e.control.value or ""
        apply_filters()

    search_field = ft.TextField(
        hint_text="Search...",
        width=300,
        border_radius=10,
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search,
    )

    # Switches: A single dictionary to store all switches per group
    all_switches = {"priority": [], "sentiment": []}

    def make_switch(field: str, val: str) -> ft.Switch:
        """
        Create a switch. When activated:
        - It disables all other switches (from both groups)
        - set active_filter
        When it is deactivated, it cleans the filter.
        """
        sw = ft.Switch(label=val, value=False)

        def on_change(e):
            if e.control.value:
                # Deactivate ALL switches in both groups except this one
                for group in all_switches.values():
                    for s in group:
                        if s is not sw:
                            s.value = False
                active_filter["field"] = field
                active_filter["value"] = val
            else:
                active_filter["field"] = None
                active_filter["value"] = None
            apply_filters()

        sw.on_change = on_change
        return sw

    for v in ["High", "Medium", "Low"]:
        all_switches["priority"].append(make_switch("priority", v))

    for v in ["Positive", "Neutral", "Negative"]:
        all_switches["sentiment"].append(make_switch("sentiment", v))

    # Nav helpers
    def logout(e=None):
        if hasattr(page.session, "token"):
            delattr(page.session, "token")
        page.views.clear()
        page.views.append(LoginView(page, go_to_main))
        page.update()

    def go_back(e):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    def open_github(e):
        asyncio.run_coroutine_threadsafe(
            page.launch_url(URL_GITHUB),
            asyncio.get_event_loop()
        )

    # Load data
    def load_history(e=None):
        loader.visible = True
        table.rows = []
        page.update()
        try:
            res = get_history(getattr(page.session, "token", None))
            if res.status_code == 200:
                all_data.clear()
                all_data.extend(res.json())
                apply_filters()
                show_snack(page, "History loaded!", ft.Colors.GREEN_600)
            elif res.status_code == 401:
                show_snack(page, "Session expired. Please login again.", ft.Colors.RED_400)
                logout()
            elif res.status_code == 429:
                show_snack(page, "Rate limit exceeded.", ft.Colors.ORANGE_400)
            else:
                show_snack(page, f"Error {res.status_code}: {res.text}", ft.Colors.RED_400)
        except requests.exceptions.ConnectionError:
            show_snack(page, "Cannot connect to backend server.", ft.Colors.RED_400)
        except Exception as ex:
            show_snack(page, f"Error: {ex}", ft.Colors.RED_400)
        finally:
            loader.visible = False
            page.update()

    load_history()

    return ft.View(
        route="/history",
        bgcolor="#0F172A",
        controls=[
            ft.Row([
                # Sidebar
                ft.Container(
                    width=90,
                    bgcolor="#1E293B",
                    border_radius=20,
                    content=ft.Column(
                        [
                            ft.IconButton(icon=ft.Icons.ANALYTICS_OUTLINED, icon_size=40, on_click=go_back),
                            ft.IconButton(icon=ft.Icons.TABLE_CHART_OUTLINED, icon_size=40, icon_color="#8B5CF6"),
                            ft.Container(expand=True),
                            ft.IconButton(icon=ft.Icons.LOGOUT, icon_size=40, on_click=logout),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ),

                ft.Container(
                    expand=True,
                    padding=30,
                    content=ft.Column(
                        [
                            ft.Text("Analysis History", size=28, weight="bold"),
                            ft.Container(height=6),

                            # Searcher + reload
                            ft.Row([
                                search_field,
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    tooltip="Recargar",
                                    on_click=load_history,
                                ),
                            ]),

                            # Filters
                            ft.Row(
                                [
                                    ft.Column([
                                        ft.Text("Priority", size=13, color="#94A3B8"),
                                        ft.Row(all_switches["priority"], spacing=10),
                                    ], spacing=5),

                                    ft.Container(width=20),

                                    ft.Column([
                                        ft.Text("Sentiment", size=13, color="#94A3B8"),
                                        ft.Row(all_switches["sentiment"], spacing=10),
                                    ], spacing=5),

                                    ft.Container(expand=True),
                                ],
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                            ),

                            ft.Container(height=10),
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
                        ],
                        spacing=10,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ], expand=True),
        ],
    )