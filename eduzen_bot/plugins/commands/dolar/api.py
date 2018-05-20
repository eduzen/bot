import logging
import requests

from emoji import emojize
from bs4 import BeautifulSoup
from eduzen_bot.keys import APP_ID

logger = logging.getLogger(__name__)

API = "https://openexchangerates.org/api/latest.json"
OTHER_API = "http://ws.geeklab.com.ar/dolar/get-dolar-json.php"
BNC = "http://www.bna.com.ar/"

dolar = emojize(":dollar:", use_aliases=True)
euro = "\n🇪🇺"
real = "\n🇧🇷"
punch = emojize(":punch:", use_aliases=True)


def get_response(url):
    response = ""
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return

    return response


def parse_bnc():
    r = get_response(BNC)

    if r.status_code != 200:
        return False

    data = r.text
    if not data:
        return False

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table", {"class": "table cotizacion"})

    if not data:
        return False

    data = data[0].get_text().strip().replace("\n", " ").replace("  ", "\n")
    data = data.replace("\n ", dolar, 1).replace("\n ", euro, 1).replace("\n ", real, 1)
    data = data.replace("U.S.A", "")
    data = f"{data}\n(*) cotización cada 100 unidades.\n{punch} by http://www.bna.com.ar/"

    return data


def get_dollar():
    r = requests.get(API, params={"app_id": APP_ID})

    if r.status_code != 200:
        logger.error(
            "Something went wrong when it gets dollar. Status code: %s", r.status_code
        )
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
    r = requests.get(OTHER_API)

    if r.status_code != 200:
        logger.error(
            "Something went wrong when it gets dollar. Status code: %s", r.status_code
        )
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api no devolvió info!"
        return text

    text = f"USD oficial {data['libre']} - Blue {data['blue']}\nby http://ws.geeklab.com.ar"
    return text
