import logging
import requests
from collections import defaultdict
import unicodedata
from emoji import emojize
from bs4 import BeautifulSoup
from eduzen_bot.keys import APP_ID

logger = logging.getLogger(__name__)

API = "https://openexchangerates.org/api/latest.json"
OTHER_API = "http://ws.geeklab.com.ar/dolar/get-dolar-json.php"
BNC = "http://www.bna.com.ar/"
DOLAR_HOY = "http://dolarhoy.com/Usd"
ROFEX = "http://www.ambito.com/economia/mercados/indices/rofex/"

dolar = emojize(":dollar:", use_aliases=True)
euro = "\n🇪🇺"
real = "\n🇧🇷"
punch = emojize(":punch:", use_aliases=True)


def get_response(url):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return

    return response


def process_bcn(response):
    data = response.text
    if not data:
        return False

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table", {"class": "table cotizacion"})

    if not data:
        return False

    data = data[0].get_text().strip().replace("\n", " ").replace("  ", "\n")
    data = data.replace("\n ", dolar, 1).replace("\n ", euro, 1).replace("\n ", real, 1)
    data = data.replace("U.S.A", "")
    data = f"{data}\n(*) cotización cada 100 unidades.\n{punch} by bna.com.ar"

    return data

def normalize(tag):
    """Normalize a single tag: remove non valid chars, lower case all."""

    tag_stripped = tag.lower().replace("banco", "").replace(" - ", "-").strip()
    value = unicodedata.normalize("NFKD", tag_stripped)
    value = value.encode('ascii', 'ignore').decode('utf-8')
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
    for table in response_soup:
        # Get cotizaciones
        for row_cotizacion in table.tbody.find_all('tr'):
            banco, compra, venta = (item.get_text() for item in row_cotizacion.find_all('td'))
            banco = normalize(banco)
            cotizaciones[banco]['compra'] = compra
            cotizaciones[banco]['venta'] = venta

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
    return MONOSPACE.format('\n'.join(
            "{:19} | {:7} | {:7}".format(banco, valor['compra'], valor['venta'])
            for banco, valor in cotizaciones.items()
        ))


def process_dolarfuturo(response):
    response.encoding = 'utf-8'
    data = response.text
    if not data:
        return False

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table")

    if not data:
        return False

    cotizaciones = []
    for table in data:
        for trs in table.find_all('tr'):
            td = [item.get_text() for item in trs.find_all('th')]

            for item in trs.find_all('td'):
                text = item.get_text().replace('Dólar', '').strip()
                td.append(text)

            cotizaciones.append(
                " ".join(td)
            )
    result = "\n".join(cotizaciones)
    data = f"```\n{result}```\n{punch} by rofex by ambito"

    return data


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

    if r and r.status_code == 200:
        return process_bcn(r)

    else:
        return "Banco nación no responde 🤷‍♀"


def parse_dolarhoy():
    r = get_response(DOLAR_HOY)
    if r and r.status_code == 200:
        return process_dolarhoy(r)
    return "Dolarhoy hoy no responde 🤷‍♀"


def parse_dolarfuturo():
    r = get_response(ROFEX)
    if r and r.status_code == 200:
        return process_dolarfuturo(r)
    return "Rofex no responde 🤷‍♀"


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
