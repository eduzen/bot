import os
from datetime import datetime
from typing import Any

import httpx
import logfire
import pytz

ow_token = os.getenv("openweathermap_token")

client = httpx.AsyncClient()

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather/"

WEATHER_EMOJIS = {
    "clear": "🌞",
    "rain": "🌧",
    "clouds": "⛅️",
    "snow": "❄️",
    "extreme": "⛈",
    "tornado": "🌪",
    "thunder": "⚡",
    "mist": "🌫",
    "drizzle": "🌧",
    "haze": "🌫",
    "fog": "🌫",
}


def get_timezone(city: str) -> str:
    city = city.replace(" ", "_").lower()
    if "," in city:
        city = city.split(",")[0]

    for timezone in pytz.all_timezones:
        if city in timezone.lower():
            return timezone
        elif city == "dallas":
            return "America/Chicago"

    return "UTC"


def get_sun_times(data: dict[str, Any], city: str) -> tuple:
    tz_name = get_timezone(city)
    tz = pytz.timezone(tz_name)
    sunrise = datetime.fromtimestamp(data["sunrise"], tz).strftime("%H:%M")
    sunset = datetime.fromtimestamp(data["sunset"], tz).strftime("%H:%M")
    return sunrise, sunset


async def get_klima(city_name: str = "Amsterdam,nl") -> str:
    params = {
        "q": city_name,
        "APPID": ow_token,
        "units": "metric",
    }
    r = await client.get(OPENWEATHERMAP_URL, params=params)
    msg = "No pudimos conseguir el clima"

    if r.status_code != 200:
        return msg

    data = r.json()
    if not data:
        return msg

    try:
        sunrise_time, sunset_time = get_sun_times(data["sys"], data["name"])
    except Exception as e:
        logfire.warn(f"error in astral time calculation: {e}")
        sunrise_time = "?"
        sunset_time = "?"

    weather = data["weather"][0]["main"].lower()
    description = data["weather"][0]["description"]
    try:
        weather_emoji = WEATHER_EMOJIS[weather]
    except KeyError:
        weather_emoji = weather

    msg = (
        f"*Clima en {data['name']}* {weather_emoji} \n"
        f"{weather.capitalize()}: {description.capitalize()}\n"
        f"Temp {data['main']['temp']} °C humedad {data['main']['humidity']}%\n"
        f"Max {data['main']['temp_max']} °C "
        f"Min {data['main']['temp_min']} °C\n"
        f"Sunrise: {sunrise_time} Sunset: {sunset_time}\n"
    )
    return msg
