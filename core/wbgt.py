
"Calculate estimated WBGT using the Open-Meteo weather data."


""""LIMITATIONS SO FAR!!!! THIS IS FORCED TO USE 1013.25 hPa, STANDARD SEA LEVEL, TRY TO MAYBE MAKE IT WORK BY DYNAMICALLY ADJUSTING ATM PRESSURE, ALSO URBAN VS RURAL."""
"""https://pypi.org/project/lwbgt/"""
from datetime import datetime
from lwbgt import Input, calculate


def calculate_wbgt(hour, latitude, longitude, urban=True):
    "Calculate WBGT for one hour of data"

    #forced to use GMT timezone "utc"
    time = datetime.fromisoformat(
        hour["time"].replace("Z", "+00:00")
    )

    #inputs
    weather = Input(
        year=time.year,
        month=time.month,
        day=time.day,
        hour=time.hour,
        minute=time.minute,
        gmt_offset_hours=0,
        averaging_minutes=60,
        latitude_deg_north=latitude,
        longitude_deg_east=longitude,

        air_temperature_c=hour["temperature_2m"],
        relative_humidity_percent=hour["relative_humidity_2m"],
        wind_speed_m_s=hour["wind_speed_10m"],
        solar_w_m2=hour["shortwave_radiation"],

        pressure_hpa=1013.25,
        wind_height_m=10,
        vertical_temperature_difference_c=1,
        urban=int(urban)
    )

    result = calculate(weather, psychrometric=False)

    if result.status != 0:
        raise ValueError(
            f"Could not calculate WBGT for {hour['time']}"
        )

    return {
        **hour,
        "wbgt": result.wbgt_c,
        "globe_temperature": round(result.globe_temperature_c, 1),
        "natural_wet_bulb": round(result.natural_wet_bulb_c, 1)
    }


def calculate_hourly_wbgt(weather_rows, latitude, longitude, urban=True):
    #calculate hourly

    results = []

    for hour in weather_rows:
        results.append(
            calculate_wbgt(hour, latitude, longitude, urban)
        )

    return results
