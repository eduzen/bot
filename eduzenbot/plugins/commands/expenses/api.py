import os

import logfire
import requests

usr = os.getenv("API_EDUZEN_USER")
psw = os.getenv("API_EDUZEN_PASS")
BASE_URL = os.getenv("BASE_URL")


def send_expense(title, amount, category=None):
    data = {"title": title, "amount": amount, "category": category}
    logfire.info(data)

    response = requests.post("{}{}".format(BASE_URL, "telegram/expense/"), json=data, auth=(usr, psw))
    logfire.info(f"status_code: {response.status_code} \n {response.text}")

    return response
