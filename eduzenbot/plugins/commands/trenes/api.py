import logging
import os
from datetime import datetime

import tweepy
from cachetools import TTLCache, cached

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")

logger = logging.getLogger("rich")


def get_tweets(api: str, username: str, count: int, date: datetime) -> str:
    tweets = [
        tweet.text
        for tweet in api.user_timeline(username, count=count)
        if (date - tweet.created_at).days < 1
    ]
    if not tweets:
        return "No hay novedades de trenes para hoy"

    return "\n".join(tweets)


@cached(cache=TTLCache(maxsize=2048, ttl=360))
def get_trenes(count: int = 20) -> str:
    if count > 20:
        count = 20
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    now = datetime.now()
    today = now.date().isoformat()
    data = get_tweets(api, "HorariosTren", count=count, date=now)
    data = f"Transito BA by @horariostren ({today}):\n{data}"
    return data
