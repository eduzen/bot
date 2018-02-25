import logging
import requests
from collections import defaultdict
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

from keys import TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def unknown(bot, update):
    logger.info("Unknown command...")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Perdón! Pero no entiendo ese comando"
    )


def start(bot, update):
    logger.info("Starting comand...")
    update.message.reply_text(
        f"Hola! Soy edu_bot! Nice to meet you"
        f"{update.message.from_user.name}!"
        "podés usar los commandos /btc, /caps"
    )


def ayuda(bot, update):
    logger.info("Help comand...")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="las opciones son /start\n/btc\n/caps"
    )


def btc(bot, update):
    logger.info("https://coinbin.org/btc...")
    btc = requests.get('https://coinbin.org/btc')
    btc_data = defaultdict(str)
    if btc.status_code == requests.codes.ok:
        btc_data.update(btc.json()['coin'])

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"1 btc --> U$S {btc_data['usd']}"
    )


def echo(bot, update):
    logger.info("echo...")
    if update.message.new_chat_members:
        answer = 'Bienvenido {}'.format(update.message.from_user.name)
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    msg = update.message.text.lower()
    if 'hola' in msg or 'hi' in msg or 'holis' in msg:
        answer = f'Hola {update.message.from_user.name}'
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    q = (
        'qué haces', 'que hacés', 'que hace', 'todo bien?', 'como va',
        'cómo va', 'todo bien?'
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
    logger.info("caps...")
    if not args:
        update.message.reply_text("No enviaste nada!")
        return

    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    logger.info("inline_caps...")
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
    ayuda_handler = CommandHandler('ayuda', ayuda)
    btc_handler = CommandHandler('btc', btc)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ayuda_handler)
    dispatcher.add_handler(btc_handler)

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
