import logging
import requests

from keys import AUTH, BASE_URL

logger = logging.getLogger(__name__)


def send_expense(title, amount, category=None):
    data = {"title": title, "amount": amount, "category": category}
    logger.info(data)

    response = requests.post(
        "{}{}".format(BASE_URL, "telegram/expense/"), json=data, auth=AUTH
    )
    logger.info(f"status_code: {response.status_code} \n {response.text}")

    return response
