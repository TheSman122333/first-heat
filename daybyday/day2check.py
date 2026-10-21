
"DAY 2 Weather and acclimatization check"

from datetime import timedelta

from core.today import fetch_today_summary
from core.acclim import Person, Session, worker_plan, athlete_plan


#todays weather
weather = fetch_today_summary()

today = weather["current_time"].date()
wbgt = weather["current_wbgt"]
region = weather["region"]

print("\nFIRSTHEAT - DAY 2")
print("Date:", today)
print("Location: Detroit, Michigan")

print("\nCURRENT WEATHER")
print("WBGT:", round(wbgt * 9 / 5 + 32, 1), "°F")
print("Category:", weather["category"].title())
print("Guidance:", weather["guidance"])
print(
    "Today's peak:",
    round(weather["peak_wbgt"] * 9 / 5 + 32, 1), "°F",
    "at", weather["peak_time"].strftime("%I:%M %p")
)


#example workers
workers = [
    Person("New", "worker"),
    Person("Experienced", "worker", experienced=True),
    Person(
        "Returning", "worker", experienced=True,
        sessions=[Session(today - timedelta(days=9), 120)]
    )
]


#heat wave examples
print("\nHEAT WAVE EXAMPLES")

for day in [1, 2, 3]:
    sessions = [
        Session(today - timedelta(days=i), 120, heat_wave=True)
        for i in range(1, day)
    ]

    person = Person(
        "Experienced", "worker",
        experienced=True, sessions=sessions
    )

    plan = worker_plan(person, today, 480, heat_wave=True)

    print(
        "Experienced / Heat wave day:", day,
        "/ Exposure:", plan["percent"], "%"
    )


#new worker on day 2 in a heat wave
new_day_two = Person(
    "New day 2", "worker",
    sessions=[Session(today - timedelta(days=1), 120)]
)

plan = worker_plan(new_day_two, today, 480, heat_wave=True)

print("New worker / Day 2, heat-wave day 1:", plan["percent"], "%")


print("\nWORKER ACCLIMATIZATION")

for person in workers:
    plan = worker_plan(person, today, 480, wbgt_c=wbgt)

    print(
        person.name,
        " / Day:", plan["day"],
        " / Exposure:", plan["percent"], "%",
        " / Minutes:", plan["max_heat_minutes"]
    )


#athlete under current conditions
athlete = Person("Athlete", "athlete")

print("\nATHLETE - CURRENT WEATHER")

plan = athlete_plan(athlete, today, wbgt_c=wbgt, sports_region=region)

print("Category:", plan["sport_category"]["category"].title())
print("Max practices:", plan["max_practices"])
print("Max minutes:", plan["max_total_practice_minutes"])


#simulate hotter days with fixed WBGT
print("\nATHLETE - SIMULATED HOT WEATHER")

for temperature in [31.5, 32.2]:
    plan = athlete_plan(
        athlete, today,
        wbgt_c=temperature,
        sports_region=region
    )

    print(
        f"\nWBGT: {temperature * 9 / 5 + 32:.1f} °F",
        "Category:", plan["sport_category"]["category"].title(),
        "Practices:", plan["max_practices"],
        "Minutes:", plan["max_total_practice_minutes"]
    )


#returning athlete after two months
print("\nATHLETE - RETURNING AFTER TWO MONTHS")

old_practices = [
    Session(today - timedelta(days=i), 120, "practice")
    for i in range(47, 61)
]

returning_athlete = Person(
    "Returning athlete", "athlete",
    sessions=old_practices
)

plan = athlete_plan(returning_athlete, today)

print("Previous practices:", len(old_practices))
print("Return day:", plan["day"])
print("Max practices:", plan["max_practices"])

assert plan["day"] == 1, "Athlete should restart at Day 1"


#athlete continues after restarting
returning_athlete.sessions.append(
    Session(today - timedelta(days=1), 120, "practice")
)

plan = athlete_plan(returning_athlete, today)

print("\nATHLETE - AFTER FIRST RETURN PRACTICE")
print("Current day:", plan["day"])
print("Max practices:", plan["max_practices"])

assert plan["day"] == 2, "Athlete should continue to Day 2"


#athlete returning after a short break
print("\nATHLETE - SHORT BREAK")

recent_practices = [
    Session(today - timedelta(days=i), 120, "practice")
    for i in range(6, 11)
]

short_break_athlete = Person(
    "Short break", "athlete",
    sessions=recent_practices
)

plan = athlete_plan(short_break_athlete, today)

print("Return day:", plan["day"])
print("Max practices:", plan["max_practices"])

assert plan["day"] == 6, "Short break should keep progress"


print("\nPlanning guidance only, not guaranteed exposure limits.")
print("Day 2 check complete!")
