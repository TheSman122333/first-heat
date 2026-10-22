#FIRSTHEAT LAUNCHER

import flet as ft

from storage import load_settings, save_settings, load_person, save_person
from views.home import build_home
from views.plan import build_plan
from views.my_plan import build_my_plan
from views.settings import build_settings


async def main(page: ft.Page):

    page.title = "FirstHeat"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 20

    #load saved settings
    prefs = ft.SharedPreferences()
    settings = await load_settings(prefs)

    try:
        person = await load_person(prefs)
    except ValueError as error:
        page.add(ft.Text(str(error), color="#991B1B"))
        return

    #save changes
    async def update_settings(changes):
        await save_settings(prefs, changes)
        settings.update(changes)

    async def update_person(changes):
        await save_person(prefs, changes)
        person.update(changes)

    #create pages
    home, refresh_home = build_home(page, settings)
    weekly, refresh_weekly = build_plan(page, settings)
    my_plan, refresh_my_plan = build_my_plan(page, settings, person, update_person)
    settings_page = build_settings(page, settings, update_settings)

    screens = [home, weekly, my_plan, settings_page]
    refreshers = {
        0: refresh_home,
        1: refresh_weekly,
        2: refresh_my_plan
    }
    
    #navigation
    def navigate(event):

        index = event.control.selected_index

        page.controls.clear()
        page.add(screens[index])

        if index in refreshers:
            page.run_task(refreshers[index])

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                label="Home"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALENDAR_MONTH,
                label="Weekly"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.EVENT_NOTE_OUTLINED,
                label="My plan"
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
