import httpx
import logfire
from bs4 import BeautifulSoup

from eduzenbot.decorators import async_cached

GEEKLAB_API = "http://ws.geeklab.com.ar/dolar/get-dolar-json.php"
BNC = "https://www.bna.com.ar/"
BLUELYTICS = "https://api.bluelytics.com.ar/v2/latest"

client = httpx.AsyncClient()

dolar = "🇺🇸"
euro = "🇪🇺"
real = "🇧🇷"
punch = "👊"


def _extract(data):
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


def _process_bcn(data: str) -> str:
    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table", {"class": "table cotizacion"})

    if not data:
        return "Banco nacion changed his html."

    data = _extract(data[0])

    # Add spaces between parts
    head = " ".join(data[:3]).strip()
    dolar = " ".join(data[3:6]).strip()
    euro = " ".join(data[6:9]).strip()
    real = " ".join(data[9:]).strip()

    result = f"{head}\n" f"{dolar}\n" f"{euro}\n" f"{real}\n" "(*) cotización cada 100 unidades.\n👊 by bna.com.ar"

    return result


def _process_bluelytics(data: dict) -> str:
    oficial = data["oficial"]
    blue = data["blue"]
    eur = data["oficial_euro"]
    oficial_venta = oficial["value_sell"]
    blue_venta = blue["value_sell"]
    brecha = round(((blue_venta / oficial_venta) - 1) * 100, 2)
    data: str = (
        "🏦 Oficial:\n"
        f"💵 Dólar {oficial['value_buy']} - {oficial_venta}\n"
        f"🇪🇺 Euro {eur['value_buy']} - {eur['value_sell']}\n"
        "\n🌳 Blue:\n"
        f"💵 Dólar {blue['value_buy']} - {blue_venta}\n"
        f"🇪🇺 Euro {data['blue_euro']['value_buy']} - {data['blue_euro']['value_sell']}\n"
        f"📊 *Brecha Dolar*: {brecha}%"
    )
    return data


@async_cached("get_banco_nacion")
async def get_banco_nacion() -> str:
    try:
        response = await client.get(BNC)
        response.raise_for_status()

        if response.status_code != 200:
            raise Exception("Banco nación no responde 🤷‍♀")

        data = response.text
        return _process_bcn(data)
    except Exception:
        logfire.exception("Error getting BNC")

    return "Banco nación no responde 🤷‍♀"


@async_cached("get_banco_nacion")
async def get_bluelytics() -> str:
    try:
        response = await client.get(BLUELYTICS)
        response.raise_for_status()
        if response.status_code != 200:
            raise Exception("Bluelytics no responde 🤷‍♀️ ")

        data = response.json()
        return _process_bluelytics(data)
    except Exception:
        logfire.exception("bluelytics")
    return "Bluelytics no responde 🤷‍♀️"


@async_cached("get_banco_nacion")
async def get_dolar_blue_geeklab() -> str:
    r = await client.get(GEEKLAB_API)
    if r.status_code != 200:
        logfire.error(f"Something went wrong when it gets dollar. Status code: {r.status_code}")
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()
    if not data:
        logfire.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api no devolvió info!"
        return text

    text = f"USD libre {data['libre']} - Blue {data['blue']}" f"\n{punch} by http://ws.geeklab.com.ar"
    return text
