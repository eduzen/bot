#!/usr/bin/env python3

import logging
import os

import requests

TOKEN = os.getenv("TOKEN")
logging.basicConfig(
    level=logging.INFO,
    filename="/home/eduzen/Projects/bot/somelog.log",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
)


logging.info("Starting request..")
response = requests.get(f"https://eduzenbot.herokuapp.com/{TOKEN}", timeout=60)
logging.info("Status Code: %s", response.status_code)
logging.info("Starts: %s", response.text[:15])
