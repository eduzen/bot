import logging
import requests

from keys import AUTH, BASE_URL

logger = logging.getLogger(__name__)

dolar_api = 'https://openexchangerates.org/api/latest.json'


def get_dolar():
    r = requests.get(dolar_api, params={'app_id': '83f44a6566f945a4abc92139fd0cc60d'})

    if r.status_code != 200:
        text = "Perdón! La api no está  disponible!"
        return text

    data = r.json()
    if not data:
        text = "Perdón! La api no está  disponible!"
        return text

    text = f"USD oficial {data['rates']['ARS']}"

    return text
