from emoji import emojize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from eduzenbot.menus.builder import build_menu
from eduzenbot.models import Question


async def q_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a menu with options."""
    keyboard = [
        InlineKeyboardButton("Only questions", callback_data="questions"),
        InlineKeyboardButton("Questions & answers", callback_data="answer"),
        InlineKeyboardButton("How to use it", callback_data="help"),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please choose:", reply_markup=reply_markup)


def get_questions(answer: bool | None = None) -> str:
    """Retrieve questions or questions with answers from the database."""
    punch = emojize(":punch:")

    if not answer:
        qs = "\n".join([f"{q.id}: {q.question}" for q in Question.select()])
        return f"{qs}\n{punch}"

    qs = "\n".join([f"{q.id}: {q.question} | {q.answer}" for q in Question.select()])
    return f"{qs}\n{punch}"


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses from the inline menu."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query to avoid timeout

    selected = query.data

    if selected == "questions":
        answer = get_questions()
    elif selected == "answer":
        answer = get_questions(answer=True)
    elif selected == "help":
        answer = (
            "Primero debes agregar una pregunta usando `/add_question <tu pregunta>`\n"
            "Esto te va a responder con un id, por ejemplo 1\n"
            "Para agregar la respuesta a tu pregunta usamos ese id: `/add_answer 1 <tu respuesta>`\n"
            "Despues resta hablarle al bot `tu pregunta? @eduzenbot`"
        )

    await query.edit_message_text(
        text=f"{answer}",
        parse_mode="Markdown",
    )
