import logging

from .api.expenses import send_expense
from .api.dolar import get_dolar
from .api.btc import get_btc
from .db import User, Question

logger = logging.getLogger(__name__)


def dolar(bot, update, args):
    logger.info(f"Dollar... by {update.message.from_user.name}")

    text = get_dolar()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )


def btc(bot, update, args):
    logger.info(f"Btc... by {update.message.from_user.name}")

    text = get_btc()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )


def get_users(bot, update, args):
    logger.info(f"Get_users... by {update.message.from_user.name}")

    txt = [user.username for user in User.select()]
    bot.send_message(
        chat_id=update.message.chat_id,
        text=", ".join(txt)
    )


def get_questions(bot, update, args):
    try:
        logger.info(f"Get_questions... by {update.message.from_user.name}")

        qs = [
            f"{q.id}: {q.questions}"
            for q in Question.select()
        ]

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
    logger.info(f"Add_question... by {update.message.from_user.name}")
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
            question=" ".join(map(str, args)),
            answer="empty"
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


def unknown(bot, update, args):
    logger.info(f"Unknown command... by {update.message.from_user.name}")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Perdón! Pero no entiendo ese comando"
    )


def start(bot, update, args):
    logger.info(f"Starting comand... by {update.message.from_user.name}")
    username = update.message.from_user.name
    user_id = update.message.from_user.id
    user = User.get_or_create(
        username=username,
        id=user_id
    )
    update.message.reply_text(
        f"Hola! Soy edu_bot!n\n"
        f"Encantado de conocerte {user.username}!\n"
        "Haciendo click en el icono de la contrabarra \\ podés ver algunos"
        "algunos de los commandos que podés usar:\n"
        "Por ejemplo: /btc, /caps, /dolar"
    )


def ayuda(bot, update, args):
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


def caps(bot, update, args):
    logger.info(f"caps... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("No enviaste nada!")
        return

    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)
