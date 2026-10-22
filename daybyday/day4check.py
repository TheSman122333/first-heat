"""DAY 4 - Check personal acclimatization"""
"AI USED"

from datetime import date, timedelta
from core.planner import project_week

today = date(2026, 10, 21)


#*example weather*
def forecast(category="green"):
    return [
        {
            "date": today + timedelta(days=i),
            "peak_wbgt": 29.5 if category == "orange" else 22,
            "peak_category": category,
            "window": None
        }
        for i in range(7)
    ]


#*compare expected and actual*
def show(name, person, expected, category="green", day=0):
    actual = project_week(person, forecast(category), 2)[day]["summary"]

    print(f"\n{name}")
    print("Expected:", expected)
    print("Actual:  ", actual)


#*new worker*
new = {
    "role": "worker",
    "experienced": False,
    "normal_minutes": 480,
    "sessions": []
}

show("New worker", new, "Day 1: 20% · up to 96 min")


#*worked yesterday*
worked = {
    **new,
    "sessions": [{
        "day": (today - timedelta(days=1)).isoformat(),
        "minutes": 96,
        "kind": "work",
        "heat_wave": False
    }]
}

show("Worked yesterday", worked, "Day 2: 40% · up to 192 min")


#*away eight days*
returning = {
    **new,
    "experienced": True,
    "sessions": [{
        "day": (today - timedelta(days=9)).isoformat(),
        "minutes": 120,
        "kind": "work",
        "heat_wave": False
    }]
}

show("Returning worker", returning, "Day 1: 20% · up to 96 min")


#*orange heat day*
show(
    "Orange forecast",
    {**new, "experienced": True},
    "Day 1: 50% · up to 240 min",
    "orange"
)


#*new athlete*
athlete = {**new, "role": "athlete"}

show("New athlete", athlete, "Day 1: 1 practice · up to 180 min")


#*athlete with five completed practices*
athlete["sessions"] = [
    {
        "day": (today - timedelta(days=i)).isoformat(),
        "minutes": 120,
        "kind": "practice",
        "heat_wave": False
    }
    for i in range(1, 6)
]

show("Athlete day 6", athlete, "Day 6: 2 practices · up to 300 min")
show("Following rest day", athlete, "Rest day", day=1)
show("After rest day", athlete, "Day 7: 2 practices · up to 300 min", day=2)

print("\nProjected sessions are not saved.")
