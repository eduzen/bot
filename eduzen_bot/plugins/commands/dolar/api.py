import calendar
import logging
import os
import re
import unicodedata
from collections import defaultdict, namedtuple

import requests
from bs4 import BeautifulSoup
from emoji import emojize

APP_ID = os.getenv("APP_ID")

logger = logging.getLogger("rich")

API = "https://openexchangerates.org/api/latest.json"
OTHER_API = "http://ws.geeklab.com.ar/dolar/get-dolar-json.php"
BNC = "http://www.bna.com.ar/"
DOLAR_HOY = "http://dolarhoy.com/Usd"
ROFEX = "https://www.rofex.com.ar/"
AMBITO_FUTURO = "https://mercados.ambito.com//dolarfuturo/datos"
BLUELYTICS = "https://api.bluelytics.com.ar/v2/latest"

client = requests.Session()

dolar = emojize(":dollar:", use_aliases=True)
euro = "🇪🇺"
real = "🇧🇷"
punch = emojize(":punch:", use_aliases=True)
DOLAR_REGEX = re.compile(r"DLR(\d{2})(\d{4})")
Contrato = namedtuple("Contrato", ["mes", "año", "valor"])


def trim(text, limit=11) -> str:
    """Trim and append . if text is too long. Else return it unmodified"""
    return f"{text[:limit]}." if len(text) > limit else text


def get_response(url, verify=True):
    try:
        response = client.get(url, verify=verify)
    except requests.exceptions.ConnectionError:
        return

    return response


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


def process_bcn(data):
    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table", {"class": "table cotizacion"})

    if not data:
        return ""

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


def prettify_rofex(contratos):
    values = "\n".join(f"{year} {month:<12} | {value[:5]}" for month, year, value in contratos)
    header = "  Dólar  | Valor\n"
    return f"```{header}{values}```" if contratos is not None else "EMPTY_MESSAGE"


def process_dolarfuturo(response):
    response.encoding = "utf-8"
    data = response.text
    if not data:
        return False
    soup = BeautifulSoup(data, "html.parser")
    data = soup.find("table", class_="table-rofex")
    cotizaciones = data.find_all("tr")[1:]  # Exclude header

    if not data:
        return False

    contratos = []
    for cotizacion in cotizaciones:
        contrato, valor, _, _, _ = cotizacion.find_all("td")
        month, year = DOLAR_REGEX.match(contrato.text).groups()
        month = calendar.month_name[int(month)]
        contratos.append(Contrato(month, year, valor.text))

    return prettify_rofex(contratos)


def process_dolarhoy(response):
    data = response.text
    if not data:
        return False

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table")

    if not data:
        return False

    cotizaciones = get_cotizaciones(data)

    data = pretty_print_dolar(cotizaciones)

    return data


def parse_bnc():
    r = get_response(BNC)

    if r and r.status_code == 200 and r.text:
        return process_bcn(r.text)

    else:
        return "Banco nación no responde 🤷‍♀"


def process_bluelytics(response):
    try:
        data = response.json()
        oficial = data["oficial"]
        blue = data["blue"]
        eur = data["oficial_euro"]
        data = (
            "Bluelytics:\n"
            f"💵 dolar {oficial['value_buy']} - {oficial['value_sell']}\n"
            f"🌳 blue {blue['value_buy']} - {blue['value_sell']}\n"
            f"🇪🇺 euro {eur['value_buy']} - {eur['value_sell']}\n"
            f"🌳 blue {data['blue_euro']['value_buy']} - {data['blue_euro']['value_sell']}\n"
        )
        return data
    except Exception:
        logger.exception("bluelytics")


def get_bluelytics():
    r = get_response(BLUELYTICS)
    if r and r.status_code == 200:
        return process_bluelytics(r)
    return "Bluelytics no responde 🤷‍♀"


def parse_dolarhoy():
    r = get_response(DOLAR_HOY)
    if r and r.status_code == 200:
        return process_dolarhoy(r)
    return "Dolarhoy hoy no responde 🤷‍♀"


def process_ambito_dolarfuturo(response):
    data = response.json()
    datos = []
    for i in data:
        mes = i["contrato"].replace("Dólar ", "")
        venta = i["venta"]
        compra = i["compra"]
        datos.append(f"{mes:<15} {venta:<7} {compra:<5}")
    valores = "\n".join(datos)
    return f"```       Mes {dolar}   Compra | Venta \n{valores}```"


def parse_dolarfuturo():
    r = get_response(AMBITO_FUTURO)
    if r and r.status_code == 200:
        return process_ambito_dolarfuturo(r)
    return "Rofex no responde 🤷‍♀"


def get_dollar():
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


def get_dolar_blue():
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
