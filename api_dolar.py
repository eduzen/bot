import logging
import requests

from keys import AUTH, BASE_URL

logger = logging.getLogger(__name__)

dolar_api = 'http://ws.geeklab.com.ar/dolar/get-dolar-json.php'


def get_dolar():
    r = requests.get(dolar_api)

    if r.status_code != 200:
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()

    if not data:
        text = "Perdón! La api no está  disponible!"
        return text

    text = f"USD oficial {data["libre"]} - Blue {data["blue"]}"

    return text
