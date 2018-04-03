import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from menus.builder import build_menu
from db import Question

from emoji import emojize

logger = logging.getLogger(__name__)


def q_menu(bot, update, args):
    keyboard = [
        InlineKeyboardButton("Only questions", callback_data="questions"),
        InlineKeyboardButton("Questions & answers", callback_data="answer"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

    bot.send_message(
        chat_id=update.message.chat_id, text="Please choose:", reply_markup=reply_markup
    )


def get_questions(answer=None):
    punch = emojize(":punch:", use_aliases=True)

    if not answer:
        qs = "\n".join([f"{q.id}: {q.question}" for q in Question.select()])
        return f"{qs}\n{punch}"

    qs = "\n".join([f"{q.id}: {q.question} | {q.answer}" for q in Question.select()])
    return f"{qs}\n{punch}"


def button(bot, update):
    query = update.callback_query

    selected = query.data

    if selected == "questions":
        answer = get_questions()
    elif selected == "answer":
        answer = get_questions(answer=True)

    bot.edit_message_text(
        text=f"{answer}",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )
