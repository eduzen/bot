"""
start - start
caps - caps
help - ayuda
msg - send_private_msg
restart - restart
"""
import logging
import os
import sys
from threading import Thread

import peewee
from telegram import Bot, Update
from telegram.ext import CallbackContext

from eduzenbot.auth.restricted import restricted
from eduzenbot.models import User

logger = logging.getLogger("rich")


def send_private_msg(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args:
        update.message.reply_text("Se usa: /msg <:user_id> <:msg>")
        return

    if len(args) < 2:
        update.message.reply_text("Se usa: /msg <:user_id> <:msg>")
        return

    context.bot.send_message(args[0], args[1])


def get_or_create_user(user: User) -> User | None:
    data = user.to_dict()
    created = None
    user = None

    try:
        user, created = User.get_or_create(**data)
    except peewee.IntegrityError:
        logger.warn("User already created")

    if user and created:
        logger.debug("User created. Id %s", user.id)
        return user

    try:
        user = User.update(**data)
        logger.debug("User updated")
        return user

    except Exception:
        logger.exception("User cannot be updated")


def start(update: Update, context: CallbackContext) -> None:
    logger.info(f"Starting comand... by {update.message.from_user.name}")
    user = update.message.from_user

    update.message.reply_text(
        f"Hola! Soy edu_bot!\n"
        f"Encantado de conocerte {user.username}!\n"
        "Haciendo click en el icono de la contrabarra \\ podés ver algunos"
        "algunos de los commandos que podés usar:\n"
        "Por ejemplo: /btc, /cambio, /caps, /dolar, /clima, /subte, /transito, /trenes"
    )


def ayuda(update: Update, context: CallbackContext) -> None:
    logger.info(f"Help comand... by {update.message.from_user.name}")
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=(
            "las opciones son:\n"
            "/start te saluda y boludeces \n"
            "/btc cotización del btc\n"
            "/dolar cotización del dolar\n"
            "/caps palabra a convertir en mayúscula\n"
            "/cambio varias divisas\n"
            "/trenes estado de trenes de baires\n"
            "/transito estado del transito de baires\n"
            "/gasto cuanto salio y nombre de gasto ej: 55 1/4 helado\n"
        ),
    )


def caps(update: Update, context: CallbackContext) -> None:
    logger.info(f"caps... by {update.message.from_user.name}")
    if not context.args:
        update.message.reply_text("No enviaste nada!")
        return

    text_caps = " ".join(context.args).upper()
    context.bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def stop_and_restart(bot: Bot) -> None:
    """Gracefully stop the Updater and replace the current process with a new one"""
    logger.info("Restarting eduzenbot...")
    bot.updater.stop()
    logger.info("Updater stop...")
    os.execl(sys.executable, sys.executable, *sys.argv)


@restricted
def restart(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("hey, I'm going to restart myself...")
    Thread(target=stop_and_restart).start()
