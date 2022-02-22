import logging

import requests
from cachetools import TTLCache, cached

COIN_BIN = "https://coinbin.org/btc"
COIN_DESK = "https://api.coindesk.com/v1/bpi/currentprice.json"
ETH = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR"
DOGECOIN = "https://sochain.com//api/v2/get_price/DOGE/USD"

ALL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,dogecoin,solana,cardano,shiba-inu,decentraland&vs_currencies=usd"
)

logger = logging.getLogger("rich")

client = requests.Session()


def get_coin_value(url):
    try:
        response = client.get(url)
    except requests.exceptions.ConnectionError:
        return

    return response


def process_coinbin(response):
    data = response.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api coinbin.org no está disponible!"
        return text

    text = f"💰 1 btc == USD {data['coin']['usd']} 💵  \n By coinbin.org"
    logger.info(data)
    return text


def process_coindesk(response):
    data = response.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api coindesk.com no está disponible!"
        return text

    usd_price = float(data["bpi"]["USD"]["rate"].replace(",", ""))
    eur_price = float(data["bpi"]["EUR"]["rate"].replace(",", ""))

    return f"₿ 1 btc == USD {usd_price:,.2f} 💵 | EUR {eur_price:,.2f} 🇪🇺 \n By coindesk.org"


def process_eth(response):
    try:
        response.raise_for_status()
        data = response.json()
        return f"⧫ 1 eth == USD {round(data['USD'], 2)} 💵 | EUR {round(data['EUR'], 2)} 🇪🇺"
    except Exception:
        logger.exception("No pudimos conseguir eth")


def process_dogecoin(response):
    try:
        response.raise_for_status()
        data = response.json()
        price = round(float(data["data"]["prices"][0]["price"]), 2)
        return f"🐶 1 dogecoin == USD {price} 💵"
    except Exception:
        logger.exception("No pudimos conseguir eth")


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def get_btc():
    r = get_coin_value(COIN_DESK)

    if r and r.status_code == 200:
        return process_coindesk(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def get_eth():
    r = get_coin_value(ETH)

    if r and r.status_code == 200:
        return process_eth(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"


def process_all(response):
    try:
        response.raise_for_status()
        data = response.json()

        btc = round(float(data["bitcoin"]["usd"]), 2)
        btc = f"₿ 1 btc == USD {btc} 💵"
        logger.debug(f"btc: {btc}")

        eth = round(float(data["ethereum"]["usd"]), 2)
        eth = f"⧫ 1 eth == USD {eth} 💵"
        logger.debug(f"eth: {eth}")

        sol = round(float(data["solana"]["usd"]), 2)
        sol = f"☀️ 1 sol == USD {sol} 💵"
        logger.debug(f"sol: {sol}")

        ada = round(float(data["cardano"]["usd"]), 2)
        ada = f"🧚‍♀️ 1 ada == USD {ada} 💵"
        logger.debug(f"ada: {ada}")

        dog = round(float(data["dogecoin"]["usd"]), 2)
        dog = f"🐶 1 dog == USD {dog} 💵"
        logger.debug(f"dog: {dog}")

        shi = round(float(data["shiba-inu"]["usd"]), 12)
        shi = f"🐕 1 shiba == USD {shi} 💵"
        logger.debug(f"shi: {shi}")

        dcl = round(float(data["decentraland"]["usd"]), 2)
        dcl = f"💥 1 mana == USD {dcl} 💵"
        logger.debug(f"dcl: {dcl}")

        return f"{btc}\n{eth}\n{dog}\n{sol}\n{ada}\n{shi}\n{dcl}"
    except Exception:
        logger.exception("No pudimos conseguir eth")


@cached(cache=TTLCache(maxsize=2048, ttl=60))
def get_dogecoin():
    r = get_coin_value(DOGECOIN)

    if r and r.status_code == 200:
        return process_dogecoin(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"


def get_all():
    r = get_coin_value(ALL)

    if r and r.status_code == 200:
        return process_all(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"
