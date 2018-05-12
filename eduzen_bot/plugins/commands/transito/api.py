from datetime import datetime

import structlog
import tweepy

from keys import TWITTER

logger = structlog.get_logger(filename=__name__)


def get_tweets(api, username, count, date):
    tweets = [tweet.text for tweet in api.user_timeline(username, count=count) if (date - tweet.created_at).days < 1]
    if not tweets:
        return "No hay novedades de subtes para hoy"

    return "\n".join(tweets)


def get_transito(count=20):
    logger.info("get_transito from twitter...")
    if count > 20:
        count = 20
    auth = tweepy.OAuthHandler(TWITTER["CONSUMER_KEY"], TWITTER["CONSUMER_SECRET"])
    auth.set_access_token(TWITTER["ACCESS_TOKEN"], TWITTER["ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth)
    now = datetime.now()
    data = get_tweets(api, "solotransito", count=count, date=now)

    return f"Transito BA by @solotransito ({now.date().isoformat()}):\n{data}"
