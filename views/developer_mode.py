
"Temporary WBGT simulator. Never changes real forecasts or attendance"
"ASSISTED BY AI"

from datetime import date
import math

import flet as ft

from core.acclim import Person, worker_plan, athlete_plan
from core.rules import get_category


def build_developer_mode(page, settings, profile):

    #hidden until enabled
    enabled = ft.Switch(
        label="Developer mode (simulation only)",
        value=False
    )

    wbgt = ft.TextField(
        label="SIMULATED WBGT (°F)",
        value="95"
    )

    region = ft.Dropdown(
        label="SIMULATED region",
        value=str(settings["region"]),
        options=[
            ft.DropdownOption(key=str(i), text=f"Region {i}")
            for i in (1, 2, 3)
        ]
    )

    role = ft.Dropdown(
        label="SIMULATED role",
        value="athlete",
        options=[
            ft.DropdownOption(key="worker", text="Worker"),
            ft.DropdownOption(key="athlete", text="Athlete")
        ]
    )

    result = ft.Text(
        "SIMULATED — no real records will change.",
        selectable=True
    )
    #calculate using existing rules
    def calculate(_event=None):

        try:
            value = float((wbgt.value or "").strip())

            if not math.isfinite(value) or not -20 <= value <= 160:
                raise ValueError()

            celsius = (value - 32) * 5 / 9

            #empty attendance keeps the simulation separate
            person = Person("Simulation", role.value, False, [])

            if role.value == "athlete":

                category = get_category(
                    celsius,
                    f"sports_{region.value}"
                )

                plan = athlete_plan(
                    person,
                    date.today(),
                    wbgt_c=celsius,
                    sports_region=int(region.value)
                )

                if plan["rest_required"]:
                    limit = "Rest day"
                elif plan["max_practices"] == 0:
                    limit = "No outdoor practice"
                else:
                    limit = (
                        f"{plan['max_practices']} practice(s), "
                        f"up to {plan['max_total_practice_minutes']} minutes"
                    )

            else:
                plan = worker_plan(
                    person,
                    date.today(),
                    profile["normal_minutes"],
                    wbgt_c=celsius
                )

                category = plan["screening"]

                limit = (
                    f"Day {plan['day']}: {plan['percent']}%, "
                    f"up to {plan['max_heat_minutes']} min"
                )

            result.value = (
                f"SIMULATED WBGT: {value:.1f} °F\n"
                f"SIMULATED risk: {category['label']}\n"
                f"SIMULATED guidance: {category['guidance']}\n"
                f"SIMULATED limit: {limit}\n"
                "Not live weather or a real attendance record."
            )

        except (ValueError, TypeError, KeyError):
            result.value = (
                "SIMULATED — enter a valid WBGT "
                "from -20 to 160 °F."
            )

        page.update()

    #simulation panel
    panel = ft.Column(
        controls=[
            ft.Text(
                "SIMULATED — for testing only",
                size=17,
                weight=ft.FontWeight.BOLD
            ),
            wbgt,
            region,
            role,
            ft.Button(
                content="Run simulation",
                on_click=calculate
            ),
            result
        ],
        spacing=10,
        visible=False
    )

    def toggle(_event=None):
        panel.visible = enabled.value
        page.update()

    enabled.on_change = toggle

    return enabled, panel
