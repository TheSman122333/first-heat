
"DAY 3 US city search and lower-heat forecasts"

from core.geocoding import search_cities
from core.plan import fetch_week_plan
from storage import default_settings


#look for cities with the same name
print("\nSPRINGFIELD SEARCH")

states = set()

for city in search_cities("Springfield", count=30):

    if city["state"] not in states:
        states.add(city["state"])

        print(
            city["name"], "/",
            city["state"], "/",
            city["timezone"]
        )

    if len(states) == 4:
        break


#compare cities
phoenix = {
    "name": "Phoenix",
    "state": "Arizona",
    "latitude": 33.4484,
    "longitude": -112.074,
    "timezone": "America/Phoenix",
    "region": 3
}

for city in [default_settings(), phoenix]:

    print(
        f"\n7-DAY PLAN - {city['name']} "
        f"(region {city['region']})"
    )

    for day in fetch_week_plan(city):

        peak_f = day["peak_wbgt"] * 9 / 5 + 32

        if day["window"]:
            start, end = day["window"]
            lower_heat = f"{start:%I %p} - {end:%I %p}"

        else:
            lower_heat = "No lower-heat daytime window"

        print(
            day["date"],
            "/ Peak:", f"{peak_f:.1f} F",
            "/", day["peak_category"].title(),
            "/ Lower heat:", lower_heat
        )
