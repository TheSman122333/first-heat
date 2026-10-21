
"HOME PAGE, Detroit only by default"

import asyncio
import flet as ft

from core.today import fetch_today_summary


#colors for each heat category
CARD_COLORS = {
    "green": ("#E5F5E9", "#166534"),
    "yellow": ("#FFF4CC", "#795500"),
    "orange": ("#FFE4D2", "#9A3412"),
    "red": ("#FCE0E0", "#991B1B"),
    "black": ("#273244", "#FFFFFF")
}

DARK = "#172033"
MUTED = "#64748B"
BACKGROUND = "#F8FAFC"


def build_home(page):

    page.bgcolor = BACKGROUND

    #header
    date_text = ft.Text(
        "Today's conditions",
        size=15,
        color=MUTED
    )

    header = ft.Column(
        controls=[
            ft.Text(
                "FirstHeat",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=DARK
            ),
            ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.LOCATION_ON_OUTLINED,
                        size=17,
                        color=MUTED
                    ),
                    ft.Text(
                        "Detroit, Michigan",
                        size=15,
                        color=MUTED
                    )
                ],
                spacing=4
            ),
            date_text
        ],
        spacing=5
    )

    #loading and errors
    loading = ft.Row(
        controls=[
            ft.ProgressRing(width=22, height=22),
            ft.Text(
                "Loading forecast...",
                color=MUTED
            )
        ],
        spacing=12
    )

    error = ft.Text(
        "",
        color="#991B1B",
        visible=False
    )

    #current heat readings
    hour = ft.Text(
        "CURRENT CONDITIONS",
        size=13,
        weight=ft.FontWeight.W_600,
        color="#166534"
    )

    temperature = ft.Text(
        "-- °F",
        size=52,
        weight=ft.FontWeight.BOLD,
        color="#166534"
    )

    category = ft.Text(
        "",
        size=19,
        weight=ft.FontWeight.BOLD,
        color="#166534"
    )

    guidance = ft.Text(
        "",
        size=15,
        color=DARK
    )

    #recommendations label
    recommendations_label = ft.Text(
        "RECOMMENDATIONS",
        size=12,
        weight=ft.FontWeight.W_600,
        color=MUTED
    )

    #current heat card
    current_card = ft.Container(
        bgcolor=CARD_COLORS["green"][0],
        border_radius=20,
        padding=25,
        visible=False,
        content=ft.Column(
            controls=[
                hour,
                temperature,
                category,
                ft.Container(
                    height=1,
                    bgcolor="#CBD5E1"
                ),
                recommendations_label,
                guidance
            ],
            spacing=12
        )
    )


    #todays highest WBGT
    peak_temperature = ft.Text(
        "-- °F",
        size=29,
        weight=ft.FontWeight.BOLD,
        color=DARK
    )

    peak_time = ft.Text(
        "",
        size=14,
        color=MUTED
    )

    peak_category = ft.Text(
        "",
        size=15,
        weight=ft.FontWeight.W_600
    )

    peak_card = ft.Container(
        bgcolor="#FFFFFF",
        border_radius=20,
        padding=24,
        visible=False,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.TRENDING_UP,
                            color=MUTED,
                            size=20
                        ),
                        ft.Text(
                            "Today's peak",
                            size=17,
                            weight=ft.FontWeight.W_600,
                            color=DARK
                        )
                    ],
                    spacing=10
                ),
                peak_temperature,
                peak_time,
                peak_category
            ],
            spacing=8
        )
    )

    #sources and links
    source = ft.Text(
        "",
        size=12,
        color=MUTED,
        visible=False
    )

    weather_link = ft.TextButton(
        content="Weather source",
        url="https://open-meteo.com/"
    )

    guidelines_link = ft.TextButton(
        content="Heat guidelines",
        url="https://www.recognizetorecover.org/environmental"
    )

    links = ft.Row(
        controls=[
            weather_link,
            guidelines_link
        ],
        spacing=8,
        wrap=True,
        visible=False
    )

    #refresh button
    refresh_button = ft.Button(
        content="Refresh forecast",
        icon=ft.Icons.REFRESH
    )

    busy = False

    async def refresh(_event=None):
        nonlocal busy

        if busy:
            return

        busy = True

        loading.visible = True
        error.visible = False
        current_card.visible = False
        peak_card.visible = False
        source.visible = False
        links.visible = False
        refresh_button.disabled = True

        page.update()

        try:
            #run weather fetching separately from the UI
            today = await asyncio.to_thread(fetch_today_summary)

            #convert to fahrenheit, round only for display
            wbgt_f = today["current_wbgt"] * 9 / 5 + 32
            peak_f = today["peak_wbgt"] * 9 / 5 + 32

            level = today["category"]
            background, text_color = CARD_COLORS[level]

            #update current conditions
            date_text.value = (
                f"{today['current_time']:%A, %B %d}"
            )

            hour.value = (
                f"CURRENT CONDITIONS · "
                f"{today['current_time']:%I:%M %p}"
            )

            temperature.value = f"{wbgt_f:.1f} °F"
            category.value = f"{level.title()} heat category"
            guidance.value = today["guidance"]

            current_card.bgcolor = background

            hour.color = text_color
            temperature.color = text_color
            category.color = text_color
            recommendations_label.color = (
                "#E2E8F0" if level == "black" else MUTED
            )

            guidance.color = (
                "#FFFFFF" if level == "black" else DARK
            )

            current_card.visible = True

            #update todays peak
            peak_temperature.value = f"{peak_f:.1f} °F"

            peak_time.value = (
                f"Expected at {today['peak_time']:%I:%M %p}"
            )

            peak_level = today["peak_category"]

            peak_category.value = (
                f"{peak_level.title()} heat category"
            )

            peak_category.color = (
                "#1F2937" if peak_level == "black"
                else CARD_COLORS[peak_level][1]
            )

            peak_card.visible = True

            #sources
            source.value = (
                f"Open-Meteo · Liljegren WBGT estimate · "
                f"Sports region {today['region']}"
            )

            guidelines_link.url = today["rule_source"]

            source.visible = True
            links.visible = True

        except Exception as exc:
            #hide old readings if the forecast fails
            error.value = (
                "Could not load today's forecast. "
                "Check your internet connection and try again.\n"
                f"{exc}"
            )

            error.visible = True

        finally:
            busy = False
            loading.visible = False
            refresh_button.disabled = False

            page.update()

    refresh_button.on_click = refresh

    #full home layout
    screen = ft.SafeArea(
        content=ft.Column(
            controls=[
                header,
                loading,
                error,
                current_card,
                peak_card,
                refresh_button,
                ft.Container(height=1, bgcolor="#E2E8F0"),
                source,
                links,
                ft.Text(
                    "Estimated WBGT, not an on-site measurement. "
                    "Follow official guidance "
                    "(NATA/KSI, OSHA/NIOSH).",
                    size=12,
                    color=MUTED
                )
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True
        )
    )

    return screen, refresh
