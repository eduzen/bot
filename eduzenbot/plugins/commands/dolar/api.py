import logging
import os
import re
import unicodedata
from collections import defaultdict, namedtuple

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache, cached
from emoji import emojize

APP_ID = os.getenv("APP_ID")

logger = logging.getLogger("rich")

API = "https://openexchangerates.org/api/latest.json"
OTHER_API = "http://ws.geeklab.com.ar/dolar/get-dolar-json.php"
BNC = "https://www.bna.com.ar/"
BLUELYTICS = "https://api.bluelytics.com.ar/v2/latest"

client = requests.Session()

dolar = emojize(":dollar:")
euro = "🇪🇺"
real = "🇧🇷"
punch = emojize(":punch:")
DOLAR_REGEX = re.compile(r"DLR(\d{2})(\d{4})")
Contrato = namedtuple("Contrato", ["mes", "año", "valor"])


def trim(text, limit=11) -> str:
    """Trim and append . if text is too long. Else return it unmodified"""
    return f"{text[:limit]}." if len(text) > limit else text


def extract(data):
    if not data:
        return ""

    values = []
    for text in data.get_text().strip().split("\n"):
        text = text.replace("\n", "").strip()
        if not text:
            continue

        if "Dolar" in text:
            value = f"{dolar} {text.replace('U.S.A', '')}"
        elif "Euro" in text:
            value = f"{euro} {text}"
        elif "Real" in text:
            value = f"{real} {text}"
        elif "/" in text:
            value = text
        else:
            try:
                value = float(text.replace(",", "."))
                value = f"{value:,.2f}"
            except (TypeError, ValueError):
                value = text

        values.append(value)

    return values


def process_bcn(data: str) -> str:
    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table", {"class": "table cotizacion"})

    if not data:
        return "Banco nacion changed his html."

    data = extract(data[0])
    head = " ".join(data[:3]).strip()
    dolar = " ".join(data[3:6]).strip()
    euro = " ".join(data[6:9]).strip()
    real = " ".join(data[9:]).strip()
    data = f"{head}\n" f"{dolar}\n" f"{euro}\n" f"{real}\n" f"(*) cotización cada 100 unidades.\n{punch} by bna.com.ar"

    return data


def normalize(tag):
    """Normalize a single tag: remove non valid chars, lower case all."""
    value = unicodedata.normalize("NFKD", tag)
    value = value.encode("ascii", "ignore").decode("utf-8")
    return value.capitalize()


def get_cotizaciones(response_soup):
    """Returns a dict of cotizaciones with banco as keys and exchange rate as value.

    {
        "Banco Nación": {
            "Compra": "30.00",
            "Venta": "32.00",
        },
        "Banco Galicia": {
            "Compra": "31.00",
            "Venta": "33.00",
        }
    }

    """
    cotizaciones = defaultdict(dict)
    table = response_soup[0]
    # Get cotizaciones
    for row_cotizacion in table.tbody.find_all("tr"):
        banco, compra, venta = (item.get_text() for item in row_cotizacion.find_all("td"))
        banco = banco.lower().replace("banco", "").replace(" - ", "-").strip()
        banco = normalize(banco)
        cotizaciones[banco]["compra"] = compra
        cotizaciones[banco]["venta"] = venta

    return cotizaciones


def pretty_print_dolar(cotizaciones):
    """Returns dolar rates separated by newlines and with code markdown syntax.
    ```
    Banco Nacion  | $30.00 | $40.00
    Banco Galicia | $30.00 | $40.00
    ...
    ```
    """
    MONOSPACE = "```\n{}\n```"
    return MONOSPACE.format(
        "\n".join(
            "{:12} | {:7} | {:7}".format(trim(banco), valor["compra"], valor["venta"])
            for banco, valor in sorted(cotizaciones.items())
        )
    )


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def parse_bnc() -> str:
    try:
        response = client.get(BNC, verify=True)
        response.raise_for_status()

        if response.status_code != 200:
            raise Exception("Banco nación no responde 🤷‍♀")

        data = response.text
        return process_bcn(data)
    except Exception:
        logger.exception("Error getting BNC")

    return "Banco nación no responde 🤷‍♀"


def process_bluelytics(data: dict) -> str:
    oficial = data["oficial"]
    blue = data["blue"]
    eur = data["oficial_euro"]
    oficial_venta = oficial["value_sell"]
    blue_venta = blue["value_sell"]
    brecha = round(((blue_venta / oficial_venta) - 1) * 100, 2)
    data = (
        "🏦 Oficial:\n"
        f"💵 Dólar {oficial['value_buy']} - {oficial_venta}\n"
        f"🇪🇺 Euro {eur['value_buy']} - {eur['value_sell']}\n"
        "\n🌳 Blue:\n"
        f"💵 Dólar {blue['value_buy']} - {blue_venta}\n"
        f"🇪🇺 Euro {data['blue_euro']['value_buy']} - {data['blue_euro']['value_sell']}\n"
        f"📊 *Brecha Dolar*: {brecha}%"
    )
    return data


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def get_bluelytics() -> str:
    try:
        response = client.get(BLUELYTICS, verify=True)
        response.raise_for_status()
        if response.status_code != 200:
            raise Exception("Bluelytics no responde 🤷‍♀️ ")

        data = response.json()
        return process_bluelytics(data)
    except Exception:
        logger.exception("bluelytics")
    return "Bluelytics no responde 🤷‍♀️"


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def get_dollar() -> str:
    r = client.get(API, params={"app_id": APP_ID})

    if r.status_code != 200:
        logger.error("Something went wrong when it gets dollar. Status code: %s", r.status_code)
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api no devolvió info!"
        return text

    text = f"USD oficial {data['rates']['ARS']}\nby https://openexchangerates.org"
    return text


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def get_dolar_blue() -> str:
    r = client.get(OTHER_API)

    if r.status_code != 200:
        logger.error("Something went wrong when it gets dollar. Status code: %s", r.status_code)
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api no devolvió info!"
        return text

    text = f"USD libre {data['libre']} - Blue {data['blue']}\nby http://ws.geeklab.com.ar"
    return text
