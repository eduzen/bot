import logging

logger = logging.getLogger(__name__)


def record_msg(msg):
    logger.info(f"record_msg")
    with open('history.txt', 'a') as f:
        f.write(msg)


def parse_msg(bot, update):
    logger.info(f"echo... by {update.message.from_user.name}")
    if update.message.new_chat_members:
        answer = 'Bienvenido {}'.format(update.message.from_user.name)
        bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    msg = update.message.text.lower()
    msg = f'{update.message.from_user.name}: {msg}\n'
    record_msg(msg)

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
        'cómo va', 'todo piola?', 'todo bien=', 'todo bien', 'como va?',
        'todo piola?', 'que haces?', 'como estas?', 'como esta?'
    )
    answer = f'Por ahora piola {update.message.from_user.name}'

    for mark in q:
        if mark in msg:
            bot.send_message(chat_id=update.message.chat_id, text=answer)
            return


def unknown(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Che, no te entiendo, no existe ese comando!"
    )
