import logging

from telegram_bot import TelegramBot

from commands import (
    btc, caps, ayuda, dolar, start, expense,
    get_questions, get_users, add_question
)
from message import (
    parse_msg
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting main...")
    bot = TelegramBot()
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
    message_handlers = {
        'parse_msg', parse_msg
    }
    bot.register_commands(commands)
    bot.register_message_handler(message_handlers)
    bot.start()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logger.exception('bye bye')
