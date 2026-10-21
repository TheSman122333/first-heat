from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from core.rules import get_category


DETROIT = ZoneInfo("America/Detroit")
LATITUDE = 42.3314
LONGITUDE = -83.0458
SPORTS_REGION = 2
WEATHER_SOURCE = "Open-Meteo hourly forecast"


def utc_time(value):
    "weather timestamps are UTC because weather.py requests GMT"

    when = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    return when.astimezone(timezone.utc)


def summarize_today(readings, now_utc=None, region=SPORTS_REGION):
    "find the current hour and highest WBGT for today's local date"

    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    if now_utc.tzinfo is None:
        raise ValueError("CURRENT TIME MUST INCLUDE A TIMEZONE")

    now_utc = now_utc.astimezone(timezone.utc)
    local_today = now_utc.astimezone(DETROIT).date()

    current_hour = now_utc.replace(
        minute=0, second=0, microsecond=0
    )

    today = []
    current = None

    for reading in readings:

        when_utc = utc_time(reading["time"])
        local_time = when_utc.astimezone(DETROIT)

        if local_time.date() != local_today:
            continue

        today.append((local_time, reading))

        #match in UTC to avoid confusion during dst
        if when_utc == current_hour:
            current = (local_time, reading)

    if not today:
        raise ValueError("NO FORECAST AVAILABLE")

    if current is None:
        raise ValueError("CURRENT HOUR IS MISSING FROM FORECAST")

    peak_time, peak = max(
        today,
        key=lambda item: item[1]["wbgt"]
    )

    current_time, current_reading = current

    current_rules = get_category(
        current_reading["wbgt"],
        f"sports_{region}"
    )

    peak_rules = get_category(
        peak["wbgt"],
        f"sports_{region}"
    )

    return {
        "current_time": current_time,
        "current_wbgt": current_reading["wbgt"],
        "category": current_rules["category"],
        "guidance": current_rules["guidance"],
        "peak_time": peak_time,
        "peak_wbgt": peak["wbgt"],
        "peak_category": peak_rules["category"],
        "region": region,
        "weather_source": WEATHER_SOURCE,
        "rule_source": current_rules["source"]
    }


def fetch_today_summary():
    "fetch the weather and calculate today's WBGT"

    from core.weather import FORECAST_URL, get_weather_data
    from core.wbgt import calculate_hourly_wbgt

    #detroits local day overlaps UTC dates
    #include yesterday so evening requests keep the full local day
    weather = get_weather_data(
        LATITUDE,
        LONGITUDE,
        FORECAST_URL,
        forecast_days=2,
        past_days=1
    )

    hourly_wbgt = calculate_hourly_wbgt(
        weather,
        LATITUDE,
        LONGITUDE
    )

    return summarize_today(hourly_wbgt)
