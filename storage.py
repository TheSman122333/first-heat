
"Save location and region using Flet preferences"

import json
import math
from zoneinfo import ZoneInfo

KEY = "firstheat.settings.v1"


def default_settings():
    return {
        "name": "Detroit",
        "state": "Michigan",
        "latitude": 42.3314,
        "longitude": -83.0458,
        "timezone": "America/Detroit",
        "region": 2
    }


def check_settings(settings):

    if not isinstance(settings, dict):
        raise ValueError("SETTINGS MUST BE AN OBJECT")

    if settings.get("region") not in (1, 2, 3):
        raise ValueError("SPORTS REIGON MUST BE 1, 2, OR 3")

    if not isinstance(settings.get("name"), str) or not settings["name"].strip():
        raise ValueError("CITY IS MISSING")

    if not isinstance(settings.get("state"), str):
        raise ValueError("STATE IS MISSING")

    latitude = float(settings["latitude"])
    longitude = float(settings["longitude"])

    if not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise ValueError("INVALID LATITUDE")

    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise ValueError("INVALID LONGITUDE")

    ZoneInfo(settings["timezone"])

    return settings


async def load_settings(prefs):
    "use detroit if there are no saved settings"

    try:
        saved = await prefs.get(KEY)

        if saved:
            return check_settings(json.loads(saved))

        return default_settings()

    except (ValueError, TypeError, KeyError, OverflowError, OSError):
        return default_settings()


async def save_settings(prefs, settings):
    "save the current location and sports region"

    check_settings(settings)

    saved = await prefs.set(KEY, json.dumps(settings))

    if not saved:
        raise RuntimeError("COULDN'T SAVE SETTINGS")
