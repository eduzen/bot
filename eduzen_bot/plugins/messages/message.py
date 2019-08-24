import os
import logging
import random
import codecs

import peewee
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

from models import User, Question
from .vocabulary import (
    GREETING_KEYWORDS,
    GREETING_RESPONSES,
    INTRO_QUESTIONS,
    NONE_RESPONSES,
    INTRO_RESPONSES,
    BYE_KEYWORDS,
    BYE_RESPONSES,
    T1000_RESPONSE,
    FASO_RESPONSE,
    WINDOWS_RESPONSE,
    JOKE_KEYWORDS,
    JOKE_RESPONSES,
    SKYNET,
    MACRI,
    MACRI_RESPONSES,
)

os.environ["NLTK_DATA"] = os.getcwd() + "/nltk_data"
from textblob import TextBlob

chats = {"-288031841": "t3"}

logger = logging.getLogger(__name__)


@run_async
def get_or_create_user(user):
    data = user.to_dict()
    created = None
    user = None

    try:
        user, created = User.get_or_create(**data)
    except peewee.IntegrityError:
        logger.warn("User already created")

    if user and created:
        logger.debug("User created. Id %s", user.id)
        return

    try:
        user = User.update(**data)
        logger.debug("User updated")
    except Exception:
        logger.exception("User cannot be updated")


@run_async
def record_msg(user, msg, chat_id):
    logger.info("Recording msg chat_id %s", chat_id)
    filename = f"history_{chat_id}.txt"
    key = chats.get(chat_id)
    if key:
        filename = f"history_{key}.txt"

    msg = f"{user}: {msg}\n"
    with codecs.open(filename, "a", "utf-8") as f:
        # msg = f"{datetime.now().isoformat()} - {msg}"
        f.write(msg)


def check_for_greeting(words):
    for word in words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


def check_for_joke(words):
    for joke in JOKE_KEYWORDS:
        if joke in words:
            return random.choice(JOKE_RESPONSES)


def check_for_bye(words):
    for word in words:
        if word.lower() in BYE_KEYWORDS:
            return random.choice(BYE_RESPONSES)


def check_for_intro_question(sentence):
    """Sometimes people greet by introducing a question."""
    if sentence in INTRO_QUESTIONS:
        return random.choice(INTRO_RESPONSES)


def get_question(question):
    try:
        return Question.get(Question.question == question).answer

    except Exception:
        logger.info("no answer")


def parse_chat(blob):
    for sentence in blob.sentences:
        resp = check_for_greeting(blob)
        if not resp:
            resp = check_for_intro_question(blob)

        if not resp:
            resp = check_for_bye(blob)

        if resp:
            break

    if not resp and "?" in blob:
        resp = get_question(blob.raw)

    if not resp:
        resp = random.choice(NONE_RESPONSES)

    return resp


def automatic_response(words, msg, vocabularies):
    for word in words:
        if word in msg:
            return random.choice(vocabularies)


def parse_regular_chat(msg):
    logger.info("parsing regular chat")
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

        question = check_for_intro_question(sentence)
        if question:
            return question, giphy

        joke = check_for_joke(words)
        if joke:
            return joke, giphy

        automatic = automatic_response(SKYNET, words, T1000_RESPONSE)
        if automatic:
            return automatic, True

        automatic = automatic_response(MACRI, words, MACRI_RESPONSES)
        if automatic:
            return automatic, True

        if "whatsapp" in words:
            return "https://media.giphy.com/media/3o6Mb4knW2GIANwmNW/giphy.gif", True

        faso = ("faso", "fasoo")
        automatic = automatic_response(faso, words, FASO_RESPONSE)
        if automatic:
            return automatic, True

        wnd = ("window", "windows", "win98", "win95")
        automatic = automatic_response(wnd, words, WINDOWS_RESPONSE)
        if automatic:
            return automatic, True

    return answer, giphy


def prepare_text(text):
    text = text.replace("@eduzenbot", "").replace("@eduzen_bot", "").strip()
    return text.replace(" ?", "?")


@run_async
def parse_msgs(bot, update):
    message = update.message
    if not message:
        return

    try:
        entities = update.message.parse_entities()
    except Exception:
        logger.exception("Parece que no hay parse_entities")
        return

    mentions = [
        value for key, value in entities.items() if "@eduzen_bot" in value or "@eduzenbot" in value
    ]

    if not mentions:
        return

    username = update.message.from_user.username
    logger.info("parse_msgs... by %s", username)

    text = prepare_text(update.message.text)
    blob = TextBlob(text)

    answer, gif = parse_regular_chat(blob)
    if answer:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if answer and not gif:
        bot.send_message(chat_id=update.message.chat_id, text=answer)
    elif answer and gif:
        bot.send_document(chat_id=update.message.chat_id, document=answer)

    return
