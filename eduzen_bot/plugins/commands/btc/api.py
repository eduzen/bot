import structlog
import requests

logger = structlog.get_logger(filename=__name__)

COIN_BIN = "https://coinbin.org/btc"
COIN_DESK = "https://api.coindesk.com/v1/bpi/currentprice.json"
ETH = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,CNY,JPY,GBP"


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

    text = f"💰 1 ₿ btc == USD {data['bpi']['USD']['rate']} 💵\n By coindesk.org"

    try:
        r = get_coin_value(ETH)
        r.raise_for_status()
        data = r.json()
        text = f"💰 1 ⧫ eth == USD {data['USD']} 💵\n{text}"
    except Exception:
        logger.exception("No pudimos conseguir eth")

    return text


def get_btc():
    r = get_coin_value(COIN_DESK)

    if r and r.status_code == 200:
        return process_coindesk(r)

    logger.error(f"Something went wrong when it gets btc. Status code: {r.status_code}")

    return "Perdón! No hay ninguna api disponible!"
