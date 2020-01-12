import requests
import structlog

from eduzen_bot.keys import AUTH, BASE_URL

logger = structlog.get_logger(filename=__name__)


def send_expense(title, amount, category=None):
    data = {"title": title, "amount": amount, "category": category}
    logger.info(data)

    response = requests.post("{}{}".format(BASE_URL, "telegram/expense/"), json=data, auth=AUTH)
    logger.info(f"status_code: {response.status_code} \n {response.text}")

    return response
