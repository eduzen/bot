import logging

from telegram import ChatAction

from api.expenses import send_expense
from api.dolar import get_dolar, parse_bnc
from api.btc import get_btc
from api.weather import get_weather
from api.twitter import get_subte, get_subte_html
from db import User, Question
from auth.restricted import restricted


logger = logging.getLogger(__name__)


def weather(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Weather... by {update.message.from_user.name}")

    text = get_weather()
    if not text:
        return

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )


def subte_novedades(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Weather... by {update.message.from_user.name}")

    try:
        amount = int(args[0])
    except Exception:
        amount = 4

    text = get_subte(amount)
    if not text:
        return

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )


def subte(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Subte... by {update.message.from_user.name}")

    try:
        amount = int(args[0])
    except Exception:
        amount = 4

    text = get_subte_html(amount)
    if not text:
        return

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text=text
    )

@restricted
def code(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Code... by {update.message.from_user.name}")

    if not args:
        return
    args = " ".join(list(args))

    args = f"```python\n{args} \n```"

    bot.send_message(
        chat_id=update.message.chat_id,
        text=args,
        parse_mode='Markdown',
        disable_notification=True,
    )


def dolar(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Dollar... by {update.message.from_user.name}")

    text = get_dolar()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )


def cotizaciones(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"cotizaciones... by {update.message.from_user.name}")

    data = parse_bnc()

    if not data:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No pudimos conseguir la info"
        )
        return

    bot.send_message(
        chat_id=update.message.chat_id,
        text=data
    )


def btc(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Btc... by {update.message.from_user.name}")

    text = get_btc()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text
    )


def get_users(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Get_users... by {update.message.from_user.name}")

    txt = [user.username for user in User.select()]
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Usuarios: , ".join(txt)
    )


def get_questions(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    try:
        logger.info(f"Get_questions... by {update.message.from_user.name}")
        qs = "\n".join([
            f"{q.id}: {q.question} | {q.answer} | by {q.user}"
            for q in Question.select()
        ])
        logger.info(f'questions: {qs}')
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"{qs}"
        )
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Mmm algo malo pasó"
        )


def edit_question(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Edit_question... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("Se usa: /edit_question <:id_pregunta> <:tu_respuesta>")
        return

    if len(args) < 2:
        update.message.reply_text("Se usa: /edit_question <:id_pregunta> <:tu_respuesta>")
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El primer parametro tiene que ser un id"
        )

    try:
        q = Question.get_by_id(question_id)
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No existe pregunta con ese id"
        )

    q.question = " ".join(list(args[1:]))
    q.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text=f"``` {q.question} guardada! ```"
    )


def add_answer(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Add_question... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("Se usa: /add_answer <:id_pregunta> <:tu_respuesta>")
        return

    if len(args) < 1:
        update.message.reply_text("Se usa: /add_answer <:id_pregunta> <:tu_respuesta>")
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El primer parametro tiene que ser un id"
        )

    try:
        q = Question.get_by_id(question_id)
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No existe pregunta con ese id"
        )

    q.answer = " ".join(list(args[1:]))
    q.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text=f"``` {q.question} guardada! ```",
    )


def add_question(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Add_question... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("Se usa: /pregunta <:tu_pregunta>")
        return

    username = update.message.from_user.name
    user_id = update.message.from_user.id
    user = User.get_or_create(
        username=username,
        id=user_id
    )
    user = user[0]
    try:
        question = " ".join(map(str, args))
        if '?' not in question:
            question = f'{question}?'

        q = Question.get_or_create(
            user=user.id,
            question=question,
        )
        q = q[0]
        logger.info("pregunta creada con id: %i", q.id)
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


def remove_question(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Add_question... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text("Se usa /remove <:id>")
        return

    if len(args) < 1:
        update.message.reply_text("Se usa /remove <:id>")
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El primer parametro tiene que ser un id"
        )

    try:
        q = Question.get(Question.id == question_id).delete_instance()
        if q == 1:
            logger.info("pregunta eliminada")
            bot.send_message(
                chat_id=update.message.chat_id,
                text="pregunta eliminada"
            )
    except Exception:
        logger.exception('no pudimos eliminar tu pregunta')
        bot.send_message(
            chat_id=update.message.chat_id,
            text="No pudimos agregar tu pregunta"
        )

@restricted
def expense(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
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
    user = user[0]
    update.message.reply_text(
        f"Hola! Soy edu_bot!\n"
        f"Encantado de conocerte {user.username}!\n"
        "Haciendo click en el icono de la contrabarra \\ podés ver algunos"
        "algunos de los commandos que podés usar:\n"
        "Por ejemplo: /btc, /cambio, /caps, /dolar, /clima, /subte"
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
