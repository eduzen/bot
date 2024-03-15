import logging
import os

import requests

usr = os.getenv("API_EDUZEN_USER")
psw = os.getenv("API_EDUZEN_PASS")
BASE_URL = os.getenv("BASE_URL")
logger = logging.getLogger("rich")


def send_expense(title, amount, category=None):
    data = {"title": title, "amount": amount, "category": category}
    logger.info(data)

    response = requests.post(
        "{}{}".format(BASE_URL, "telegram/expense/"), json=data, auth=(usr, psw)
    )
    logger.info(f"status_code: {response.status_code} \n {response.text}")

    return response
