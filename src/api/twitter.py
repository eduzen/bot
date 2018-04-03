from datetime import datetime

import tweepy
import requests
from bs4 import BeautifulSoup

from keys import TWITTER

consumer_key = TWITTER["CONSUMER_KEY"]
consumer_secret = TWITTER["CONSUMER_SECRET"]
access_token = TWITTER["ACCESS_TOKEN"]
access_token_secret = TWITTER["ACCESS_TOKEN_SECRET"]


def get_tweets(api, username, count, date):
    tweets = [
        tweet.text
        for tweet in api.user_timeline(username, count=count)
        if (date - tweet.created_at).days < 1
    ]
    if not tweets:
        return "No hay novedades de subtes para hoy"

    return "\n".join(tweets)


def get_subte(count=20):
    if count > 20:
        count = 20
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    now = datetime.now()
    today = now.date().isoformat()
    data = get_tweets(api, "subteba", count=count, date=now)
    data = f"Estado Subtes BA by @subteba ({today}):\n{data}"
    return data


def get_subte_html(amount=0):
    r = requests.get("http://enelsubte.com/estado/")
    r.encoding = "utf-8"
    msg = "No pudimos conseguir el subte via web"

    if r.status_code != 200:
        return msg

    data = r.text
    if not data:
        return msg

    soup = BeautifulSoup(data, "html.parser")
    data = soup.find_all("table", {"id": "tabla-estado"})

    if not data:
        return msg

    data = data[0].text.strip().replace("\r\n", "\n").replace("\n", "")
    data = data.replace("A", "*A* ")
    for linea in ("B", "C", "D", "E", "P", "H", "U"):
        data = data.replace(linea, f"\n*{linea}* ")

    data = data.replace("Normal", " Normal")
    data = data.replace("Actualizado", "Actualizado ")

    return data
