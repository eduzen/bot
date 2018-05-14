import structlog
from telegram import ChatAction

from models import User, Question

logger = structlog.get_logger(filename=__name__)


def get_users(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Get_users... by {update.message.from_user.name}")

    txt = [user.username for user in User.select()]
    bot.send_message(chat_id=update.message.chat_id, text="Usuarios: , ".join(txt))


def get_questions(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    try:
        logger.info(f"Get_questions... by {update.message.from_user.name}")
        qs = "\n".join(
            [
                f"{q.id}: {q.question} | {q.answer} | by {q.user}"
                for q in Question.select()
            ]
        )
        bot.send_message(chat_id=update.message.chat_id, text=f"{qs}")
    except Exception:
        logger.exception("Problems with get_questions")
        bot.send_message(chat_id=update.message.chat_id, text="Mmm algo malo pasó")


def edit_question(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Edit_question... by {update.message.from_user.name}")
    if not args:
        update.message.reply_text(
            "Se usa: /edit_question <:id_pregunta> <:tu_respuesta>"
        )
        return

    if len(args) < 2:
        update.message.reply_text(
            "Se usa: /edit_question <:id_pregunta> <:tu_respuesta>"
        )
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="El primer parametro tiene que ser un id",
        )

    try:
        q = Question.get_by_id(question_id)
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id, text="No existe pregunta con ese id"
        )

    q.question = " ".join(list(args[1:]))
    q.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode="Markdown",
        text=f"``` {q.question} guardada! ```",
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
            text="El primer parametro tiene que ser un id",
        )

    try:
        q = Question.get_by_id(question_id)
    except Exception:
        bot.send_message(
            chat_id=update.message.chat_id, text="No existe pregunta con ese id"
        )

    q.answer = " ".join(list(args[1:]))
    q.save()

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode="Markdown",
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
    user = User.get_or_create(username=username, id=user_id)
    user = user[0]
    try:
        question = " ".join(map(str, args))
        if "?" not in question:
            question = f"{question}?"

        q = Question.get_or_create(user=user.id, question=question)
        q = q[0]
        logger.info("pregunta creada con id: %i", q.id)
        txt = f"Pregunta creada con id: {q.id}"
        bot.send_message(chat_id=update.message.chat_id, text=txt)
    except Exception:
        logger.exception("no pudimos agregar preguntas")
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos agregar tu pregunta"
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
            text="El primer parametro tiene que ser un id",
        )

    try:
        q = Question.get(Question.id == question_id).delete_instance()
        if q == 1:
            logger.info("pregunta eliminada")
            bot.send_message(chat_id=update.message.chat_id, text="pregunta eliminada")
    except Exception:
        logger.exception("no pudimos eliminar tu pregunta")
        bot.send_message(
            chat_id=update.message.chat_id, text="No pudimos agregar tu pregunta"
        )
