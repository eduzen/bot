import logging
import requests
from collections import defaultdict
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from telegram import ReplyKeyboardMarkup

from keys import TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def unknown(bot, update):
    logging.info("unknown...")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Perdón! Pero no entiendo ese comando"
    )


def start(bot, update):
    logging.info("Starting...")
    bot.send_message(chat_id=update.message.chat_id, text="Hola! Soy edu_bot!")
    update.message.reply_text("I'm a bot, Nice to meet you!")


def btc(bot, update):
    logging.info("https://coinbin.org/btc...")
    btc = requests.get('https://coinbin.org/btc')
    btc_data = defaultdict(str)
    if btc.status_code == requests.codes.ok:
        btc_data.update(btc.json()['coin'])

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"1 btc --> U$S {btc_data['usd']}"
    )


def echo(bot, update):
    logging.info("echo...")
    if update.message.new_chat_members:
        answer = 'Bienvenido {}'.format(update.message.from_user.name)
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    msg = update.message.text.lower()
    if 'hola' in msg or 'hi' in msg or 'holis' in msg:
        answer = 'Hola {}'.format(update.message.from_user.name)
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update, args):
    logging.info("caps...")
    if not args:
        update.message.reply_text("No enviaste nada!")
        return

    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    logging.info("inline_caps...")
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


def main():
    logging.info("Starting main...")
    updater = Updater(token=TOKEN)
    logging.info("Created updater for %s", updater.bot.name)
    dispatcher = updater.dispatcher

    echo_handler = MessageHandler(Filters.text, echo)
    start_handler = CommandHandler('start', start)
    btc_handler = CommandHandler('btc', btc)
    # pass_args=True is required to let the handler know that you want it
    # to pass the list of command arguments to the callback
    caps_handler = CommandHandler('caps', caps, pass_args=True)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(btc_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(caps_handler)
    dispatcher.add_handler(unknown_handler)
    dispatcher.add_handler(inline_caps_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # execute only if run as a script
    main()
