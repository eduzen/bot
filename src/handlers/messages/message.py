import logging
import random
import codecs
from datetime import datetime

from db import User

from .vocabulary import (
    GREETING_KEYWORDS, GREETING_RESPONSES,
    BYE_KEYWORDS, INTRO_QUESTIONS
)

logger = logging.getLogger(__name__)


def check_for_greeting(sentence):
    """If any of the words in the user's input was a greeting,
    return a greeting response
    """
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


def check_for_answer(sentence, keywords):
    """If any of the words in the user's input
    was a greeting, return a greeting response
    """
    for word in sentence.split(" "):
        if word.lower() in keywords:
            return True
    return False


def record_msg(msg):
    with codecs.open('history.txt', 'a', "utf-8") as f:
        msg = f'{datetime.now().isoformat()} - {msg}'
        f.write(msg)


def parse_msgs(bot, update):
    logger.info(f"echo... by {update.message.from_user.name}")
    msg = update.message.text.lower()

    msg = f'{update.message.from_user.name}: {msg}\n'
    record_msg(msg)
    username = update.message.from_user.name
    user_id = update.message.from_user.id
    User.get_or_create(
        username=username,
        id=user_id
    )

    if check_for_answer(msg, GREETING_KEYWORDS):
        answer = f'Hola {update.message.from_user.name}'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    if check_for_answer(msg, BYE_KEYWORDS):
        answer = f'nos vemos humanoide {update.message.from_user.name}!'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    if check_for_answer(msg, INTRO_QUESTIONS):
        answer = f'Por ahora piola {update.message.from_user.name}'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return


def unknown(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Che, no te entiendo, no existe ese comando!"
    )
