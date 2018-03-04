import logging
import requests

from keys import APP_ID

logger = logging.getLogger(__name__)

API = 'https://openexchangerates.org/api/latest.json'


def get_dolar():
    r = requests.get(API, params={'app_id': APP_ID})

    if r.status_code != 200:
        logger.error(
            "Something went wrong when it gets dollar. Status code: %s",
            r.status_code
        )
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()
    if not data:
        logger.error("Something went wrong when it gets dollar. No data!")
        text = "Perdón! La api no devolvió info!"
        return text

    text = f"USD oficial {data['rates']['ARS']}"
    return text
