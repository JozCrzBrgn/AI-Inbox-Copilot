import flet as ft


def get_priority_color(priority):
    if priority == "high":
        return ft.Colors.RED_400
    if priority == "medium":
        return ft.Colors.ORANGE_400
    return ft.Colors.GREEN_400


def result_card(title, content, color=None):
    is_dark_bg = color is not None or True

    text_color = ft.Colors.WHITE if is_dark_bg else ft.Colors.BLACK

    return ft.Container(
        content=ft.Column([
            ft.Text(title, weight=ft.FontWeight.BOLD, size=14, color=text_color),
            ft.Text(content, selectable=True, color=text_color)
        ]),
        padding=15,
        border_radius=12,
        bgcolor=color or ft.Colors.BLUE_GREY_900,
        expand=True
    )