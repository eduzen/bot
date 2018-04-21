from datetime import datetime

import tweepy

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


def get_transito(count=20):
    if count > 20:
        count = 20
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    now = datetime.now()
    today = now.date().isoformat()
    data = get_tweets(api, "solotransito", count=count, date=now)
    data = f"Transito BA by @solotransito ({today}):\n{data}"
    return data


def get_trenes(count=20):
    if count > 20:
        count = 20
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    now = datetime.now()
    today = now.date().isoformat()
    data = get_tweets(api, "HorariosTren", count=count, date=now)
    data = f"Transito BA by @horariostren ({today}):\n{data}"
    return data


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
