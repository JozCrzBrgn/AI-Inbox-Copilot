import flet as ft


def show_snack(page, message, color=None):
    snack = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=color,
        duration=3000
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()