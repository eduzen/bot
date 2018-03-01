import logging
import requests
from collections import defaultdict
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

from keys import TOKEN
from api_expenses import send_expense
from api_dolar import get_dolar
from db import User, Question


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def dolar(bot, update):
    logger.info(f"dolar... by {update.message.from_user.name}")

    text = get_dolar()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )

def get_users(bot, update):
    logger.info(f"get_users... by {update.message.from_user.name}")

    users = User.select()
    txt = [user.username for user in users]
    bot.send_message(
        chat_id=update.message.chat_id,
        text=txt
    )


def get_questions(bot, update):
    try:
        logger.info(f"get_users... by {update.message.from_user.name}")

        qs = [f"{q.id}: {q.questions}" for q in Question.select()]

        bot.send_message(
            chat_id=update.message.chat_id,
            text="\n".join(qs)
        )
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No hay preguntas o algo pasó"
        )

def add_question(bot, update, args):
    logger.info(f"get_users... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("mmm no enviaste nada!")
        return

    username = update.message.from_user.name
    user_id = update.message.from_user.id
    user = User.get_or_create(
        username=username,
        id=user_id
    )
    try:
        q = Question.create(
            user=user[0].id,
            question=" ".join(map(str, args))
        )
        txt = f"Pregunta creada con id: {q.id}"
        bot.send_message(
            chat_id=update.message.chat_id,
            text=txt
        )
    except Exception:
        logger.exception('no pudimos agregar preguntas')
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No pudimos agregar tu pregunta"
        )



def expense(bot, update, args):
    logger.info(f"expenses... by {update.message.from_user.name}")
    if not update.message.from_user.name == '@eduzen':
        update.message.reply_text(
            f"Mmm... no es para ti! Humano {update.message.from_user.name} "
            "inferior ya callate! No es un comando que tu pueadas usar"
        )
        return

    if not args:
        update.message.reply_text("mmm no enviaste nada!")
        return

    try:
        amount = float(args[0])
    except Exception:
        logger.error('No pudimos convertir %s', args)

    try:
        title = args[1]
    except Exception:
        title = 'gasto desconocido'

    try:
        r = send_expense(title, amount)
    except Exception:
        logger.exception('algo paso')
        update.message.reply_text(
            "Chequea que algo paso y no pudimos enviar el gasto!"
        )
        return

    if r.status_code != 201:
        update.message.reply_text(
            "Chequea que algo paso y no pudimos enviar el gasto!"
        )
        return

    update.message.reply_text(
        f"Joya {update.message.from_user.name}! Gasto agendado!"
    )


def unknown(bot, update):
    logger.info(f"Unknown command... by {update.message.from_user.name}")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Perdón! Pero no entiendo ese comando"
    )


def start(bot, update):
    logger.info(f"Starting comand... by {update.message.from_user.name}")
    username = update.message.from_user.name
    user_id = update.message.from_user.id
    user = User.get_or_create(
        username=username,
        id=user_id
    )
    update.message.reply_text(
        f"Hola! Soy edu_bot! Nice to meet you "
        f"{update.message.from_user.name}! "
        "podés usar los commandos:\n /btc, /caps, /dolar, /gasto (solo eduzen)"
    )


def ayuda(bot, update):
    logger.info(f"Help comand... by {update.message.from_user.name}")
    bot.send_message(
        chat_id=update.message.chat_id,
        text=(
            "las opciones son:\n"
            "/start te saluda y boludeces \n"
            "/btc cotización del btc\n"
            "/dolar cotización del dolar\n"
            "/caps palabra a convertir en mayúscula\n"
            "/gasto cuanto salio y nombre de gasto ej: 55 1/4 helado\n"
        )
    )


def btc(bot, update):
    logger.info(f"https://coinbin.org/btc... by {update.message.from_user.name}")
    btc = requests.get('https://coinbin.org/btc')
    btc_data = defaultdict(str)
    if btc.status_code == requests.codes.ok:
        btc_data.update(btc.json()['coin'])

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"1 btc --> U$S {btc_data['usd']}"
    )


def echo(bot, update):
    logger.info(f"echo... by {update.message.from_user.name}")
    if update.message.new_chat_members:
        answer = 'Bienvenido {}'.format(update.message.from_user.name)
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    msg = update.message.text.lower()
    if 'hola' in msg or 'hi' in msg or 'holis' in msg:
        answer = f'Hola {update.message.from_user.name}'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    if 'bye' in msg or 'chau' in msg or 'nos vemos' in msg:
        answer = f'nos vemos humanoide {update.message.from_user.name}!'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    q = (
        'qué haces', 'que hacés', 'que hace', 'todo bien?', 'como va',
        'cómo va', 'todo piola?', 'todo bien=', 'todo bien'
    )
    answer = f'Por ahora piola {update.message.from_user.name}'

    for mark in q:
        if mark in msg:
            bot.send_message(chat_id=update.message.chat_id, text=answer)
            return

    bot.send_message(
        chat_id=update.message.chat_id,
        text='sabés que no te capto'
    )


def caps(bot, update, args):
    logger.info(f"caps... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("No enviaste nada!")
        return

    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    logger.info(f"inline_caps... by {update.message.from_user.name}")
    query = update.inline_query.query
    if not query:
        return

    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    logger.info("Starting main...")
    updater = Updater(token=TOKEN)
    logger.info("Created updater for %s", updater.bot.name)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    users_handler = CommandHandler('users', get_users)
    ayuda_handler = CommandHandler('ayuda', ayuda)
    dolar_handler = CommandHandler('dolar', dolar)
    btc_handler = CommandHandler('btc', btc)
    question_handler = CommandHandler('questions', get_questions)
    expense_handler = CommandHandler('gasto', expense, pass_args=True)
    add_question_handler = CommandHandler('add_question', add_question, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(users_handler)
    dispatcher.add_handler(ayuda_handler)
    dispatcher.add_handler(dolar_handler)
    dispatcher.add_handler(btc_handler)
    dispatcher.add_handler(question_handler)
    dispatcher.add_handler(add_question_handler)
    dispatcher.add_handler(expense_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)

    # log all errors
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    try:
        # execute only if run as a script
        main()
    except Exception:
        logger.exception('bye bye')
