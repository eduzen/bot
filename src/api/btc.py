import logging
import requests

logger = logging.getLogger(__name__)

API = 'https://coinbin.org/btc'


def get_btc():
    r = requests.get(API)

    if r.status_code != 200:
        logger.error(
            "Something went wrong when it gets btc. Status code: %s",
            r.status_code
        )
        text = "Perdón! La api coinbin.org no está  disponible!"
        return text

    data = r.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api coinbin.org no está  disponible!"
        return text

    text = f"1 btc == USD {data['coin']['usd']}"

    return text
