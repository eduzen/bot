from collections.abc import Awaitable, Callable

import httpx
import logfire
from cachetools import TTLCache, cached

COIN_BIN = "https://coinbin.org/btc"
COIN_DESK = "https://api.coindesk.com/v1/bpi/currentprice.json"
ETH = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR"
DOGECOIN = "https://sochain.com//api/v2/get_price/DOGE/USD"

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,solana,cardano,decentraland,kava,kusama&vs_currencies=usd"
)


client = httpx.AsyncClient()


async def fetch_and_process(url: str, process_func: Callable[[httpx.Response], str]) -> Awaitable[str]:
    try:
        response = await client.get(url)
        if response.status_code == 200:
            return process_func(response)  # type: ignore
        logfire.error(f"Status code: {response.status_code}")
    except httpx.HTTPError as exc:
        logfire.exception("HTTP Error fetching coin data", extra={"url": url, "error": str(exc)})

    return "Perdón! No hay ninguna api disponible!"  # type: ignore


def process_coindesk(response: httpx.Response) -> str:
    data = response.json()
    if not data:
        logfire.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api coindesk.com no está disponible!"
        return text

    usd_price = float(data["bpi"]["USD"]["rate"].replace(",", ""))
    eur_price = float(data["bpi"]["EUR"]["rate"].replace(",", ""))

    return f"₿ 1 btc == USD {usd_price:,.2f} 💵 | EUR {eur_price:,.2f} 🇪🇺 \n By coindesk.org"


def process_eth(response: httpx.Response) -> str:
    try:
        data = response.json()
        return f"⧫ 1 eth == USD {round(data['USD'], 2)} 💵 | EUR {round(data['EUR'], 2)} 🇪🇺"
    except Exception:
        logfire.exception("No pudimos conseguir eth")
        return "Perdón! No hay ninguna api disponible!"


def process_dogecoin(response: httpx.Response) -> str:
    try:
        data = response.json()
        price = round(float(data["data"]["prices"][0]["price"]), 2)
        return f"🐶 1 dogecoin == USD {price} 💵"
    except Exception:
        logfire.exception("No pudimos conseguir eth")
        return "Perdón! No hay ninguna api disponible!"


def process_all(response: httpx.Response) -> str:
    try:
        data = response.json()

        btc = str(round(float(data["bitcoin"]["usd"]), 2))
        btc = f"₿ 1 btc == USD {btc} 💵"
        logfire.debug(f"btc: {btc}")

        eth = str(round(float(data["ethereum"]["usd"]), 2))
        eth = f"⧫ 1 eth == USD {eth} 💵"
        logfire.debug(f"eth: {eth}")

        sol = str(round(float(data["solana"]["usd"]), 2))
        sol = f"☀️ 1 sol == USD {sol} 💵"
        logfire.debug(f"sol: {sol}")

        ada = str(round(float(data["cardano"]["usd"]), 2))
        ada = f"🧚‍♀️ 1 ada == USD {ada} 💵"
        logfire.debug(f"ada: {ada}")

        return f"{btc}\n{eth}\n{sol}\n{ada}"
    except Exception:
        logfire.exception("No pudimos conseguir eth")

    return "Perdón! No hay ninguna api disponible!"


@cached(cache=TTLCache(maxsize=2048, ttl=60))
async def get_eth() -> Awaitable[str]:
    return await fetch_and_process(ETH, process_eth)


@cached(cache=TTLCache(maxsize=2048, ttl=60))
async def get_btc() -> Awaitable[str]:
    return await fetch_and_process(COIN_DESK, process_coindesk)


@cached(cache=TTLCache(maxsize=2048, ttl=60))
async def get_dogecoin() -> Awaitable[str]:
    return await fetch_and_process(DOGECOIN, process_dogecoin)


@cached(cache=TTLCache(maxsize=2048, ttl=60))
async def get_all() -> Awaitable[str]:
    return await fetch_and_process(COINGECKO_URL, process_all)
