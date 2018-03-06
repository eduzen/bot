import logging
import requests

from keys import APP_ID

logger = logging.getLogger(__name__)

API = 'https://openexchangerates.org/api/latest.json'
OTHER_API = 'http://ws.geeklab.com.ar/dolar/get-dolar-json.php'


def get_dolar():
    r = requests.get(API, params={'app_id': APP_ID})
    r2 = requests.get(OTHER_API)

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

    if r2.status_code == 200 and r2.json():
        info = r2.json()
        text = (
            f"OpenExchange:\nUSD oficial {data['rates']['ARS']}\n"
            f"GeekLab:\nUSD oficial {info['libre']} - Blue {info['blue']}"
        )
        return text

    text = f"USD oficial {data['rates']['ARS']}"
    return text
