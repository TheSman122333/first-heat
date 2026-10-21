"""This file is meant to fetch hourly data from the Open-Meteo endpoint hourly"""

#imports
from __future__ import annotations

import json
import math
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

#defining endpoints

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

#options

OPTIONS = (
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "shortwave_radiation",
)


def get_weather_data(latitude,longitude,url=FORECAST_URL,**extra_params):
    "Pull hourly readings (with the specified options)"

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be in between -90 and 90")

    if not -180 <=longitude<=180: 
        raise ValueError("Longitude must be in between -180 and 180")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(OPTIONS),
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms",
        "timezone": "GMT"
    }

    params.update(extra_params)

    request_url = url + "?" + urlencode(params)

    try:
        with urlopen(request_url, timeout=15) as response:
            data = json.load(response)
    except (URLError, HTTPError, TimeoutError) as error:
        raise RuntimeError(
            f"COULD NOT GET WEATHER DATA {error}"
        ) from error

    if data.get("error"):
        raise RuntimeError(data.get("reason","WEATHER API ERROR"))

    hourly = data.get("hourly")

    if not hourly or "time" not in hourly:
        raise ValueError("NO HOURLY DATA RETURNED")

    times = hourly["time"]

    #each field should have 1 value for every hour

    for field in OPTIONS:
        if field not in hourly or len(hourly[field]) != len(times):
            raise ValueError(f"MISSING HOURLY DATA FOR {field}")

    weather_rows = []

    for i, time in enumerate(times):
        hour = {"time":time}

        for field in OPTIONS:
            hour[field] = hourly[field][i]
        weather_rows.append(hour)

    return weather_rows

def fetch_forecast(latitude,longitude,days=1):
    "Gets the next few days' forecast"
    if not isinstance (days, int) or not 1 <= days <= 16:
        raise ValueError("DAYS MUST BE IN BETWEEN 1 AND 16")

    return get_weather_data(
        latitude,
        longitude,
        FORECAST_URL,
        forecast_days=days
    )



def fetch_history(latitude, longitude, start_date, end_date):
    "Gets previous history (using archive)"

    if isinstance(start_date,date):
        start_date = start_date.isoformat()

    if isinstance(end_date, date):
        end_date = end_date.isoformat()

    start = date.fromisoformat(start_date)
    end= date.fromisoformat(end_date)

    if start > end:
        raise ValueError("START CANNOT BE AFTER END")

    return get_weather_data(
        latitude,
        longitude,
        url=ARCHIVE_URL,
        start_date=start.isoformat(),
        end_date=end.isoformat()
    )


def fetch_hourly_weather(
    latitude, longitude,
    start_date=None, end_date=None, 
    forecast_days=1
):
    "Historical weather or a forecast for today"

    if start_date is None and end_date is None:
        return fetch_forecast(latitude, longitude,forecast_days)

    if start_date is None or end_date is None:
        raise ValueError("BOTH VALUES ARE NEEDED")

    return fetch_history(
        latitude,longitude,start_date,end_date
    )


if __name__ == "__main__":

    latitude = 42.3314
    longitude = -83.0458

    try:
        weather = fetch_history(
            latitude,
            longitude,
            "2024-06-19",
            "2024-06-19"
        )

        print(f"Found {len(weather)} hourly readings\n")

        for hour in weather:
            print(
                hour["time"],
                "Temp:", hour["temperature_2m"], "degrees C",
                "Humidity:", hour["relative_humidity_2m"], "%",
                "Wind:", hour["wind_speed_10m"], "m/s",
                "Solar:", hour["shortwave_radiation"], "W/m squared"
            )

    except (RuntimeError, ValueError) as error:
        print("Weather fetch failed:", error)