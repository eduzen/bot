import logging

from telegram_bot import TelegramBot

from commands import (
    btc, caps, ayuda, dolar, start, expense,
    get_questions, get_users, add_question
)
from message import (
    parse_msg
)

logger = logging.getLogger()

handler = logging.StreamHandler()
fh = logging.FileHandler('bot.log')

formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.INFO)


def main():
    logger.info("Starting main...")
    commands = {
        'btc': btc,
        'caps': caps,
        'ayuda': ayuda,
        'dolar': dolar,
        'start': start,
        'users': get_users,
        'questions': get_questions,
        'gasto': expense,
        'add_question': add_question
    }
    message_handlers = [parse_msg, ]

    bot = TelegramBot()
    bot.register_commands(commands)
    bot.register_message_handler(message_handlers)
    bot.start()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logger.exception('bye bye')
