import os
from datetime import datetime

import tweepy
from emoji import emojize

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")


metro = emojize(":metro:")


def get_tweets(api: str, username: str, count: int, date: datetime) -> str:
    tweets = [tweet.text for tweet in api.user_timeline(username, count=count) if (date - tweet.created_at).days < 1]
    if not tweets:
        return f"No hay novedades de subtes {metro} para hoy"

    return "\n".join(tweets)


def get_subte(count: int = 20) -> str:
    if count > 20:
        count = 20
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    now = datetime.now()
    today = now.date().isoformat()
    data = get_tweets(api, "subteba", count=count, date=now)
    data = f"Estado Subtes {metro} BA by @subteba ({today}):\n{data}"
    return data
