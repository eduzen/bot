"""
start - start
help - ayuda
msg - send_private_msg
restart - restart
"""
import logging
import os
import sys
from threading import Thread

from telegram import Update
from telegram.ext import CallbackContext

from eduzenbot.auth.restricted import restricted

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


def start(update: Update, context: CallbackContext) -> None:
    logger.info(f"Starting comand... by {update.message.from_user.name}")
    user = update.message.from_user

    update.message.reply_text(
        f"Hola! Soy edu_bot!\n"
        f"Encantado de conocerte {user.username}!\n"
        "Haciendo click en el icono de la contrabarra \\ podés ver algunos"
        "algunos de los commandos que podés usar:\n"
        "Por ejemplo: /btc, /caps, /dolar, /clima, /subte, /transito, /trenes"
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


def stop_and_restart() -> None:
    """Gracefully stop the Updater and replace the current process with a new one"""
    logger.info("Restarting eduzenbot...")
    os.execl(sys.executable, sys.executable, *sys.argv)


@restricted
def restart(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("hey, I'm going to restart myself...")
    Thread(target=stop_and_restart).start()
