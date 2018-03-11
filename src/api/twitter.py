import tweepy
from keys import TWITTER

consumer_key = TWITTER['CONSUMER_KEY']
consumer_secret = TWITTER['CONSUMER_SECRET']
access_token = TWITTER['ACCESS_TOKEN']
access_token_secret = TWITTER['ACCESS_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def get_subte(count=1):
    if count > 10:
        count = 10

    twts = api.get_user('subteba').timeline(count=count)

    data = '\n'.join([t.text for t in twts])

    return data
