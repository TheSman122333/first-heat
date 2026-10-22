
"Combine acclimatization with the seven-day weather forecast"

"USED AI TO ASSIST AND STRUCTURE project_week. "

from datetime import date

from core.acclim import Person, Session, worker_plan, athlete_plan


HOT_CATEGORIES = ("orange", "red", "black")


def project_week(profile, forecast, region):
    "calculate today's plan and six projected days"

    if not forecast:
        raise ValueError("WEEKLY FORECAST IS EMPTY")

    #load past attendance
    sessions = [
        Session(
            date.fromisoformat(item["day"]),
            item["minutes"],
            item["kind"],
            item["heat_wave"]
        )
        for item in profile["sessions"]
    ]

    person = Person(
        "Me",
        profile["role"],
        profile["experienced"],
        sessions
    )

    results = []
    first_day = forecast[0]["date"]

    for day in forecast:

        when = day["date"]

        if when < first_day:
            raise ValueError("Forecast days must be in order")

        if any(session.day > when for session in person.sessions):
            raise ValueError("Attendance cannot be dated in the future")

        #only count sessions before the day being calculated
        past = [
            session for session in person.sessions
            if session.day < when
        ]

        current_person = Person(
            person.name,
            person.role,
            person.experienced,
            past
        )

        #orange or higher is our heat-wave planning flag
        hot = day["peak_category"] in HOT_CATEGORIES

        if person.role == "worker":

            plan = worker_plan(
                current_person,
                when,
                profile["normal_minutes"],
                heat_wave=hot,
                wbgt_c=day["peak_wbgt"]
            )

            limit = plan["max_heat_minutes"]

            summary = (
                f"Day {plan['day']}: {plan['percent']}% "
                f"· up to {limit} min"
            )

        else:

            plan = athlete_plan(
                current_person,
                when,
                wbgt_c=day["peak_wbgt"],
                sports_region=region
            )

            limit = plan["max_total_practice_minutes"]
            count = plan["max_practices"]

            noun = "practice" if count == 1 else "practices"

            summary = (
                f"Day {plan['day']}: {count} {noun} "
                f"· up to {limit} min"
            )

        completed = any(
            session.day == when
            for session in person.sessions
        )

        results.append({
            "date": when,
            "peak_wbgt": day["peak_wbgt"],
            "category": day["peak_category"],
            "window": day["window"],
            "heat_wave_proxy": hot,
            "completed": completed,
            "limit_minutes": limit,
            "summary": summary,
            "plan": plan,
            "projected": when != first_day
        })

        #assume attendance on future days with permitted activity
        #simulating future attendance
        if not completed and limit > 0:
            kind = "work" if person.role == "worker" else "practice"
            count = plan["max_practices"] if person.role == "athlete" else 1

            minutes_each = (
                [limit] if count == 1
                else [limit // 2, limit - limit // 2]
            )

            for minutes in minutes_each:
                if minutes > 0:
                    person.sessions.append(Session(when, minutes, kind, hot))

    return results
