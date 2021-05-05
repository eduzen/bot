import requests
import structlog

logger = structlog.get_logger(filename=__name__)

COIN_BIN = "https://coinbin.org/btc"
COIN_DESK = "https://api.coindesk.com/v1/bpi/currentprice.json"
ETH = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,CNY,JPY,GBP"
DOGECOIN = "https://sochain.com//api/v2/get_price/DOGE/USD"


def get_coin_value(url):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return

    return response


def process_coinbin(response):
    data = response.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api coinbin.org no está disponible!"
        return text

    text = f"💰 1 btc == USD {data['coin']['usd']} 💵\n By coinbin.org"
    logger.info(data)
    return text


def process_coindesk(response):
    data = response.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api coindesk.com no está disponible!"
        return text

    return f"₿ 1 btc == USD {data['bpi']['USD']['rate']} 💵\n By coindesk.org"


def process_eth(response):
    try:
        response.raise_for_status()
        data = response.json()
        return f"⧫ 1 eth == USD {data['USD']} 💵"
    except Exception:
        logger.exception("No pudimos conseguir eth")


def process_dogecoin(response):
    try:
        response.raise_for_status()
        data = response.json()
        print(data)
        return f"🐶 1 dogecoin == USD {data['data']['prices'][0]['price']} 💵"
    except Exception:
        logger.exception("No pudimos conseguir eth")


def get_btc():
    r = get_coin_value(COIN_DESK)

    if r and r.status_code == 200:
        return process_coindesk(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"


def get_eth():
    r = get_coin_value(ETH)

    if r and r.status_code == 200:
        return process_eth(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"


def get_dogecoin():
    r = get_coin_value(DOGECOIN)

    if r and r.status_code == 200:
        return process_dogecoin(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"
