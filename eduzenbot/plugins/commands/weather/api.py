import os
from datetime import datetime
from typing import Any

import httpx
import logfire
import pytz
from bs4 import BeautifulSoup
from cachetools import TTLCache, cached

ow_token = os.getenv("openweathermap_token")

client = httpx.Client()


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


lanacion = "http://servicios.lanacion.com.ar/pronostico-del-tiempo/capital-federal/capital-federal"

headers = {
    "Host": "servicios.lanacion.com.ar",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather/"


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


@cached(cache=TTLCache(maxsize=2048, ttl=360))
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
    return f"{msg}\nBy api.openweathermap.org"


@cached(cache=TTLCache(maxsize=2048, ttl=360))
async def get_weather() -> str:
    r = await client.get(lanacion, headers=headers)
    r.encoding = "utf-8"
    msg = "No pudimos conseguir el clima"

    if r.status_code != 200:
        return msg

    data = r.text
    if not data:
        return msg

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("div", {"class": "floatFix cuadroTemp"})

    if not data:
        return msg

    msg = []
    for element in data[0].children:
        text = element.get_text()
        text = text.replace("ST", " ST")
        text = text.replace("%", "% ")
        text = text.replace("km/h", "km/h ")
        text = text.replace("hPa", "hPa\n")
        msg.append(text)

    msg = "\n".join(msg)
    return f"Capital federal: {msg}\nBy lanacion.com.ar"
