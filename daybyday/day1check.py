
"""Check weather, WBGT, and heat categories from start to finish.

Run:
    python day1_check.py

Other locations need their coordinates, time zone, and sports region.
Climate-region boundaries can cross state lines.
"""

"""WRITTEN BY AI!!!!!"""

import argparse
import math
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from core.weather import fetch_history
from core.wbgt import calculate_hourly_wbgt
from core.rules import get_category, load_rules

DETROIT_LAT = 42.3314
DETROIT_LON = -83.0458


def check_rules():
    """Check the main category boundaries before fetching weather."""

    rules = load_rules()

    for region, settings in rules["sports"]["regions"].items():
        assert settings["unit"] == "F" and settings["source"]

        for level, cutoff in settings["minimums"].items():
            result = get_category(cutoff, f"sports_{region}", unit="F")
            assert result["category"] == level

        assert get_category(-40, f"sports_{region}")["category"] == "green"
        assert get_category(60, f"sports_{region}")["category"] == "black"

    for workload, settings in rules["workers"]["workloads"].items():
        assert settings["unit"] == "C" and settings["source"]

        for status, limit in settings["limits"].items():
            name = f"workers_{workload}_{status}"

            assert get_category(limit - 0.01, name)["category"] == "below_limit"
            assert get_category(limit, name)["category"] == "review"

    # 86°F equals 30°C.
    assert (
        get_category(86, "sports_2", unit="F")["category"]
        == get_category(30, "sports_2")["category"]
    )

    try:
        get_category(30, "sports_99")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid rule set was accepted")

    print("Rules and boundaries: passed")


def run_check(args):
    check_rules()

    location = ZoneInfo(args.timezone)

    first_day = date.fromisoformat(args.start)
    last_day = date.fromisoformat(args.end)

    if first_day > last_day:
        raise ValueError("Start date must be on or before end date")

    is_detroit = (
        args.latitude == DETROIT_LAT
        and args.longitude == DETROIT_LON
    )

    region = args.region

    if region is None:
        if not is_detroit:
            raise ValueError(
                "For another location, specify --region 1, 2 or 3"
            )
        region = 2

    # Fetch extra UTC days so we don't lose hours near local midnight.
    weather = fetch_history(
        args.latitude,
        args.longitude,
        first_day - timedelta(days=1),
        last_day + timedelta(days=1)
    )

    readings = calculate_hourly_wbgt(
        weather, args.latitude, args.longitude
    )

    print(f"\nHourly estimated WBGT | {args.timezone} | sports region {region}")
    print("Advisory guidance only; not an on-site measurement or state law.")
    print("Times are LOCAL. weather.py must request timezone='GMT'.\n")

    daily = {}

    for hour in readings:

        timestamp = datetime.fromisoformat(
            hour["time"].replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        local = timestamp.astimezone(location)

        # Only show readings from the requested local dates.
        if not first_day <= local.date() <= last_day:
            continue

        wbgt = hour["wbgt"]

        if not isinstance(wbgt, (int, float)) or not math.isfinite(wbgt):
            raise ValueError(f"Invalid WBGT at {hour['time']}")

        # wbgt.py may already round to 0.1°C.
        # Do not round again before choosing the category.
        result = get_category(wbgt, f"sports_{region}")

        day = local.date().isoformat()

        if day not in daily:
            daily[day] = []
            print(f"\n{day}")

        daily[day].append((wbgt, result["category"], local.hour))

        print(
            f"  {local:%I:%M %p}  "
            f"{wbgt:5.1f}°C  "
            f"{result['label']}"
        )

    print("\nDaily summary (local time)")

    for day in sorted(daily):
        points = daily[day]

        peak = max(points, key=lambda row: row[0])
        lowest = min(points, key=lambda row: row[0])
        counts = Counter(row[1] for row in points)

        print(
            f"{day}: low {lowest[0]:.1f}°C; "
            f"high {peak[0]:.1f}°C ({peak[1]}); "
            f"{len(points)} readings; {dict(counts)}"
        )

        # Normal days have 24 hours. DST days may have 23 or 25.
        midnight = datetime.combine(
            date.fromisoformat(day),
            datetime.min.time(),
            location
        )

        next_midnight = datetime.combine(
            date.fromisoformat(day) + timedelta(days=1),
            datetime.min.time(),
            location
        )

        expected = int(
            (
                next_midnight.astimezone(timezone.utc)
                - midnight.astimezone(timezone.utc)
            ).total_seconds() / 3600
        )

        if len(points) != expected:
            print(
                f"  WARNING: expected {expected} hourly readings, "
                f"got {len(points)}"
            )

    total_days = (last_day - first_day).days + 1

    if len(daily) != total_days:
        print(
            f"WARNING: expected {total_days} calendar days "
            f"but got {len(daily)}"
        )

    if not daily:
        raise RuntimeError("No local hourly readings returned")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="FirstHeat historical WBGT Day 1 check"
    )

    parser.add_argument("--latitude", type=float, default=DETROIT_LAT)
    parser.add_argument("--longitude", type=float, default=DETROIT_LON)
    parser.add_argument("--timezone", default="America/Detroit")
    parser.add_argument("--region", type=int, choices=(1, 2, 3))
    parser.add_argument("--start", default="2024-06-15")
    parser.add_argument("--end", default="2024-06-19")

    run_check(parser.parse_args())
