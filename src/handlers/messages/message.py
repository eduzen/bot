import os
import logging
import random
import codecs
from datetime import datetime

from telegram import ChatAction

from db import User
from .vocabulary import (
    GREETING_KEYWORDS,
    GREETING_RESPONSES,
    INTRO_QUESTIONS,
    NONE_RESPONSES,
    INTRO_RESPONSES, BYE_KEYWORDS,
    BYE_RESPONSES

)
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'
from textblob import TextBlob

logger = logging.getLogger(__name__)


def record_msg(msg):
    with codecs.open('history.txt', 'a', "utf-8") as f:
        msg = f'{datetime.now().isoformat()} - {msg}'
        f.write(msg)


def check_for_greeting(sentence):
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


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


def parse_chat(blob):
    for sentence in blob.sentences:
        resp = check_for_greeting(blob)
        if not resp:
            resp = check_for_intro_question(blob)

        if not resp:
            resp = check_for_bye(blob)

        if resp:
            break

    if not resp:
        resp = random.choice(NONE_RESPONSES)

    return resp


def parse_regular_chat(msg):
    answer = False
    for sentence in msg.sentences:
        answer = check_for_greeting(sentence)
        if answer:
            return answer
        bye = check_for_bye(sentence)
        if bye:
            return bye
        question = check_for_intro_question(sentence)
        if question:
            return question

    return answer


def parse_msgs(bot, update):
    logger.info(f"parse_msgs... by {update.message.from_user.name}")
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    msg = update.message.text
    msg = f'{update.message.from_user.name}: {msg}\n'
    record_msg(msg)

    get_or_create_user(
        update.message.from_user.name,
        update.message.from_user.id
    )

    raw_msg = update.message.text_html
    if 'jaja' in raw_msg.lower() or 'jeje' in raw_msg.lower():
        bot.send_message(chat_id=update.message.chat_id, text='jaja')
        return

    raw_msg = raw_msg.replace('@eduzenbot', '').replace('@eduzen_bot', '').strip()
    blob = TextBlob(raw_msg)

    entities = update.message.parse_entities()
    if not entities:
        answer = parse_regular_chat(blob)
        if answer:
            bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    mentions = [value for key, value in entities.items()]

    if '@eduzen_bot' not in mentions and '@eduzenbot' not in mentions:
        return

    answer = parse_chat(blob)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=answer
    )
