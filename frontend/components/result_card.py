import flet as ft
from components.ui_system import GlassContainer


def get_priority_color(priority):
    if priority == "high":
        return ft.Colors.RED_400
    if priority == "medium":
        return ft.Colors.ORANGE_400
    return ft.Colors.GREEN_400

def result_card(title, value, color):
        return GlassContainer(
            padding=15,
            content=ft.Column([
                ft.Text(title, size=12, color="#94A3B8", weight="w500"),
                ft.Text(value, size=20, color=color, weight="bold"),
            ], spacing=5)
        )