from handlers.commands.questions import q_menu
from handlers.commands.commands import (
    btc,
    caps,
    ayuda,
    dolar,
    start,
    expense,
    get_questions,
    get_users,
    add_question,
    add_answer,
    cotizaciones,
    weather,
    code,
    subte,
    subte_novedades,
    remove_question,
    edit_question,
)

COMMANDS = {
    "caps": caps,
    "ayuda": ayuda,
    "start": start,
    "users": get_users,
    "gasto": expense,
    "code": code,
    "question_menu": q_menu,
    "qmenu": q_menu,
}
