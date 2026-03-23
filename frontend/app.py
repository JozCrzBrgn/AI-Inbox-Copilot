import flet as ft
from views.login_view import LoginView
from views.main_view import MainView


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK

    def go_to_main(token):
        setattr(page.session, "token", token)
        page.views.clear()
        page.views.append(MainView(page, go_to_main))
        page.update()

    token = getattr(page.session, "token", None)

    if token:
        page.views.append(MainView(page, go_to_main))
    else:
        page.views.append(LoginView(page, go_to_main))

    page.update()


ft.run(
    main=main,
    view=ft.AppView.WEB_BROWSER,
    port=8550,
)