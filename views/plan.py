
"Plan: seven days of lower-heat forecast windows"

import asyncio
import flet as ft

from core.plan import fetch_week_plan


COLORS = {
    "green": "#166534",
    "yellow": "#795500",
    "orange": "#9A3412",
    "red": "#991B1B",
    "black": "#1F2937"
}


def build_plan(page, settings):

    location = ft.Text("", color="#64748B")
    spinner = ft.ProgressRing(width=20, height=20, visible=False)
    status = ft.Text("", color="#64748B")

    rows = ft.Column(spacing=10)

    refresh_button = ft.Button(
        content="Refresh plan",
        icon=ft.Icons.REFRESH
    )

    busy = False

    async def refresh(_event=None):
        nonlocal busy

        if busy:
            return

        busy = True
        spinner.visible = True
        refresh_button.disabled = True
        rows.controls.clear()
        status.value = "Loading seven-day forecast..."

        location.value = (
            f"{settings['name']}, {settings['state']} "
            f"· Region {settings['region']}"
        )

        page.update()

        try:
            #fetch and calculate outside the UI thread
            week = await asyncio.to_thread(
                fetch_week_plan,
                settings.copy()
            )

            for day in week:

                peak_f = day["peak_wbgt"] * 9 / 5 + 32
                level = day["peak_category"]
                window = day["window"]

                if window:
                    start, end = window
                    window_text = (
                        f"Lower heat: {start:%I %p}–{end:%I %p}"
                    )
                else:
                    window_text = "No lower-heat daytime window forecast"

                rows.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        border_radius=14,
                        padding=16,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"{day['date']:%a, %b %d}",
                                    weight=ft.FontWeight.BOLD,
                                    size=17
                                ),
                                ft.Text(
                                    f"Peak: {peak_f:.1f} °F · {level.title()}",
                                    color=COLORS[level]
                                ),
                                ft.Text(window_text, size=14)
                            ],
                            spacing=6
                        )
                    )
                )

            status.value = (
                "Hours shown in local time • "
                "lower heat = Green or Yellow"
            )

        except Exception as exc:
            rows.controls.clear()
            status.value = f"Could not load the plan: {exc}"

        finally:
            busy = False
            spinner.visible = False
            refresh_button.disabled = False
            page.update()

    refresh_button.on_click = refresh

    #plan layout
    screen = ft.SafeArea(
        content=ft.Column(
            controls=[
                ft.Text(
                    "7-day training plan (Heat Forecast)",
                    size=30,
                    weight=ft.FontWeight.BOLD
                ),
                location,
                ft.Text(
                    "Lower-heat windows are 6 AM–8 PM hours below "
                    "Orange, not permission to exercise."
                ),
                ft.Row([refresh_button, spinner]),
                status,
                rows,
                ft.Text(
                    "Estimated WBGT from Open-Meteo and Liljegren. "
                    "Follow official guidance and local rules. "
                    "Heat risk also depends on activity, clothing "
                    "and acclimatization.",
                    color="#64748B",
                    size=12
                )
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    )

    return screen, refresh
