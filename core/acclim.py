
"""SOURCE FOR ACCLIMATIZATION USE CAUTION
Sources:
NIOSH: https://www.cdc.gov/niosh/heat-stress/recommendations/acclimatization.html
NATA: https://pmc.ncbi.nlm.nih.gov/articles/PMC2681206/
NATA: https://www.nata.org/sites/default/files/2025-08/preseason_heat-acclimatization_guidelines_for_secondary_school_athletics.pdf
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from math import floor, isfinite

from core.rules import get_category


NIOSH_SOURCE = "https://www.cdc.gov/niosh/heat-stress/recommendations/acclimatization.html"
NATA_SOURCE = "https://pmc.ncbi.nlm.nih.gov/articles/PMC2681206/"
SPORTS_SOURCE = "https://www.recognizetorecover.org/s/Heat-Guidelines.pdf"


@dataclass(frozen=True)
class Session:
    day: date
    minutes: int
    kind: str = "work"
    heat_wave: bool = False


@dataclass
class Person:
    name: str
    role: str
    experienced: bool = False
    sessions: list[Session] = field(default_factory=list)


def check_person(person, today):
   #check person and that previous session was valid

    if not isinstance(person, Person):
        raise ValueError("EXPECTED A PERSON")

    if person.role not in ("worker", "athlete"):
        raise ValueError("ROLE MUST BE 'worker' OR 'athlete'")

    if not isinstance(today, date) or isinstance(today, datetime):
        raise ValueError("TODAY MUST BE A DATE")

    if person.role == "worker":
        allowed_kinds = {"work"}
    else:
        allowed_kinds = {"practice", "walkthrough"}

    for session in person.sessions:

        if not isinstance(session, Session):
            raise ValueError("INVALID SESSION")

        if not isinstance(session.day, date) or isinstance(session.day, datetime):
            raise ValueError("SESSION DAY MUST BE A DATE")

        if session.day >= today:
            raise ValueError("ONLY COMPLETETD SESSIONS CAN COUNT")

        if session.kind not in allowed_kinds:
            raise ValueError(f"INVALID SESSION TYPE: {session.kind}")

        if type(session.minutes) is not int or session.minutes <= 0:
            raise ValueError("SESSION DURATION MUST BE A POSITIVE INTEGER")


def recent_work_days(sessions, today, kind=None):
    "get attendance days since the last long break"

    days = sorted(
        {
            session.day
            for session in sessions
            if kind is None or session.kind == kind
        },
        reverse=True
    )

    if not days or (today - days[0]).days > 7:
        return []

    recent = [days[0]]

    for newer, older in zip(days, days[1:]):
        if (newer - older).days > 7:
            break

        recent.append(older)

    return recent


def worker_plan(
    person,
    today,
    normal_minutes,
    heat_wave=False,
    wbgt_c=None,
    workload="moderate",
    clothing_adjustment_c=0
):
    #calculate gradual return to activity for workers

    check_person(person, today)

    if person.role != "worker":
        raise ValueError("USE athlete_plan FOR ATHLETES")

    if isinstance(normal_minutes, bool) or not isinstance(normal_minutes, (int, float)):
        raise ValueError("NORMAL DURATION MUST BE A POSITIVE NUMBER")

    if not isfinite(normal_minutes) or normal_minutes <= 0:
        raise ValueError("NORMAL DURATION MUST BE A POSITIVE NUMBER")

    if not isinstance(heat_wave, bool):
        raise ValueError("heat_wave MUST BE True or False")

    work_days = recent_work_days(person.sessions, today)

    day_number = len(work_days) + 1

    back_after_break = bool(person.sessions) and not work_days

    use_new_worker_plan = not person.experienced or back_after_break

    #new workers start at 20% and build up.a
    if use_new_worker_plan:

        fraction = min(day_number * 0.20, 1.0)
        rule = "NIOSH new-worker progression"

    else:

        schedule = [0.50, 0.60, 0.80, 1.0]
        fraction = schedule[min(day_number - 1, 3)]
        rule = "NIOSH experienced-worker progression"

    heat_wave_day = None

    if heat_wave:

        hot_days = {
            session.day
            for session in person.sessions
            if session.heat_wave
        }

        previous_hot_days = 0

        for work_day in work_days:

            if work_day not in hot_days:
                break

            previous_hot_days += 1

        heat_wave_day = previous_hot_days + 1

        heat_schedule = [0.50, 0.60, 0.80, 1.0]
        heat_fraction = heat_schedule[min(heat_wave_day - 1, 3)]

        #NEVER LET ONE RULE OVERRULE ANOTHER!!!!!!!
        fraction = min(fraction, heat_fraction)

        rule += " and heat-wave guidance (stricter limit used)"

    minutes = floor(normal_minutes * fraction)

    warnings = [
        "This is an acclimatization planning limit, not a safe-work guarantee."
        "Keep using appropriate water, rest, shade and supervision."
    ]

    if back_after_break:
        warnings.append(
            "Progress restarted with the new-worker plan after a long break."
        )

    screening = None

    if wbgt_c is not None:

        if not use_new_worker_plan and day_number >= 4:
            status = "acclimatized"
        else:
            status = "unacclimatized"

        screening = get_category(
            wbgt_c,
            f"workers_{workload}_{status}",
            clothing_adjustment_c=clothing_adjustment_c
        )

        if screening["category"] == "review":
            warnings.append(
                "The OSHA/NIOSH WBGT screening level was reached."
                "Review site conditions."
            )

    return {
        "role": "worker",
        "day": day_number,
        "heat_wave_day": heat_wave_day,
        "percent": round(fraction * 100),
        "max_heat_minutes": minutes,
        "rule": rule,
        "source": NIOSH_SOURCE,
        "screening": screening,
        "warnings": warnings
    }


def athlete_plan(person, today, wbgt_c=None, sports_region=None):
    #calculate athlete preseason training limits

    check_person(person, today)

    if person.role != "athlete":
        raise ValueError("USE worker_plan FOR workers")

    if (wbgt_c is None) != (sports_region is None):
        raise ValueError("GIVE BOTH WBGT AND A SPORTS REIGON, OR NEITHER")

    #ONLY COUNT PRACTICES FROM CURRENT PERIOD!!! THIS WAS A BUG, A USER COULD'VE COME BACK AFTER 3 MONTHS, DOUBLE PRACTICED, AND PLAYED 5 HRS
    practice_days = set(
        recent_work_days(person.sessions, today, "practice")
    )

    day_number = len(practice_days) + 1

    #check whether athlete returns from long break
    all_practices = [
        session for session in person.sessions
        if session.kind == "practice"
    ]

    restarted = bool(all_practices) and not practice_days
    preseason = day_number <= 14

    #SIX DAYS NEEDS A DAY OFF!!!
    yesterday = today - timedelta(days=1)

    consecutive_days = 0
    check_day = yesterday

    while check_day in practice_days:
        consecutive_days += 1
        check_day -= timedelta(days=1)

    rest_required = preseason and consecutive_days >= 6

    yesterday_sessions = sum(
        1
        for session in person.sessions
        if session.kind == "practice" and session.day == yesterday
    )

    #NO DOUBLE PRACTICES IN FIRST 5 DAYS OR IMMEDIATELY AFTER ANOTHER DOUBLE PRACTICE DAY.
    if day_number <= 5 or yesterday_sessions >= 2:

        max_practices = 1
        max_total = 180

    else:

        max_practices = 2
        max_total = 300

    max_single = 180

    if rest_required:
        max_practices = 0
        max_total = 0
        max_single = 0

    warnings = [
        "Check school, league and local heat policies too. "
        "They may be stricter."
    ]

    if restarted:
        warnings.append(
            "Acclimatization restarted after a long break. "
            "Check your school's return-to-practice policy."
        )

    if day_number <= 5:
        warnings.append(
            "Days 1-5: one practice lasting no more than three hours."
        )

    if preseason and max_practices == 2:
        warnings.append(
            "Allow at least three hours of cool rest between two practices."
        )

    if rest_required:
        warnings.append(
            "Rest day needed after six consecutive practice days."
        )

    warnings.append(
        "Walkthroughs have separate limits and rest requirements."
    )

    sport_category = None

    if wbgt_c is not None:

        sport_category = get_category(
            wbgt_c,
            f"sports_{sports_region}"
        )

        category = sport_category["category"]

        #REIGONAL RESTRICTIONS CAN ONLY LOWER THE LIMIT!!!
        heat_caps = {
            "orange": 120,
            "red": 60,
            "black": 0
        }

        if category in heat_caps:

            max_total = min(max_total, heat_caps[category])
            max_single = min(max_single, max_total)

            if max_total == 0:
                max_practices = 0

            warnings.append(
                "Regional heat guidance further restricts practice."
            )

        warnings.append(sport_category["guidance"])

    return {
        "role": "athlete",
        "day": day_number,
        "preseason": preseason,
        "rest_required": rest_required,
        "max_practices": max_practices,
        "max_single_practice_minutes": max_single,
        "max_total_practice_minutes": max_total,
        "max_walkthrough_minutes": 60 if day_number <= 5 and not rest_required else None,
        "min_cool_rest_hours": 3 if preseason else None,
        "sport_category": sport_category,
        "source": NATA_SOURCE,
        "regional_source": SPORTS_SOURCE if sport_category else None,
        "warnings": warnings,
        "restarted_after_break": restarted,
    }


def acclimatization_plan(person, today, normal_minutes=None, **options):
    #choose plan for worker or athlete

    if not isinstance(person, Person):
        raise ValueError("EXPECTED A PERSON")

    if person.role == "worker":

        if normal_minutes is None:
            raise ValueError("WORKERS NEED A NORMAL SHIFT DURATION")

        return worker_plan(
            person,
            today,
            normal_minutes,
            **options
        )

    if person.role == "athlete":

        if normal_minutes is not None:
            raise ValueError(
                "ATHLETES USE NATA PRACTICE LIMITS NOT SHIFT LIMITS"
            )

        return athlete_plan(person, today, **options)

    raise ValueError("Unknown role")
