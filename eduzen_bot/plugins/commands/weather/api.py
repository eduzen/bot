import logging
import os
from datetime import datetime
from typing import Tuple

import requests
from astral import LocationInfo
from astral.sun import sun
from bs4 import BeautifulSoup

ow_token = os.getenv("openweathermap_token")

logger = logging.getLogger("rich")

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

openweathermap = f"https://api.openweathermap.org/data/2.5/weather?APPID={ow_token}&units=metric"


CITY_LOCATION = {
    "buenos aires" : LocationInfo("BA", "Argentina", "America/Buenos_Aires", -34.6037, -58.3816),
    "amsterdam" : LocationInfo("Amsterdam", "England", "Europe/Amsterdam", 52.3676,4.9041),
    "heidelberg,de" : LocationInfo("Heil", "England", "Europe/Berlin", 49.3988, 8.672)
}

def get_sun_times(city_name) -> Tuple[str, str]:
    """Calculates sunset and sunrise at current time at `city_name` city
    
    Args:
        `city_name`: must be a key of `CITY_LOCATION`

    Raises:
        KeyError: if `city_name` is not present at `CITY_LOCATION`
    """
    city = CITY_LOCATION[city_name]
    s = sun(city.observer, date=datetime.datetime.today().date())
    return s["sunrise"], s["sunset"]


def get_klima(city_name="München"):
    r = requests.get(f"{openweathermap}&q={city_name}")
    msg = "No pudimos conseguir el clima"

    if r.status_code != 200:
        return msg

    data = r.json()
    if not data:
        return msg

    try:
        sunrise_time, sunset_time = get_sun_times(city_name=city_name)
    except Exception as e:
        logger.warning(f"error in astral time calculation: {e}")
        sunrise_time = "?"
        sunset_time = "?"

    msg = (
        f"*Clima en {data['name']}*\n"
        f"Temp {data['main']['temp']} °C probabilidades de lluvia {data['main']['humidity']}%\n"
        f"Max {data['main']['temp_max']} °C\n"
        f"Min {data['main']['temp_min']} °C\n"
        f"Sunrise: {sunrise_time} \n"
        f"Sunset: {sunset_time}\n"
    )
    return f"{msg}\nBy api.openweathermap.org"


def get_weather():
    r = requests.get(lanacion, headers=headers)
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
