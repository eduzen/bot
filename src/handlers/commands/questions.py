import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from menus.builder import build_menu
from db import Question

logger = logging.getLogger(__name__)


def q_menu(bot, update, args):
    keyboard = [
        InlineKeyboardButton("List questions", callback_data="list"),
        InlineKeyboardButton("Add question", callback_data="question"),
        InlineKeyboardButton("Add answer", callback_data="answer"),
        InlineKeyboardButton("Remove question", callback_data="remove")
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

    bot.send_message(chat_id=update.message.chat_id, text="Please choose:", reply_markup=reply_markup)

    # update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    selected = query.data

    if selected == 'list':
        qs = "\n".join([
            f"{q.id}: {q.question} | {q.answer} | by {q.user}"
            for q in Question.select()
        ])
        bot.edit_message_text(
            text=f"{qs}",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        return

    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
