import os
import re
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
NOMINATIM_HEADERS = {
    "User-Agent": "WeatherApp/1.0 (student project; contact: local user)",
    "Accept-Language": "en",
}
SETTLEMENT_TYPES = {
    "city",
    "town",
    "village",
    "hamlet",
    "municipality",
    "borough",
    "suburb",
    "quarter",
    "neighbourhood",
}
REJECTED_TYPES = {
    "country",
    "continent",
    "state",
    "region",
    "province",
    "county",
    "postcode",
    "highway",
    "road",
    "building",
    "house",
    "amenity",
    "shop",
    "tourism",
    "office",
    "aeroway",
    "natural",
    "waterway",
    "peak",
    "island",
}
NAME_FILLER = {
    "city",
    "town",
    "village",
    "hamlet",
    "municipality",
    "borough",
    "greater",
    "of",
    "the",
    "st",
    "saint",
    "district",
    "metro",
    "metropolitan",
}
EMOJI_MAP = {
    "sunny": "☀️",
    "clear": "☀️",
    "partly cloudy": "⛅",
    "cloudy": "☁️",
    "overcast": "☁️",
    "mist": "🌫️",
    "fog": "🌫️",
    "rain": "🌧️",
    "snow": "❄️",
    "thunder": "⛈️",
}


def normalize_name(value):
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()
    value = value.replace("saint ", "st ").replace("st. ", "st ")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def query_tokens(value):
    return [token for token in normalize_name(value).split() if token]


def names_match(query, *candidates):
    query_norm = normalize_name(query)
    query_words = query_tokens(query)
    if not query_norm or not query_words:
        return False

    for candidate in candidates:
        candidate_norm = normalize_name(candidate)
        if not candidate_norm:
            continue
        if query_norm == candidate_norm:
            return True

        candidate_words = candidate_norm.split()
        candidate_set = set(candidate_words)
        if not all(word in candidate_set for word in query_words):
            continue

        extra = candidate_set - set(query_words) - NAME_FILLER
        if not extra:
            return True
    return False


def settlement_label(place):
    address = place.get("address") or {}
    for key in ("city", "town", "village", "hamlet", "municipality", "borough"):
        if address.get(key):
            return address[key], key
    name = place.get("name") or ""
    addresstype = (place.get("addresstype") or place.get("type") or "").lower()
    if addresstype in SETTLEMENT_TYPES and name:
        return name, addresstype
    return None, None


def is_real_settlement(place, query):
    if not isinstance(place, dict):
        return False

    addresstype = (place.get("addresstype") or "").lower()
    place_type = (place.get("type") or "").lower()
    category = (place.get("category") or place.get("class") or "").lower()

    if addresstype in REJECTED_TYPES or place_type in REJECTED_TYPES:
        return False
    if category in REJECTED_TYPES:
        return False

    label, label_type = settlement_label(place)
    if not label:
        return False

    if label_type not in SETTLEMENT_TYPES and addresstype not in SETTLEMENT_TYPES:
        if not (category == "place" and place_type in SETTLEMENT_TYPES):
            return False

    display_name = place.get("display_name") or ""
    namedetails = place.get("namedetails") or {}
    return names_match(
        query,
        place.get("name"),
        label,
        namedetails.get("name"),
        namedetails.get("name:en"),
        display_name.split(",")[0],
    )


def lookup_place(query):
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "namedetails": 1,
        "limit": 5,
        "featureType": "settlement",
    }
    response = requests.get(
        NOMINATIM_SEARCH_URL,
        params=params,
        headers=NOMINATIM_HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()
    if not isinstance(results, list):
        raise ValueError("The geocoding service returned an invalid response.")

    for place in results:
        if is_real_settlement(place, query):
            return place
    return None


def condition_emoji(condition):
    for weather, emoji in EMOJI_MAP.items():
        if weather in condition:
            return emoji
    return "🌤️"


def format_local_time(timestamp, utc_offset):
    local_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    local_time += timedelta(seconds=utc_offset)
    return local_time.strftime("%I:%M %p")


def show_weather(place, query, api_key):
    response = requests.get(
        OPENWEATHER_URL,
        params={
            "lat": place["lat"],
            "lon": place["lon"],
            "appid": api_key,
            "units": "metric",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    current = data["main"]
    weather = data["weather"][0]
    system = data["sys"]
    utc_offset = data["timezone"]
    label, _ = settlement_label(place)
    display_name = label or place.get("name") or query
    condition = weather["description"].lower()
    wind_kmh = round(data["wind"]["speed"] * 3.6, 1)

    print(f"\n        ----------- {display_name} ------------")
    print(f"   Weather: {condition_emoji(condition)} {condition.title()}")
    print(f"   Temperature: 🌡️ {current['temp']}°C")
    print(
        f"   Humidity: 💧 {current['humidity']}%"
        f" | Wind speed: 🌬️ {wind_kmh} km/h"
    )
    print(
        f"   Sunrise: 🌅 {format_local_time(system['sunrise'], utc_offset)}"
        f" | Sunset: 🌇 {format_local_time(system['sunset'], utc_offset)}"
    )
    print("      " + "-" * 35)


def print_not_a_place():
    print("\nNot a real place.")
    print("      " + "-" * 35)


def main():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Missing OPENWEATHER_API_KEY. Add it to day-2/.env and try again.")
        return

    print("\n" + "    ============WEATHER APP============")
    print("       Welcome to my weather app")

    cities = input("Enter city names separated by commas: ").split(",")
    lookup_count = 0

    for city in cities:
        city = city.strip()
        if not city:
            continue

        if lookup_count:
            time.sleep(1)
        lookup_count += 1

        try:
            place = lookup_place(city)
        except requests.RequestException:
            print("\nCould not contact the geocoding service. Please try again.")
            continue
        except (KeyError, TypeError, ValueError):
            print("\nThe geocoding service returned invalid place data.")
            continue

        if not place:
            print_not_a_place()
            continue

        try:
            show_weather(place, city, api_key)
        except requests.RequestException:
            print(f"\nCould not fetch weather for {city}. Please try again.")
        except (KeyError, IndexError, TypeError, ValueError):
            print(f"\nThe weather service returned invalid data for {city}.")


if __name__ == "__main__":
    main()
