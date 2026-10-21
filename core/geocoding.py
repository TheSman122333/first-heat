
"Find US cities using Open-Meteo's geocoding service"

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

SEARCH_URL = "https://geocoding-api.open-meteo.com/v1/search"


def search_cities(name, count=10):
    "return city names, states, coordinates and time zones"

    name = name.strip()

    if len(name) < 2:
        return []

    if not 1 <= count <= 100:
        raise ValueError("COUNT MUST BE IN BETWEEN 1 and 100")

    query = urlencode({
        "name": name,
        "count": count,
        "countryCode": "US"
    })

    try:
        with urlopen(f"{SEARCH_URL}?{query}", timeout=15) as response:
            data = json.load(response)

    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"City search failed: {error}") from error

    if data.get("error"):
        raise RuntimeError(data.get("reason", "City search failed"))

    cities = []

    for city in data.get("results", []):

        if city.get("country_code") != "US":
            continue

        if not all(
            key in city
            for key in ("name", "latitude", "longitude", "timezone")
        ):
            continue

        cities.append({
            "name": city["name"],
            "state": city.get("admin1", ""),
            "latitude": float(city["latitude"]),
            "longitude": float(city["longitude"]),
            "timezone": city["timezone"]
        })

    return cities
