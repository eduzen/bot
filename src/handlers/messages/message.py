import os
import logging
import random
import codecs
from datetime import datetime

from telegram import ChatAction

from db import User, Question
from .vocabulary import (
    GREETING_KEYWORDS,
    GREETING_RESPONSES,
    INTRO_QUESTIONS,
    NONE_RESPONSES,
    INTRO_RESPONSES, BYE_KEYWORDS,
    BYE_RESPONSES,
    T1000_RESPONSE,
    FASO_RESPONSE,
    WINDOWS_RESPONSE,
    JOKE_KEYWORDS, JOKE_RESPONSES,
    skynet,
)
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'
from textblob import TextBlob

logger = logging.getLogger(__name__)


def record_msg(user, msg):
    msg = f'{user}: {msg}\n'
    with codecs.open('history.txt', 'a', "utf-8") as f:
        msg = f'{datetime.now().isoformat()} - {msg}'
        f.write(msg)


def check_for_greeting(sentence):
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


def check_for_joke(sentence):
    for joke in JOKE_KEYWORDS:
        if joke in words:
            return random.choice(JOKE_RESPONSES)


def check_for_bye(sentence):
    for word in sentence.words:
        if word.lower() in BYE_KEYWORDS:
            return random.choice(BYE_RESPONSES)


def check_for_intro_question(sentence):
    """Sometimes people greet by introducing a question."""
    if sentence in INTRO_QUESTIONS:
        return random.choice(INTRO_RESPONSES)


def get_or_create_user(username, userid):
    User.get_or_create(
        username=username,
        id=userid
    )


def get_question(question):
    try:
        return Question.get(Question.question == question).answer
    except Exception:
        logger.info('no answer')


def parse_chat(blob):
    for sentence in blob.sentences:
        resp = check_for_greeting(blob)
        if not resp:
            resp = check_for_intro_question(blob)

        if not resp:
            resp = check_for_bye(blob)

        if resp:
            break

    if not resp and '?' in blob:
        resp = get_question(blob.raw)

    if not resp:
        resp = random.choice(NONE_RESPONSES)

    return resp


def automatic_response(words, msg, vocabularies):
    for word in words:
        if word in msg:
            return random.choice(vocabularies)


def parse_regular_chat(msg):
    answer = False
    giphy = False
    for sentence in msg.sentences:
        words = [w.lower() for w in sentence.words]
        answer = check_for_greeting(words)
        if answer:
            return answer, giphy
        bye = check_for_bye(words)
        if bye:
            return bye, giphy
        question = check_for_intro_question(words)
        if question:
            return question
        joke = check_for_joke(words)
        if joke:
            return joke, giphy

        automatic = automatic_response(skynet, words, T1000_RESPONSE)
        if response:
            return automatic, True

        faso = ('faso', 'fasoo', )
        automatic = automatic_response(faso, words, FASO_RESPONSE)
        if response:
            return automatic, True


        wnd = ('window', 'windows', 'win98', 'win95')
        automatic = automatic_response(wnd, WINDOWS_RESPONSE)
        if response:
            return automatic, True

    return answer, giphy


def prepare_text(text):
    raw_msg = raw_msg.replace('@eduzenbot', '').replace('@eduzen_bot', '').strip()
    raw_msg = raw_msg.replace(' ?', '?')

    return text

def parse_msgs(bot, update):
    logger.info(f"parse_msgs... by {update.message.from_user.name}")
    record_msg(update.message.from_user.name, update.message.text)

    get_or_create_user(
        update.message.from_user.name,
        update.message.from_user.id
    )

    text = prepare_text(raw_msg)
    blob = TextBlob(raw_msg)

    entities = update.message.parse_entities()
    if not entities:
        answer, gif = parse_regular_chat(blob)
        if answer:
            bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        if answer and not gif:
            bot.send_message(chat_id=update.message.chat_id, text=answer)
        elif answer and gif:
            bot.send_document(chat_id=update.message.chat_id, document=response)
        return

    mentions = [
        value for key, value in entities.items()
        if '@eduzen_bot' in value or '@eduzenbot' in value
    ]
    if not mentions:
        return

    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    answer = parse_chat(blob)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=answer
    )
