import flet as ft

from views.home import build_home


def main(page: ft.Page):

    page.title = "FirstHeat"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    home, refresh = build_home(page)

    page.add(home)
    page.run_task(refresh)


if __name__ == "__main__":
    ft.run(main)
