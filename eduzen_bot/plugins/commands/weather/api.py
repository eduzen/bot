import os

import requests
import structlog
from bs4 import BeautifulSoup

openweathermap_token = os.getenv("openweathermap_token")

logger = structlog.get_logger(filename=__name__)

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

openweathermap = "https://api.openweathermap.org/data/2.5/weather?q={city_name}&APPID={token}&units=metric"


def get_klima(city_name="München"):
    r = requests.get(openweathermap.format(city_name=city_name, token=openweathermap_token))
    msg = "No pudimos conseguir el clima"

    if r.status_code != 200:
        return msg

    data = r.json()
    if not data:
        return msg

    msg = (
        f"*Das Klima in {city_name}*\n"
        f"Temperatur {data['main']['temp']} °C regentage {data['main']['humidity']}%\n"
        f"Temperaturmaximum {data['main']['temp_max']} °C\n"
        f"Temperaturminimum {data['main']['temp_min']} °C\n"
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
