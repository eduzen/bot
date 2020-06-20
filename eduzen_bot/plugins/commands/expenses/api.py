import os
import requests
import structlog

usr = os.getenv("API_EDUZEN_USER")
psw = os.getenv("API_EDUZEN_PASS")
BASE_URL = os.getenv("BASE_URL")
logger = structlog.get_logger(filename=__name__)


def send_expense(title, amount, category=None):
    data = {"title": title, "amount": amount, "category": category}
    logger.info(data)

    response = requests.post("{}{}".format(BASE_URL, "telegram/expense/"), json=data, auth=(usr, psw))
    logger.info(f"status_code: {response.status_code} \n {response.text}")

    return response
