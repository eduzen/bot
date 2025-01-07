"""
start - start
help - ayuda
msg - send_private_msg
restart - restart
"""

import os
import sys
from threading import Thread

import logfire
from telegram import Update
from telegram.ext import ContextTypes

from eduzenbot.auth.restricted import restricted


async def send_private_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Se usa: /msg <:user_id> <:msg>")
        return

    user_id = args[0]
    msg = " ".join(args[1:])  # Combine all remaining args as the message
    try:
        await context.bot.send_message(chat_id=user_id, text=msg)
        await update.message.reply_text(f"Mensaje enviado a {user_id}")
    except Exception as e:
        logfire.error(f"Error sending message: {e}")
        await update.message.reply_text("Error al enviar el mensaje.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logfire.info(f"Starting command... by {update.effective_user.username}")
    user = update.effective_user

    await update.message.reply_text(
        f"Hola! Soy edu_bot!\n"
        f"Encantado de conocerte {user.username}!\n"
        "Haciendo click en el icono de la contrabarra \\ podés ver algunos"
        "de los comandos que podés usar:\n"
        "Por ejemplo: /btc, /caps, /dolar, /clima, /subte, /transito, /trenes"
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logfire.info(f"Help command... by {update.effective_user.username}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Las opciones son:\n"
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
    """Gracefully stop the bot and replace the current process with a new one"""
    logfire.info("Restarting eduzenbot...")
    os.execl(sys.executable, sys.executable, *sys.argv)


@restricted
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hey, I'm going to restart myself...")
    Thread(target=stop_and_restart).start()
