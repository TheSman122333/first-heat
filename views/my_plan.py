"""Plan Page: attendance and seven-day heat plan"""

import asyncio
import flet as ft

from core.plan import fetch_week_plan
from core.planner import project_week


DARK = "#172033"
MUTED = "#64748B"


def build_my_plan(page, settings, profile, on_save):

    #personal settings
    role = ft.Dropdown(
        label="Activity",
        value=profile["role"],
        options=[
            ft.DropdownOption(key="worker", text="Outdoor worker"),
            ft.DropdownOption(key="athlete", text="Athlete")
        ]
    )

    experienced = ft.Checkbox(
        label="Experienced in the heat",
        value=profile["experienced"]
    )

    shift = ft.TextField(
        label="Usual shift (minutes)",
        value=str(profile["normal_minutes"])
    )

    duration = ft.TextField(
        label="Actual minutes completed today",
        hint_text="e.g. 60"
    )

    status = ft.Text("", color=MUTED)
    progress = ft.ProgressRing(width=20, height=20, visible=False)

    current = ft.Column(spacing=7)
    coming = ft.Column(spacing=10)

    mark_button = ft.Button(
        content="Mark today done",
        disabled=True
    )

    reset_button = ft.Button(
        content="Reset my attendance",
        disabled=not bool(profile["sessions"])
    )

    refresh_button = ft.Button(
        content="Refresh forecast",
        icon=ft.Icons.REFRESH
    )

    cached_week = None
    busy = False
    #format lower heat hours
    def window_text(window):

        if not window:
            return "No lower-heat window forecast"

        start, end = window
        return f"{start:%I %p}–{end:%I %p}"

    #display current and future plans
    def display():

        if cached_week is None:
            return

        days = project_week(
            profile,
            cached_week,
            settings["region"]
        )

        today = days[0]

        current.controls.clear()
        coming.controls.clear()

        current.controls.extend([
            ft.Text(
                today["summary"],
                size=20,
                weight=ft.FontWeight.BOLD,
                color=DARK
            ),
            ft.Text(
                f"Peak: {today['peak_wbgt'] * 9 / 5 + 32:.1f} °F WBGT "
                f"· {today['category'].title()}"
            ),
            ft.Text(
                "Lower heat: " + window_text(today["window"])
            )
        ])

        #heat warnings
        if today["heat_wave_proxy"]:
            current.controls.append(
                ft.Text(
                    "Orange+ peak: cautious heat-wave planning applied."
                )
            )

        screening = today["plan"].get("screening")

        if screening and screening["category"] == "review":
            current.controls.append(
                ft.Text(
                    "OSHA/NIOSH screening reached. "
                    "Review worksite conditions."
                )
            )

        if today["limit_minutes"] == 0:

            if today["plan"].get("rest_required"):
                warning = "Rest day under NATA guidance."
            elif today["category"] == "black":
                warning = "No outdoor practice under these guidelines."
            else:
                warning = "No practice under today's plan."

            current.controls.append(ft.Text(warning))

        mark_button.disabled = (
            today["completed"] or today["limit_minutes"] == 0
        )

        mark_button.content = (
            "Completed today" if today["completed"]
            else "Mark today done"
        )

        reset_button.disabled = not bool(profile["sessions"])

        #coming days
        for day in days[1:]:

            coming.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    border_radius=12,
                    padding=14,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"{day['date']:%a, %b %d} "
                                f"· {day['category'].title()}",
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(day["summary"]),
                            ft.Text(
                                "Lower heat: " + window_text(day["window"]),
                                color=MUTED
                            )
                        ],
                        spacing=5
                    )
                )
            )

        page.update()

    #save personal settings
    async def save_form(_event=None):

        try:
            if profile["sessions"] and role.value != profile["role"]:
                role.value = profile["role"]
                raise ValueError(
                    "Reset attendance before changing activity."
                )

            #*check shift duration*
            if role.value == "worker":
                text = (shift.value or "").strip()

                if not text.isdecimal():
                    raise ValueError("Enter your usual shift in minutes.")

                minutes = int(text)

                if not 1 <= minutes <= 1440:
                    raise ValueError(
                        "Shift must be between 1 and 1440 minutes."
                    )
            else:
                minutes = profile["normal_minutes"]

            updated = {
                **profile,
                "role": role.value,
                "experienced": bool(experienced.value),
                "normal_minutes": minutes
            }

            await on_save(updated)

            shift.visible = role.value == "worker"
            experienced.visible = role.value == "worker"

            status.value = "Preferences saved"
            display()

        except (ValueError, RuntimeError) as error:
            status.value = str(error)

        page.update()

    #mark todays attendance
    async def mark_done(_event=None):

        if cached_week is None:
            status.value = "Load the forecast first."
            page.update()
            return

        try:
            text = (duration.value or "").strip()

            if not text.isdecimal():
                raise ValueError("Enter the minutes you completed today.")

            minutes = int(text)

            if not 1 <= minutes <= 1440:
                raise ValueError(
                    "Enter a duration between 1 and 1440 minutes."
                )

            today = project_week(
                profile,
                cached_week,
                settings["region"]
            )[0]

            if today["completed"]:
                raise ValueError("Today has already been recorded.")

            if today["limit_minutes"] == 0:
                raise ValueError("No activity is planned for today.")

            record = {
                "day": today["date"].isoformat(),
                "minutes": minutes,
                "kind": (
                    "work" if profile["role"] == "worker"
                    else "practice"
                ),
                "heat_wave": today["heat_wave_proxy"]
            }

            await on_save({
                **profile,
                "sessions": profile["sessions"] + [record]
            })

            status.value = "Today's attendance saved."

            if minutes > today["limit_minutes"]:
                status.value += (
                    " You exceeded the planning limit. "
                    "Review your heat precautions."
                )

            duration.value = ""
            display()

        except (ValueError, RuntimeError) as error:
            status.value = str(error)

        page.update()

    #reset saved attendance
    async def reset_attendance(_event=None):

        try:
            await on_save({
                **profile,
                "sessions": []
            })

            page.pop_dialog()

            duration.value = ""
            reset_button.disabled = True
            status.value = "Attendance history reset."

            display()

        except (ValueError, RuntimeError) as error:
            status.value = f"Could not reset attendance: {error}"

        page.update()

    #confirm before resetting
    reset_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Reset attendance?"),
        content=ft.Text(
            "This will permanently delete your attendance history "
            "and restart your acclimatization progress."
        ),
        actions=[
            ft.TextButton(
                content="Cancel",
                on_click=lambda e: page.pop_dialog()
            ),
            ft.TextButton(
                content="Reset",
                on_click=reset_attendance
            )
        ]
    )

    #load forecast without freezing the app
    async def refresh(_event=None):
        nonlocal cached_week, busy

        if busy:
            return

        busy = True
        progress.visible = True
        refresh_button.disabled = True
        status.value = "Loading your plan..."

        page.update()

        try:
            cached_week = await asyncio.to_thread(
                fetch_week_plan,
                settings.copy()
            )

            display()
            status.value = "Forecast updated"

        except Exception as error:
            cached_week = None
            current.controls.clear()
            coming.controls.clear()
            mark_button.disabled = True
            status.value = f"Could not load your plan: {error}"

        finally:
            busy = False
            progress.visible = False
            refresh_button.disabled = False
            page.update()

    #button and field actions
    role.on_select = save_form
    experienced.on_change = save_form

    shift.on_blur = save_form
    shift.on_submit = save_form

    mark_button.on_click = mark_done
    reset_button.on_click = lambda e: page.show_dialog(reset_dialog)
    refresh_button.on_click = refresh

    shift.visible = profile["role"] == "worker"
    experienced.visible = profile["role"] == "worker"

    #page layout
    screen = ft.SafeArea(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text(
                    "My Acclimation Planner",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=DARK
                ),
                ft.Text(
                    "Your attendance changes the plan. "
                    "Future days assume you attend each day "
                    "with permitted activity.",
                    color=MUTED
                ),
                role,
                experienced,
                shift,
                ft.Row([refresh_button, progress]),
                status,
                ft.Text(
                    "Today",
                    size=21,
                    weight=ft.FontWeight.BOLD
                ),
                current,
                duration,
                mark_button,
                reset_button,
                ft.Divider(),
                ft.Text(
                    "Coming days · projected",
                    size=21,
                    weight=ft.FontWeight.BOLD
                ),
                coming,
                ft.Text(
                    "Estimated WBGT, not an on-site measurement. "
                    "Orange+ is an app-defined heat-wave flag, "
                    "not an official NIOSH threshold. "
                    "Follow local heat policies.",
                    color=MUTED,
                    size=12
                )
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    )

    return screen, refresh
