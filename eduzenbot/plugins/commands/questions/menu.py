import logging

from emoji import emojize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from eduzenbot.menus.builder import build_menu
from eduzenbot.models import Question

logger = logging.getLogger("rich")


def q_menu(update, context):
    keyboard = [
        InlineKeyboardButton("Only questions", callback_data="questions"),
        InlineKeyboardButton("Questions & answers", callback_data="answer"),
        InlineKeyboardButton("How to use it", callback_data="help"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

    context.bot.send_message(chat_id=update.message.chat_id, text="Please choose:", reply_markup=reply_markup)


def get_questions(answer=None):
    punch = emojize(":punch:")

    if not answer:
        qs = "\n".join([f"{q.id}: {q.question}" for q in Question.select()])
        return f"{qs}\n{punch}"

    qs = "\n".join([f"{q.id}: {q.question} | {q.answer}" for q in Question.select()])
    return f"{qs}\n{punch}"


def button(update, context):
    query = update.callback_query

    selected = query.data

    if selected == "questions":
        answer = get_questions()
    elif selected == "answer":
        answer = get_questions(answer=True)
    elif selected == "help":
        answer = (
            "Primero debes agregar una pregunta usando `/add_question <tu pregunta>`\n"
            "Esto te va a responder con un id, por ejemplo 1\n"
            "Para agregar la respuesta a tu pregunta usamos ese id: `/add_answer 1 <tu respuesta>`\n"
            "Despues resta hablarle al bot `tu pregunta? @eduzenbot`"
        )

    context.bot.edit_message_text(
        text=f"{answer}",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        parse_mode="Markdown",
    )
