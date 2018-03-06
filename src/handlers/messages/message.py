import logging
from datetime import datetime

from db import User

logger = logging.getLogger(__name__)

GREETING_KEYWORDS = (
    "hello", "hi", "greetings", "sup", "what's up",
    "hola", "holas", "holis"
)

BYE_KEYWORDS = (
    'bye', 'chau', 'chauuu',
)

MOOD_KEYWORDS = (
    'qué haces', 'que hacés', 'que hace', 'todo bien?', 'como va',
    'cómo va', 'todo piola?', 'todo bien=', 'todo bien', 'como va?',
    'todo piola?', 'que haces?', 'como estas?', 'como esta?'
)


def check_for_answer(sentence, keywords):
    """If any of the words in the user's input
    was a greeting, return a greeting response
    """
    for word in sentence.split(" "):
        if word.lower() in keywords:
            return True
    return False


def record_msg(msg):
    logger.info(f"record_msg")
    with open('history.txt', 'a') as f:
        msg = f'{datetime.now().isoformat()} - {msg}'
        f.write(msg)


def parse_msg(bot, update):
    logger.info(f"echo... by {update.message.from_user.name}")
    if update.message.new_chat_members:
        answer = 'Bienvenido {}'.format(update.message.from_user.name)
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

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

    if check_for_answer(msg, MOOD_KEYWORDS):
        answer = f'Por ahora piola {update.message.from_user.name}'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return


def unknown(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Che, no te entiendo, no existe ese comando!"
    )
