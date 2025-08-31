import httpx
import logfire
from bs4 import BeautifulSoup

GEEKLAB_API = "http://ws.geeklab.com.ar/dolar/get-dolar-json.php"
BNC = "https://www.bna.com.ar/Personas"
BLUELYTICS = "https://api.bluelytics.com.ar/v2/latest"

# Configure client with proper timeouts
client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=15.0))

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
        return "Banco Nación cambió su HTML."

    data = _extract(data[0])

    # Add spaces between parts
    head = " ".join(data[:3]).strip()
    dolar = " ".join(data[3:6]).strip()
    euro = " ".join(data[6:9]).strip()
    real = " ".join(data[9:]).strip()

    result = f"{head}\n{dolar}\n{euro}\n{real}\n(*) cotización cada 100 unidades.\n👊 by bna.com.ar"
    return result


def _process_bluelytics(payload: dict) -> str:
    try:
        oficial = payload["oficial"]
        blue = payload["blue"]
        eur = payload["oficial_euro"]
        blue_eur = payload["blue_euro"]

        def fmt(x) -> str:
            try:
                return f"{float(x):,.2f}"
            except Exception:
                return str(x)

        oficial_venta = float(oficial["value_sell"])  # for brecha
        blue_venta = float(blue["value_sell"])  # for brecha
        brecha = round(((blue_venta / oficial_venta) - 1) * 100, 2)

        text: str = (
            "🏦 Oficial:\n"
            f"💵 Dólar {fmt(oficial['value_buy'])} - {fmt(oficial['value_sell'])}\n"
            f"🇪🇺 Euro {fmt(eur['value_buy'])} - {fmt(eur['value_sell'])}\n"
            "\n🌳 Blue:\n"
            f"💵 Dólar {fmt(blue['value_buy'])} - {fmt(blue['value_sell'])}\n"
            f"🇪🇺 Euro {fmt(blue_eur['value_buy'])} - {fmt(blue_eur['value_sell'])}\n"
            f"📊 Brecha Dólar: {brecha}%"
        )
        return text
    except KeyError:
        logfire.warning("Bluelytics response missing expected keys")
        return ""


async def get_banco_nacion() -> str:
    try:
        response = await client.get(BNC)
        response.raise_for_status()

        if response.status_code != 200:
            raise Exception("Banco nación no responde 🤷‍♀")

        data = response.text
        return _process_bcn(data)
    except httpx.TimeoutException:
        logfire.warning("BNC request timed out")
        return "Banco nación no responde (timeout) 🤷‍♀"
    except httpx.RequestError as e:
        logfire.exception(f"BNC network error: {e}")
        return "Banco nación no responde (network error) 🤷‍♀"
    except Exception:
        logfire.exception("Error getting BNC")

    return "Banco nación no responde 🤷‍♀"


async def get_bluelytics() -> str:
    try:
        response = await client.get(BLUELYTICS)
        response.raise_for_status()
        if response.status_code != 200:
            raise Exception("Bluelytics no responde 🤷‍♀️ ")

        data = response.json()
        return _process_bluelytics(data)
    except httpx.TimeoutException:
        logfire.warning("Bluelytics request timed out")
        return "Bluelytics no responde (timeout) 🤷‍♀️"
    except httpx.RequestError as e:
        logfire.exception(f"Bluelytics network error: {e}")
        return "Bluelytics no responde (network error) 🤷‍♀️"
    except Exception:
        logfire.exception("bluelytics")
    return "Bluelytics no responde 🤷‍♀️"


async def get_dolar_blue_geeklab() -> str:
    try:
        r = await client.get(GEEKLAB_API)
        if r.status_code != 200:
            logfire.error(f"Something went wrong when it gets dollar. Status code: {r.status_code}")
            return ""

        data = r.json()
        logfire.info(f"Geeklab API response: {data}")
        if not data or data.get("libre") is None or data.get("blue") is None:
            logfire.error("Geeklab API returned incomplete data.")
            # Skip user-facing noise; still log the incident.
            return ""

        return f"USD libre {data['libre']} - Blue {data['blue']}\n{punch} by http://ws.geeklab.com.ar"
    except httpx.TimeoutException:
        logfire.warning("Geeklab request timed out")
        return "Geeklab no responde (timeout) 🤷‍♂️"
    except httpx.RequestError as e:
        logfire.exception(f"Geeklab network error: {e}")
        return "Geeklab no responde (network error) 🤷‍♂️"
    except Exception as e:
        logfire.exception(f"Error getting Geeklab data: {e}")
        return "Error obteniendo datos de Geeklab 🤷‍♂️"
