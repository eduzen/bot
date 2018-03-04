import logging

logger = logging.getLogger(__name__)


def echo(bot, update, args):
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
