"""
users - get_users
questions - get_questions
edit_question - edit_question
remove - remove_question
add_question - add_question
add_answer - add_answer
edit_question - edit_question

"""
import structlog
from telegram import ChatAction

from eduzen_bot.auth.restricted import restricted
from eduzen_bot.decorators import create_user
from eduzen_bot.models import Question, User

logger = structlog.get_logger(filename=__name__)


@restricted
@create_user
def get_users(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    try:
        txt = "\n".join([str(user) for user in User.select()])
    except Exception:
        logger.error("DB problem")
        txt = "No hay usuarios"

    context.bot.send_message(chat_id=update.message.chat_id, text=txt)


@create_user
def get_questions(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    try:
        qs = "\n".join([f"{q.id}: {q.question} | {q.answer} | by {q.user}" for q in Question.select()])
        context.bot.send_message(chat_id=update.message.chat_id, text=f"{qs}")
    except Exception:
        logger.exception("Problems with get_questions")
        context.bot.send_message(chat_id=update.message.chat_id, text="Mmm algo malo pasó")


@create_user
def edit_question(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if not context.args:
        update.message.reply_text("Se usa: /edit_question <:id_pregunta> <:tu_respuesta>")
        return

    if len(args) < 2:
        update.message.reply_text("Se usa: /edit_question <:id_pregunta> <:tu_respuesta>")
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        context.bot.send_message(chat_id=update.message.chat_id, text="El primer parametro tiene que ser un id")

    try:
        q = Question.get_by_id(question_id)
    except Exception:
        context.bot.send_message(chat_id=update.message.chat_id, text="No existe pregunta con ese id")

    q.question = " ".join(list(args[1:]))
    q.save()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode="Markdown",
        text=f"``` {q.question} guardada! ```",
    )


def add_answer(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    logger.info(f"Add_question... by {update.message.from_user.name}")
    if not context.args:
        update.message.reply_text("Se usa: /add_answer <:id_pregunta> <:tu_respuesta>")
        return

    if len(args) < 1:
        update.message.reply_text("Se usa: /add_answer <:id_pregunta> <:tu_respuesta>")
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        context.bot.send_message(chat_id=update.message.chat_id, text="El primer parametro tiene que ser un id")

    try:
        q = Question.get_by_id(question_id)
    except Exception:
        context.bot.send_message(chat_id=update.message.chat_id, text="No existe pregunta con ese id")

    q.answer = " ".join(list(args[1:]))
    q.save()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode="Markdown",
        text=f"``` {q.question} guardada! ```",
    )


@create_user
def add_question(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if not context.args:
        update.message.reply_text("Se usa: /add_question <:tu_pregunta>")
        return

    username = update.message.from_user.name
    user_id = update.message.from_user.id
    try:
        user = User.get_or_create(username=username, id=user_id)
        user = user[0]
    except Exception:
        update.message.reply_text("No disponible")
        return

    try:
        question = " ".join(map(str, args))
        if "?" not in question:
            question = f"{question}?"

        q = Question.get_or_create(user=user.id, question=question)
        q = q[0]
        logger.info("pregunta creada con id: %i", q.id)
        txt = f"Pregunta creada con id: {q.id}"
        context.bot.send_message(chat_id=update.message.chat_id, text=txt)
    except Exception:
        logger.exception("no pudimos agregar preguntas")
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos agregar tu pregunta")


@create_user
def remove_question(update, context, *args, **kwargs):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if not context.args:
        update.message.reply_text("Se usa /remove <:id>")
        return

    if len(args) < 1:
        update.message.reply_text("Se usa /remove <:id>")
        return

    try:
        question_id = int(args[0])
    except (ValueError, TypeError):
        context.bot.send_message(chat_id=update.message.chat_id, text="El primer parametro tiene que ser un id")

    try:
        q = Question.get(Question.id == question_id).delete_instance()
        if q == 1:
            logger.info("pregunta eliminada")
            context.bot.send_message(chat_id=update.message.chat_id, text="pregunta eliminada")
    except Exception:
        logger.exception("no pudimos eliminar tu pregunta")
        context.bot.send_message(chat_id=update.message.chat_id, text="No pudimos agregar tu pregunta")
