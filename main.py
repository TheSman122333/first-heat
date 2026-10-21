#FIRSTHEAT LAUNCHER

import flet as ft

from storage import load_settings, save_settings
from views.home import build_home
from views.plan import build_plan
from views.settings import build_settings


async def main(page: ft.Page):

    page.title = "FirstHeat"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 20

    #load saved settings
    prefs = ft.SharedPreferences()
    settings = await load_settings(prefs)

    async def update_settings(changes):

        await save_settings(prefs, changes)
        settings.update(changes)

    #create screens (preload)
    home, refresh_home = build_home(page, settings)
    plan, refresh_plan = build_plan(page, settings)
    setting_screen = build_settings(page, settings, update_settings)

    screens = [
        home,
        plan,
        setting_screen
    ]

    #navigation
    def navigate(event):

        index = event.control.selected_index

        page.controls.clear()
        page.add(screens[index])

        if index == 0:
            page.run_task(refresh_home)

        elif index == 1:
            page.run_task(refresh_plan)

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                label="Home"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALENDAR_MONTH,
                label="Plan"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                label="Settings"
            )
        ],
        on_change=navigate
    )

    page.add(home)
    page.run_task(refresh_home)


if __name__ == "__main__":
    ft.run(main)
